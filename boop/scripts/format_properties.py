#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format Properties",
  "description": "格式化 Java Properties 文件",
  "icon": "📝",
  "tags": ["properties","format","java"],
  "dependencies": [],
  "help": "格式化 Java Properties 配置文件\n\n示例:\n输入:\nkey=value\n\n输出:\nkey = value"
}"""

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
    """Format Properties text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Properties formatted")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))
        else:
            print("Error formatting Properties: {}".format(str(e)))
