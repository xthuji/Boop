#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Color RGB Hex",
  "description": "RGB 与十六进制颜色值互相转换",
  "icon": "↔️",
  "tags": ["color", "rgb", "hex", "convert", "toggle"],
  "help": "RGB 与十六进制颜色值互相转换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- rgb/r: 强制转换为 RGB 格式\n- hex/h: 强制转换为 Hex 格式\n- toggle/t: 自动检测并切换 (默认)\n\n示例 1 (转 Hex):\n输入:\nhex\n255, 0, 0\n\n输出:\n#FF0000\n\n示例 2 (转 RGB):\n输入:\nrgb\n#FF0000\n\n输出:\nrgb(255, 0, 0)"
}
'''

import re


def hex_to_rgb(hex_color):
    """
    将十六进制颜色值转换为 RGB 格式
    """
    hex_color = hex_color.lstrip('#')

    if len(hex_color) == 3:
        hex_color = ''.join([c * 2 for c in hex_color])

    if len(hex_color) != 6:
        return None

    try:
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"rgb({r}, {g}, {b})"
    except ValueError:
        return None


def rgb_to_hex(text):
    """
    将 RGB 颜色值转换为十六进制格式
    """
    if text.strip().startswith('rgb('):
        text = text.strip().replace('rgb(', '').replace(')', '')

    rgb_array = [c.strip() for c in re.split(r'[\s,]+', text) if c.strip()]

    if len(rgb_array) != 3:
        return None

    try:
        r, g, b = map(int, rgb_array)
        if any(value < 0 or value > 255 for value in [r, g, b]):
            return None
        return f'#{r:02x}{g:02x}{b:02x}'.upper()
    except ValueError:
        return None


def run(text):
    """
    自动检测输入格式并转换
    """
    text = text.strip()

    hex_match = re.match(r'^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$', text)
    if hex_match:
        result = hex_to_rgb(text)
        if result:
            return result

    # 支持 rgb()、逗号、空格分隔的 RGB 格式
    rgb_match = re.match(r'^(rgb\()?\s*\d+\s*[,\s]\s*\d+\s*[,\s]\s*\d+\s*(\))?', text)
    if rgb_match:
        result = rgb_to_hex(text)
        if result:
            return result

    return text


def run_with_mode(text, mode='toggle'):
    """
    根据指定模式转换颜色格式
    """
    text = text.strip()

    if mode == 'rgb':
        return hex_to_rgb(text) or text
    elif mode == 'hex':
        return rgb_to_hex(text) or text
    else:
        return run(text)


def main(state):
    """
    主函数，调用 run 函数处理输入文本
    """
    original = state.text.strip()
    lines = original.split('\n')
    first_line = lines[0].strip().lower()

    mode = 'toggle'
    text_to_process = original

    mode_map = {
        'rgb': 'rgb',
        'r': 'rgb',
        'hex': 'hex',
        'h': 'hex',
        'toggle': 'toggle',
        't': 'toggle'
    }

    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_process = '\n'.join(lines[1:])

    result = run_with_mode(text_to_process, mode)

    if result and result != text_to_process:
        state.text = result
        if mode == 'rgb':
            state.post_info("Hex → RGB")
        elif mode == 'hex':
            state.post_info("RGB → Hex")
        else:
            if result.startswith('#'):
                state.post_info("RGB → Hex")
            elif result.startswith('rgb('):
                state.post_info("Hex → RGB")
    else:
        state.post_info("无法识别的颜色格式")
