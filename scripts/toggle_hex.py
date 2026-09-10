#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Hex",
  "description": "在十六进制和文本之间转换",
  "icon": "↔️",
  "tags": ["hex", "encode", "decode"],
  "help": "在十六进制和文本之间转换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- encode/e: 强制编码为十六进制\n- decode/d: 强制解码十六进制\n- toggle/t: 自动检测并切换模式 (默认)\n\n示例 1 (强制编码):\n输入:\nencode\nhello\n\n输出:\n68656c6c6f\n\n示例 2 (强制解码):\n输入:\ndecode\n68656c6c6f\n\n输出:\nhello"
}
'''

def _encode_hex(text):
    """将文本编码为十六进制"""
    lines = text.split('\n')
    encoded_lines = []
    for line in lines:
        try:
            if not line:
                encoded_lines.append('')
            else:
                encoded = line.encode('utf-8').hex()
                encoded_lines.append(encoded)
        except Exception:
            encoded_lines.append(line)
    return '\n'.join(encoded_lines)


def _decode_hex(text):
    """将十六进制解码为文本"""
    lines = text.split('\n')
    decoded_lines = []
    for line in lines:
        try:
            if not line:
                decoded_lines.append('')
            else:
                clean_hex = line.replace(' ', '').replace('0x', '')
                if len(clean_hex) % 2 == 0 and all(c in '0123456789abcdefABCDEF' for c in clean_hex):
                    decoded = bytes.fromhex(clean_hex).decode('utf-8')
                    decoded_lines.append(decoded)
                else:
                    decoded_lines.append(line)
        except Exception:
            decoded_lines.append(line)
    return '\n'.join(decoded_lines)


def _toggle_hex(text):
    """自动切换十六进制编码/解码模式"""
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        if not line:
            processed_lines.append('')
            continue

        clean_line = line.replace(' ', '').replace('0x', '')
        if len(clean_line) % 2 == 0 and all(c in '0123456789abcdefABCDEF' for c in clean_line):
            try:
                decoded = bytes.fromhex(clean_line).decode('utf-8')
                if decoded != line:
                    processed_lines.append(decoded)
                    continue
            except Exception:
                pass

        try:
            encoded = line.encode('utf-8').hex()
            processed_lines.append(encoded)
        except Exception:
            processed_lines.append(line)
    return '\n'.join(processed_lines)


def run(text):
    """
    在十六进制编码和解码之间切换
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
        return _encode_hex(text_to_process)
    elif mode == 'decode':
        return _decode_hex(text_to_process)
    else:
        return _toggle_hex(text_to_process)


def main(state):
    """
    主函数，调用 run 函数处理输入文本
    """
    original = state.text.strip()
    lines = original.split('\n')
    first_line = lines[0].strip().lower()

    mode_map = {
        'encode': '→ Hex',
        'e': '→ Hex',
        'decode': '→ Dec',
        'd': '→ Dec',
        'toggle': '↔',
        't': '↔'
    }

    mode = first_line if first_line in mode_map else 'toggle'
    result = run(original)

    if result != original:
        state.text = result
        state.post_info(f"Hex {mode_map.get(mode, '↔')}")
    else:
        state.post_info("Hex 无变化")
