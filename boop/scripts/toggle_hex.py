#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Hex",
  "description": "在十六进制和文本之间转换",
  "icon": "🔢",
  "tags": ["hex","encode","decode"],
  "help": "在十六进制和文本之间转换\n\n示例:\n输入:\nhello\n\n输出:\n68656c6c6f"
}
'''

def run(text):
    """
    在十六进制编码和解码之间切换
    """
    try:
        # 尝试解码
        # 移除可能的空格和0x前缀
        hex_str = text.replace(' ', '').replace('0x', '')
        decoded = bytes.fromhex(hex_str).decode('utf-8')
        return decoded
    except Exception:
        # 尝试编码
        try:
            encoded = text.encode('utf-8').hex()
            return encoded
        except Exception:
            return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("十六进制编解码")
