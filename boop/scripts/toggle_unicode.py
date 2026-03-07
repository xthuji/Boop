#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Unicode",
  "description": "在 Unicode 转义和文本之间转换",
  "icon": "↔️",
  "tags": ["unicode", "encode", "decode"],
  "help": "在 Unicode 转义和文本之间转换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- encode/e: 强制编码为 Unicode 转义\n- decode/d: 强制解码 Unicode 转义\n- toggle/t: 自动检测并切换模式 (默认)\n\n示例 1 (强制编码):\n输入:\nencode\nhello\n\n输出:\n\\u0068\\u0065\\u006c\\u006c\\u006f\n\n示例 2 (强制解码):\n输入:\ndecode\n\\u0068\\u0065\\u006c\\u006c\\u006f\n\n输出:\nhello"
}
'''

import re

def _encode_unicode(text):
    """将文本编码为 Unicode 转义序列"""
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
    """将 Unicode 转义序列解码为文本"""
    lines = text.split('\n')
    decoded_lines = []
    for line in lines:
        try:
            if not line:
                decoded_lines.append('')
            else:
                unicode_pattern = re.compile(r'\\u([0-9a-fA-F]{4})')
                decoded = unicode_pattern.sub(lambda m: chr(int(m.group(1), 16)), line)
                decoded_lines.append(decoded)
        except Exception:
            decoded_lines.append(line)
    return '\n'.join(decoded_lines)


def _toggle_unicode(text):
    """自动切换 Unicode 编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue

        if '\\u' in line:
            try:
                decoded = _decode_unicode(line)
                if decoded != line:
                    processed_lines.append(decoded)
                    continue
            except Exception:
                pass

        try:
            encoded = _encode_unicode(line)
            processed_lines.append(encoded)
        except Exception:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def run(text):
    """
    在 Unicode 转义序列和字符之间切换
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
    else:
        return _toggle_unicode(text_to_process)


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
        state.post_info(f"Unicode {mode_map.get(mode, '↔')}")
    else:
        state.post_info("Unicode 无变化")
