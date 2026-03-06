#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Tab to Space",
  "description": "将制表符转换为空格",
  "icon": "⏮️",
  "tags": ["tab","space","convert","indent","code"],
  "help": "将制表符转换为空格 (默认 1 个制表符=4 个空格)\n\n示例:\n输入:\n\thello\n\tworld\n\n输出:\n    hello\n    world"
}
'''

def run(text):
    """
    将制表符转换为空格
    """
    lines = text.split('\n')
    first_line = lines[0].strip()
    
    space_count = 2
    text_to_convert = text
    
    if first_line.isdigit():
        space_count = int(first_line)
        text_to_convert = '\n'.join(lines[1:])
    
    spaces = ' ' * space_count
    return text_to_convert.replace('\t', spaces)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("制表符转空格")
