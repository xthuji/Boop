#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format INI",
  "description": "格式化 INI 配置文件",
  "icon": "✨",
  "tags": ["ini","format","fmt","config","code"],
  "dependencies": [],
  "help": "格式化 INI 配置文件\n\n示例:\n输入:\n[section]\nkey=value\n\n输出:\n[section]\nkey = value"
}"""

import configparser
import io

def format_code(text):
    """Format INI file."""
    if not text or not text.strip():
        return text

    import re
    lines = text.split('\n')
    formatted = []
    in_section = False

    for line in lines:
        stripped = line.strip()

        # Skip empty lines
        if not stripped:
            continue

        # Handle section headers
        if stripped.startswith('[') and stripped.endswith(']'):
            formatted.append(stripped)
            in_section = True
        # Handle comments
        elif stripped.startswith('#') or stripped.startswith(';'):
            formatted.append(stripped)
        # Handle key-value pairs
        elif '=' in stripped and in_section:
            key, value = stripped.split('=', 1)
            key = key.strip()
            value = value.strip()
            formatted.append('{} = {}'.format(key, value))
        else:
            formatted.append(stripped)

    return '\n'.join(formatted).strip()

def main(state):
    """Format INI text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("INI formatted")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))
        else:
            print("Error formatting INI: {}".format(str(e)))
