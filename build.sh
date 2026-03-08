#!/bin/bash
#
# Boop - Build Script for macOS, Linux, and Windows
#
# Usage:
#   ./build.sh              # Build for current platform
#   ./build.sh --macos      # Build for macOS only
#   ./build.sh --linux      # Build for Linux only
#   ./build.sh --windows    # Build for Windows only
#   ./build.sh --clean      # Clean build artifacts
#   ./build.sh --verbose    # Show detailed output
#

# Configuration
readonly PROJECT_NAME="Boop"
readonly APP_BUNDLE_ID="com.xthuji.boop"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Read version from version.txt file
readonly VERSION=$(grep -E '^VERSION = ' "${SCRIPT_DIR}/version.txt" | cut -d ' ' -f 3)
readonly BUILD_DIR="${SCRIPT_DIR}/build"
readonly DIST_DIR="${SCRIPT_DIR}/dist"
readonly PYTHON="$HOME/miniconda3/envs/python39/bin/python3"
readonly RESERVE_FILE_ARRAY=(-macos.dmg -windows.zip -linux.tar.gz)
readonly RESERVE_DIR_ARRAY=(".app")

# App files and directories to include in the build
# For macOS, the files will be placed in Contents/Resources
readonly APP_FILES=("${SCRIPT_DIR}/boop/scripts:scripts"
                   "${SCRIPT_DIR}/boop/core/script_wrapper.py:boop/core"
                   "${SCRIPT_DIR}/version.txt:."
                   "${SCRIPT_DIR}/USER_GUIDE.md:.")

# Configuration file is now in project root, no need to include in build

PLATFORM="$(uname)"

# State
VERBOSE=false
BUILD_MACOS=false BUILD_LINUX=false BUILD_WINDOWS=false CLEAN_ONLY=false

# Exclude modules list - only exclude non-essential modules
# 根据项目代码分析，只排除确实不需要的模块
readonly EXCLUDE_MODULES=(
    # 测试相关
    "test" "tkinter.test" "unittest" "doctest"
    # 调试和分析工具
    "trace" "profile" "pstats" "tabnanny" "pyclbr"
    # 模块工具
    "pickletools" "zipimport" "modulefinder" "lib2to3"
    # 数据库
    "sqlite3"
    # 网络相关
    "email" "urllib3" "requests" "http" "html" "webbrowser"
    # 并发（项目使用threading，不使用multiprocessing和asyncio）
    "multiprocessing" "asyncio" "concurrent"
    # 包管理
    "distutils" "setuptools" "pkg_resources"
    # 工具
    "timeit" "optparse" "configparser" "csv" "calendar" "statistics"
    # 终端相关
    "tty" "pty" "termios" "readline" "nis" "grp" "pwd" "spwd" "crypt"
    # 其他
    "secrets" "usercustomize" "sitecustomize"
    # 额外排除模块
    "curses" "dbm"
    "xmlrpc" "httplib2"
    "ftplib" "poplib" "imaplib" "smtplib"
    "telnetlib"
    # 图像处理（项目可能使用Pillow，但只在构建时使用）
    "opencv" "tensorflow" "torch"
    # Web框架
    "sqlalchemy" "django" "flask_sqlalchemy"
    # 科学计算
    "numpy" "scipy" "pandas" "matplotlib"
    # 其他GUI框架（项目使用tkinter）
    "PyQt5" "gi" "wx" "PySide2"
)

#------------------------------------------------------------------------------
# Logging
#------------------------------------------------------------------------------

log() { echo "[INFO] $1"; }
success() { echo "[OK] $1"; }
error() { echo "[ERROR] $1" >&2; }

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------

