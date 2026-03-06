#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Quotes",
  "description": "在单引号和双引号之间切换",
  "icon": "↔️",
  "tags": ["quotes","toggle"],
  "help": "在单引号和双引号之间切换\n\n示例:\n输入:\n\"hello\"\n\n输出:\n'hello'"
}
'''

def _wrap_with_quotes(text, quote):
    """Wrap text with specified quotes."""
    lines = text.split('\n')
    wrapped_lines = []
    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            wrapped_lines.append(line)
            continue
        
        if trimmed.startswith(quote) and trimmed.endswith(quote):
            wrapped_lines.append(line)
            continue
        
        # Escape same quotes inside
        escaped = trimmed.replace(quote, f'\\{quote}')
        wrapped_line = line.replace(trimmed, f'{quote}{escaped}{quote}')
        wrapped_lines.append(wrapped_line)
    return '\n'.join(wrapped_lines)


def _escape_quotes(text, quote):
    """Escape specified quotes."""
    lines = text.split('\n')
    escaped_lines = [line.replace(quote, f'\\{quote}') for line in lines]
    return '\n'.join(escaped_lines)


def _toggle_quotes_type(text):
    """Toggle between single and double quotes."""
    single_count = text.count("'")
    double_count = text.count('"')
    
    if single_count > double_count:
        return _toggle_quotes(text, "'", '"')
    else:
        return _toggle_quotes(text, '"', "'")


def _toggle_quotes(text, from_quote, to_quote):
    """Toggle specific quotes."""
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


def run(text):
    """
    在不同引号之间切换
    """
    lines = text.split('\n')
    first_line = lines[0].strip()
    
    mode = 'double'
    text_to_process = text
    
    mode_map = {
        "'": 'single',
        '"': 'double',
        "\\'": 'escape_single',
        '\\"': 'escape_double',
        'toggle': 'toggle',
        't': 'toggle'
    }
    
    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_process = '\n'.join(lines[1:])
    
    if mode == 'single':
        return _wrap_with_quotes(text_to_process, "'")
    elif mode == 'double':
        return _wrap_with_quotes(text_to_process, '"')
    elif mode == 'escape_single':
        return _escape_quotes(text_to_process, "'")
    elif mode == 'escape_double':
        return _escape_quotes(text_to_process, '"')
    elif mode == 'toggle':
        return _toggle_quotes_type(text_to_process)
    else:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("切换引号")
