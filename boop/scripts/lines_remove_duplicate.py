#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Remove Duplicate Lines",
  "description": "移除文本中的重复行",
  "icon": "🗑️",
  "tags": ["text","remove","duplicate","lines"],
  "help": "移除文本中的重复行\n\n示例:\n输入:\napple\nbanana\napple\ncherry\n\n输出:\napple\nbanana\ncherry"
}"""


def main(state):
    """Remove duplicate lines, keeping first occurrence."""
    lines = state.text.split('\n')
    seen = set()
    unique_lines = []

    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    state.text = '\n'.join(unique_lines)
