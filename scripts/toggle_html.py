#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle HTML Text",
  "description": "在 HTML 实体和文本之间转换",
  "icon": "↔️",
  "tags": ["html", "entities", "encode", "decode"],
  "help": "在 HTML 实体和文本之间转换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- encode/e: 强制编码为 HTML 实体\n- decode/d: 强制解码 HTML 实体\n- toggle/t: 自动检测并切换模式 (默认)\n\n示例 1 (强制编码):\n输入:\nencode\n<div>Hello</div>\n\n输出:\n&lt;div&gt;Hello&lt;/div&gt;\n\n示例 2 (强制解码):\n输入:\ndecode\n&lt;div&gt;Hello&lt;/div&gt;\n\n输出:\n<div>Hello</div>"
}
'''

import html

def _encode_html(text):
    """将文本编码为 HTML 实体"""
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
    """将 HTML 实体解码为文本"""
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
    """自动切换 HTML 编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue

        if '&' in line:
            try:
                decoded = html.unescape(line)
                if decoded != line:
                    processed_lines.append(decoded)
                    continue
            except Exception:
                pass

        try:
            encoded = html.escape(line)
            processed_lines.append(encoded)
        except Exception:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def run(text):
    """
    在 HTML 实体和字符之间切换
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
    else:
        return _toggle_html(text_to_process)


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
        state.post_info(f"HTML {mode_map.get(mode, '↔')}")
    else:
        state.post_info("HTML 无变化")
