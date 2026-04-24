#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Trim Lines",
  "description": "移除每行首尾的空白字符",
  "icon": "🧹",
  "tags": ["trim","lines","whitespace"],
  "help": "移除每行首尾的空白字符\n\n示例:\n输入:\n  hello  \n  world  \n\n输出:\nhello\nworld"
}
'''

def run(text):
    """
    修剪每行文本的空白字符
    """
    lines = text.split('\n')
    first_line = lines[0].strip().lower()
    
    mode = 'both'
    text_to_trim = text
    
    mode_map = {
        'start': 'start',
        's': 'start',
        'left': 'start',
        'l': 'start',
        'end': 'end',
        'e': 'end',
        'right': 'end',
        'r': 'end',
        'trailing': 'end'
    }
    
    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_trim = '\n'.join(lines[1:])
    
    lines_to_trim = text_to_trim.split('\n')
    
    if mode == 'start':
        trimmed_lines = [line.lstrip() for line in lines_to_trim]
    elif mode == 'end':
        trimmed_lines = [line.rstrip() for line in lines_to_trim]
    else:  # both
        trimmed_lines = [line.strip() for line in lines_to_trim]
    
    return '\n'.join(trimmed_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("修剪行空白")
