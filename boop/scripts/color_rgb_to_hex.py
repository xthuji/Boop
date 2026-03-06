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
    # 移除 rgb() 包装器
    if text.strip().startswith('rgb('):
        text = text.strip().replace('rgb(', '').replace(')', '')
    
    # 按逗号或空格分割
    rgb_array = [c.trim() for c in re.split(r'[,\s]+', text) if c.trim()]
    
    if len(rgb_array) != 3:
        return text
    
    try:
        r, g, b = map(int, rgb_array)
        # 确保值在0-255范围内
        if any(value < 0 or value > 255 for value in [r, g, b]):
            return text
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
