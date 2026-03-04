#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Shuffle Characters",
  "description": "随机打乱字符顺序",
  "icon": "🔀",
  "tags": ["text","shuffle","random"],
  "help": "随机打乱字符顺序\n\n示例:\n输入:\nhello\n\n输出:\n(随机结果)"
}"""

import random


def _shuffle_string(string):
    """Shuffle characters in a string."""
    chars = list(string)
    random.shuffle(chars)
    return ''.join(chars)


def main(state):
    """Shuffle characters randomly for each line."""
    lines = state.text.split('\n')
    shuffled_lines = [_shuffle_string(line) for line in lines]
    state.text = '\n'.join(shuffled_lines)
