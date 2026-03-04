#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format JSON",
  "description": "Professional JSON code formatter and minifier",
  "icon": "pineapple",
  "tags": ["json", "format", "minify"],
  "dependencies": ["json5"],
  "help": "Format or minify JSON text using json5 for compatibility.\n\nExample:\nInput: {\"name\":\"John\",\"age\":30}\nOutput: {\n    \"name\": \"John\",\n    \"age\": 30\n}\n\nIf the JSON is already formatted, it will be minified."
}
"""

import json
import json5

def is_minified(text):
    """Check if JSON is minified."""
    text = text.strip()
    return not ('\n' in text or '  ' in text) and ((text.startswith('{') and text.endswith('}')) or (text.startswith('[') and text.endswith(']')))

def minify_code(text):
    """Minify JSON."""
    if not text or not text.strip():
        return text
    
    try:
        parsed = json5.loads(text)
        return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False) + '\n'
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError("Invalid JSON: {}".format(e))

def format_code(text, indent=4):
    """Format JSON text using json5 for compatibility."""
    if not text or not text.strip():
        return text
    
    try:
        parsed = json5.loads(text)
        return json.dumps(parsed, indent=indent, ensure_ascii=False) + '\n'
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
        state.text = process_format_code(state.text, indent).strip() + '\n'
    except ValueError as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))
        else:
            print("Error formatting JSON: {}".format(str(e)))


