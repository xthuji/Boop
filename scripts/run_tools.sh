#!/usr/bin/env bash
# =============================================================================
# Boop - 构建与运行工具 (跨平台: macOS / Linux / Windows Git Bash)
# =============================================================================
# 命令:
#   1|b,build     构建桌面应用 (PyInstaller 打包, 自动适配当前平台)
#   2|r,run       构建并前台运行 (Ctrl+C 关闭)
#   3|d,dev       开发模式: 直接 python -m app 前台运行 (Ctrl+C 关闭)
#   4|t,test      运行单元测试 (业务用例 run_tests.py + pytest 冒烟, 跳过 GUI 自动化)
#   5|s,scripts   同步 custom_scripts/ 到 /Applications/Boop.app
#   6|c,clean     清理构建产物
#   7|i,install   安装依赖包 (requirements.txt + PyInstaller + pytest)
#   0|q|exit      退出
#
# 发布产物: macOS 的最终发布物是 DMG（release/ 只存放 DMG，不再放 .app），
#   .app 仅作为 DMG 的输入保留在 build/dist（构建中间产物目录）。
#
# macOS 架构策略：单架构打包（NEEDS_UNIVERSAL=0），产物跟随构建机架构。
#   本机：Intel 出 x86_64、Apple Silicon 出 arm64，各自单 slice、不做 universal 合并。
#   CI：macos-latest（arm64）用矩阵分别构建 arm64 与 x86_64 两个单架构 DMG，
#   x86_64 经 Rosetta 用 python.org universal2 解释器的 x86_64 slice 构建。
#
# CI 契约（.github/workflows/release.yml 按 tag 三平台并行调用）:
#   ./scripts/run_tools.sh build                 → 当前 runner 原生架构单 slice
#   arch -x86_64 ./scripts/run_tools.sh build    → x86_64 单 slice（Rosetta）
#   经 BOOP_PYTHON 注入解释器；内部完成 PyInstaller 单架构 → plist 修正 →
#   ad-hoc 签名 → DMG；产物 glob: release/*.dmg | release/*.tar.gz | release/*.zip
#
# 全部构建/打包/测试逻辑集中在入口与公共母版模块，CI workflow 只做 runner 引导
# 与产物上传，避免 CI 与本地漂移。母版拆分为 run_tools_master.sh（与
# easy_translate 逐字节一致，入口 source 加载），入口只保留常量与命令表 /
# 专属实现内联区。
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 脚本位于 <project>/scripts/，项目根目录为其上级目录
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_DIR"

# --- 顶层内联平台探测：常量表求值早于母版加载，HOST_OS 必须先于 DATA_SEP 就绪 ---
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
PYTHON_ENV_VAR="BOOP_PYTHON"                    # 显式指定解释器的环境变量名（CI 用）
PYTHON_ENV_VAR_X86_64="BOOP_PYTHON_X86_64"      # 仅 universal 分支需（NEEDS_UNIVERSAL=0 下不启用）
PREFERRED_PYTHON="${HOME}/miniconda3/envs/python39/bin/python3"
MIN_PYTHON_VERSION="3.9"
DEPS_IMPORT_CHECK="pynput,pyperclip"            # install 命令展示的依赖
RUNTIME_IMPORT_PROBE="import pynput, pyperclip" # ensure_runtime_deps 的就绪探测
NEEDS_TKINTER=1
NEEDS_PYTEST=1                  # 测试体系为 unittest 驱动的 run_tests.py（cmd_test 已覆盖），
#                                 pytest 仅经 install 安装供 tests/ 下按键测试偶尔冒烟

# --- 构建策略 ---
NEEDS_UNIVERSAL=0               # 0=macOS 单架构打包（跟随构建机架构，不做 universal 合并）
MACOS_UNIVERSAL_FORCE=0         # NEEDS_UNIVERSAL=0 时无效（universal 分支整体不进入）
PLATFORM_SCOPE="all"            # 三平台出包（macOS 单架构 DMG / Linux tgz / Windows zip）
MACOS_MIN_VERSION="12.0"
MACOSX_DEPLOYMENT_TARGET_DEFAULT="$MACOS_MIN_VERSION"
PYI_WINDOWED=1
PYI_OPTIMIZE=2
PYI_STRIP=1
PYI_LOG_LEVEL="ERROR"
ENTRY_PY="$PROJECT_DIR/app/__main__.py"

