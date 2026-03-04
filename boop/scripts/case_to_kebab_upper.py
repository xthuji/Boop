#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Kebab Upper Case",
  "description": "将文本转换为大写短横线命名格式",
  "icon": "🐪",
  "tags": ["format","case","kebab","upper"],
  "help": "将文本转换为大写短横线命名格式 (KEBAB-CASE)\n\n示例:\n输入:\nhello world\n\n输出:\nHELLO-WORLD"
}
'''

import re

def run(text):
    """
    将文本转换为KEBAB-CASE大写命名格式
    """
    # 移除所有非字母数字字符，将所有单词转为大写并以连字符连接
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 所有单词大写，以连字符连接
    kebab_upper_case = '-'.join(word.upper() for word in words)
    return kebab_upper_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为KEBAB-CASE")
