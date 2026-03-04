#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Insert Sequence Number",
  "description": "在每行前插入序列号",
  "icon": "🔢",
  "tags": ["sequence","number"],
  "help": "在每行前插入序列号\n\n首行参数格式:\nstart:step:type:separator:width\n\n参数说明:\n- start: 起始值 (数字或字母)\n- step: 步长 (默认 1)\n- type: 类型 (1/num/n: 阿拉伯数字, 2/zh/c: 中文数字, a/u/upper: 大写字母, b/l/lower: 小写字母)\n- separator: 分隔符 (默认空格)\n- width: 数字宽度 (仅阿拉伯数字有效)\n\n示例 1 (默认设置):\n输入:\napple\nbanana\ncherry\n\n输出:\n1 apple\n2 banana\n3 cherry\n\n示例 2 (自定义设置):\n输入:\n5:2:upper:.\napple\nbanana\ncherry\n\n输出:\nE. apple\nG. banana\nI. cherry"
}"""


def _number_to_chinese(num):
    """Convert Arabic number to Chinese number representation."""
    chinese_digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    num_str = str(num)
    result = ''
    for digit in num_str:
        result += chinese_digits[int(digit)]
    return result


def _generate_incremental_values(start, step, format_type, count, placeholder_format):
    """Generate incremental values based on format."""
    current = start if isinstance(start, int) else ord(start)
    result = []

    for _ in range(count):
        value = ''

        if format_type == 'arabic':
            num = int(current)
            if placeholder_format:
                # Parse format like %02d
                import re
                match = re.search(r'\d+', placeholder_format)
                if match:
                    width = int(match.group())
                    value = str(num).zfill(width)
                else:
                    value = str(num)
            else:
                value = str(num)
        elif format_type == 'chinese':
            value = _number_to_chinese(int(current))
        elif format_type == 'english_upper':
            value = chr(current)
        elif format_type == 'english_lower':
            value = chr(current)

        current += step
        result.append(value)

    return result


def main(state):
    """Insert sequence numbers at the beginning of each line."""
    lines = state.text.split('\n')
    first_line = lines[0]

    start = 1
    step = 1
    format_type = 'arabic'
    separator = ' '
    placeholder_format = None
    text_to_process = state.text

    config_parts = first_line.split(':')
    first_part = config_parts[0].strip() if config_parts else ''
    is_first_part_number = first_part.isdigit()
    is_first_part_letter = len(first_part) == 1 and first_part.isalpha()

    if is_first_part_number or is_first_part_letter:
        # Parse start value
        if is_first_part_number:
            start = int(first_part)
        else:
            start = first_part.upper() if first_part.isupper() else first_part.lower()

        # Parse step
        if len(config_parts) >= 2 and config_parts[1]:
            step_str = config_parts[1].strip()
            if step_str.isdigit():
                step = int(step_str)

        # Parse type
        if len(config_parts) >= 3 and config_parts[2]:
            type_str = config_parts[2].strip().lower()
            type_map = {
                '1': 'arabic', 'n': 'arabic', 'num': 'arabic',
                '2': 'chinese', 'c': 'chinese', 'zh': 'chinese',
                'a': 'english_upper', 'u': 'english_upper', 'upper': 'english_upper',
                'b': 'english_lower', 'l': 'english_lower', 'lower': 'english_lower'
            }
            format_type = type_map.get(type_str, 'arabic')

        # Parse separator
        if len(config_parts) >= 4:
            separator = config_parts[3]

        # Parse width
        if len(config_parts) >= 5 and config_parts[4]:
            width_str = config_parts[4].strip()
            if width_str.isdigit():
                width = int(width_str)
                placeholder_format = f'%0{width}d'

        text_to_process = '\n'.join(lines[1:])

    # Count lines to process
    count = len([l for l in text_to_process.split('\n') if l.strip()])
    if count == 0:
        count = len(text_to_process.split('\n'))

    # Generate values
    values = _generate_incremental_values(start, step, format_type, count, placeholder_format)

    # Insert values
    process_lines = text_to_process.split('\n')
    result_lines = []
    for i, line in enumerate(process_lines):
        if i < len(values):
            result_lines.append(f'{values[i]}{separator}{line}')
        else:
            result_lines.append(line)

    state.text = '\n'.join(result_lines)
