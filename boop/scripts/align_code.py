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
    
    if lines:
        first_line = lines[0].strip()
        # 检查是否为配置行
        config_parts = first_line.split(':')
        space_mode_options = ['both', 'after', 'none']
        found_space_mode = False
        
        for i in range(1, len(config_parts)):
            if config_parts[i] and config_parts[i].trim().lower() in space_mode_options:
                found_space_mode = True
                break
        
        if found_space_mode:
            # 解析配置
            if config_parts[0] and config_parts[0].trim():
                symbol = config_parts[0].trim()
            
            for i in range(1, len(config_parts)):
                if config_parts[i] and config_parts[i].trim().lower() in space_mode_options:
                    space_mode = config_parts[i].trim().lower()
                    break
            
            for i in range(2, len(config_parts)):
                if config_parts[i] and config_parts[i].trim().lower() in ['true', 'false']:
                    align_all = config_parts[i].trim().lower() == 'true'
                    break
            
            text_to_align = '\n'.join(lines[1:]).strip()
    
    if not text_to_align or symbol not in text_to_align:
        return text
    
    if space_mode == 'none':
        return text_to_align
    
    align_lines = text_to_align.split('\n')
    result_lines = align_lines.copy()
    
    # 分析每行
    def analyze_line(line):
        leading_whitespace_match = re.match(r'^\s*', line)
        leading_whitespace = leading_whitespace_match.group(0) if leading_whitespace_match else ''
        
        symbol_positions = []
        current_index = 0
        while True:
            index = line.find(symbol, current_index)
            if index == -1:
                break
            symbol_positions.append(index)
            current_index = index + len(symbol)
        
        # 处理制表符
        leading_space_pos_diff = len(leading_whitespace.replace('\t', ' ' * 4)) - len(leading_whitespace)
        
        return {
            'leading_whitespace': leading_whitespace,
            'leading_space_pos_diff': leading_space_pos_diff,
            'symbol_positions': symbol_positions,
            'original_line': line
        }
    
    # 对齐每行
    def align_line(line_info, max_symbol_position, current_symbol_index):
        new_line = line_info['leading_whitespace']
        current_pos_in_origin_line = len(line_info['leading_whitespace'])
        
        symbol_pos = line_info['symbol_positions'][current_symbol_index] if current_symbol_index < len(line_info['symbol_positions']) else -1
        
        if symbol_pos >= 0:
            # 添加符号前的内容
            new_line += line_info['original_line'][current_pos_in_origin_line:symbol_pos].strip()
            
            # 计算需要的空格
            spaces_needed = max_symbol_position - len(new_line) - line_info['leading_space_pos_diff']
            if spaces_needed > 0:
                new_line += ' ' * spaces_needed
            
            # 添加符号
            new_line += symbol
            
            # 添加符号后的空格
            if space_mode in ['both', 'after']:
                new_line += ' '
            
            current_pos_in_origin_line = symbol_pos + len(symbol)
        
        # 添加符号后的内容
        if current_pos_in_origin_line < len(line_info['original_line']):
            new_line += line_info['original_line'][current_pos_in_origin_line:].strip()
        
        return new_line
    
    # 对齐处理
    line_infos = [analyze_line(line) for line in align_lines]
    max_line_symbol_count = max(len(info['symbol_positions']) for info in line_infos)
    
    for i in range(max_line_symbol_count):
        max_current_symbol_position = -1
        
        if i > 0:
            line_infos = [analyze_line(line) for line in result_lines]
        
        # 计算当前符号位置的最大值
        for info in line_infos:
            if i < len(info['symbol_positions']):
                current_symbol_pos = info['symbol_positions'][i]
                position = current_symbol_pos
                if space_mode == 'both' and current_symbol_pos >= 1 and not info['original_line'][current_symbol_pos - 1].isspace():
                    position += 1
                max_current_symbol_position = max(max_current_symbol_position, position + info['leading_space_pos_diff'])
        
        # 对齐当前符号
        if max_current_symbol_position != -1:
            result_lines = [align_line(info, max_current_symbol_position, i) for info in line_infos]
        
        if not align_all:
            break
    
    # 重建文本
    if lines and found_space_mode:
        return '\n'.join([lines[0]] + result_lines)
    else:
        return '\n'.join(result_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("对齐代码")
