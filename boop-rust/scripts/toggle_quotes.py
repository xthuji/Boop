#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Quotes",
  "description": "在单引号和双引号之间切换",
  "icon": "↔️",
  "tags": ["quotes", "toggle"],
  "help": "在单引号和双引号之间切换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- double/d: 转换为双引号（无引号时包裹双引号）\n- single/s: 转换为单引号（无引号时包裹单引号）\n- escape_double/ed: 转义双引号\n- escape_single/es: 转义单引号\n- toggle/t: 自动切换 (默认)\n\n示例 1 (双引号):\n输入:\ndouble\nhello 'world'\n\n输出:\nhello \"world\"\n\n示例 2 (单引号):\n输入:\nsingle\nhello \"world\"\n\n输出:\nhello 'world'"
}
'''


def _wrap_with_quotes(text, quote):
    """用指定引号包裹文本"""
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            wrapped_lines.append(line)
            continue

        # 如果已经用相同引号包裹，保持不变
        if trimmed.startswith(quote) and trimmed.endswith(quote) and len(trimmed) > 1:
            wrapped_lines.append(line)
            continue

        # 转义内部的相同引号
        escaped = trimmed.replace(quote, f'\\{quote}')
        wrapped_line = f'{quote}{escaped}{quote}'
        wrapped_lines.append(wrapped_line)
    return '\n'.join(wrapped_lines)


def _convert_quotes(text, from_quote, to_quote):
    """将一种引号转换为另一种引号"""
    result = ''
    escape_next = False

    for char in text:
        if escape_next:
            result += char
            escape_next = False
            continue

        if char == '\\':
            result += char
            escape_next = True
            continue

        if char == from_quote:
            result += to_quote
        elif char == to_quote:
            result += from_quote
        else:
            result += char

    return result


def _escape_quotes(text, quote):
    """转义指定引号"""
    lines = text.split('\n')
    escaped_lines = []
    for line in lines:
        # 转义引号，但保留已转义的
        result = ''
        escape_next = False
        for char in line:
            if escape_next:
                result += char
                escape_next = False
            elif char == '\\':
                result += char
                escape_next = True
            elif char == quote:
                result += f'\\{quote}'
            else:
                result += char
        escaped_lines.append(result)
    return '\n'.join(escaped_lines)


def _has_quotes(text, quote):
    """检查文本是否包含指定引号"""
    escape_next = False
    for char in text:
        if escape_next:
            escape_next = False
            continue
        if char == '\\':
            escape_next = True
            continue
        if char == quote:
            return True
    return False


def _toggle_quotes_type(text):
    """自动切换单双引号"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line.strip():
            processed_lines.append(line)
            continue

        has_single = _has_quotes(line, "'")
        has_double = _has_quotes(line, '"')

        if has_single and not has_double:
            # 只有单引号，转为双引号
            processed_lines.append(_convert_quotes(line, "'", '"'))
        elif has_double and not has_single:
            # 只有双引号，转为单引号
            processed_lines.append(_convert_quotes(line, '"', "'"))
        elif not has_single and not has_double:
            # 没有引号，包裹双引号
            processed_lines.append(_wrap_with_quotes(line, '"'))
        else:
            # 两种引号都有，保持不变
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def run(text):
    """
    在不同引号之间切换
    """
    lines = text.split('\n')
    first_line = lines[0].strip()

    # 默认模式：无引号时包裹双引号
    mode = 'default'
    text_to_process = text

    mode_map = {
        'double': 'double',
        'd': 'double',
        'single': 'single',
        's': 'single',
        'escape_double': 'escape_double',
        'ed': 'escape_double',
        'escape_single': 'escape_single',
        'es': 'escape_single',
        'toggle': 'toggle',
        't': 'toggle'
    }

    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_process = '\n'.join(lines[1:])

    if mode == 'double':
        # 转换为双引号：单引号转双引号，无引号时包裹
        if _has_quotes(text_to_process, "'"):
            return _convert_quotes(text_to_process, "'", '"')
        elif _has_quotes(text_to_process, '"'):
            return text_to_process  # 已有双引号，不变
        else:
            return _wrap_with_quotes(text_to_process, '"')
    elif mode == 'single':
        # 转换为单引号：双引号转单引号，无引号时包裹
        if _has_quotes(text_to_process, '"'):
            return _convert_quotes(text_to_process, '"', "'")
        elif _has_quotes(text_to_process, "'"):
            return text_to_process  # 已有单引号，不变
        else:
            return _wrap_with_quotes(text_to_process, "'")
    elif mode == 'escape_double':
        return _escape_quotes(text_to_process, '"')
    elif mode == 'escape_single':
        return _escape_quotes(text_to_process, "'")
    elif mode == 'toggle':
        return _toggle_quotes_type(text_to_process)
    else:  # default
        # 默认行为：无引号时包裹双引号
        if _has_quotes(text_to_process, "'") or _has_quotes(text_to_process, '"'):
            return text_to_process
        else:
            return _wrap_with_quotes(text_to_process, '"')


def main(state):
    """
    主函数，调用 run 函数处理输入文本
    """
    original = state.text.strip()
    lines = original.split('\n')
    first_line = lines[0].strip()

    mode_map = {
        'double': '"',
        'd': '"',
        'single': "'",
        's': "'",
        'escape_double': 'es"',
        'ed': 'es"',
        'escape_single': "es'",
        'es': "es'",
        'toggle': '↔',
        't': '↔'
    }

    mode = first_line if first_line in mode_map else 'default'
    result = run(original)

    if result != original:
        state.text = result
        if first_line in mode_map:
            state.post_info(f"Quotes {mode_map[first_line]}")
        else:
            state.post_info('Quotes "')
    else:
        state.post_info("Quotes 无变化")
