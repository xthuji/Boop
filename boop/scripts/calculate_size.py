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
    
    # 格式化结果
    if byte_size > 1000000:
        mb_size = byte_size / 1000000
        result = f"{mb_size:.2f} Mb"
    elif byte_size > 1000:
        kb_size = byte_size / 1000
        result = f"{kb_size:.2f} Kb"
    else:
        result = f"{byte_size} bytes"
    
    return result

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("计算文件大小")
