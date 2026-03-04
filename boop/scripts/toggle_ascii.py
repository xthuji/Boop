#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle ASCII",
  "description": "在 ASCII 和可读文本之间转换",
  "icon": "🔤",
  "tags": ["ascii","encode","decode"],
  "help": "在 ASCII 编码和可读文本之间转换\n\n示例:\n输入:\nhello\n\n输出:\n104 101 108 108 111"
}
'''

import re

def run(text):
    """
    在ASCII码和字符之间切换
    """
    # 检查是否是ASCII码序列
    ascii_match = re.findall(r'\b\d{1,3}\b', text)
    if ascii_match and len(ascii_match) > 0:
        try:
            # 转换为字符
            chars = []
            for code in ascii_match:
                code = int(code)
                if 0 <= code <= 127:
                    chars.append(chr(code))
            return ''.join(chars)
        except Exception:
            pass
    
    # 转换为ASCII码
    try:
        ascii_codes = [str(ord(c)) for c in text]
        return ' '.join(ascii_codes)
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("ASCII转换")
