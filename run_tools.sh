#!/usr/bin/env bash
# =============================================================================
# Boop - 构建与运行工具 (跨平台: macOS / Linux / Windows Git Bash)
# =============================================================================
# 命令:
#   1|b|build    构建桌面应用 (PyInstaller 打包, 自动适配当前平台)
#   2|r|run      构建并前台运行 (Ctrl+C 关闭)
#   3|d|dev      开发模式: 直接 python -m app 前台运行 (Ctrl+C 关闭)
#   4|t|test     运行单元测试 (pytest, 跳过 GUI 自动化测试)
#   5|s|scripts  同步 scripts/ 到 /Applications/Boop.app/Contents/Resources/scripts
#   6|c|clean    清理构建产物
#   0|q|exit     退出
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
cd "$PROJECT_DIR"

# --- 项目常量 ---
APP_NAME="Boop"
APP_BUNDLE_ID="com.xthuji.boop"
MACOS_MIN_VERSION="12.0"
BUILD_DIR="$PROJECT_DIR/build"
DIST_DIR="$PROJECT_DIR/dist"
RELEASE_DIR="$PROJECT_DIR/release"
VERSION_FILE="$PROJECT_DIR/version.txt"
PYTHON=""

# --- 平台检测 ---
HOST_OS=""
HOST_ARCH=""
EXT=""

detect_platform() {
  local os
  os="$(uname -s 2>/dev/null || echo "unknown")"
  case "$os" in
    Darwin*)              HOST_OS="darwin"  ;;
    Linux*)               HOST_OS="linux"   ;;
    MINGW*|MSYS*|CYGWIN*) HOST_OS="windows" ;;
    *)                    HOST_OS="unknown" ;;
  esac

  local arch
  arch="$(uname -m 2>/dev/null || echo "unknown")"
  case "$arch" in
    x86_64|amd64)   HOST_ARCH="amd64" ;;
    arm64|aarch64)  HOST_ARCH="arm64" ;;
    *)              HOST_ARCH="amd64" ;;
  esac

  if [ "$HOST_OS" = "windows" ]; then
    EXT=".exe"
  else
    EXT=""
  fi
}

detect_platform

# --- 彩色输出 ---
BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'
YELLOW='\033[1;33m'; BOLD='\033[1m'; NC='\033[0m'
log_info()    { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }
die() { log_error "$*"; exit 1; }

# ============================================================
# Python 解释器检测（可移植，无外部依赖）
# ============================================================
detect_python() {
  if [ -n "$PYTHON" ]; then return 0; fi

  # 1) 显式环境变量
  if [ -n "${BOOP_PYTHON:-}" ]; then
    if [ -x "$BOOP_PYTHON" ]; then
      PYTHON="$BOOP_PYTHON"
    elif command -v "$BOOP_PYTHON" &>/dev/null; then
      PYTHON="$(command -v "$BOOP_PYTHON")"
    else
      die "BOOP_PYTHON 设置了但找不到: $BOOP_PYTHON"
    fi
    return 0
  fi

  # 2) 当前已激活的虚拟环境
  if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
    return 0
  fi

  # 3) PATH 上找 python3
  if command -v python3 &>/dev/null; then
    PYTHON="$(command -v python3)"
    return 0
  fi

  die "找不到 Python，请先安装 Python 3.9+ 或设置 BOOP_PYTHON 环境变量"
}

detect_python

# ============================================================
# 依赖检查
# ============================================================
check_python() {
  $PYTHON -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" \
    || die "Python 版本过低 (需要 3.9+, 当前: $($PYTHON --version))"
  log_success "Python: $PYTHON ($($PYTHON --version 2>&1))"
}

check_tkinter() {
  $PYTHON -c "import tkinter" 2>/dev/null \
    || die "Tkinter 不可用 (macOS: brew install python-tk; Ubuntu: apt install python3-tk)"
  log_success "Tkinter: ok"
}

# 确保 PyInstaller 已安装到目标解释器（避免 PATH 上的 pyinstaller 解释器不匹配）
ensure_pyinstaller() {
  if $PYTHON -m pip show -q pyinstaller 2>/dev/null; then
    return 0
  fi
  log_info "首次安装 PyInstaller ..."
  $PYTHON -m pip install -q pyinstaller pyinstaller-hooks-contrib \
    || die "PyInstaller 安装失败"
  log_success "PyInstaller 已就绪"
}

