#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Sort Lines",
  "description": "对文本行进行排序",
  "icon": "📋",
  "tags": ["text","sort","lines"],
  "help": "对文本行进行排序 (字母顺序)\n\n示例:\n输入:\nbanana\napple\ncherry\n\n输出:\napple\nbanana\ncherry"
}
'''

def main(state):
    """Sort lines alphabetically"""
    lines = state.full_text.split('\n')
    sorted_lines = sorted(lines)
    state.full_text = '\n'.join(sorted_lines)
    state.post_info("Lines sorted")
