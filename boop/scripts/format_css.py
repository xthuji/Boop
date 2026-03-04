#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format CSS",
  "description": "Professional CSS code formatter and minifier",
  "icon": "pineapple",
  "tags": ["css", "format", "minify"],
  "help": "Format or minify CSS text.\n\nExample:\nInput:\nbody{margin:0;padding:0;}\n\nOutput:\nbody {\n    margin: 0;\n    padding: 0;\n}"
}
"""

import re

def is_minified(text):
    """Check if CSS is minified."""
    return not '\n' in text and '{' in text

def minify_code(css):
    """Minify CSS."""
    if not css or not css.strip():
        return css
    
    # 移除注释
    css = re.sub(r'/\*[\s\S]*?\*/', '', css)
    # 移除多余空格
    css = re.sub(r'\s*([\{\};:,])\s*', r'\1', css)
    # 移除多余空格
    css = re.sub(r'\s+', ' ', css)
    # 移除大括号前的分号
    css = re.sub(r';\}', '}', css)
    return css.strip()

def format_code(text):
    """Format CSS text with 4-space indentation."""
    if not text or not text.strip():
        return text
    
    indent_size = 4
    indent_level = 0
    
    # 预处理：标准化符号，补全缺失的分号
    formatted = re.sub(r'\s*([\{\};:,])\s*', r'$1', text)  # 移除多余空格
    formatted = re.sub(r'([^\{\};\n])(?=\})', r'\1;', formatted)  # 核心修复：如果右大括号前没有分号，强制补一个
    formatted = re.sub(r'/\*([\s\S]*?)\*/', r'\n/* \1 */\n', formatted)  # 保护并隔离注释
    formatted = re.sub(r'\{', ' {\n', formatted)
    formatted = re.sub(r'\}', '\n}\n', formatted)
    formatted = re.sub(r';', ';\n', formatted)
    # 精准空格控制
    formatted = re.sub(r':(?![^\{]*\{)(?![^\}]*\{)', r': ', formatted)
    formatted = re.sub(r'\(([^)]+)\)', lambda m: m.group(0).replace(':', ': '), formatted)
    formatted = re.sub(r'\s*!important', ' !important', formatted)
    formatted = re.sub(r',', ', ', formatted)
    
    lines = formatted.split('\n')
    result = []
    
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue
        
        if trimmed.startswith('}'):
            indent_level = max(0, indent_level - 1)
        
        current_indent = ' ' * indent_size * indent_level
        
        # 规范注释内部空格
        if trimmed.startswith('/*'):
            trimmed = re.sub(r'/\*\s*(.*?)\s*\*/', r'/* $1 */', trimmed)
        
        result.append(current_indent + trimmed)
        
        if trimmed.endswith('{'):
            indent_level += 1
    
    return '\n'.join(result).replace('\n{2,}', '\n').strip() + '\n'

def process_format_code(text):
    """Process CSS text - format or minify based on input state."""
    if not text or not text.strip():
        return text
    
    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)

def main(state):
    """Format or minify CSS text."""
    if not state.text or not state.text.strip():
        return
    
    try:
        state.text = process_format_code(state.text)
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error("Error formatting CSS: {}".format(str(e)))
        else:
            print("Error formatting CSS: {}".format(str(e)))