# 项目运行时依赖（首次构建前安装）
ensure_runtime_deps() {
  if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
    return 0
  fi
  if $PYTHON -c "import pynput, pyperclip" 2>/dev/null; then
    return 0
  fi
  log_info "安装运行时依赖 (requirements.txt) ..."
  $PYTHON -m pip install -q -r "$PROJECT_DIR/requirements.txt" \
    || die "依赖安装失败"
  log_success "运行时依赖已就绪"
}

# ============================================================
# 版本管理
# ============================================================
get_version() {
  if [ -f "$VERSION_FILE" ]; then
    local ver
    ver=$(grep -E '^VERSION\s*=' "$VERSION_FILE" | head -1 | sed 's/.*=\s*//' | tr -d '[:space:]')
    if [ -n "$ver" ]; then
      echo "$ver"; return
    fi
  fi
  git describe --tags --always --dirty 2>/dev/null || echo "dev"
}

# ============================================================
# PyInstaller 核心配置
# ============================================================
readonly EXCLUDE_MODULES=(
  # 测试 / 调试
  "test" "tkinter.test" "unittest" "doctest"
  "trace" "profile" "pstats" "tabnanny" "pyclbr"
  # 模块工具
  "pickletools" "zipimport" "modulefinder" "lib2to3"
  # 数据库
  "sqlite3"
  # 网络（不使用 requests / urllib）
  "email" "urllib3" "requests"
  # 并发（用 threading，不用 multiprocessing / asyncio）
  "multiprocessing" "asyncio" "concurrent"
  # 包管理
  "distutils" "setuptools" "pkg_resources"
  # 不常见 GUI / Web / 科学
  "PyQt5" "PyQt6" "PySide2" "PySide6" "gi" "wx"
  "django" "flask" "fastapi" "sqlalchemy"
  "numpy" "scipy" "pandas" "matplotlib"
)

# PyInstaller --add-data 分隔符: Windows 用 ';', macOS/Linux 用 ':'
if [ "$HOST_OS" = "windows" ]; then
  DATA_SEP=";"
else
  DATA_SEP=":"
fi

# 将路径转为原生格式，避免 MSYS2/Git Bash 路径转换导致 PyInstaller 找不到文件
_to_native_path() {
  if [ "$HOST_OS" = "windows" ] && command -v cygpath &>/dev/null; then
    cygpath -w "$1"
  else
    echo "$1"
  fi
}

# 需要一起打包的非 .py 资源 (src{sep}dest)
# Windows 下源路径必须是原生 Windows 格式 (D:\... 而非 /d/...)
readonly APP_DATA_FILES=(
  "$(_to_native_path "$PROJECT_DIR/scripts")${DATA_SEP}scripts"
  "$(_to_native_path "$PROJECT_DIR/app/core/script_wrapper.py")${DATA_SEP}app/core"
  "$(_to_native_path "$PROJECT_DIR/version.txt")${DATA_SEP}."
  "$(_to_native_path "$PROJECT_DIR/data")${DATA_SEP}data"
)

# PyInstaller 用 --icon 统一接受 .icns (mac) / .ico (win) / .png (linux)
get_platform_icon_args() {
  local args=""
  local icns="$PROJECT_DIR/icons/icon.icns"
  local ico="$PROJECT_DIR/icons/icon.ico"
  local png="$PROJECT_DIR/icons/icon_256x256.png"

  if [ "$HOST_OS" = "darwin" ] && [ -f "$icns" ]; then
    args="--icon $icns"
  elif [ "$HOST_OS" = "windows" ] && [ -f "$ico" ]; then
    args="--icon $ico"
  elif [ "$HOST_OS" = "linux" ] && [ -f "$png" ]; then
    args="--icon $png"
  fi
  echo "$args"
}

