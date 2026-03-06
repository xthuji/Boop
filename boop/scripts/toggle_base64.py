#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Base64",
  "description": "在 Base64 编码和解码之间切换",
  "icon": "↔️",
  "tags": ["base64","encode","decode"],
  "help": "在 Base64 编码和解码之间切换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- encode/e: 强制编码为 Base64\n- decode/d: 强制解码 Base64\n- toggle/t: 自动检测并切换模式 (默认)\n\n示例 1 (强制解码):\n输入:\ndecode\naGVsbG8gd29ybGQ=\n\n输出:\nhello world\n\n示例 2 (强制编码):\n输入:\nencode\nhello world\n\n输出:\naGVsbG8gd29ybGQ="
}
'''

import base64

def _encode_base64(text):
    """将文本编码为Base64"""
    lines = text.split('\n')
    encoded_lines = []
    for line in lines:
        try:
            if not line:
                encoded_lines.append('')
            else:
                encoded = base64.b64encode(line.encode('utf-8')).decode('utf-8')
                encoded_lines.append(encoded)
        except Exception:
            encoded_lines.append(line)
    return '\n'.join(encoded_lines)


def _decode_base64(text):
    """将Base64解码为文本"""
    lines = text.split('\n')
    decoded_lines = []
    for line in lines:
        try:
            if not line:
                decoded_lines.append('')
            else:
                decoded = base64.b64decode(line).decode('utf-8')
                decoded_lines.append(decoded)
        except Exception:
            decoded_lines.append(line)
    return '\n'.join(decoded_lines)


def _toggle_base64(text):
    """自动切换Base64编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue
        
        try:
            # 尝试解码
            decoded = base64.b64decode(line).decode('utf-8')
            # 如果解码后的结果与原始输入不同，说明输入是Base64编码的
            if decoded != line:
                processed_lines.append(decoded)
                continue
        except Exception:
            pass
        
        # 编码
        try:
            encoded = base64.b64encode(line.encode('utf-8')).decode('utf-8')
            processed_lines.append(encoded)
        except Exception:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def run(text):
    """
    在Base64编码和解码之间切换
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
        return _encode_base64(text_to_process)
    elif mode == 'decode':
        return _decode_base64(text_to_process)
    else:  # toggle
        return _toggle_base64(text_to_process)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("Base64编解码")
