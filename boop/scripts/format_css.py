#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format/Minify CSS",
  "description": "格式化或压缩 CSS 样式代码",
  "icon": "✨",
  "tags": ["css","format","minify","fmt","code"],
  "dependencies": [],
  "help": "格式化或压缩 CSS 样式代码\n\n如果代码已格式化，将进行压缩。\n\n示例:\n输入:\nbody{color:red}\n\n输出:\nbody {\n    color: red;\n}"
}"""

import re

def is_minified(text):
    """Check if CSS is minified."""
    # 如果包含换行符，则认为已经格式化，需要压缩
    if '\n' in text:
        return False
    # 如果不包含换行符，则认为是压缩的，需要格式化
    return True

def minify_code(css):
    """Minify CSS."""
    if not css or not css.strip():
        return css

    # Simple minification
    return css.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').strip()

def format_code(text):
    """Format CSS text with 4-space indentation."""
    if not text or not text.strip():
        return text

    # 简单的 CSS 格式化实现
    indent_size = 4
    indent_level = 0
    formatted_lines = []

    # 处理 CSS 规则
    # 首先移除所有多余的空格
    text = re.sub(r'\s+', ' ', text)
    # 处理花括号
    text = re.sub(r'\s*\{\s*', ' {\n', text)
    text = re.sub(r'\s*\}\s*', '\n}\n', text)
    # 处理分号
    text = re.sub(r'\s*;\s*', ';\n', text)
    # 确保每个属性后都有分号，但不在花括号后添加分号
    text = re.sub(r'([^;\n{}])\n\s*([^}])', r'\1;\n\2', text)
    # 移除花括号后的多余分号
    text = re.sub(r'\{\s*;', '{', text)
    # 处理冒号（注意：伪类选择器中的冒号不应添加空格）
    # 先处理所有冒号，确保没有多余空格
    text = re.sub(r'\s*:\s*', ':', text)
    # 处理 @media 规则中的条件部分
    # 匹配 @media (...) 中的内容
    text = re.sub(r'@media\s*\(([^)]+)\)', lambda m: '@media (' + re.sub(r'([a-zA-Z0-9_\-]+):([^;()])', r'\1: \2', m.group(1)) + ')', text)
    # 然后只在属性中的冒号后添加空格（避免影响伪类选择器）
    # 我们将文本按花括号分割，只处理花括号内的内容
    parts = text.split('{')
    for i in range(1, len(parts)):
        if '}' in parts[i]:
            content, rest = parts[i].split('}', 1)
            # 在花括号内的所有冒号后添加空格
            content = re.sub(r'([a-zA-Z0-9_\-]+):([^;])', r'\1: \2', content)
            parts[i] = content + '}' + rest
    text = '{'.join(parts)
    # 处理选择器中的逗号
    text = re.sub(r'\s*,\s*', ', ', text)
    # 处理其他空格
    text = re.sub(r'\s*([+>~])\s*', ' \1 ', text)
    # 处理注释
    text = re.sub(r'\s*/\*\s*', '/* ', text)
    text = re.sub(r'\s*\*/\s*', ' */', text)
    # 确保注释单独成行
    text = re.sub(r'([^\n])\s*(/\*[^*]*\*/)', r'\1\n\2', text)
    text = re.sub(r'(/\*[^*]*\*/)\s*([^\n])', r'\1\n\2', text)
    # 处理 !important
    text = re.sub(r'!\s*important', ' !important', text)

    # 处理缩进
    lines = text.split('\n')
    formatted_lines = []

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # 减少缩进级别
        if line.startswith('}'):
            indent_level = max(0, indent_level - 1)

        # 确保最后一个属性后有分号，但注释行除外
        if i > 0 and not line.startswith('}') and not line.endswith('{') and not line.endswith(';') and not line.startswith('/*'):
            line += ';'
        # 移除注释行后的分号
        if line.startswith('/*') and line.endswith(';'):
            line = line[:-1]

        # 添加缩进
        formatted_lines.append(' ' * indent_size * indent_level + line)

        # 增加缩进级别
        if line.endswith('{'):
            indent_level += 1

    return '\n'.join(formatted_lines)

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
