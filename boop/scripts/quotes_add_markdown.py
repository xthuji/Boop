#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Add Markdown Quotes",
  "description": "为文本添加 Markdown 引用格式",
  "icon": "📝",
  "tags": ["markdown","quotes","format"],
  "help": "为文本添加 Markdown 引用格式\n\n示例:\n输入:\nhello\nworld\n\n输出:\n> hello\n> world"
}
'''

def run(text):
    """
    为文本添加Markdown引号格式
    """
    lines = text.split('\n')
    quoted_lines = ['> ' + line for line in lines]
    return '\n'.join(quoted_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("添加Markdown引号")
