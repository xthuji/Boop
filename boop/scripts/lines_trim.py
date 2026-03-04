#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Trim Lines",
  "description": "移除每行首尾的空白字符",
  "icon": "✂️",
  "tags": ["text","trim","lines"],
  "help": "移除每行首尾的空白字符\n\n示例:\n输入:\n  hello  \n  world  \n\n输出:\nhello\nworld"
}
'''

def run(text):
    """
    修剪每行文本的空白字符
    """
    lines = text.split('\n')
    trimmed_lines = [line.strip() for line in lines]
    return '\n'.join(trimmed_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("修剪行空白")