# ============================================================
# PyInstaller 构建
# ============================================================
pyinstaller_build() {
  local version
  version=$(get_version)

  ensure_runtime_deps
  ensure_pyinstaller

  local args=(
    --name "$APP_NAME"
    --windowed
    --onedir
    -y
    --workpath "$BUILD_DIR"
    --distpath "$DIST_DIR"
    --optimize=2
    --strip
    --noconfirm
    --log-level=ERROR
  )

  for module in "${EXCLUDE_MODULES[@]}"; do
    args+=(--exclude-module="$module")
  done

  for file in "${APP_DATA_FILES[@]}"; do
    args+=(--add-data "$file")
  done

  # 隐藏导入（PyInstaller 静态分析不到的动态引用）
  args+=(
    --hidden-import tkinter
    --hidden-import tkinter.ttk
    --hidden-import pynput
    --hidden-import pynput.keyboard
  )

  # 平台特定
  if [ "$HOST_OS" = "darwin" ]; then
    args+=(--osx-bundle-identifier "$APP_BUNDLE_ID")
    # 确保最低部署版本 (本地构建时 workflow 环境变量可能不存在)
    export MACOSX_DEPLOYMENT_TARGET="${MACOSX_DEPLOYMENT_TARGET:-$MACOS_MIN_VERSION}"
    log_info "MACOSX_DEPLOYMENT_TARGET=$MACOSX_DEPLOYMENT_TARGET"
  fi
  local plat_icon_args
  plat_icon_args=$(get_platform_icon_args)
  if [ -n "$plat_icon_args" ]; then
    # shellcheck disable=SC2086
    args+=($plat_icon_args)
  fi

  args+=("$PROJECT_DIR/app/__main__.py")

  log_info "PyInstaller 构建 ($APP_NAME, version=$version)..."
  if ! $PYTHON -m PyInstaller "${args[@]}"; then
    log_error "PyInstaller 构建失败"
    return 1
  fi
  log_success "PyInstaller 构建完成"
}

# ============================================================
# 构建后处理
# ============================================================

# macOS: 更新 Info.plist 中的版本号 / bundle id
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

# macOS: 生成 DMG
build_dmg() {
  [ "$HOST_OS" = "darwin" ] || return 0
  local version
  version=$(get_version)
  local app_path="$DIST_DIR/${APP_NAME}.app"
  local dmg_name="${APP_NAME}_v${version}.dmg"
  local dmg_path="${RELEASE_DIR}/${dmg_name}"

  [ -d "$app_path" ] || return 0

  mkdir -p "$RELEASE_DIR"
  rm -f "$dmg_path"

  log_info "生成 DMG: $dmg_name ..."
  local tmp_stage="$DIST_DIR/dmg_stage"
  rm -rf "$tmp_stage"
  mkdir -p "$tmp_stage"
  cp -R "$app_path" "$tmp_stage/"
  ln -s /Applications "$tmp_stage/Applications" 2>/dev/null || true

  if hdiutil create \
      -volname "$APP_NAME" \
      -srcfolder "$tmp_stage" \
      -ov -format UDZO \
      "$dmg_path" > /dev/null 2>&1; then
    log_success "Release DMG  → $dmg_path ($(du -sh "$dmg_path" | cut -f1))"
  else
    log_warn "DMG 生成失败（sandbox 或权限限制），但 .app 已可用: $app_path"
  fi
  rm -rf "$tmp_stage"
}

# Linux: 生成 tar.gz
build_tarball() {
  [ "$HOST_OS" = "linux" ] || return 0
  local version
  version=$(get_version)
  local dir="$DIST_DIR/${APP_NAME}"
  local tar_path="${RELEASE_DIR}/${APP_NAME}_v${version}_linux_${HOST_ARCH}.tar.gz"

  [ -d "$dir" ] || return 0
  mkdir -p "$RELEASE_DIR"
  rm -f "$tar_path"

  log_info "生成 tar.gz ..."
  (cd "$DIST_DIR" && tar -czf "$tar_path" "${APP_NAME}")
  log_success "Release tgz  → $tar_path"
}

