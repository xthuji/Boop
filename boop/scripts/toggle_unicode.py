#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Unicode",
  "description": "在 Unicode 转义和文本之间转换",
  "icon": "↔️",
  "tags": ["unicode","encode","decode"],
  "help": "在 Unicode 转义和文本之间转换\n\n示例:\n输入:\nhello\n\n输出:\n\\u0068\\u0065\\u006c\\u006c\\u006f"
}
'''

import re

def _encode_unicode(text):
    """将文本编码为Unicode转义序列"""
    lines = text.split('\n')
    encoded_lines = []
    for line in lines:
        try:
            if not line:
                encoded_lines.append('')
            else:
                encoded = ''.join(f'\\u{ord(c):04x}' for c in line)
                encoded_lines.append(encoded)
        except Exception:
            encoded_lines.append(line)
    return '\n'.join(encoded_lines)


def _decode_unicode(text):
    """将Unicode转义序列解码为文本"""
    lines = text.split('\n')
    decoded_lines = []
    for line in lines:
        try:
            if not line:
                decoded_lines.append('')
            else:
                # 处理Unicode转义序列
                decoded = line
                # 查找所有\uXXXX格式的转义序列
                unicode_pattern = re.compile(r'\\u([0-9a-fA-F]{4})')
                decoded = unicode_pattern.sub(lambda m: chr(int(m.group(1), 16)), decoded)
                decoded_lines.append(decoded)
        except Exception:
            decoded_lines.append(line)
    return '\n'.join(decoded_lines)


def _toggle_unicode(text):
    """自动切换Unicode编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue
        
        # 检查是否包含Unicode转义序列
        if '\\u' in line:
            # 尝试解码
            try:
                decoded = _decode_unicode(line)
                # 如果解码后的结果与原始输入不同，说明输入是Unicode编码的
                if decoded != line:
                    processed_lines.append(decoded)
                    continue
            except Exception:
                pass
        
        # 编码
        try:
            encoded = _encode_unicode(line)
            processed_lines.append(encoded)
        except Exception:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def run(text):
    """
    在Unicode转义序列和字符之间切换
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
        return _encode_unicode(text_to_process)
    elif mode == 'decode':
        return _decode_unicode(text_to_process)
    else:  # toggle
        return _toggle_unicode(text_to_process)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("Unicode转换")
