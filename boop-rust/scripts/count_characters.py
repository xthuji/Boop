#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Count Characters",
  "description": "计算文本中的字符数量",
  "icon": "🤖",
  "tags": ["count","characters"],
  "help": "计算文本中的字符数量\n\n示例:\n输入:\nhello world\n\n输出:\n总字符数：11\n非空白字符数：11\n单词数：2"
}
'''

def run(text):
    """
    计算文本中的字符数量
    """
    # 计算总字符数
    total_chars = len(text)
    return total_chars

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    count = run(state.text)
    state.post_info(f"{count} characters")
    state.text = str(count)
