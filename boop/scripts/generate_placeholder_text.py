#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Generate Placeholder Text",
  "description": "生成占位符文本",
  "icon": "📄",
  "tags": ["placeholder","text","zhanwei"],
  "help": "生成占位符文本 (Lorem Ipsum)\n\n示例:\n输入:\n5\n\n输出:\nLorem ipsum dolor sit amet, consectetur adipiscing elit."
}"""

import random


def main(state):
    """Generate Lorem Ipsum placeholder text."""
    words = [
        "ad", "adipisicing", "aliqua", "aliquip", "amet", "anim", "aute",
        "cillum", "commodo", "consectetur", "consequat", "culpa", "cupidatat",
        "deserunt", "do", "dolor", "dolore", "duis", "ea", "eiusmod", "elit",
        "enim", "esse", "est", "et", "eu", "ex", "excepteur", "exercitation",
        "fugiat", "id", "in", "incididunt", "ipsum", "irure", "labore",
        "laboris", "laborum", "Lorem", "magna", "minim", "mollit", "nisi",
        "non", "nostrud", "nulla", "occaecat", "officia", "pariatur", "proident",
        "qui", "quis", "reprehenderit", "sint", "sit", "sunt", "tempor",
        "ullamco", "ut", "velit", "veniam", "voluptate"
    ]

    sentence = ""
    for _ in range(100):
        pos = random.randint(0, len(words) - 2)
        sentence += words[pos] + " "

    # Capitalize first letter and add period
    sentence = sentence[0].upper() + sentence[1:].strip() + "."

    state.text = sentence
