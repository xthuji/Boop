#!/bin/bash
#
# Boop - Silent Build Script for macOS, Linux, and Windows
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
readonly APP_BUNDLE_ID="com.okatbest.boop"
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
                   "${SCRIPT_DIR}/version.txt:.")

# Configuration file is now in project root, no need to include in build

PLATFORM="$(uname)"

# State
VERBOSE=false
BUILD_MACOS=false BUILD_LINUX=false BUILD_WINDOWS=false CLEAN_ONLY=false

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
    rm -rf "${BUILD_DIR}" "${DIST_DIR}" "${SCRIPT_DIR}/${PROJECT_NAME}.spec"
    find "${SCRIPT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "${SCRIPT_DIR}" -type f -name "*.pyc" -delete 2>/dev/null || true
    # Skip cleaning system files that might have permission issues
}

#------------------------------------------------------------------------------
# Build Helpers
#------------------------------------------------------------------------------

check_deps() {
    command -v "$PYTHON" >/dev/null || { error "Python 3.9+ required"; exit 1; }
    $PYTHON -m pip show -q pyinstaller 2>/dev/null || $PYTHON -m pip install -q pyinstaller
    $PYTHON -c "import tkinter" 2>/dev/null || { error "Tkinter not found"; exit 1; }
}

pyinstaller_build() {
    local name="$1" icon="$2"
    shift 2
    local extra_args=($@)
    log "Building ${name}..."

    local args=(--name "${PROJECT_NAME}" --windowed --onedir -y
                --workpath "${BUILD_DIR}"
                --distpath "${DIST_DIR}"
                --upx-dir /usr/local/bin
                --optimize=2
                --strip
                --noconfirm
                --log-level=ERROR
                --exclude-module=tkinter.test
                --exclude-module=unittest
                --exclude-module=doctest
                --exclude-module=sqlite3
                --exclude-module=email
                --exclude-module=xml
                --exclude-module=xmlrpc
                --exclude-module=html
                --exclude-module=http
                --exclude-module=ssl
                --exclude-module=bz2
                --exclude-module=zlib
                --exclude-module=ctypes
                --exclude-module=distutils
                --exclude-module=multiprocessing
                --version-file "${SCRIPT_DIR}/version.txt")
    
    # Add data files
    for file in "${APP_FILES[@]}"; do
        args+=(--add-data "$file")
    done
    
    # Add macOS-specific files if building for macOS
    if [[ "$name" == "macOS" ]]; then
        args+=(--add-data "${SCRIPT_DIR}/icons/icon.icns:.")
    fi
    
    args+=(--hidden-import tkinter --hidden-import tkinter.ttk
           --hidden-import boop.ui.main
           --hidden-import boop.ui.script_picker
           --hidden-import boop.core.script
           --hidden-import boop.config.settings)
    [[ -n "$icon" ]] && args+=($icon)
    [[ ${#extra_args[@]} -gt 0 ]] && args+=(${extra_args[@]})
    args+=("${SCRIPT_DIR}/boop/__main__.py")

    $PYTHON -m PyInstaller "${args[@]}" || { error "Build failed for ${name}"; exit 1; }
}

create_dmg() {
    log "Creating DMG..."
    mkdir -p "${DIST_DIR}/dmg_temp"

    if [[ -d "${DIST_DIR}/${PROJECT_NAME}.app" ]]; then
        cp -r "${DIST_DIR}/${PROJECT_NAME}.app" "${DIST_DIR}/dmg_temp/"
    else
        error "No .app bundle found"
        exit 1
    fi

    ln -s /Applications "${DIST_DIR}/dmg_temp/Applications"
    hdiutil create -volname "${PROJECT_NAME}" -srcfolder "${DIST_DIR}/dmg_temp" -ov -format UDZO "${DIST_DIR}/${PROJECT_NAME}-${VERSION}-macos.dmg"
    rm -rf "${DIST_DIR}/dmg_temp"
}

create_tarball() {
    log "Creating tarball..."
    (cd "${DIST_DIR}" && tar -czf "${PROJECT_NAME}-${VERSION}-linux.tar.gz" "${PROJECT_NAME}")
}

create_zip() {
    log "Creating ZIP..."
    (cd "${DIST_DIR}" && zip -rq "${PROJECT_NAME}-${VERSION}-windows.zip" "${PROJECT_NAME}")
}

keep_artifact() {
    # Create a temporary directory to store files to keep
    local tmp=$(mktemp -d)
    
    # Keep files matching RESERVE_FILE_ARRAY patterns
    for pattern in "${RESERVE_FILE_ARRAY[@]}"; do
        find "${DIST_DIR}" -type f -name "*${pattern}" -exec mv {} "$tmp/" 2>/dev/null \;
    done
    
    # Keep directories matching RESERVE_DIR_ARRAY patterns
    for pattern in "${RESERVE_DIR_ARRAY[@]}"; do
        find "${DIST_DIR}" -type d -name "*${pattern}" -exec mv {} "$tmp/" 2>/dev/null \;
    done
    
    # Clean up the dist directory
    rm -rf "${DIST_DIR:?}"/*
    
    # Move back the kept files and directories
    mv "$tmp"/* "${DIST_DIR}/" 2>/dev/null
    
    # Clean up temporary directory
    rm -rf "$tmp"
}

final_cleanup() {
    # Clean up temporary files only
    rm -rf "${DIST_DIR}/dmg_temp"
    rm -f "${SCRIPT_DIR}/${PROJECT_NAME}.spec"
    find "${SCRIPT_DIR}" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    
    # Clean up build directory
    rm -rf "${BUILD_DIR}"
    
    # Keep artifacts (DMG and .app for macOS)
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
    if [[ -f "${DIST_DIR}/${PROJECT_NAME}.app/Contents/Info.plist" ]]; then
        log "Updating version in Info.plist"
        # Use PlistBuddy to update version keys
        /usr/libexec/PlistBuddy -c "Set :CFBundleVersion ${VERSION}" "${DIST_DIR}/${PROJECT_NAME}.app/Contents/Info.plist"
        /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString ${VERSION}" "${DIST_DIR}/${PROJECT_NAME}.app/Contents/Info.plist"
        success "Updated version in Info.plist to ${VERSION}"
    else
        error "Info.plist file not found"
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
  --macos, -m     Build for macOS
  --linux, -l     Build for Linux
  --windows, -w   Build for Windows
  --clean, -c     Clean build artifacts only
  --verbose, -v   Show detailed output
  --help, -h      Show this help

Examples:
  $0 -m           # Build for macOS
  $0 -l -v        # Build for Linux with verbose output
  $0 -c           # Clean build files
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
if [[ "$CLEAN_ONLY" == true ]]; then clean; exit 0; fi

if [[ "$BUILD_MACOS" == false && "$BUILD_LINUX" == false && "$BUILD_WINDOWS" == false ]]; then
    error "No platform specified. Use -m, -l, or -w"
    exit 1
fi

mkdir -p "${BUILD_DIR}" "${DIST_DIR}"
clean

if [[ "$BUILD_MACOS" == true ]]; then build_macos; fi
if [[ "$BUILD_LINUX" == true ]]; then build_linux; fi
if [[ "$BUILD_WINDOWS" == true ]]; then build_windows; fi

exit 0
