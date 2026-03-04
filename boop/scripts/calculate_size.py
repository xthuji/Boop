#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Calculate Size",
  "description": "计算文本的字节大小",
  "icon": "🧮",
  "tags": ["size","calculate"],
  "help": "计算文本的字节大小和 KB 大小\n\n示例:\n输入:\nhello world\n\n输出:\n11 bytes\n0.01 KB"
}
'''

def run(text):
    """
    计算文本的字节大小
    """
    # 计算字节大小
    byte_size = len(text.encode('utf-8'))
    
    # 转换为KB
    kb_size = byte_size / 1024
    
    # 格式化结果
    result = f"{byte_size} bytes\n"
    result += f"{kb_size:.2f} KB"
    
    return result

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("计算文件大小")