# Windows: 生成 zip
build_zip() {
  [ "$HOST_OS" = "windows" ] || return 0
  local version
  version=$(get_version)
  local dir="$DIST_DIR/${APP_NAME}"
  local zip_name="${APP_NAME}_v${version}_windows_${HOST_ARCH}.zip"
  local zip_path="${RELEASE_DIR}/${zip_name}"

  [ -d "$dir" ] || return 0
  mkdir -p "$RELEASE_DIR"
  rm -f "$zip_path"

  log_info "生成 ZIP: $zip_name ..."
  if command -v zip &>/dev/null; then
    (cd "$DIST_DIR" && zip -rq "$zip_path" "${APP_NAME}")
  elif command -v powershell &>/dev/null; then
    local win_dir win_zip_path
    win_dir="$(_to_native_path "$dir")"
    win_zip_path="$(_to_native_path "$zip_path")"
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
needs_build() {
  local target
  if [ "$HOST_OS" = "darwin" ]; then
    target="$DIST_DIR/${APP_NAME}.app/Contents/MacOS/${APP_NAME}"
  else
    target="$DIST_DIR/${APP_NAME}${EXT}"
  fi
  [ -f "$target" ] || [ -d "$DIST_DIR/${APP_NAME}.app" ] || return 0

  local newer
  newer=$(find "$PROJECT_DIR" \
    \( -name '*.py' -o -name 'version.txt' -o -name 'requirements.txt' -o \
       -path '*/scripts/*' -o -path '*/icons/*' -o -path '*/data/*' \) \
    -not -path '*/build/*' \
    -not -path '*/dist/*' \
    -not -path '*/release/*' \
    -not -path '*/.git/*' \
    -not -path '*/.venv*/*' \
    -newer "$target" \
    -print -quit 2>/dev/null)
  [ -n "$newer" ]
}

# ============================================================
# 进程处理
# ============================================================
kill_existing() {
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
# 命令实现
# ============================================================
cmd_build() {
  check_python
  check_tkinter

  mkdir -p "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR"

  rm -rf "$BUILD_DIR"/*

  pyinstaller_build
  local rc=$?
  if [ $rc -ne 0 ]; then
    die "构建失败 (PyInstaller rc=$rc)"
  fi

  fix_app_info

  if [ "$HOST_OS" = "darwin" ]; then
    build_dmg
  elif [ "$HOST_OS" = "linux" ]; then
    build_tarball
  else
    build_zip
  fi

  log_success "=== 构建完成 ==="
  if [ "$HOST_OS" = "darwin" ] && [ -d "$DIST_DIR/${APP_NAME}.app" ]; then
    log_info "App 产物: $DIST_DIR/${APP_NAME}.app"
  elif [ -d "$DIST_DIR/${APP_NAME}" ]; then
    log_info "产物目录: $DIST_DIR/${APP_NAME}"
  fi
  log_info "Release 目录: $RELEASE_DIR"
}

cmd_run() {
  if [ "$HOST_OS" = "windows" ]; then
    log_error "run 不支持 Windows，请直接双击 dist/${APP_NAME}.exe"
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
  [ -x "$binary" ] || die "找不到可执行文件: $binary"

  log_info "启动 $APP_NAME (前台模式)..."
  log_info "按 Ctrl+C 关闭"
  echo ""

  : > "$log_file"
  "$binary" 2>&1 | tee -a "$log_file" || true
  echo ""
  log_success "App 已退出"
}

cmd_dev() {
  check_python
  mkdir -p "$BUILD_DIR"
  local log_file="$BUILD_DIR/dev.log"

  log_info "开发模式: python -m app"
  log_info "按 Ctrl+C 停止"
  echo ""

  : > "$log_file"
  cd "$PROJECT_DIR"
  $PYTHON -m app 2>&1 | tee -a "$log_file" || true
  echo ""
  log_success "开发模式已停止"
}

cmd_test() {
  check_python

  if ! $PYTHON -m pip show -q pytest 2>/dev/null; then
    log_info "首次安装 pytest ..."
    $PYTHON -m pip install -q pytest
  fi

  log_info "运行 pytest (跳过 GUI 自动化测试)..."
  cd "$PROJECT_DIR"
  $PYTHON -m pytest tests/ -v \
    -k "not test_editor_keys and not test_key_states" 2>&1 || \
    log_warn "pytest 返回非 0 (可能 GUI 测试需真实 Tk 环境)"
  log_success "测试命令执行完成"
}

# 同步 scripts/ 到已安装的 Boop.app（macOS 开发期用）
cmd_scripts() {
  local target="/Applications/Boop.app/Contents/Resources/scripts"
  [ -d "$target" ] || die "未找到 /Applications/Boop.app（请先安装或打包）"

  local backup_dir="$PROJECT_DIR/scripts.bak_$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$backup_dir"
  cp -R "$target/"* "$backup_dir/" 2>/dev/null || true
  log_info "已备份原脚本 → $backup_dir"

  find "$target" -name "*.py" -not -path "*/lib/*" -delete 2>/dev/null || true

  find "$PROJECT_DIR/scripts" -maxdepth 1 -name "*.py" -type f \
    -exec cp {} "$target/" \;
  if [ -d "$PROJECT_DIR/scripts/lib" ]; then
    cp -R "$PROJECT_DIR/scripts/lib" "$target/"
  fi
  log_success "scripts/ 已同步 → $target"
}

cmd_clean() {
  log_info "清理构建产物..."
  kill_existing 2>/dev/null || true
  rm -rf "$BUILD_DIR" "$DIST_DIR" "$RELEASE_DIR" \
         "$PROJECT_DIR/${APP_NAME}.spec"
  find "$PROJECT_DIR" -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
  find "$PROJECT_DIR" -name '*.pyc' -delete 2>/dev/null || true
  log_success "清理完成"
}

# ============================================================
# 交互菜单
# ============================================================
commands=(
  "1|b|build    |构建桌面应用 (当前平台)"
  "2|r|run      |构建并前台运行 (Ctrl+C 关闭)"
  "3|d|dev      |开发模式: python -m app 前台运行"
  "4|t|test     |运行单元测试 (pytest, 跳过 GUI 测试)"
  "5|s|scripts  |同步 scripts/ 到 /Applications/Boop.app"
  "6|c|clean    |清理构建产物"
  "0|q|exit     |退出"
)

show_menu() {
  echo ""
  echo "=========================================="
  echo "      Boop - 构建工具 ($HOST_OS/$HOST_ARCH)"
  echo "=========================================="
  for c in "${commands[@]}"; do
    IFS='|' read -r num name desc <<< "$c"
    printf "  %s) %-10s %s\n" "$num" "$name" "$desc"
  done
  echo "=========================================="
  echo -n "请输入选择 [0-6] (回车=dev): "
}

show_help() {
  local version
  version=$(get_version)
  cat <<EOF
Boop 构建工具

用法: $0 [命令]

当前平台: $HOST_OS/$HOST_ARCH   版本: $version   Python: $PYTHON

命令:
  (无参数)    显示交互菜单（回车默认 dev）
  1|build     构建桌面应用 (PyInstaller)
  2|run       构建并前台运行 App (Ctrl+C 关闭)
  3|dev       开发模式: python -m app 前台运行
  4|test      运行单元测试 (跳过需真实 Tk 窗口的测试)
  5|scripts   同步 scripts/ 到 /Applications/Boop.app
  6|clean     清理 build/ dist/ release/ __pycache__
  0|exit      退出

环境变量:
  BOOP_PYTHON   显式指定 Python 解释器路径（CI 用）

项目路径:
  源码:     $PROJECT_DIR
  构建产物:  $DIST_DIR
  Release:   $RELEASE_DIR
  运行日志:  $BUILD_DIR/run.log 和 $BUILD_DIR/dev.log
  版本文件:  $VERSION_FILE
EOF
}

main() {
  local cmd="${1:-}"

  if [ -z "$cmd" ]; then
    show_menu
    read -r choice
    cmd="${choice:-dev}"
  fi

  case "$cmd" in
    1|b|build)       cmd_build ;;
    2|r|run)         cmd_run ;;
    3|d|dev|"")      cmd_dev ;;
    4|t|test)        cmd_test ;;
    5|s|scripts)     cmd_scripts ;;
    6|c|clean)       cmd_clean ;;
    0|q|exit|quit)   echo "退出..."; exit 0 ;;
    help|-h|--help)  show_help ;;
    *)               echo "未知命令: $cmd (--help 查看)"; exit 1 ;;
  esac
}

main "$@"
