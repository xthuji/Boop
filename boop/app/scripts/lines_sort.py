#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Sort Lines",
  "description": "对文本行进行排序",
  "icon": "↕️",
  "tags": ["sort","lines","asc","desc","random","shuffle","reverse","number","string"],
  "help": "对文本行进行排序\n\n首行参数格式:\n1. mode (排序模式)\n2. column:order:type:delimiter (按列排序)\n\n支持的模式:\n- asc/ascending: 升序排序 (默认)\n- desc/descending: 降序排序\n- random/shuffle: 随机排序\n- reverse/r: 反转顺序\n\n按列排序参数:\n- column: 列索引 (从0开始)\n- order: 排序顺序 (asc/desc)\n- type: 数据类型 (string/number)\n- delimiter: 分隔符 (默认 ',')\n\n示例 1 (降序排序):\n输入:\ndesc\nbanana\napple\ncherry\n\n输出:\ncherry\nbanana\napple\n\n示例 2 (按第二列排序):\n输入:\n1:asc:number,\napple,3\nbanana,1\ncherry,2\n\n输出:\nbanana,1\ncherry,2\napple,3"
}
'''

import random


def _shuffle_array(array):
    """Shuffle array in place."""
    random.shuffle(array)
    return array


def _sort_lines_by_column(text, config_line):
    """Sort lines by specified column."""
    config_parts = config_line.split(':')
    column_idx = int(config_parts[0]) if config_parts else 0
    order = config_parts[1].strip().lower() if len(config_parts) > 1 and config_parts[1].strip().lower() in ['asc', 'desc'] else 'asc'
    type_ = config_parts[2].strip().lower() if len(config_parts) > 2 and config_parts[2].strip().lower() in ['string', 'number'] else 'string'
    delimiter = config_parts[3].strip() if len(config_parts) > 3 else ','
    
    lines = [line for line in text.split('\n') if line.strip()]
    
    def compare_values(a, b):
        if type_ == 'number':
            try:
                num_a = float(a)
                num_b = float(b)
                return (num_a - num_b) if order == 'asc' else (num_b - num_a)
            except ValueError:
                return 0
        else:  # string
            return (a < b) - (a > b) if order == 'asc' else (b < a) - (b > a)
    
    def key_func(line):
        parts = line.split(delimiter)
        if column_idx >= len(parts):
            return ''
        return parts[column_idx]
    
    return '\n'.join(sorted(lines, key=key_func, reverse=(order == 'desc')))


def main(state):
    """Sort lines with configurable modes."""
    lines = state.text.split('\n')
    first_line = lines[0].strip()
    
    mode = 'asc'
    text_to_sort = state.text
    
    mode_map = {
        'asc': 'asc',
        'ascending': 'asc',
        'desc': 'desc',
        'descending': 'desc',
        'random': 'random',
        'shuffle': 'random',
        'reverse': 'reverse',
        'r': 'reverse'
    }
    
    if first_line.lower() in mode_map:
        mode = mode_map[first_line.lower()]
        text_to_sort = '\n'.join(lines[1:]).strip()
    else:
        config_parts = first_line.split(':')
        first_part = config_parts[0].strip() if config_parts else ''
        if first_part.isdigit() and int(first_part) >= 0:
            mode = 'column'
            text_to_sort = '\n'.join(lines[1:]).strip()
    
    if not text_to_sort.strip():
        return
    
    sort_lines = [line for line in text_to_sort.split('\n') if line.strip()]
    
    if not sort_lines:
        return
    
    if mode == 'asc':
        state.text = '\n'.join(sorted(sort_lines))
    elif mode == 'desc':
        state.text = '\n'.join(sorted(sort_lines, reverse=True))
    elif mode == 'random':
        state.text = '\n'.join(_shuffle_array(sort_lines))
    elif mode == 'reverse':
        state.text = '\n'.join(reversed(sort_lines))
    elif mode == 'column':
        state.text = _sort_lines_by_column(text_to_sort, first_line)
    
    state.post_info("Lines sorted")
