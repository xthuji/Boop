#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Count Words",
  "description": "计算文本中的单词数量",
  "icon": "📝",
  "tags": ["count","words"],
  "help": "计算文本中的单词数量\n\n示例:\n输入:\nhello world\n\n输出:\n单词数：2"
}
'''

def run(text):
    """
    计算文本中的单词数量
    """
    # 分割单词并计数
    words = text.split()
    word_count = len(words)
    
    # 格式化结果
    result = f"单词数: {word_count}"
    
    return result

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("单词计数")
