#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Remove Empty Lines",
  "description": "移除文本中的空行",
  "icon": "🗑️",
  "tags": ["text","remove","empty","lines"],
  "help": "移除文本中的空行\n\n示例:\n输入:\nhello\n\nworld\n\n输出:\nhello\nworld"
}
'''

def run(text):
    """
    移除文本中的空行
    """
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("移除空行")
