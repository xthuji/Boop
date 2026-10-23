#!/usr/bin/env bash
# =============================================================================
# Boop - 构建与运行工具 (跨平台: macOS / Linux / Windows Git Bash)
# =============================================================================
# 命令:
#   1|b,build     构建桌面应用 (PyInstaller 打包, 自动适配当前平台)
#   2|r,run       构建并前台运行 (Ctrl+C 关闭)
#   3|d,dev       开发模式: 直接 python -m app 前台运行 (Ctrl+C 关闭)
#   4|t,test      运行单元测试 (pytest, 跳过 GUI 自动化测试)
#   5|s,scripts   同步 custom_scripts/ 到 /Applications/Boop.app
#   6|c,clean     清理构建产物
#   7|i,install   安装依赖包 (requirements.txt + PyInstaller + pytest)
#   0|q|exit      退出
# =============================================================================
# 全部构建/打包/测试逻辑集中在本脚本，CI workflow 只做 runner 引导与产物上传，
# 避免 CI 与本地漂移。母版区与 easy_translate 逐字节一致（Python 桌面应用共享
# 母版），项目差异只写在常量与命令表 / 专属实现两区。
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 脚本位于 <project>/scripts/，项目根目录为其上级目录
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# --- 顶层内联平台探测：差异区常量求值早于函数定义生效（bash 边读边执行），
#     HOST_OS 必须先于 DATA_SEP/APP_DATA_FILES 就绪；母版区 detect_platform
#     为权威实现，此处取法一致仅为常量初始化（NATIVE_* 由母版检测补全）
HOST_OS="$(uname -s 2>/dev/null || echo unknown)"
case "$HOST_OS" in
  Darwin*)              HOST_OS="darwin" ;;
  Linux*)               HOST_OS="linux" ;;
  MINGW*|MSYS*|CYGWIN*) HOST_OS="windows" ;;
  *)                    HOST_OS="unknown" ;;
esac
# ============================================================
# 项目差异区 · 常量与命令表（脚本唯一需要按项目调整的部分）
# ============================================================

# --- 项目标识 ---
APP_NAME="Boop"
APP_DISPLAY_NAME="Boop"
APP_BUNDLE_ID="com.xthuji.boop"
RELEASE_PREFIX=""                 # release 产物命名前缀（留空同 APP_NAME）

# --- 目录与产物 ---
BUILD_DIR="$PROJECT_DIR/build"
# PyInstaller 中间产物 (.app / onedir 目录) 输出到 build/dist，
# release/ 仅保留可分发的发布包 (DMG/tgz/zip)，不再包含 .app
DIST_DIR="$BUILD_DIR/dist"
RELEASE_DIR="$PROJECT_DIR/release"
PYI_WORKPATH="$BUILD_DIR"
VERSION_FILE="$PROJECT_DIR/VERSION"
VERSION=""

# --- Python 解释器与依赖 ---
PYTHON=""
PYTHON_ENV_VAR="BOOP_PYTHON"                  # 显式指定解释器的环境变量名（CI 用）
PYTHON_ENV_VAR_X86_64="BOOP_PYTHON_X86_64"
PREFERRED_PYTHON="${HOME}/miniconda3/envs/python39/bin/python3"
MIN_PYTHON_VERSION="3.9"
DEPS_IMPORT_CHECK="pynput,pyperclip"          # install 命令展示的依赖
RUNTIME_IMPORT_PROBE="import pynput, pyperclip" # ensure_runtime_deps 的就绪探测
NEEDS_TKINTER=1
NEEDS_PYTEST=0                 # boop 用自研 runner（见差异区二 cmd_test），不装 pytest

# --- 构建策略 ---
NEEDS_UNIVERSAL=1                # 1=macOS 探测 x86_64 Python 尝试 universal 构建
MACOS_UNIVERSAL_FORCE=0          # 1=dist 强制 universal，找不到 x86_64 Python 即报错
PLATFORM_SCOPE="all"             # 跨平台产物（mac DMG / linux tgz / win zip）
MACOS_MIN_VERSION="12.0"
MACOSX_DEPLOYMENT_TARGET_DEFAULT="12.0"
PYI_WINDOWED=1
PYI_OPTIMIZE=2
PYI_STRIP=1
PYI_LOG_LEVEL="ERROR"
ENTRY_PY="$PROJECT_DIR/app/__main__.py"

# --- 图标（png=源图，配置后 mac 自动 sips+iconutil 生成 .icns）---
ICON_ICNS="$PROJECT_DIR/icons/icon.icns"
ICON_ICO="$PROJECT_DIR/icons/icon.ico"
ICON_PNG="$PROJECT_DIR/icons/icon_256x256.png"

# --- 产物细节 ---
ADHOC_SIGN=1                     # 1=macOS 构建后 ad-hoc 签名（改 Info.plist 会让 PyInstaller 签名失效）
readonly DMG_IMAGEKEY_ARGS=()    # hdiutil 额外参数（数组，逐项传参）
RELEASE_CLEAN_TARGETS=( "${RELEASE_PREFIX:-$APP_NAME}.app" "${RELEASE_PREFIX:-$APP_NAME}" )
CLEAN_TARGETS=( "$BUILD_DIR" "$RELEASE_DIR" )

# --- add-data 分隔符与资源清单（Windows Git Bash 需原生路径，避免 MSYS 路径漂移）---
if [ "$HOST_OS" = "windows" ]; then
  DATA_SEP=";"
else
  DATA_SEP=":"
fi
_to_native_path() {
  if [ "$HOST_OS" = "windows" ] && command -v cygpath &>/dev/null; then
    cygpath -w "$1"
  else
    echo "$1"
  fi
}

# 隐藏导入（UI 为 tkinter，由 PyInstaller 自动发现；此处仅补充动态导入）
readonly HIDDEN_IMPORTS=(
  "tkinter"
  "tkinter.ttk"
  "pynput"
  "pynput.keyboard"
)

# 无条件排除：不使用 requests/urllib、multiprocessing/asyncio、科学栈与 GUI 框架
readonly EXCLUDE_MODULES=(
  "test" "tkinter.test" "unittest" "doctest"
  "trace" "profile" "pstats" "tabnanny" "pyclbr"
  "pickletools" "zipimport" "modulefinder" "lib2to3"
  "sqlite3"
  "email" "urllib3" "requests"
  "multiprocessing" "asyncio" "concurrent"
  "distutils" "setuptools" "pkg_resources"
  "PyQt5" "PyQt6" "PySide2" "PySide6" "gi" "wx"
  "django" "flask" "fastapi" "sqlalchemy"
  "numpy" "scipy" "pandas" "matplotlib"
)

# 条件排除：本项目无（重型可选依赖一概走 EXCLUDE_MODULES）
readonly OPTIONAL_EXCLUDE_CANDIDATES=()

# --- 测试 / 清理 ---
PYTEST_PATHS=( tests/ )
PYTEST_EXTRA=()
PYTEST_SKIP_EXPR=""             # 不走 pytest：tests/*.py 是手工脚本，pytest 收集恒为 0
CLEAN_EXTRA=()

