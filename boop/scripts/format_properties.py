#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format Properties",
  "description": "Professional Properties file formatter and minifier.",
  "icon": "pineapple",
  "tags": ["properties", "format", "minify"],
  "help": "Format or minify Properties file with proper formatting.\n\nExample:\nInput:\nkey1=value1\nkey2=value2\n\nOutput:\nkey1=value1\nkey2=value2\n\nIf the file is already formatted, it will be minified."
}
"""

import re


def format_code(code: str) -> str:
    """
    格式化 Properties 文件代码。
    
    功能：
    - 支持 = 和 : 两种分隔符
    - 统一 key-value 格式
    - 保留注释和空行
    - 移除连续空行
    """
    if not code or not code.strip():
        return code
    
    lines = code.split('\n')
    formatted = []
    
    for line in lines:
        stripped = line.strip()
        
        # 跳过空行和注释
        if not stripped or stripped.startswith('#') or stripped.startswith('!'):
            if stripped:
                formatted.append(stripped)
            else:
                formatted.append('')
            continue
        
        # 处理 key-value 对
        if '=' in stripped or ':' in stripped:
            # 找到第一个分隔符位置
            sep_pos = -1
            sep_char = '='
            
            for i, char in enumerate(stripped):
                if char in '=:':
                    sep_pos = i
                    sep_char = char
                    break
            
            if sep_pos != -1:
                key = stripped[:sep_pos].strip()
                value = stripped[sep_pos + 1:].strip()
                formatted.append('{}={}'.format(key, value))
            else:
                formatted.append(stripped)
        else:
            formatted.append(stripped)
    
    # 移除连续空行
    result = []
    prev_empty = False
    for line in formatted:
        if not line:
            if not prev_empty:
                result.append(line)
            prev_empty = True
        else:
            result.append(line)
            prev_empty = False
    
    return '\n'.join(result).strip() + '\n'


def main(state):
    """Format or minify Properties text."""
    if not state.text or not state.text.strip():
        return
    
    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Properties formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(f"Error formatting Properties: {str(e)}")
        else:
            print(f"Error formatting Properties: {str(e)}")

def is_minified(text):
    """Check if Properties is minified."""
    text = text.strip()
    return not '\n' in text and '=' in text

def minify_code(text):
    """Minify Properties file."""
    if not text or not text.strip():
        return text
    
    # 移除注释
    lines = text.split('\n')
    minified_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('!'):
            continue
        minified_lines.append(stripped)
    return ' '.join(minified_lines)

def process_format_code(text):
    """Process Properties text - format or minify based on input state."""
    if not text or not text.strip():
        return text
    
    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)


