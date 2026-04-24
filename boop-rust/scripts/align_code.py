#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Align Code",
  "description": "对齐代码中的赋值语句",
  "icon": "📏",
  "tags": ["format","code","align","assignment","dq"],
  "help": "对齐代码中的赋值语句，使等号对齐整齐\n\n用法：在第一行指定配置（可选）\n  格式：symbol:spaceMode:alignAll\n\n参数说明：\n  symbol - 对齐的符号（默认为 =）\n  spaceMode - 空格模式：both（默认，等号两侧空格）、after（等号后空格）、none（无空格）\n  alignAll - 是否对齐所有符号：true（默认，对齐所有）、false（仅对齐第一个）\n\n示例:\n输入:\n=:both:true\na = 1\nbb = 2\nccc = 3\n\n输出:\na   = 1\nbb  = 2\nccc = 3"
}
'''

import re

def run(text):
    """
    对齐代码中的赋值语句，支持首行自定义参数
    """
    lines = text.split('\n')
    
    # 处理首行自定义参数
    symbol = '='
    space_mode = 'both'
    align_all = True
    text_to_align = text
    found_space_mode = False
    
    if lines:
        first_line = lines[0].strip()
        # 检查是否为配置行
        config_parts = first_line.split(':')
        space_mode_options = ['both', 'after', 'none']
        
        for i in range(1, len(config_parts)):
            if config_parts[i] and config_parts[i].strip().lower() in space_mode_options:
                found_space_mode = True
                break
        
        if found_space_mode:
            # 解析配置
            if config_parts[0] and config_parts[0].strip():
                symbol = config_parts[0].strip()
            
            for i in range(1, len(config_parts)):
                if config_parts[i] and config_parts[i].strip().lower() in space_mode_options:
                    space_mode = config_parts[i].strip().lower()
                    break
            
            for i in range(2, len(config_parts)):
                if config_parts[i] and config_parts[i].strip().lower() in ['true', 'false']:
                    align_all = config_parts[i].strip().lower() == 'true'
                    break
            
            text_to_align = '\n'.join(lines[1:]).strip() or ''
    
    if not text_to_align:
        return text
    
    if space_mode == 'none':
        return text_to_align
    
    align_lines = text_to_align.split('\n')
    result_lines = align_lines.copy()
    
    # 对齐处理
    # 计算符号前内容的最大长度
    max_content_length = 0
    for line in align_lines:
        if symbol in line:
            content_before = line.split(symbol)[0].strip()
            max_content_length = max(max_content_length, len(content_before))
    
    # 对齐每行
    result_lines = []
    for line in align_lines:
        if symbol in line:
            # 分割行，获取符号前和符号后的内容
            parts = line.split(symbol, 1)
            content_before = parts[0].strip()
            content_after = parts[1].strip()
            
            # 计算需要的空格
            spaces_needed = max_content_length - len(content_before)
            
            # 构建新行
            new_line = ''
            # 添加前导空格
            leading_whitespace = re.match(r'^\s*', line)
            if leading_whitespace:
                new_line += leading_whitespace.group(0)
            
            # 添加符号前的内容
            new_line += content_before
            
            # 添加对齐空格
            if spaces_needed > 0:
                new_line += ' ' * spaces_needed
            
            # 添加符号前的空格
            new_line += ' '
            
            # 添加符号
            new_line += symbol
            
            # 添加符号后的空格
            new_line += ' '
            
            # 添加符号后的内容
            if content_after:
                new_line += content_after
            
            result_lines.append(new_line)
        else:
            # 没有符号，直接添加原行
            result_lines.append(line)
    
    # 直接返回对齐后的结果，不包含配置行
    return '\n'.join(result_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("对齐代码")
