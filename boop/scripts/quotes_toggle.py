#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Quotes",
  "description": "在单引号和双引号之间切换",
  "icon": "📝",
  "tags": ["quotes","toggle","text"],
  "help": "在单引号和双引号之间切换\n\n示例:\n输入:\n\"hello\"\n\n输出:\n'hello'"
}
'''

def run(text):
    """
    在不同引号之间切换
    """
    # 检查是否包含双引号
    if '"' in text:
        # 转换为单引号
        return text.replace('"', "'")
    else:
        # 转换为双引号
        return text.replace("'", '"')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("切换引号")
