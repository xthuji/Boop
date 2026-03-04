#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Space to Tab",
  "description": "将空格转换为制表符",
  "icon": "⏭️",
  "tags": ["space","tab","convert"],
  "help": "将空格转换为制表符 (默认 4 个空格=1 个制表符)\n\n示例:\n输入:\n    hello\n    world\n\n输出:\n\thello\n\tworld"
}
'''

def run(text):
    """
    将空格转换为制表符
    """
    # 将4个连续空格转换为制表符
    return text.replace('    ', '\t')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("空格转制表符")