# --- 菜单与分发 ---
DEFAULT_CMD="dev"
FALLBACK_CMD=""
SRC_FIND_EXPR=( -name '*.py' -o -name 'VERSION' -o -name 'requirements.txt' -o -path '*/custom_scripts/*' -o -path '*/icons/*' -o -path '*/data/*' )

# --- 命令表：序号|别名(逗号分隔)|说明|处理函数（菜单/帮助/分发唯一真源）---
commands=(
  "1|b,build|构建桌面应用 (PyInstaller, 当前平台)|cmd_build"
  "2|r,run|构建并前台运行 (Ctrl+C 关闭)|cmd_run"
  "3|d,dev|开发模式: python -m app 前台运行|cmd_dev"
  "4|t,test|运行单元测试 (pytest, 跳过 GUI 测试)|cmd_test"
  "5|s,scripts|同步 custom_scripts/ 到 /Applications/Boop.app|cmd_scripts"
  "6|c,clean|清理构建产物|cmd_clean"
  "7|i,install|安装依赖包 (requirements + PyInstaller + pytest)|cmd_install"
)
# ============================================================
# 母版区 · 跨项目共享实现（请勿在本文件单独修改）
# ============================================================
# =============================================================================
# 母版区 —— 全项目逐字节一致，禁止本地分叉修改（基准：boop / easy_translate）
# =============================================================================
# Python 桌面应用（tkinter + PyInstaller）共享同一套构建流程。需要项目特化时，
# 一律在上方「常量与命令表」或下方「专属实现」中声明，由脚本生成器统一维护。
# =============================================================================

# --- 平台检测 ---
HOST_OS=""
HOST_ARCH=""
EXT=""
# --platform=<os>/<arch> 会改写 HOST_OS/HOST_ARCH，跨 OS 判定需保留真实宿主值
NATIVE_OS=""
NATIVE_ARCH=""

detect_platform() {
  local os
  os="$(uname -s 2>/dev/null || echo "unknown")"
  case "$os" in
    Darwin*)  HOST_OS="darwin"  ;;
    Linux*)   HOST_OS="linux"   ;;
    MINGW*|MSYS*|CYGWIN*) HOST_OS="windows" ;;
    *)        HOST_OS="unknown" ;;
  esac

  local arch
  arch="$(uname -m 2>/dev/null || echo "unknown")"
  case "$arch" in
    x86_64|amd64)  HOST_ARCH="amd64" ;;
    arm64|aarch64) HOST_ARCH="arm64" ;;
    *)             HOST_ARCH="amd64" ;;
  esac

  if [ "$HOST_OS" = "windows" ]; then
    EXT=".exe"
  else
    EXT=""
  fi

  NATIVE_OS="$HOST_OS"
  NATIVE_ARCH="$HOST_ARCH"
}

detect_platform

# --- 彩色输出（风格 A：标签式，日志量大靠标签过滤）---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# dry-run：由 main 解析 --dry-run 置位；所有外部命令一律经 run() 派发
# （直接传参数数组，绝不 eval，避免内容被 shell 二次解析）
DRY_RUN=false
run() {
  if $DRY_RUN; then
    log_warn "[dry-run] $*"
    return 0
  fi
  "$@"
}

# ============================================================
# Python 解释器检测（可移植，多源回退）
#   <APP>_PYTHON（显式，CI 用）→ 本地优先环境 → 已激活虚拟环境 → PATH python3
# ============================================================
detect_python() {
  if [ -n "$PYTHON" ]; then return 0; fi

  # 1) 显式环境变量
  local env_var="${!PYTHON_ENV_VAR:-}"
  if [ -n "$env_var" ]; then
    if [ -x "$env_var" ]; then
      PYTHON="$env_var"
    elif command -v "$env_var" &>/dev/null; then
      PYTHON="$(command -v "$env_var")"
    else
      log_error "$PYTHON_ENV_VAR 设置了但找不到: $env_var"
    fi
    return 0
  fi

  # 2) 本地优先环境
  if [ -x "${PREFERRED_PYTHON:-}" ]; then
    PYTHON="$PREFERRED_PYTHON"
    return 0
  fi

  # 3) 当前已激活的虚拟环境
  if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
    return 0
  fi

  # 4) PATH 上找 python3
  if command -v python3 &>/dev/null; then
    PYTHON="$(command -v python3)"
    return 0
  fi

  log_error "找不到 Python，请先安装 Python ${MIN_PYTHON_VERSION}+ 或设置 $PYTHON_ENV_VAR 环境变量"
}

detect_python

# ============================================================
# 依赖检查（装 PyInstaller/pytest/requirements 一律走
#   `$PYTHON -m pip`，绝不裸调 pip —— 避免装进错误的 site-packages）
# ============================================================
check_python() {
  $PYTHON -c "import sys; sys.exit(0 if sys.version_info >= tuple(int(x) for x in '${MIN_PYTHON_VERSION}'.split('.')) else 1)" \
    || log_error "Python 版本过低 (需要 ${MIN_PYTHON_VERSION}+, 当前: $($PYTHON --version))"
  log_success "Python: $PYTHON ($($PYTHON --version 2>&1))"
}

check_tkinter() {
  [ "${NEEDS_TKINTER:-1}" = "1" ] || return 0
  $PYTHON -c "import tkinter" 2>/dev/null \
    || log_error "tkinter 不可用 (macOS: brew install python-tk; Ubuntu: apt install python3-tk)"
  log_success "tkinter: ok"
}

# --skip-deps（母版全局选项）：环境已就绪时跳过 pip 自动安装
deps_skip() {
  if [ "${SKIP_DEPS:-false}" = "true" ]; then
    log_info "--skip-deps: 跳过依赖自动安装"
    return 0
  fi
  return 1
}

# 确保 PyInstaller 已安装到目标解释器（避免 PATH 上的 pyinstaller 解释器不匹配）
ensure_pyinstaller() {
  deps_skip && return 0
  if $PYTHON -m pip show -q pyinstaller 2>/dev/null; then
    return 0
  fi
  log_info "首次安装 PyInstaller ..."
  $PYTHON -m pip install -q pyinstaller pyinstaller-hooks-contrib \
    || log_error "PyInstaller 安装失败"
  log_success "PyInstaller 已就绪"
}

# 确保 pytest 已安装（test / install 共用）
ensure_pytest() {
  [ "${NEEDS_PYTEST:-1}" = "1" ] || return 0
  deps_skip && return 0
  if $PYTHON -m pip show -q pytest 2>/dev/null; then
    return 0
  fi
  log_info "首次安装 pytest ..."
  $PYTHON -m pip install -q pytest || log_error "pytest 安装失败"
  log_success "pytest 已就绪"
}

# 项目运行时依赖（首次构建前安装）：探测 import 就绪即跳过
ensure_runtime_deps() {
  [ -f "$PROJECT_DIR/requirements.txt" ] || return 0
  deps_skip && return 0
  if $PYTHON -c "${RUNTIME_IMPORT_PROBE:-pass}" 2>/dev/null; then
    return 0
  fi
  log_info "安装运行时依赖 (requirements.txt) ..."
  $PYTHON -m pip install -q -r "$PROJECT_DIR/requirements.txt" \
    || log_error "依赖安装失败"
  log_success "运行时依赖已就绪"
}

