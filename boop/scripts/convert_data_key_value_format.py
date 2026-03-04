#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Convert Key-Value Format",
  "description": "在不同键值对格式之间转换",
  "icon": "📊",
  "tags": ["convert","data","key-value"],
  "help": "在不同键值对格式之间转换 (等号格式和冒号格式)\n\n示例:\n输入:\nkey1=value1\nkey2=value2\n\n输出:\nkey1: value1\nkey2: value2"
}
'''

def run(text):
    """
    在不同键值对格式之间转换
    """
    lines = text.split('\n')
    converted_lines = []
    
    for line in lines:
        if '=' in line:
            # 转换为冒号格式
            key, value = line.split('=', 1)
            converted_lines.append(f'{key.strip()}: {value.strip()}')
        elif ':' in line:
            # 转换为等号格式
            key, value = line.split(':', 1)
            converted_lines.append(f'{key.strip()}={value.strip()}')
        else:
            converted_lines.append(line)
    
    return '\n'.join(converted_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("键值对格式转换")
