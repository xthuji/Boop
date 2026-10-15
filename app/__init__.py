"""
Boop Python - A text manipulation tool powered by Python scripts
Inspired by the original Boop macOS app
"""

import sys
from pathlib import Path

__author__ = "Boop Python Team"


def _read_version() -> str:
    """从 VERSION 文件读取版本号（单一版本来源，文件内容即纯版本号，同时被 run_tools.sh / release.sh 解析）"""
    # 1. PyInstaller 打包环境: VERSION 位于解包资源目录
    if hasattr(sys, '_MEIPASS'):
        version_file = Path(sys._MEIPASS) / "VERSION"
    # 2. 开发环境: boop/VERSION
    else:
        version_file = Path(__file__).resolve().parent.parent / "VERSION"
    try:
        version = version_file.read_text(encoding='utf-8').strip()
        if version:
            return version
    except Exception:
        pass
    return "0.0.0"


__version__ = _read_version()