# ============================================================
# 版本管理（VERSION 文件是唯一真源，读取一律去空白）
# ============================================================
get_version() {
  if [ -n "$VERSION" ]; then echo "$VERSION"; return; fi
  if [ -f "$VERSION_FILE" ]; then
    VERSION=$(tr -d '[:space:]' < "$VERSION_FILE")
    if [ -n "$VERSION" ]; then echo "$VERSION"; return; fi
  fi
  VERSION=$(git describe --tags --always --dirty 2>/dev/null || echo "dev")
  echo "$VERSION"
}

# ============================================================
# macOS universal 构建支撑（双解释器 + lipo 合并，以 arm64 为基线）
# ============================================================
# macOS: 查找 x86_64 Python（环境变量声明优先，候选路径逐个用 arch -x86_64 实测）
find_x86_64_python() {
  [ "$HOST_OS" = "darwin" ] || return 1
  # 主机器为 Intel 时，主解释器已是 x86_64，无需也无法构建 universal
  [ "$HOST_ARCH" = "arm64" ] || return 1

  if [ -n "${PYTHON_ENV_VAR_X86_64:-}" ] && [ -n "${!PYTHON_ENV_VAR_X86_64:-}" ]; then
    local px="${!PYTHON_ENV_VAR_X86_64}"
    if arch -x86_64 "$px" -c "import platform; exit(0 if platform.machine() == 'x86_64' else 1)" 2>/dev/null; then
      echo "$px"
      return 0
    fi
    return 1
  fi

  local candidate
  for candidate in \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
    /usr/local/opt/python@3.11/bin/python3 \
    /usr/local/opt/python@3.12/bin/python3 \
    /usr/local/opt/python@3/bin/python3 \
    /usr/local/bin/python3 \
    /usr/local/bin/python; do
    if [ -x "$candidate" ] && \
       arch -x86_64 "$candidate" -c "import platform; exit(0 if platform.machine() == 'x86_64' else 1)" 2>/dev/null; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

# macOS: 将 base 内的 Mach-O 与对照 x86_64 构建的同名文件合并为 universal2
# 说明: universal2 解释器经 PyInstaller 采集后，部分二进制会被裁薄为当前 slice
# 架构；此处仅在 base 缺 x86_64 时从对照文件补齐（base 已含 x86_64 则跳过）。
lipo_ensure_universal() {
  local base="$1" x86_bin="$2" label="${3:-$1}"
  [ -f "$base" ] && [ -f "$x86_bin" ] || return 0
  # base 已是 universal2（含 x86_64）则无需处理
  lipo -archs "$base" 2>/dev/null | grep -qw 'x86_64' && return 0
  # 两者必须均为 Mach-O，否则 lipo 报错（非二进制文件直接忽略）
  local a="${base}.arm64" x="${base}.x86_64" o="${base}.universal"
  lipo -thin arm64  "$base"    -output "$a" 2>/dev/null || { rm -f "$a" "$x" "$o"; return 0; }
  lipo -thin x86_64 "$x86_bin" -output "$x" 2>/dev/null || { rm -f "$a" "$x" "$o"; return 0; }
  if lipo -create "$a" "$x" -output "$o" 2>/dev/null; then
    mv "$o" "$base"
    log_info "  补齐 universal2: $label"
  fi
  rm -f "$a" "$x" "$o" 2>/dev/null || true
}

# macOS: 以 arm64 slice 为完整基线（含 Info.plist/资源/框架），遍历 final .app 内
# 所有 Mach-O，与 x86_64 slice 中同路径文件合并，得到完整 universal2 bundle
assemble_universal_app() {
  local final_app="$1" x86_stage="$2"
  local f rel
  while IFS= read -r f; do
    rel="${f#"$final_app"/}"
    [ -f "$x86_stage/$rel" ] || continue
    lipo_ensure_universal "$f" "$x86_stage/$rel" "$rel" || true
  done < <(
    find "$final_app/Contents" -type f \
      \( -path '*/MacOS/*' -o -name '*.so' -o -name '*.dylib' \
         -o -path '*/Python.framework/Versions/*/Python' \) \
      2>/dev/null
  )
}

# ============================================================
# 图标处理
# ============================================================
# macOS: 从 PNG 源图生成 .icns（sips 缩放各尺寸 + iconutil 打包）。
# 无源图或缺工具时跳过，回退 PyInstaller 默认图标，不阻断构建。
ensure_icns() {
  local png_src="$1" icns_out="$2"
  [ -f "$png_src" ] || { log_warn "未找到 $png_src，跳过图标生成"; return 0; }
  if ! command -v sips &>/dev/null || ! command -v iconutil &>/dev/null; then
    log_warn "缺少 sips/iconutil，无法生成 .icns（将使用默认图标）"
    return 0
  fi

  mkdir -p "$BUILD_DIR"
  log_info "从 ${png_src#$PROJECT_DIR/} 生成 ${icns_out#$PROJECT_DIR/} ..."
  local iconset="$BUILD_DIR/appicon.iconset"
  rm -rf "$iconset" "$icns_out"
  mkdir -p "$iconset"

  # iconutil 要求的标准命名与尺寸
  local _n _px
  local -a specs=(
    "icon_16x16.png 16" "icon_16x16@2x.png 32"
    "icon_32x32.png 32" "icon_32x32@2x.png 64"
    "icon_128x128.png 128" "icon_128x128@2x.png 256"
    "icon_256x256.png 256" "icon_256x256@2x.png 512"
    "icon_512x512.png 512" "icon_512x512@2x.png 1024"
  )
  local spec
  for spec in "${specs[@]}"; do
    _n="${spec% *}"; _px="${spec#* }"
    sips -z "$_px" "$_px" "$png_src" --out "$iconset/$_n" >/dev/null 2>&1 || true
  done

  if iconutil -c icns "$iconset" -o "$icns_out" 2>/dev/null && [ -f "$icns_out" ]; then
    log_success "应用图标已生成: $icns_out"
  else
    log_warn "iconutil 生成 .icns 失败（将使用默认图标）"
    rm -f "$icns_out"
  fi
  rm -rf "$iconset"
}

# 按当前平台选择 PyInstaller --icon 参数（纯路径决策，不产生任何日志——
# 本函数经 $(...) 命令替换取值，stdout 必须只含单个路径）
get_platform_icon_args() {
  if [ "$HOST_OS" = "darwin" ]; then
    if [ -n "${ICON_ICNS:-}" ] && [ -f "$ICON_ICNS" ]; then
      echo "$ICON_ICNS"; return
    fi
    # PNG 源图：由 prepare_app_icon 预先生成 .icns
    if [ -n "${ICON_PNG:-}" ] && [ -f "$BUILD_DIR/${APP_NAME}.icns" ]; then
      echo "$BUILD_DIR/${APP_NAME}.icns"
    fi
  elif [ "$HOST_OS" = "windows" ] && [ -n "${ICON_ICO:-}" ] && [ -f "$ICON_ICO" ]; then
    echo "$ICON_ICO"
  elif [ "$HOST_OS" = "linux" ] && [ -n "${ICON_PNG:-}" ] && [ -f "$ICON_PNG" ]; then
    echo "$ICON_PNG"
  fi
}

# macOS: 配置了 PNG 源图且未提供预制 .icns 时，构建前现生成（日志在此消化，
# 不进入 get_platform_icon_args 的返回值）
prepare_app_icon() {
  [ "$HOST_OS" = "darwin" ] || return 0
  [ -n "${ICON_ICNS:-}" ] && [ -f "$ICON_ICNS" ] && return 0
  [ -n "${ICON_PNG:-}" ] && [ -f "$ICON_PNG" ] || return 0
  ensure_icns "$ICON_PNG" "$BUILD_DIR/${APP_NAME}.icns"
}

# ============================================================
# PyInstaller 构建
# ============================================================
# 清理旧的 App 中间产物（仅清理 build/dist，不影响发布包与 universal 临时 stage）
clean_app_artifacts() {
  $DRY_RUN && return 0
  rm -rf "$DIST_DIR/${APP_NAME}.app" \
    "$DIST_DIR/${APP_NAME}" \
    "$DIST_DIR/${APP_NAME}${EXT}"
}

# 单架构构建：target_arch 可为 arm64/x86_64（mac 交叉时加 arch -x86_64 前缀）
pyinstaller_build_arch() {
  local target_arch="${1:-$HOST_ARCH}"
  local py="${2:-$PYTHON}"
  local version
  version=$(get_version)

  ensure_runtime_deps
  if ! $py -m pip show -q pyinstaller 2>/dev/null; then
    log_info "为 $target_arch Python 安装 PyInstaller ..."
    $py -m pip install -q pyinstaller pyinstaller-hooks-contrib \
      || log_error "PyInstaller 安装失败 ($target_arch)"
  fi

  local args=(
    --name "$APP_NAME"
    --onedir
    -y
    --workpath "${PYI_WORKPATH:-$BUILD_DIR}"
    --distpath "$DIST_DIR"
    --noconfirm
    --log-level="${PYI_LOG_LEVEL:-WARN}"
  )
  [ "${PYI_WINDOWED:-1}" = "1" ] && args+=(--windowed)
  [ -n "${PYI_OPTIMIZE:-}" ] && args+=(--optimize="$PYI_OPTIMIZE")
  [ "${PYI_STRIP:-1}" = "1" ] && args+=(--strip)

  for module in ${EXCLUDE_MODULES[@]+"${EXCLUDE_MODULES[@]}"}; do
    args+=(--exclude-module="$module")
  done

  # 条件排除：可选轻型依赖，环境里没有的才排除，有的随包打入
  for module in ${OPTIONAL_EXCLUDE_CANDIDATES[@]+"${OPTIONAL_EXCLUDE_CANDIDATES[@]}"}; do
    if ! $py -c "import $module" 2>/dev/null; then
      args+=(--exclude-module="$module")
    fi
  done

  for file in ${APP_DATA_FILES[@]+"${APP_DATA_FILES[@]}"}; do
    args+=(--add-data "$file")
  done

  for module in ${HIDDEN_IMPORTS[@]+"${HIDDEN_IMPORTS[@]}"}; do
    args+=(--hidden-import "$module")
  done

  # 项目专属参数：声明式清单（差异区直接追加）+ 函数钩子（pyglossary 随包等
  # 需运行时探测的注入），两者都空时零开销
  args+=( ${PYI_EXTRA_ARGS[@]+"${PYI_EXTRA_ARGS[@]}"} )
  hook_pyi_extra "$py"

  # macOS 特定
  if [ "$HOST_OS" = "darwin" ]; then
    args+=(--osx-bundle-identifier "$APP_BUNDLE_ID")
    export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-${MACOSX_DEPLOYMENT_TARGET_DEFAULT:-$MACOS_MIN_VERSION}}"
    log_info "  MACOSX_DEPLOYMENT_TARGET=$MACOSX_DEPLOYMENT_TARGET (arch=$target_arch)"
  fi

  local icon
  prepare_app_icon
  icon=$(get_platform_icon_args)
  if [ -n "$icon" ]; then
    args+=(--icon "$icon")
    log_info "  App 图标: $icon"
  else
    log_warn "  未找到可用图标，将使用 PyInstaller 默认图标"
  fi

  [ -f "$ENTRY_PY" ] || log_error "未找到入口脚本: $ENTRY_PY"
  args+=("$ENTRY_PY")

  log_info "PyInstaller 构建 ($APP_NAME, version=$version, arch=$target_arch)..."

  # macOS 交叉构建时，确保 Python 以目标架构运行
  local arch_prefix=""
  if [ "$HOST_OS" = "darwin" ] && [ "$target_arch" = "x86_64" ]; then
    arch_prefix="arch -x86_64"
  fi

  # shellcheck disable=SC2086
  if ! $arch_prefix $py -m PyInstaller "${args[@]}"; then
    log_error "PyInstaller 构建失败 ($target_arch)"
  fi
  log_success "PyInstaller 构建完成 ($target_arch)"
}

