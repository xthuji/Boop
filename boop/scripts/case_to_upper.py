#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Upper Case",
  "description": "转为大写格式",
  "icon": "⤴️",
  "tags": ["format","case","upper","all","var"],
  "help": "将文本转换为全大写格式\n\n示例:\n输入:\nhello world\n\n输出:\nHELLO WORLD"
}
'''

def run(text):
    """
    将文本转换为大写
    """
    return text.upper()

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为大写")
