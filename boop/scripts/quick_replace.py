#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Quick Replace",
  "description": "快速替换文本",
  "icon": "🔄",
  "tags": ["text","replace"],
  "help": "快速替换文本\n\n用法:\n第一行：查找内容\n第二行：替换内容\n其余行：待处理文本\n\n示例:\n输入:\nhello\nhi\nhello world\nhello there\n\n输出:\nhi world\nhi there"
}
'''

def run(text):
    """
    快速替换文本中的内容
    """
    lines = text.split('\n')
    if len(lines) < 3:
        return text
    
    content = '\n'.join(lines[:-2])
    old = ''
    new = ''
    
    for line in lines[-2:]:
        if line.startswith('old: '):
            old = line[5:]
        elif line.startswith('new: '):
            new = line[5:]
    
    if old:
        content = content.replace(old, new)
    
    return content

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("快速替换")
