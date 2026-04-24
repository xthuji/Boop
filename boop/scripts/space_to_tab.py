#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Space to Tab",
  "description": "将空格转换为制表符",
  "icon": "⏭️",
  "tags": ["space","tab","convert","indent","code"],
  "help": "将空格转换为制表符 (默认 4 个空格=1 个制表符)\n\n示例:\n输入:\n    hello\n    world\n\n输出:\n\thello\n\tworld"
}
'''

def run(text):
    """
    将空格转换为制表符
    """
    lines = text.split('\n')
    first_line = lines[0].strip()
    
    space_count = 1
    text_to_convert = text
    
    if first_line.isdigit():
        space_count = int(first_line)
        text_to_convert = '\n'.join(lines[1:])
    
    spaces = ' ' * space_count
    return text_to_convert.replace(spaces, '\t')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("空格转制表符")
