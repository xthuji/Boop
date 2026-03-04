#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Find Duplicate Lines",
  "description": "查找文本中的重复行",
  "icon": "🔍",
  "tags": ["text","duplicate","lines"],
  "help": "查找文本中的重复行\n\n示例:\n输入:\napple\nbanana\napple\ncherry\nbanana\n\n输出:\n重复行:\napple (2 次)\nbanana (2 次)"
}"""

from collections import Counter


def main(state):
    """Find and display duplicate lines."""
    lines = state.text.split('\n')
    line_count = Counter(lines)

    duplicates = []
    for line, count in line_count.items():
        if count > 1:
            duplicates.append(f"{line} ({count} occurrences)")

    if not duplicates:
        state.text = 'No duplicate lines found.'
    else:
        state.text = '\n'.join(duplicates)
