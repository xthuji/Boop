#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format/Minify JSON",
  "description": "格式化或压缩 JSON 数据",
  "icon": "✨",
  "tags": ["json","format","minify","fmt","code"],
  "dependencies": ["json5"],
  "help": "格式化或压缩 JSON 数据\n\n如果数据已格式化，将进行压缩。\n\n示例:\n输入:\n{\"name\":\"John\",\"age\":30}\n\n输出:\n{\n    \"name\": \"John\",\n    \"age\": 30\n}"
}"""

import json
import json5

def is_minified(text):
    """Check if JSON is minified."""
    # 去除首尾空白后再判断
    text = text.strip()
    # 如果包含换行符，则认为已经格式化，需要压缩
    if '\n' in text:
        return False
    # 如果不包含换行符，则认为是压缩的，需要格式化
    return True

def minify_code(text):
    """Minify JSON."""
    if not text or not text.strip():
        return text

    try:
        parsed = json5.loads(text)
        return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError("Invalid JSON: {}".format(e))

def format_code(text, indent=4):
    """Format JSON text using json5 for compatibility."""
    if not text or not text.strip():
        return text

    try:
        # Use json5 for compatibility with various JSON formats
        parsed = json5.loads(text)
        return json.dumps(parsed, indent=indent, ensure_ascii=False)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError("Invalid JSON: {}".format(e))

def process_format_code(text, indent=4):
    """Process JSON text - format or minify based on input state."""
    if not text or not text.strip():
        return text

    if is_minified(text):
        return format_code(text, indent)
    else:
        return minify_code(text)

def main(state):
    """Format or minify JSON text."""
    if not state.text or not state.text.strip():
        return

    # 处理自定义参数
    indent = 4
    if hasattr(state, 'args') and state.args:
        try:
            # 解析参数，例如 "indent=2"
            for arg in state.args:
                if arg.startswith('indent='):
                    indent = int(arg.split('=')[1])
        except (ValueError, IndexError):
            pass

    try:
        state.text = process_format_code(state.text, indent).strip()
    except ValueError as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))
        else:
            print("Error formatting JSON: {}".format(str(e)))
