#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Count Characters",
  "description": "计算文本中的字符数量",
  "icon": "🔤",
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
    # 计算非空白字符数
    non_whitespace_chars = len(text.strip())
    # 计算单词数（简单分割）
    words = text.split()
    word_count = len(words)
    
    # 格式化结果
    result = f"总字符数: {total_chars}\n"
    result += f"非空白字符数: {non_whitespace_chars}\n"
    result += f"单词数: {word_count}"
    
    return result

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("字符计数")
