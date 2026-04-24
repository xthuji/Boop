#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle ASCII",
  "description": "在 ASCII 码和可读文本之间转换",
  "icon": "↔️",
  "tags": ["ascii", "encode", "decode"],
  "help": "在 ASCII 码和可读文本之间转换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- encode/e: 强制编码为 ASCII 码\n- decode/d: 强制解码 ASCII 码\n- toggle/t: 自动检测并切换模式 (默认)\n\n示例 1 (强制编码):\n输入:\nencode\nhello\n\n输出:\n104 101 108 108 111\n\n示例 2 (强制解码):\n输入:\ndecode\n104 101 108 108 111\n\n输出:\nhello"
}
'''

import re

def _encode_ascii(text):
    """将文本编码为 ASCII 码"""
    lines = text.split('\n')
    encoded_lines = [' '.join(str(ord(c)) for c in line) for line in lines]
    return '\n'.join(encoded_lines)


def _decode_ascii(text):
    """将 ASCII 码解码为文本"""
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
    """自动切换 ASCII 编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue

        parts = re.split(r'[ ,]+', line)
        parts = [p.strip() for p in parts if p.strip()]
        if all(p.isdigit() and 0 <= int(p) <= 127 for p in parts):
            try:
                decoded = _decode_ascii(line)
                if decoded != line:
                    processed_lines.append(decoded)
                    continue
            except Exception:
                pass

        processed_lines.append(_encode_ascii(line))
    return '\n'.join(processed_lines)


def run(text):
    """
    在 ASCII 码和字符之间切换
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
    else:
        return _toggle_ascii(text_to_process)


def main(state):
    """
    主函数，调用 run 函数处理输入文本
    """
    original = state.text.strip()
    lines = original.split('\n')
    first_line = lines[0].strip().lower()

    mode_map = {
        'encode': '→ Enc',
        'e': '→ Enc',
        'decode': '→ Dec',
        'd': '→ Dec',
        'toggle': '↔',
        't': '↔'
    }

    mode = first_line if first_line in mode_map else 'toggle'
    result = run(original)

    if result != original:
        state.text = result
        state.post_info(f"ASCII {mode_map.get(mode, '↔')}")
    else:
        state.post_info("ASCII 无变化")
