#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "To Snake Upper Case",
  "description": "转为大写蛇形命名格式",
  "icon": "🐍",
  "tags": ["format","case","snake","upper","var"],
  "help": "将文本转换为大写蛇形命名格式 (SNAKE_CASE)\n\n示例:\n输入:\nhello world\n\n输出:\nHELLO_WORLD"
}
'''

import re

def case_preprocess(string):
    """
    预处理文本，将各种格式转换为空格分隔的单词
    """
    string = string.strip().replace('-', ' ')
    if string == '_' * len(string):
        return []
    
    # 处理开头的下划线
    underscore_at_start = ''
    if string.startswith('_'):
        j = 1
        for i in range(len(string)):
            if i + 1 < len(string) and string[i + 1] == string[i]:
                j += 1
            else:
                break
        underscore_at_start = '_' * j
    
    # 处理结尾的下划线
    underscore_at_end = ''
    if string.endswith('_'):
        j = 1
        for i in range(len(string) - 1, 0, -1):
            if string[i - 1] == string[i]:
                j += 1
            else:
                break
        underscore_at_end = '_' * j
    
    string = string.replace('_', ' ')
    string = underscore_at_start + string + underscore_at_end
    
    # 处理驼峰命名
    string = re.sub(r'(.)([A-Z][a-z]+)', r'\1 \2', string)
    string = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', string).lower()
    
    # 分割单词并过滤空字符串
    words = string.split()
    return [word for word in words if word]

def run(text):
    """
    将文本转换为SNAKE_CASE大写命名格式
    """
    # 按行处理
    lines = text.split('\n')
    converted_lines = []
    
    for line in lines:
        words = case_preprocess(line)
        if words:
            # 所有单词大写，以下划线连接
            snake_upper_case = '_'.join(word.upper() for word in words)
            converted_lines.append(snake_upper_case)
        else:
            converted_lines.append(line)
    
    return '\n'.join(converted_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为SNAKE_CASE")