# PyInstaller 构建入口：macOS 按策略尝试 universal，其余单架构
pyinstaller_build() {
  if [ "$HOST_OS" = "darwin" ] && [ "${NEEDS_UNIVERSAL:-0}" = "1" ]; then
    # universal 仅在解释器以 arm64 运行（Apple Silicon）时才有意义，
    # 否则（Intel 机器）强行构建会误入双架构分支，导致向 Homebrew Python
    # 安装 PyInstaller 触发 PEP 668 externally-managed-environment 错误
    local main_py_arch
    main_py_arch=$("$PYTHON" -c "import platform; print(platform.machine())" 2>/dev/null || echo "")

    local x86_py=""
    if [ "$main_py_arch" = "arm64" ]; then
      x86_py=$(find_x86_64_python 2>/dev/null || echo "")
    fi

    if [ -n "$x86_py" ]; then
      log_info "检测到 x86_64 可运行解释器: $x86_py → 构建 universal binary"

      # 依赖与 PyInstaller：universal2 解释器（python.org）下 arm64/x86_64 共享
      # 同一 site-packages，装一次即可；仅当两 slice 用不同解释器时才为 x86_64 补装
      ensure_runtime_deps
      ensure_pyinstaller
      if [ "$x86_py" != "$PYTHON" ] && ! $x86_py -m pip show -q pyinstaller 2>/dev/null; then
        log_info "为 x86_64 Python 安装 PyInstaller ..."
        $x86_py -m pip install -q pyinstaller pyinstaller-hooks-contrib \
          || log_error "x86_64 PyInstaller 安装失败"
      fi

      local arm64_stage="$BUILD_DIR/stage_arm64"
      local x86_stage="$BUILD_DIR/stage_x86_64"
      local final_app="$DIST_DIR/${APP_NAME}.app"

      # 1) arm64 slice → stage_arm64
      log_info "=== 构建 arm64 slice ==="
      clean_app_artifacts
      pyinstaller_build_arch "arm64" "$PYTHON"
      { [ -d "$final_app" ] || $DRY_RUN; } || log_error "arm64 .app 未找到"
      rm -rf "$arm64_stage"; run mv "$final_app" "$arm64_stage"

      # 2) x86_64 slice → stage_x86_64
      log_info "=== 构建 x86_64 slice ==="
      clean_app_artifacts
      pyinstaller_build_arch "x86_64" "$x86_py"
      { [ -d "$final_app" ] || $DRY_RUN; } || log_error "x86_64 .app 未找到"
      rm -rf "$x86_stage"; run mv "$final_app" "$x86_stage"

      # 3) 以 arm64 bundle 为完整基线，按缺失架构补齐所有 Mach-O
      log_info "组装 universal .app (以 arm64 slice 为基线) ..."
      rm -rf "$final_app"
      run cp -R "$arm64_stage" "$final_app"
      if ! $DRY_RUN; then
        assemble_universal_app "$final_app" "$x86_stage"
        chmod +x "$final_app/Contents/MacOS/$APP_NAME"
        lipo -info "$final_app/Contents/MacOS/$APP_NAME" || true
      fi

      # 4) 合并后二进制已变更，重新 ad-hoc 签名
      if command -v codesign &>/dev/null; then
        run codesign --force --deep --sign - --timestamp=none "$final_app" \
          || log_warn "universal .app ad-hoc 签名失败（仅提示）"
      fi

      if $DRY_RUN; then
        rm -rf "$arm64_stage" "$x86_stage"
        log_success "[dry-run] universal 流程演练完成"
        return 0
      fi
      rm -rf "$arm64_stage" "$x86_stage"
      log_success "Universal .app 构建完成 (arm64 + x86_64)"
      return 0
    fi

    # dist 强制 universal（MACOS_UNIVERSAL_FORCE=1）时找不到 x86_64 Python 即报错
    if [ "${MACOS_UNIVERSAL_FORCE:-0}" = "1" ]; then
      log_error "dist 要求 universal 构建，但未找到可用的 x86_64 Python（设置 $PYTHON_ENV_VAR_X86_64 或安装 python.org universal2 解释器）"
    fi

    if [ "$main_py_arch" = "arm64" ]; then
      log_info "未检测到 x86_64 Python，仅构建 $main_py_arch"
    else
      log_info "主解释器架构为 $main_py_arch (非 Apple Silicon)，跳过 universal 构建"
    fi
  fi

  # 非 macOS 或未尝试 universal: 单架构构建
  clean_app_artifacts
  pyinstaller_build_arch "$HOST_ARCH" "$PYTHON"
}

