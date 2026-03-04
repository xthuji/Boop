#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Unicode",
  "description": "在 Unicode 转义和文本之间转换",
  "icon": "🔤",
  "tags": ["unicode","encode","decode"],
  "help": "在 Unicode 转义和文本之间转换\n\n示例:\n输入:\nhello\n\n输出:\n\\u0068\\u0065\\u006c\\u006c\\u006f"
}
'''

import re

def run(text):
    """
    在Unicode转义序列和字符之间切换
    """
    # 检查是否包含Unicode转义序列
    if '\\u' in text:
        try:
            # 转换为字符
            decoded = text.encode('utf-8').decode('unicode_escape')
            return decoded
        except Exception:
            pass
    
    # 转换为Unicode转义序列
    try:
        encoded = ''.join(f'\\u{ord(c):04x}' if ord(c) > 127 else c for c in text)
        return encoded
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("Unicode转换")
