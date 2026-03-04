#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Count Lines",
  "description": "计算文本的行数",
  "icon": "📏",
  "tags": ["count","lines"],
  "help": "计算文本的行数\n\n示例:\n输入:\nHello\nWorld\n\n输出:\n2"
}
'''

def main(state):
    """Count the number of lines"""
    if not state.full_text:
        line_count = 0
    else:
        lines = state.full_text.split('\n')
        line_count = len(lines)
    state.text = str(line_count)
    state.post_info(f"{line_count} lines")
