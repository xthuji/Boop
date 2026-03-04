#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Lower Case",
  "description": "将文本转换为小写格式",
  "icon": "🐪",
  "tags": ["format","case","lower"],
  "help": "将文本转换为全小写格式\n\n示例:\n输入:\nHELLO WORLD\n\n输出:\nhello world"
}
'''

def run(text):
    """
    将文本转换为小写
    """
    return text.lower()

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为小写")
