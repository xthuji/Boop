#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Count Words",
  "description": "计算文本中的单词数量",
  "icon": "🤖",
  "tags": ["count","words"],
  "help": "计算文本中的单词数量\n\n示例:\n输入:\nhello world\n\n输出:\n单词数：2"
}
'''

import re

def run(text):
    """
    计算文本中的单词数量
    """
    # 使用正则表达式匹配非空白字符序列作为单词
    words = re.findall(r'\S+', text)
    word_count = len(words)
    return word_count

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    count = run(state.text)
    state.post_info(f"{count} words")
    state.text = str(count)
