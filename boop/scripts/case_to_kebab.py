#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Kebab Case",
  "description": "将文本转换为短横线命名格式",
  "icon": "🐪",
  "tags": ["format","case","kebab"],
  "help": "将文本转换为短横线命名格式 (kebab-case)\n\n示例:\n输入:\nhello world\n\n输出:\nhello-world"
}
'''

import re

def run(text):
    """
    将文本转换为kebab-case命名格式
    """
    # 移除所有非字母数字字符，将所有单词转为小写并以连字符连接
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 所有单词小写，以连字符连接
    kebab_case = '-'.join(word.lower() for word in words)
    return kebab_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为kebab-case")