clean() {
    log "清理构建产物..."
    rm -rf "${BUILD_DIR}" "${DIST_DIR}" "${SCRIPT_DIR}/${PROJECT_NAME}.spec"
    find "${SCRIPT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "${SCRIPT_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
    # Skip cleaning system files that might have permission issues
}

#------------------------------------------------------------------------------
# Build Helpers
#------------------------------------------------------------------------------

check_deps() {
    log "检查依赖..."
    command -v "$PYTHON" >/dev/null || { error "Python 3.9+ required"; exit 1; }
    $PYTHON -m pip show -q pyinstaller 2>/dev/null || $PYTHON -m pip install -q pyinstaller
    $PYTHON -c "import tkinter" 2>/dev/null || { error "Tkinter not found"; exit 1; }
}

pyinstaller_build() {
    local name="$1" icon="$2"
    shift 2
    local extra_args=($@)
    log "构建 ${name} 版本..."

    local args=(--name "${PROJECT_NAME}" --windowed --onedir -y
                --workpath "${BUILD_DIR}"
                --distpath "${DIST_DIR}"
                --upx-dir /usr/local/bin
                --upx-exclude=vcruntime140.dll
                --upx-exclude=msvcp140.dll
                --optimize=2
                --strip
                --noconfirm
                --log-level=ERROR
                --version-file "${SCRIPT_DIR}/version.txt")
    
    # Add exclude modules
    for module in "${EXCLUDE_MODULES[@]}"; do
        args+=(--exclude-module="$module")
    done
    
    # Add data files
    # scripts目录会被直接复制，包含其中的.py文件（不使用.pyc文件）
    for file in "${APP_FILES[@]}"; do
        args+=(--add-data "$file")
    done
    
    # Add macOS-specific files if building for macOS
    if [[ "$name" == "macOS" ]]; then
        args+=(--add-data "${SCRIPT_DIR}/icons/icon.icns:." )
    fi
    
    args+=(--hidden-import tkinter --hidden-import tkinter.ttk
           --hidden-import boop.ui.main
           --hidden-import boop.ui.script_picker
           --hidden-import boop.core.script
           --hidden-import boop.config.settings
           --hidden-import boop.core.global_hotkey
           --hidden-import pynput
           --hidden-import pynput.keyboard)
    log "默认启用全局快捷键支持"
    [[ -n "$icon" ]] && args+=($icon)
    [[ ${#extra_args[@]} -gt 0 ]] && args+=(${extra_args[@]})
    args+=("${SCRIPT_DIR}/boop/__main__.py")

    $PYTHON -m PyInstaller "${args[@]}" || { error "${name} 版本构建失败"; exit 1; }
}

create_dmg() {
    log "创建 DMG 安装包..."
    rm -rf "${DIST_DIR}/dmg_temp"
    mkdir -p "${DIST_DIR}/dmg_temp"

    if [[ -d "${DIST_DIR}/${PROJECT_NAME}.app" ]]; then
        cp -r "${DIST_DIR}/${PROJECT_NAME}.app" "${DIST_DIR}/dmg_temp/"
    else
        error "未找到 .app 包"
        exit 1
    fi

    ln -s /Applications "${DIST_DIR}/dmg_temp/Applications"
    hdiutil create -volname "${PROJECT_NAME}" -srcfolder "${DIST_DIR}/dmg_temp" -ov -format UDZO "${DIST_DIR}/${PROJECT_NAME}-${VERSION}-macos.dmg"
    rm -rf "${DIST_DIR}/dmg_temp"
}

create_tarball() {
    log "创建 tarball 压缩包..."
    (cd "${DIST_DIR}" && tar -czf "${PROJECT_NAME}-${VERSION}-linux.tar.gz" "${PROJECT_NAME}")
}

create_zip() {
    log "创建 ZIP 压缩包..."
    (cd "${DIST_DIR}" && zip -rq "${PROJECT_NAME}-${VERSION}-windows.zip" "${PROJECT_NAME}")
}

keep_artifact() {
    log "清理 dist 目录，只保留指定文件和目录..."
    
    # 遍历 dist 目录下的所有第一级文件和目录
    for item in "${DIST_DIR}"/*; do
        if [[ -e "$item" ]]; then
            local basename=$(basename "$item")
            local keep=false
            
            # 检查是否匹配 RESERVE_FILE_ARRAY 中的模式
            if [[ -f "$item" ]]; then
                for pattern in "${RESERVE_FILE_ARRAY[@]}"; do
                    if [[ "$basename" == *"$pattern" ]]; then
                        keep=true
                        break
                    fi
                done
            # 检查是否匹配 RESERVE_DIR_ARRAY 中的模式
            elif [[ -d "$item" ]]; then
                for pattern in "${RESERVE_DIR_ARRAY[@]}"; do
                    if [[ "$basename" == *"$pattern" ]]; then
                        keep=true
                        break
                    fi
                done
            fi
            
            # 如果不需要保留，则删除
            if [[ "$keep" == false ]]; then
                log "删除不需要的项: $basename"
                rm -rf "$item"
            else
                log "保留项: $basename"
            fi
        fi
    done
}

clean_py_files() {
    log "清理 .py 文件，只保留 .pyc 文件..."
    # 删除所有 .py 文件，但保留 scripts 目录中的 .py 文件
    find "${DIST_DIR}" -type f -name "*.py" -not -path "*/scripts/*" -delete 2>/dev/null
    # 确保 .pyc 文件存在
    find "${DIST_DIR}" -type f -name "*.pyc" | head -5 && log "确认 .pyc 文件存在"
}

final_cleanup() {
    # 清理临时文件
    rm -rf "${DIST_DIR}/dmg_temp"
    rm -f "${SCRIPT_DIR}/${PROJECT_NAME}.spec"
    find "${SCRIPT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # 清理构建目录
    rm -rf "${BUILD_DIR}"
    
    # 清理 .py 文件，只保留 .pyc 文件
    clean_py_files
    
    # 保留指定的文件和目录
    keep_artifact
}

#------------------------------------------------------------------------------
# Platform Builds
#------------------------------------------------------------------------------

build_macos() {
    check_deps
    pyinstaller_build "macOS" \
        "--icon ${SCRIPT_DIR}/icons/icon.icns" \
        "--osx-bundle-identifier ${APP_BUNDLE_ID}"
    
    # Update version in plist file for macOS
    log "更新 .app 包中的版本号..."
    PLIST_FILE="${DIST_DIR}/${PROJECT_NAME}.app/Contents/Info.plist"
    if [[ -f "$PLIST_FILE" ]]; then
        # Use PlistBuddy to update version keys
        /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString ${VERSION}" "$PLIST_FILE" || \
        /usr/libexec/PlistBuddy -c "Add :CFBundleShortVersionString string ${VERSION}" "$PLIST_FILE"
        log "版本号已更新为 ${VERSION}"
    else
        error "未找到 Info.plist 文件"
    fi
    
    create_dmg
    final_cleanup
    success "${DIST_DIR}/${PROJECT_NAME}-${VERSION}-macos.dmg"
}

build_linux() {
    check_deps
    pyinstaller_build "Linux" \
        "--icon ${SCRIPT_DIR}/icons/icon_256x256.png"
    create_tarball
    final_cleanup
    success "${DIST_DIR}/${PROJECT_NAME}-${VERSION}-linux.tar.gz"
}

build_windows() {
    check_deps
    pyinstaller_build "Windows" \
        "--icon ${SCRIPT_DIR}/icons/icon.ico"
    create_zip
    final_cleanup
    success "${DIST_DIR}/${PROJECT_NAME}-${VERSION}-windows.zip"
}

#------------------------------------------------------------------------------
# CLI
#------------------------------------------------------------------------------

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
  --macos, -m     构建 macOS 版本
  --linux, -l     构建 Linux 版本
  --windows, -w   构建 Windows 版本
  --clean, -c     仅清理构建产物
  --verbose, -v   显示详细输出
  --help, -h      显示帮助信息

示例:
  $0 -m           # 构建 macOS 版本
  $0 -l -v        # 构建 Linux 版本并显示详细输出
  $0 -c           # 清理构建文件
EOF
}

# Parse arguments
if [[ $# -eq 0 ]]; then
    case "$PLATFORM" in
        Darwin)  BUILD_MACOS=true ;;
        Linux)   BUILD_LINUX=true ;;
        *)       BUILD_WINDOWS=true ;;
    esac
fi

while [[ $# -gt 0 ]]; do
    case "$1" in
        --macos|-m) BUILD_MACOS=true; shift ;;
        --linux|-l) BUILD_LINUX=true; shift ;;
        --windows|-w) BUILD_WINDOWS=true; shift ;;
        --clean|-c) CLEAN_ONLY=true; shift ;;
        --verbose|-v) VERBOSE=true; shift ;;
        --help|-h) usage; exit 0 ;;
        *) error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Main
if [[ "$CLEAN_ONLY" == true ]]; then 
    clean 
    success "清理完成"
    exit 0
fi

if [[ "$BUILD_MACOS" == false && "$BUILD_LINUX" == false && "$BUILD_WINDOWS" == false ]]; then
    error "未指定平台。使用 -m, -l 或 -w"
    exit 1
fi

mkdir -p "${BUILD_DIR}" "${DIST_DIR}"
clean

log "正在安装依赖..."
$PYTHON -m pip install -r requirements.txt

# 预编译字节码（忽略scripts目录）
log "正在预编译字节码..."
$PYTHON -m compileall -b . --exclude "boop/scripts" 2>/dev/null || log "字节码预编译完成"

# Build
if [[ "$BUILD_MACOS" == true ]]; then build_macos; fi
if [[ "$BUILD_LINUX" == true ]]; then build_linux; fi
if [[ "$BUILD_WINDOWS" == true ]]; then build_windows; fi

exit 0