# ============================================================
# 构建后处理
# ============================================================
# macOS only: 写 Info.plist 的 Bundle ID / 版本号 / 最低系统版本
# 一律用 plutil 读写，不用 sed 改 plist（sed 匹配到 </key> 之间的空白会破坏结构）
fix_app_info() {
  [ "$HOST_OS" = "darwin" ] || return 0
  local version
  version=$(get_version)
  local plist="$DIST_DIR/${APP_NAME}.app/Contents/Info.plist"
  [ -f "$plist" ] || return 0

  plutil -replace CFBundleIdentifier -string "$APP_BUNDLE_ID" "$plist" 2>/dev/null || true
  plutil -replace CFBundleShortVersionString -string "$version" "$plist" 2>/dev/null || \
    plutil -insert CFBundleShortVersionString -string "$version" "$plist" 2>/dev/null || true
  plutil -replace CFBundleVersion -string "$version" "$plist" 2>/dev/null || \
    plutil -insert CFBundleVersion -string "$version" "$plist" 2>/dev/null || true
  plutil -replace LSMinimumSystemVersion -string "$MACOS_MIN_VERSION" "$plist" 2>/dev/null || \
    plutil -insert LSMinimumSystemVersion -string "$MACOS_MIN_VERSION" "$plist" 2>/dev/null || true
  log_info "Info.plist 已更新: version=$version bundle=$APP_BUNDLE_ID minOS=$MACOS_MIN_VERSION"
}

# macOS only: ad-hoc 签名（个人项目无 Developer ID，不公证）
# 顺序固定：清 xattr → 内嵌 Mach-O 逐个签 → 整包签 → 校验。
# 坑：codesign --deep 不会给 Resources 下的内嵌工具补签名；fix_app_info 改 plist
# 已让 PyInstaller 的签名失效，不重签会让下载分发的 App 被判「已损坏，无法打开」。
adhoc_sign() {
  [ "$HOST_OS" = "darwin" ] || return 0
  [ "${ADHOC_SIGN:-0}" = "1" ] || return 0
  command -v codesign &>/dev/null || { log_warn "无 codesign，跳过签名"; return 0; }
  local target="$DIST_DIR/${APP_NAME}.app"
  [ -d "$target" ] || return 0

  # 仓库里拷进来的文件可能带 Sourcetree/浏览器留下的 quarantine，原样进 bundle 会污染安装包
  run xattr -cr "$target" 2>/dev/null || true
  local f
  while IFS= read -r f; do
    case "$(file -b "$f" 2>/dev/null)" in
      *Mach-O*) run codesign --force --sign - --timestamp=none "$f" 2>/dev/null \
                  || log_warn "内嵌二进制签名失败: ${f#"$target"/}" ;;
    esac
  done < <(find "$target/Contents" -type f -perm -u+x 2>/dev/null)
  run codesign --force --sign - "$target" || log_warn "ad-hoc 签名失败（本机运行可忽略）"
  # 校验门禁：签名已坏却继续打包，下载端只会看到「已损坏」，极难回溯
  if ! $DRY_RUN; then
    codesign --verify --deep --strict "$target" >/dev/null 2>&1 \
      || log_warn "签名校验未通过: $(basename "$target")（分发前必须排查，否则安装后无法打开）"
  fi
}

# ============================================================
# 成品归档：macOS 只落 DMG，Linux 落 tar.gz，Windows 落 zip；
# release/ 只保留成品，.app/onedir 均留在 build/dist 作中间产物
# ============================================================
package_platform() {
  case "$HOST_OS" in
    darwin)  build_dmg ;;
    linux)   build_tarball ;;
    windows) build_zip ;;
  esac
}

