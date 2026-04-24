"""
Boop Python - A text manipulation tool powered by Python scripts
Inspired by the original Boop macOS app
"""

import re
import sys
from pathlib import Path

__author__ = "Boop Python Team"


def _read_version() -> str:
    """从 version.txt 读取版本号（单一版本来源，同时被 build.sh / release.sh 解析）"""
    # 1. PyInstaller 打包环境: version.txt 位于解包资源目录
    if hasattr(sys, '_MEIPASS'):
        version_file = Path(sys._MEIPASS) / "version.txt"
    # 2. 开发环境: boop/version.txt
    else:
        version_file = Path(__file__).resolve().parent.parent / "version.txt"
    try:
        match = re.search(r'^VERSION = ([\d.]+)', version_file.read_text(encoding='utf-8'), re.MULTILINE)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "0.0.0"


__version__ = _read_version()
