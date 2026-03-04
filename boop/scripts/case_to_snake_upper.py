#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Snake Upper Case",
  "description": "将文本转换为大写蛇形命名格式",
  "icon": "🐍",
  "tags": ["format","case","snake","upper"],
  "help": "将文本转换为大写蛇形命名格式 (SNAKE_CASE)\n\n示例:\n输入:\nhello world\n\n输出:\nHELLO_WORLD"
}
'''

import re

def run(text):
    """
    将文本转换为SNAKE_CASE大写命名格式
    """
    # 移除所有非字母数字字符，将所有单词转为大写并以下划线连接
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 所有单词大写，以下划线连接
    snake_upper_case = '_'.join(word.upper() for word in words)
    return snake_upper_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为SNAKE_CASE")
