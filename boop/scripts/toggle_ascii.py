#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle ASCII",
  "description": "在 ASCII 和可读文本之间转换",
  "icon": "↔️",
  "tags": ["ascii","encode","decode"],
  "help": "在 ASCII 编码和可读文本之间转换\n\n示例:\n输入:\nhello\n\n输出:\n104 101 108 108 111"
}
'''

import re

def _encode_ascii(text):
    """将文本编码为ASCII码"""
    lines = text.split('\n')
    encoded_lines = []
    for line in lines:
        codes = [str(ord(c)) for c in line]
        encoded_lines.append(' '.join(codes))
    return '\n'.join(encoded_lines)


def _decode_ascii(text):
    """将ASCII码解码为文本"""
    lines = text.split('\n')
    decoded_lines = []
    for line in lines:
        parts = re.split(r'[ ,]+', line)
        chars = []
        for part in parts:
            part = part.strip()
            if part:
                try:
                    code = int(part)
                    if 0 <= code <= 127:
                        chars.append(chr(code))
                except ValueError:
                    pass
        decoded_lines.append(''.join(chars))
    return '\n'.join(decoded_lines)


def _toggle_ascii(text):
    """自动切换ASCII编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue
        
        # 检查是否为ASCII码序列
        parts = re.split(r'[ ,]+', line)
        parts = [p.strip() for p in parts if p.strip()]
        if all(p.isdigit() and 0 <= int(p) <= 127 for p in parts):
            # 尝试解码
            try:
                decoded = _decode_ascii(line)
                # 如果解码后的结果与原始输入不同，说明输入是ASCII码序列
                if decoded != line:
                    processed_lines.append(decoded)
                    continue
            except Exception:
                pass
        
        # 编码
        processed_lines.append(_encode_ascii(line))
    return '\n'.join(processed_lines)


def run(text):
    """
    在ASCII码和字符之间切换
    """
    lines = text.split('\n')
    first_line = lines[0].strip().lower()
    
    mode = 'toggle'
    text_to_process = text
    
    mode_map = {
        'encode': 'encode',
        'e': 'encode',
        'decode': 'decode',
        'd': 'decode',
        'toggle': 'toggle',
        't': 'toggle'
    }
    
    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_process = '\n'.join(lines[1:])
    
    if mode == 'encode':
        return _encode_ascii(text_to_process)
    elif mode == 'decode':
        return _decode_ascii(text_to_process)
    else:  # toggle
        return _toggle_ascii(text_to_process)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("ASCII转换")
