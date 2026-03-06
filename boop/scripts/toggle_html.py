#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle HTML Text",
  "description": "在 HTML 实体和文本之间转换",
  "icon": "↔️",
  "tags": ["html","entities","encode","decode"],
  "help": "在 HTML 实体和文本之间转换\n\n示例:\n输入:\nhello & world\n\n输出:\nhello &amp; world"
}
'''

import html

def _encode_html(text):
    """将文本编码为HTML实体"""
    lines = text.split('\n')
    encoded_lines = []
    for line in lines:
        try:
            if not line:
                encoded_lines.append('')
            else:
                encoded = html.escape(line)
                encoded_lines.append(encoded)
        except Exception:
            encoded_lines.append(line)
    return '\n'.join(encoded_lines)


def _decode_html(text):
    """将HTML实体解码为文本"""
    lines = text.split('\n')
    decoded_lines = []
    for line in lines:
        try:
            if not line:
                decoded_lines.append('')
            else:
                decoded = html.unescape(line)
                decoded_lines.append(decoded)
        except Exception:
            decoded_lines.append(line)
    return '\n'.join(decoded_lines)


def _toggle_html(text):
    """自动切换HTML编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue
        
        # 检查是否包含HTML实体
        if '&' in line:
            # 尝试解码
            try:
                decoded = html.unescape(line)
                # 如果解码后的结果与原始输入不同，说明输入是HTML编码的
                if decoded != line:
                    processed_lines.append(decoded)
                    continue
            except Exception:
                pass
        
        # 编码
        try:
            encoded = html.escape(line)
            processed_lines.append(encoded)
        except Exception:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def run(text):
    """
    在HTML实体和字符之间切换
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
        return _encode_html(text_to_process)
    elif mode == 'decode':
        return _decode_html(text_to_process)
    else:  # toggle
        return _toggle_html(text_to_process)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("HTML实体转换")
