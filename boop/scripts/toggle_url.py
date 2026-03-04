#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle URL Encoding",
  "description": "在 URL 编码和解码之间切换",
  "icon": "🌐",
  "tags": ["url","encode","decode"],
  "help": "在 URL 编码和解码之间切换\n\n示例:\n输入:\nhello world\n\n输出:\nhello%20world"
}
'''

import urllib.parse

def run(text):
    """
    URL编码与解码
    """
    try:
        # 尝试解码
        decoded = urllib.parse.unquote(text)
        if decoded != text:
            return decoded
        # 尝试编码
        encoded = urllib.parse.quote(text)
        return encoded
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("URL编解码")
