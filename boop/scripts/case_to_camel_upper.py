#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Camel Case Upper",
  "description": "转为首字母大写驼峰命名格式",
  "icon": "🐪",
  "tags": ["format","case","camel","upper","first","var"],
  "help": "将文本转换为首字母大写驼峰命名格式 (首单词大写，后续单词首字母大写)\n\n示例:\n输入:\nhello world\n\n输出:\nHelloWorld"
}
'''

import re

def run(text):
    """
    将文本转换为首字母大写驼峰命名格式
    """
    # 移除所有非字母数字字符，将首字母小写，后续单词首字母大写
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 第一个单词大写，其余单词首字母大写
    camel_case = words[0].capitalize() + ''.join(word.capitalize() for word in words[1:])
    return camel_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为驼峰命名 (首字母大写)")
