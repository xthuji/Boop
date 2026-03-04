#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Tab to Space",
  "description": "将制表符转换为空格",
  "icon": "⏮️",
  "tags": ["tab","space","convert"],
  "help": "将制表符转换为空格 (默认 1 个制表符=4 个空格)\n\n示例:\n输入:\n\thello\n\tworld\n\n输出:\n    hello\n    world"
}
'''

def run(text):
    """
    将制表符转换为空格
    """
    # 将制表符转换为4个空格
    return text.replace('\t', '    ')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("制表符转空格")