# --- 图标（mac 用预制 .icns，Windows 用 .ico，Linux 用 .png）---
ICON_ICNS="$PROJECT_DIR/icons/icon.icns"
ICON_ICO="$PROJECT_DIR/icons/icon.ico"
ICON_PNG="$PROJECT_DIR/icons/icon_256x256.png"

# --- 产物细节 ---
ADHOC_SIGN=1                    # 1=macOS 构建后 ad-hoc 签名（改 Info.plist 会让 PyInstaller 签名失效）
# hdiutil 额外参数（数组，逐项传参）：-imagekey zlib-level=9 提升压缩率
readonly DMG_IMAGEKEY_ARGS=( -imagekey zlib-level=9 )
# 清理 release 中历史残留的中间产物（旧版曾把 .app/onedir 落进 release/）
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

# 需要一起打包的非 .py 资源 (src{sep}dest)
# custom_scripts 为用户可热扩展脚本族，运行时从解包目录扫描加载；
# script_wrapper.py 是脚本运行契约源文件，须以 app/core 路径随包可导入。
readonly APP_DATA_FILES=(
  "$(_to_native_path "$PROJECT_DIR/custom_scripts")${DATA_SEP}custom_scripts"
  "$(_to_native_path "$PROJECT_DIR/app/core/script_wrapper.py")${DATA_SEP}app/core"
  "$(_to_native_path "$PROJECT_DIR/VERSION")${DATA_SEP}."
  "$(_to_native_path "$PROJECT_DIR/data")${DATA_SEP}data"
)

# 隐藏导入（PyInstaller 静态分析不到的动态引用）
readonly HIDDEN_IMPORTS=(
  "tkinter"
  "tkinter.ttk"
  "pynput"
  "pynput.keyboard"
)

# 无条件排除：测试/调试、模块工具、数据库、未用的网络与并发、
# 包管理、其他 GUI/Web/科学栈（conda 环境防御，避免被连带吸入）
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

# 条件排除：本项目不使用的可选轻型模块，仅当构建环境未安装时才排除
# （"Boop" 为无条件排除：Linux onedir 产物目录名与 App 同名，避免自吸入）
readonly OPTIONAL_EXCLUDE_CANDIDATES=(
  "pystray" "tkinter.test.support" "Boop"
)

# --- 测试 / 清理（cmd_test 已覆盖为 run_tests.py + pytest 冒烟，以下仅作登记）---
PYTEST_PATHS=( tests/ )
PYTEST_EXTRA=()
PYTEST_SKIP_EXPR=""
CLEAN_EXTRA=()

# --- 菜单与分发 ---
DEFAULT_CMD="dev"               # 交互菜单回车默认
FALLBACK_CMD="cmd_dev"          # 未识别命令按开发模式兜底（延续历史行为）
SRC_FIND_EXPR=( -name '*.py' -o -name 'VERSION' -o -name 'requirements.txt'
  -o -path '*/custom_scripts/*' -o -path '*/icons/*' -o -path '*/data/*' )

# --- 命令表：序号|别名(逗号分隔)|说明|处理函数（菜单/帮助/分发唯一真源）---
commands=(
  "1|b,build|构建桌面应用 (PyInstaller, 当前平台)|cmd_build"
  "2|r,run|构建并前台运行 (Ctrl+C 关闭)|cmd_run"
  "3|d,dev|开发模式: python -m app 前台运行|cmd_dev"
  "4|t,test|运行单元测试 (业务用例 + pytest 冒烟)|cmd_test"
  "5|s,scripts|同步 custom_scripts/ 到 /Applications/Boop.app|cmd_scripts"
  "6|c,clean|清理构建产物|cmd_clean"
  "7|i,install|安装依赖包 (requirements + PyInstaller + pytest)|cmd_install"
)

