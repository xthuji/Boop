#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "RGB to Hex Color",
  "description": "将 RGB 颜色值转换为十六进制格式",
  "icon": "🎨",
  "tags": ["color","rgb","hex","convert"],
  "help": "将 RGB 颜色值转换为十六进制颜色格式\n\n支持的输入格式:\n- rgb(255, 255, 255)\n- 255, 255, 255\n- 255 255 255\n\n示例:\n输入:\n255, 255, 255\n\n输出:\n#FFFFFF"
}
'''

import re

def run(text):
    """
    将RGB颜色值转换为HEX格式
    """
    # 匹配RGB格式
    rgb_match = re.search(r'\b(\d{1,3})[\s,]+(\d{1,3})[\s,]+(\d{1,3})\b', text)
    if not rgb_match:
        return text
    
    try:
        r, g, b = map(int, rgb_match.groups())
        # 确保值在0-255范围内
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        # 转换为HEX格式
        hex_color = f'#{r:02x}{g:02x}{b:02x}'.upper()
        return hex_color
    except ValueError:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("RGB转HEX")
