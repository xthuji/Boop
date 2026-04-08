#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Quick Replace",
  "description": "快速替换文本",
  "icon": "💫",
  "tags": ["replace","string"],
  "help": "快速替换文本中的内容\n\n首行参数格式:\nsource:target\n\n参数说明:\n- source: 要查找的内容\n- target: 要替换的内容\n\n示例:\n输入:\nhello:hi\nhello world\nhello there\n\n输出:\nhi world\nhi there"
}
'''

def run(text):
    """
    快速替换文本中的内容
    """
    lines = text.split('\n')
    if len(lines) < 2:
        return text
    
    first_line = lines[0].strip()
    if not first_line or ':' not in first_line:
        return text
    
    parts = first_line.split(':', 1)
    if len(parts) < 2:
        return text
    
    source = parts[0]
    target = parts[1]
    
    text_to_replace = '\n'.join(lines[1:])
    result = text_to_replace.replace(source, target)
    
    return result

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("快速替换")
