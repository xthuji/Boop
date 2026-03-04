#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Convert Number Base",
  "description": "在不同进制之间转换数字",
  "icon": "🔢",
  "tags": ["convert","number","base"],
  "help": "在不同进制之间转换数字\n\n支持的进制：2（二进制）、8（八进制）、10（十进制）、16（十六进制）\n输入格式：数字和当前进制，例如：\"1010 2\" 表示二进制的 1010\n\n示例:\n输入:\n1010 2\n\n输出:\n十进制：10\n二进制：1010\n八进制：12\n十六进制：A"
}
'''

import re

def run(text):
    """
    数字进制转换
    """
    # 匹配输入格式：数字 进制
    match = re.search(r'\b(\w+)\s+(\d+)\b', text)
    if not match:
        return "输入格式错误，请使用：数字 进制（例如：1010 2）"
    
    number_str = match.group(1)
    base = int(match.group(2))
    
    # 验证进制
    if base not in [2, 8, 10, 16]:
        return "不支持的进制，仅支持 2、8、10、16"
    
    try:
        # 转换为十进制
        decimal = int(number_str, base)
        
        # 转换为其他进制
        binary = bin(decimal)[2:]
        octal = oct(decimal)[2:]
        hexadecimal = hex(decimal)[2:].upper()
        
        # 格式化结果
        result = f"十进制: {decimal}\n"
        result += f"二进制: {binary}\n"
        result += f"八进制: {octal}\n"
        result += f"十六进制: {hexadecimal}"
        
        return result
    except ValueError:
        return "无效的数字格式"

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("数字进制转换")
