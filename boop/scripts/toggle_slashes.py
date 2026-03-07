#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Slashes",
  "description": "在正斜杠和反斜杠之间切换",
  "icon": "↔️",
  "tags": ["slashes", "toggle", "path"],
  "help": "在正斜杠 (/) 和反斜杠 (\\) 之间切换\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- forward/f: 转换为正斜杠 (/)\n- back/b: 转换为反斜杠 (\\)\n- toggle/t: 自动检测并切换 (默认)\n\n示例 1 (转反斜杠):\n输入:\nback\npath/to/file\n\n输出:\npath\\to\\file\n\n示例 2 (转正斜杠):\n输入:\nforward\npath\\to\\file\n\n输出:\npath/to/file"
}
'''


def _to_backslash(text):
    """将正斜杠转换为反斜杠"""
    return text.replace('/', '\\')


def _to_forward_slash(text):
    """将反斜杠转换为正斜杠"""
    return text.replace('\\', '/')


def _is_backslash(text):
    """检查文本是否包含反斜杠"""
    return '\\' in text


def _toggle_slashes(text):
    """自动切换正斜杠和反斜杠"""
    if _is_backslash(text):
        return _to_forward_slash(text)
    else:
        return _to_backslash(text)


def run(text):
    """
    在正斜杠和反斜杠之间切换
    """
    lines = text.split('\n')
    first_line = lines[0].strip().lower()

    mode = 'toggle'
    text_to_process = text

    mode_map = {
        'forward': 'forward',
        'f': 'forward',
        'back': 'back',
        'b': 'back',
        'toggle': 'toggle',
        't': 'toggle'
    }

    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_process = '\n'.join(lines[1:])

    if mode == 'forward':
        return _to_forward_slash(text_to_process)
    elif mode == 'back':
        return _to_backslash(text_to_process)
    else:  # toggle
        return _toggle_slashes(text_to_process)


def main(state):
    """
    主函数，调用 run 函数处理输入文本
    """
    original = state.text.strip()
    lines = original.split('\n')
    first_line = lines[0].strip().lower()

    mode_map = {
        'forward': '→ /',
        'f': '→ /',
        'back': '→ \\',
        'b': '→ \\',
        'toggle': '↔',
        't': '↔'
    }

    mode = first_line if first_line in mode_map else 'toggle'
    result = run(original)

    if result != original:
        state.text = result
        state.post_info(f"Slashes {mode_map.get(mode, '↔')}")
    else:
        state.post_info("Slashes 无变化")
