#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Reverse String",
  "description": "反转字符串",
  "icon": "🔄",
  "tags": ["text","reverse","string"],
  "help": "反转字符串\n\n示例:\n输入:\nhello\n\n输出:\nolleh"
}"""


def main(state):
    """Reverse string for each line."""
    lines = state.text.split('\n')
    reversed_lines = [line[::-1] for line in lines]
    state.text = '\n'.join(reversed_lines)
