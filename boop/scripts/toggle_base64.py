#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Base64",
  "description": "在 Base64 编码和解码之间切换",
  "icon": "🔒",
  "tags": ["base64","encode","decode"],
  "help": "在 Base64 编码和解码之间切换\n\n- 如果输入是编码后的 Base64，进行解码\n- 如果输入是未编码的文本，进行编码\n\n示例 1 (解码):\n输入:\naGVsbG8gd29ybGQ=\n\n输出:\nhello world\n\n示例 2 (编码):\n输入:\nhello world\n\n输出:\naGVsbG8gd29ybGQ="
}
'''

import base64

def run(text):
    """
    在Base64编码和解码之间切换
    """
    try:
        # 尝试解码
        decoded = base64.b64decode(text).decode('utf-8')
        return decoded
    except Exception:
        # 尝试编码
        try:
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return encoded
        except Exception:
            return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("Base64编解码")