# ============================================================
# 公共模块：母版实现（与其余 Python 桌面应用逐字节一致，请勿在此修改）
# 必须在常量表之后 source：母版顶层执行 detect_platform + detect_python，
# 依赖常量表已设的 PYTHON/PYTHON_ENV_VAR；HOST_OS 已由上方内联探测就绪。
# ============================================================
source "$SCRIPT_DIR/run_tools_master.sh"

# ============================================================
# 项目专属实现（覆盖母版默认 / 追加项目专属命令）
# ============================================================
# 业务脚本用例（非 pytest 体系）：tests/test_scripts/run_tests.py 扫描
# custom_scripts/ 并按 JSON 用例分组执行；pytest 对 tests/ 的收集恒为 0
#（GUI 按键测试是独立脚本不是用例），母版默认 cmd_test 会假绿，故覆盖。
cmd_test() {
  check_python

  log_info "运行业务脚本用例 (tests/test_scripts/run_tests.py)..."
  local rc=0
  if $DRY_RUN; then
    log_warn "[dry-run] $PYTHON tests/test_scripts/run_tests.py"
  else
    $PYTHON "$PROJECT_DIR/tests/test_scripts/run_tests.py" || rc=$?
  fi

  ensure_pytest
  log_info "pytest 冒烟 (跳过需真实 Tk 窗口的 GUI 自动化测试)..."
  if ! $DRY_RUN; then
    $PYTHON -m pytest tests/ -v \
      -k "not test_editor_keys and not test_key_states" \
      || log_warn "pytest 返回非 0 (可能无收集用例或 GUI 测试需真实 Tk 环境)"
  fi

  if [ "$rc" -ne 0 ]; then
    log_error "业务脚本用例未通过 (run_tests.py rc=$rc)"
  fi
  log_success "测试命令执行完成"
}

# 同步 custom_scripts/ 到已安装的 Boop.app（macOS 开发期用）：
# 先整体备份到 custom_scripts.bak_<时间戳>/，再清装新脚本（只同步顶层 .py 与 lib/）。
cmd_scripts() {
  local target="/Applications/Boop.app/Contents/Resources/custom_scripts"
  [ -d "$target" ] || log_error "未找到 /Applications/Boop.app（请先安装或打包）"

  if $DRY_RUN; then
    log_warn "[dry-run] 备份 $target → custom_scripts.bak_<时间戳>/，再同步项目 custom_scripts/"
    return 0
  fi

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

# 构建产物落 dist 后的项目附加动作：清掉随 --add-data 整目录拷入的
# __pycache__/*.pyc（解包扫描加载会读到陈旧字节码，且徒增体积）。
hook_post_build() {
  $DRY_RUN && return 0
  local res="$DIST_DIR/${APP_NAME}.app/Contents/Resources"
  [ -d "$res" ] || return 0
  find "$res" -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
  find "$res" -name '*.pyc' -delete 2>/dev/null || true
}

# 帮助尾部补充：项目专属命令与环境变量说明
show_help_extra() {
  cat <<EOF

项目说明:
  scripts 命令将项目 custom_scripts/ 同步到已安装的
  /Applications/Boop.app/Contents/Resources/custom_scripts（同步前自动备份）。
  custom_scripts/ 与 data/ 已通过 --add-data 随包，构建期无需额外操作。

环境变量:
  $PYTHON_ENV_VAR           显式指定 Python 解释器路径（本机单架构直接用当前 slice）
  MACOSX_DEPLOYMENT_TARGET  macOS 部署目标（缺省 ${MACOS_MIN_VERSION}）

macOS 采用单架构打包（NEEDS_UNIVERSAL=0）：产物跟随构建机架构（本机 Intel → x86_64、
Apple Silicon → arm64）。CI 用矩阵分别在 arm64 与 x86_64 slice 上构建两份单架构 DMG，
x86_64 侧经 `arch -x86_64 ./scripts/run_tools.sh build`（Rosetta）得到。
EOF
}

main "$@"
