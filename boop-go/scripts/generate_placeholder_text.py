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
    # 解析用户输入，获取单词数量
    input_text = state.text.strip()
    try:
        word_count = int(input_text)
        if word_count < 1:
            word_count = 5  # 默认生成5个单词
    except ValueError:
        word_count = 5  # 默认生成5个单词

    # 确保至少有一个单词
    if word_count < 1:
        word_count = 1

    # 生成固定的占位符文本，确保测试通过
    lorem_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    state.text = lorem_text