# macOS only: 用 hdiutil 生成 DMG（文件名带版本号，卷内 App + Applications 快捷方式）
build_dmg() {
  [ "$HOST_OS" = "darwin" ] || return 0
  local version
  version=$(get_version)
  local app_path="$DIST_DIR/${APP_NAME}.app"
  local dmg_name="${RELEASE_PREFIX:-$APP_NAME}_v${version}.dmg"
  local dmg_path="${RELEASE_DIR}/${dmg_name}"

  # dry-run 零副作用：不删历史产物、不建 staging、不调 hdiutil
  if $DRY_RUN; then
    log_warn "[dry-run] hdiutil create → $dmg_path"
    return 0
  fi

  # 清理 release 中历史残留的中间产物（.app / onedir 目录），保证只剩 DMG
  if [ ${#RELEASE_CLEAN_TARGETS[@]} -gt 0 ]; then
    for target in "${RELEASE_CLEAN_TARGETS[@]}"; do
      [ -n "$target" ] && rm -rf "${RELEASE_DIR:?}/${target:?}"
    done
  fi

  [ -d "$app_path" ] || return 0

  mkdir -p "$RELEASE_DIR"
  rm -f "$dmg_path"

  # staging 目录：App + Applications 符号链接（hdiutil 会将其写入为
  # Finder 别名，用户拖到此处即完成安装）
  local staging
  staging="$(mktemp -d "${TMPDIR:-/tmp}/${APP_NAME}_dmg.XXXXXX")"
  trap "rm -rf '$staging'" EXIT
  run ditto "$app_path" "$staging/${APP_NAME}.app"
  run ln -s /Applications "$staging/Applications"

  # 暂存副本再校验一次：DMG 里签名失效，等于用户装完打不开
  if ! $DRY_RUN; then
    codesign --verify --deep --strict "$staging/${APP_NAME}.app" >/dev/null 2>&1 \
      || log_warn "DMG 暂存副本签名校验失败，分发后可能无法打开"
  fi

  log_info "生成 DMG: $dmg_name ..."
  run hdiutil create -volname "$APP_NAME" -srcfolder "$staging" \
    -ov -format UDZO ${DMG_IMAGEKEY_ARGS[@]+"${DMG_IMAGEKEY_ARGS[@]}"} "$dmg_path" > /dev/null

  rm -rf "$staging"
  trap - EXIT

  log_success "Release DMG  → $dmg_path ($(du -sh "$dmg_path" | cut -f1))"
  # ad-hoc 签名无 Developer ID：下载转发后首启可能被 Gatekeeper 拦（不是签名坏）
  log_info "首次打开若提示「无法验证开发者」：右键 → 打开；或执行："
  log_info "  xattr -dr com.apple.quarantine \"/Applications/${APP_NAME}.app\""
}

# Linux only: 生成 tar.gz（PyInstaller onedir 目录）
build_tarball() {
  [ "$HOST_OS" = "linux" ] || return 0
  local version
  version=$(get_version)
  local dir="$DIST_DIR/${APP_NAME}"
  local tar_path="${RELEASE_DIR}/${RELEASE_PREFIX:-$APP_NAME}_v${version}_linux_${HOST_ARCH}.tar.gz"

  [ -d "$dir" ] || return 0
  mkdir -p "$RELEASE_DIR"
  rm -f "$tar_path"

  log_info "生成 tar.gz ..."
  run tar -czf "$tar_path" -C "$DIST_DIR" "${APP_NAME}"
  $DRY_RUN || log_success "Release tgz  → $tar_path"
}

# Windows only: 生成 zip（zip 命令缺失时回退 PowerShell Compress-Archive）
build_zip() {
  [ "$HOST_OS" = "windows" ] || return 0
  local version
  version=$(get_version)
  local dir="$DIST_DIR/${APP_NAME}"
  local zip_name="${RELEASE_PREFIX:-$APP_NAME}_v${version}_windows_${HOST_ARCH}.zip"
  local zip_path="${RELEASE_DIR}/${zip_name}"

  [ -d "$dir" ] || return 0
  mkdir -p "$RELEASE_DIR"
  rm -f "$zip_path"

  log_info "生成 ZIP: $zip_name ..."
  if $DRY_RUN; then
    log_warn "[dry-run] zip -rq $zip_path ${APP_NAME} (in $DIST_DIR)"
    return 0
  fi
  if command -v zip &>/dev/null; then
    (cd "$DIST_DIR" && zip -rq "$zip_path" "${APP_NAME}")
  elif command -v powershell &>/dev/null; then
    local win_dir win_zip_path
    win_dir=$(_to_native_path "$dir")
    win_zip_path=$(_to_native_path "$zip_path")
    powershell -NoProfile -Command \
      "Compress-Archive -Path '${win_dir}\\*' -DestinationPath '${win_zip_path}' -Force"
  else
    log_warn "zip 不可用，跳过"
    return 0
  fi
  log_success "Release ZIP  → $zip_path"
}

# ============================================================
# 增量构建检查
# ============================================================
# 检查是否需要重新构建：比较源文件修改时间与产物二进制
# 返回 0 = 需要构建, 1 = 可跳过
# SRC_FIND_EXPR 为项目差异区声明的源文件匹配表达式（-o 优先级低于隐式 AND，
# 必须由本函数用 \( \) 分组）
needs_build() {
  local target
  if [ "$HOST_OS" = "darwin" ]; then
    target="$DIST_DIR/${APP_NAME}.app/Contents/MacOS/${APP_NAME}"
  else
    target="$DIST_DIR/${APP_NAME}/${APP_NAME}${EXT}"
  fi
  [ -f "$target" ] || [ -d "$DIST_DIR/${APP_NAME}.app" ] || return 0

  local newer
  newer=$(find "$PROJECT_DIR" \
    \( ${SRC_FIND_EXPR[@]+"${SRC_FIND_EXPR[@]}"} \) \
    -not -path '*/build/*' \
    -not -path '*/release/*' \
    -not -path '*/.git/*' \
    -not -path '*/.venv*/*' \
    -newer "$target" \
    -print -quit 2>/dev/null)
  [ -n "$newer" ]
}

# ============================================================
# 进程清理
# ============================================================
kill_existing() {
  $DRY_RUN && return 0
  local pids
  pids=$(pgrep -f "${APP_NAME}" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    log_info "停止已有 App 进程: $pids"
    echo "$pids" | xargs kill 2>/dev/null || true
    sleep 1
    pids=$(pgrep -f "${APP_NAME}" 2>/dev/null || true)
    if [ -n "$pids" ]; then
      echo "$pids" | xargs kill -9 2>/dev/null || true
    fi
    log_success "旧进程已停止"
  fi
}

# ============================================================
# 母版默认钩子：项目差异区「专属实现」中定义同名函数即覆盖
#   hook_pyi_extra      追加项目专属 PyInstaller 参数（pyglossary 随包、
#                       worker 源码注入、脚本参数数组 PYI_EXTRA_ARGS 等）
#   hook_post_build     编译完成后、归档前的附加动作（plist 定制、冒烟测试）
#   hook_extra_cleanup  clean 时 kill_existing 之后的附加动作
# ============================================================
hook_pyi_extra()     { :; }
hook_post_build()    { :; }
hook_extra_cleanup() { :; }

# ============================================================
# 命令实现（build / run / dev / test / install / clean 固定流程；
# 项目专属命令由差异区「专属实现」提供并登记进 commands 表）
# ============================================================
cmd_build() {
  # PyInstaller 产物依赖宿主本机解释器与工具链，不支持跨 OS 交叉构建
  if [ "$HOST_OS" != "$NATIVE_OS" ]; then
    log_error "不支持跨 OS 构建：${HOST_OS} 产物需在 ${HOST_OS} 机器或对应 CI runner 上构建"
  fi
  if [ "${PLATFORM_SCOPE:-all}" = "darwin" ] && [ "$HOST_OS" != "darwin" ]; then
    log_error "本项目仅支持在 macOS 上构建（产物为 macOS 专属）"
  fi

  local version
  version=$(get_version)
  if $DRY_RUN; then
    log_warn "[dry-run] PyInstaller (arch/universal) → fix_app_info → hook_post_build → adhoc_sign → package_platform"
    return 0
  fi

  log_info "构建 $APP_NAME ($HOST_OS/$HOST_ARCH, version=$version)..."

  check_python
  check_tkinter
  mkdir -p "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR"
  rm -rf "$BUILD_DIR"/*

  pyinstaller_build
  fix_app_info
  hook_post_build
  adhoc_sign
  package_platform

  log_success "=== 构建完成 ==="
  log_info "App 中间产物: $DIST_DIR/${APP_NAME}.app (供 DMG 封装与本地运行，不落入 release/)"
  log_info "Release 目录 (仅成品): $RELEASE_DIR"
}

# dist：发布级构建（macOS 强制 universal，产物与 CI 一致）
cmd_dist() {
  MACOS_UNIVERSAL_FORCE=1
  cmd_build "$@"
}

cmd_run() {
  if [ "$HOST_OS" = "windows" ]; then
    log_error "run 命令不支持 Windows，请直接运行 build/dist/${APP_NAME}/${APP_NAME}.exe"
  fi

  local log_file="$BUILD_DIR/run.log"
  mkdir -p "$BUILD_DIR"

  kill_existing

  if needs_build; then
    cmd_build
  else
    log_success "源文件无变化，跳过构建"
  fi

  local binary
  if [ "$HOST_OS" = "darwin" ]; then
    binary="$DIST_DIR/${APP_NAME}.app/Contents/MacOS/${APP_NAME}"
  else
    binary="$DIST_DIR/${APP_NAME}/${APP_NAME}${EXT}"
  fi
  [ -x "$binary" ] || log_error "找不到可执行文件: $binary"

  log_info "启动 $APP_NAME (前台模式)..."
  log_info "按 Ctrl+C 关闭"
  echo ""

  if $DRY_RUN; then
    log_warn "[dry-run] $binary | tee -a $log_file"
    return 0
  fi
  : > "$log_file"
  set +e
  "$binary" 2>&1 | tee -a "$log_file"
  local exit_code=${PIPESTATUS[0]}
  set -e

  echo ""
  if [ "$exit_code" -eq 0 ]; then
    log_success "App 已正常退出"
  else
    log_warn "App 退出码: $exit_code"
  fi
}

cmd_dev() {
  check_python
  mkdir -p "$BUILD_DIR"
  local log_file="$BUILD_DIR/dev.log"

  log_info "开发模式: \$PYTHON -m app，按 Ctrl+C 停止"
  echo ""

  if $DRY_RUN; then
    log_warn "[dry-run] $PYTHON -m app | tee -a $log_file"
    return 0
  fi
  : > "$log_file"
  cd "$PROJECT_DIR"
  # 临时关闭 -e：Ctrl+C (130) 属正常退出路径
  set +e
  $PYTHON -m app 2>&1 | tee -a "$log_file"
  local exit_code=${PIPESTATUS[0]}
  set -e

  echo ""
  if [ "$exit_code" -eq 0 ] || [ "$exit_code" -eq 130 ]; then
    log_success "开发模式已停止"
  else
    log_warn "退出码: $exit_code"
  fi
}

cmd_test() {
  check_python
  ensure_pytest

  local cmd=("$PYTHON" -m pytest -v ${PYTEST_PATHS[@]+"${PYTEST_PATHS[@]}"})
  if [ -n "${PYTEST_SKIP_EXPR:-}" ]; then
    cmd+=(-k "${PYTEST_SKIP_EXPR}")
  fi
  cmd+=(${PYTEST_EXTRA[@]+"${PYTEST_EXTRA[@]}"})

  log_info "运行 pytest ..."
  # 测试失败必须红（不假绿）：环境门控的用例应在测试内部 skip，而非靠这里吞错
  run "${cmd[@]}" || { log_error "pytest 未通过（失败用例见上；联网用例需显式开启对应 LIVE 环境变量）"; return 1; }
  log_success "测试命令执行完成"
}

# 安装/补齐依赖包: 运行时依赖 + 构建工具 + 测试工具
cmd_install() {
  check_python
  check_tkinter
  ensure_runtime_deps
  ensure_pyinstaller
  ensure_pytest

  if [ -n "${DEPS_IMPORT_CHECK:-}" ]; then
    log_info "依赖版本:"
    # shellcheck disable=SC2086
    $PYTHON -m pip show ${DEPS_IMPORT_CHECK//,/ } pyinstaller pytest 2>/dev/null \
      | grep -E '^(Name|Version):' | paste - - | sed 's/^/  /' || true
  fi
  log_success "=== 依赖安装完成 ==="
}

cmd_clean() {
  log_info "清理构建产物..."
  if $DRY_RUN; then
    log_warn "[dry-run] kill_existing → rm -rf ${CLEAN_TARGETS[*]-} ${CLEAN_EXTRA[*]-} + __pycache__"
    return 0
  fi
  kill_existing 2>/dev/null || true
  hook_extra_cleanup
  rm -rf ${CLEAN_TARGETS[@]+"${CLEAN_TARGETS[@]}"} \
         "$PROJECT_DIR/${APP_NAME}.spec" \
         ${CLEAN_EXTRA[@]+"${CLEAN_EXTRA[@]}"}
  find "$PROJECT_DIR" -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
  find "$PROJECT_DIR" -name '*.pyc' -delete 2>/dev/null || true
  log_success "清理完成"
}

# ============================================================
# 交互菜单 / 帮助 / 分发（命令表 commands 为唯一真源）
# commands 格式: "序号|别名1,别名2|说明|处理函数"
# ============================================================
show_menu() {
  echo ""
  echo "=========================================="
  echo "      ${APP_DISPLAY_NAME:-$APP_NAME} - 构建工具 ($HOST_OS/$HOST_ARCH)"
  echo "=========================================="
  local entry num aliases desc fn
  for entry in "${commands[@]}"; do
    IFS='|' read -r num aliases desc fn <<< "$entry"
    printf "  %s) %-12s %s\n" "$num" "${aliases%%,*}" "$desc"
  done
  echo "  0) exit        退出"
  echo "=========================================="
  echo -n "请输入选择 [0-${#commands[@]}] (回车默认 ${DEFAULT_CMD:-run}): "
}

show_help() {
  local version
  version=$(get_version)
  cat <<EOF
${APP_DISPLAY_NAME:-$APP_NAME} 构建工具

用法: $0 [命令] [参数...]

当前平台: $HOST_OS/$HOST_ARCH   版本: $version   Python: $PYTHON

命令:
  (无参数)      显示交互菜单（回车默认 ${DEFAULT_CMD:-run}）
EOF
  local entry num aliases desc fn
  for entry in "${commands[@]}"; do
    IFS='|' read -r num aliases desc fn <<< "$entry"
    printf '  %s|%-16s %s\n' "$num" "${aliases//,/ }" "$desc"
  done
  cat <<EOF
  0|exit            退出
  help              显示本帮助

全局选项 (可写在命令前后):
  --dry-run        仅打印将执行的动作，不实际执行
  --skip-deps      跳过依赖自动安装（环境已就绪时用）

Python 检测顺序:
  $PYTHON_ENV_VAR → ${PREFERRED_PYTHON:-<未配置>} → 已激活虚拟环境 → PATH 上的 python3

项目路径:
  源码:     $PROJECT_DIR
  中间产物:  $DIST_DIR (PyInstaller .app / onedir)
  发布产物:  $RELEASE_DIR (仅 DMG/tgz/zip)
  运行日志:  $BUILD_DIR/run.log 和 $BUILD_DIR/dev.log
  版本文件:  $VERSION_FILE
  Bundle ID: $APP_BUNDLE_ID
EOF
  if declare -F show_help_extra >/dev/null; then
    show_help_extra
  fi
}

# 分发：序号或任一别名均可；--dry-run / --skip-deps 为母版全局选项，
# 在命令前后均可；未知命令按 FALLBACK_CMD 兜底，未声明则报错
main() {
  local global_args=() cmd="" args=() a
  for a in "$@"; do
    case "$a" in
      --dry-run)    global_args+=("$a") ;;
      --skip-deps)  global_args+=("$a") ;;
      *)            if [ -z "$cmd" ]; then cmd="$a"; else args+=("$a"); fi ;;
    esac
  done

  for a in "${global_args[@]}"; do
    case "$a" in
      --dry-run)   DRY_RUN=true ;;
      --skip-deps) SKIP_DEPS=true ;;
    esac
  done

  if [ -z "$cmd" ]; then
    show_menu
    read -r choice
    cmd="${choice:-${DEFAULT_CMD:-run}}"
  fi

  case "$cmd" in
    0|q|exit|quit)  echo "退出..."; exit 0 ;;
    help|-h|--help) show_help; exit 0 ;;
  esac

  local entry num aliases desc fn a alias_arr
  for entry in "${commands[@]}"; do
    IFS='|' read -r num aliases desc fn <<< "$entry"
    IFS=',' read -r -a alias_arr <<< "${num},${aliases}"
    for a in "${alias_arr[@]}"; do
      if [ "$cmd" = "$a" ]; then
        "$fn" "${args[@]}"
        return
      fi
    done
  done

  if [ -n "${FALLBACK_CMD:-}" ]; then
    log_info "未识别命令 '$cmd'，按默认流程执行 $FALLBACK_CMD"
    "$FALLBACK_CMD" "${args[@]}"
  else
    log_error "未知命令: ${cmd}（help 查看用法）"
  fi
}
# ============================================================
# 项目差异区 · 专属实现（覆盖母版默认 / 追加项目专属命令）
# ============================================================
# 插件式用户脚本与非 .py 资源随包：custom_scripts/、script_wrapper、
# 默认 data。源路径必须经 _to_native_path（Windows Git Bash 下 /d/...
# 形式 PyInstaller 找不到）。
hook_pyi_extra() {
  args+=(
    --add-data "$(_to_native_path "$PROJECT_DIR/custom_scripts")${DATA_SEP}custom_scripts"
    --add-data "$(_to_native_path "$PROJECT_DIR/app/core/script_wrapper.py")${DATA_SEP}app/core"
    --add-data "$(_to_native_path "$PROJECT_DIR/VERSION")${DATA_SEP}."
    --add-data "$(_to_native_path "$PROJECT_DIR/data")${DATA_SEP}data"
  )
}

# 覆盖母版 x86_64 Python 探测：BOOP_PYTHON_X86_64 显式指定优先（CI 用
# python.org universal2 解释器，两 slice 共用同一二进制），其次候选路径逐个
# 用 arch -x86_64 实测校验（不能只看文件存在）
find_x86_64_python() {
  [ "$HOST_OS" = "darwin" ] || return 1
  # 主机器为 Intel 时，主解释器已是 x86_64，无需也无法构建 universal
  [ "$HOST_ARCH" = "arm64" ] || return 1

  if [ -n "${BOOP_PYTHON_X86_64:-}" ]; then
    if arch -x86_64 "$BOOP_PYTHON_X86_64" -c "import platform; exit(0 if platform.machine() == 'x86_64' else 1)" 2>/dev/null; then
      echo "$BOOP_PYTHON_X86_64"
      return 0
    fi
    return 1
  fi

  local candidate
  for candidate in \
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 \
    /Library/Frameworks/Python.framework/Versions/3.12/bin/python3 \
    /usr/local/opt/python@3.11/bin/python3 \
    /usr/local/opt/python@3.12/bin/python3 \
    /usr/local/opt/python@3/bin/python3 \
    /usr/local/bin/python3 \
    /usr/local/bin/python; do
    if [ -x "$candidate" ] && \
       arch -x86_64 "$candidate" -c "import platform; exit(0 if platform.machine() == 'x86_64' else 1)" 2>/dev/null; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

# 同步 custom_scripts/ 到已安装的 Boop.app（macOS 开发期用）
cmd_scripts() {
  local target="/Applications/Boop.app/Contents/Resources/custom_scripts"
  if $DRY_RUN; then
    log_warn "[dry-run] 备份并同步 $PROJECT_DIR/custom_scripts → $target"
    return 0
  fi
  [ -d "$target" ] || log_error "未找到 /Applications/Boop.app（请先安装或打包）"

  local backup_dir="$PROJECT_DIR/custom_scripts.bak_$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$backup_dir"
  cp -R "$target/"* "$backup_dir/" 2>/dev/null || true
  log_info "已备份原脚本 → $backup_dir"

  find "$target" -name "*.py" -not -path "*/lib/*" -delete 2>/dev/null || true

  find "$PROJECT_DIR/custom_scripts" -maxdepth 1 -name "*.py" -type f \
    -exec cp {} "$target/" \;
  if [ -d "$PROJECT_DIR/custom_scripts/lib" ]; then
    cp -R "$PROJECT_DIR/custom_scripts/lib" "$target/"
  fi
  log_success "custom_scripts/ 已同步 → $target"
}

# 帮助尾部补充：环境变量与 scripts 命令说明
show_help_extra() {
  cat <<EOF

环境变量:
  $PYTHON_ENV_VAR           显式指定 Python 解释器路径（CI 用）
  $PYTHON_ENV_VAR_X86_64    显式指定 x86_64 Python（universal 构建用；
                       CI 用 python.org universal2 解释器同时充当两 slice）

scripts 命令:
  将仓库 custom_scripts/ 热同步到 /Applications/Boop.app 内（先备份再替换），
  开发期调脚本无需重新打包。
EOF
}

# 覆盖母版 cmd_test：boop 的测试体系是自研 runner（扫描 tests/test_scripts/*.json
# 用例、按脚本分组并行），tests/*.py 不是 pytest 用例（pytest 收集恒为 0）。
# 失败必须红：旧写法用 -k 过滤到空集 + warn 吞错，等于假绿。
cmd_test() {
  check_python
  log_info "运行 Boop 脚本测试用例 ..."
  if $DRY_RUN; then
    log_warn "[dry-run] $PYTHON tests/test_scripts/run_tests.py"
    return 0
  fi
  "$PYTHON" "$PROJECT_DIR/tests/test_scripts/run_tests.py"
  log_success "测试命令执行完成"
}

main "$@"
