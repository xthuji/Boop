#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Snake Case",
  "description": "转为蛇形命名格式",
  "icon": "🐍",
  "tags": ["format","case","snake","var"],
  "help": "将文本转换为蛇形命名格式 (snake_case)\n\n示例:\n输入:\nhello world\n\n输出:\nhello_world"
}
'''

import re

def run(text):
    """
    将文本转换为snake_case命名格式
    """
    # 移除所有非字母数字字符，将所有单词转为小写并以下划线连接
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 所有单词小写，以下划线连接
    snake_case = '_'.join(word.lower() for word in words)
    return snake_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为snake_case")
