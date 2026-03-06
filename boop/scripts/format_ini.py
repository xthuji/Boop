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
    """Format INI file using configparser."""
    if not text or not text.strip():
        return text

    # Use configparser for INI formatting
    try:
        cfg = configparser.ConfigParser()
        cfg.read_string(text)

        # Format the output
        output = io.StringIO()
        cfg.write(output)
        result = output.getvalue()

        # Remove default section header if it was not in the original
        import re
        if not re.search(r'^\s*\[DEFAULT\]', text, re.IGNORECASE | re.MULTILINE):
            result = re.sub(r'^\[DEFAULT\]\s*\n', '', result, flags=re.IGNORECASE)

        return result
    except Exception as e:
        raise Exception("Error formatting INI: {}".format(e))

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
