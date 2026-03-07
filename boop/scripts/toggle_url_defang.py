#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle URL Defang",
  "description": "对 URL 进行伪装处理",
  "icon": "↔️",
  "tags": ["url", "defang", "security"],
  "help": "对 URL 进行伪装处理 (用于安全分析)\n\n首行参数格式:\nmode (指定转换模式)\n\n支持的模式:\n- defang/d: 强制去危险化 (伪装 URL)\n- refang/r: 强制恢复 URL\n- toggle/t: 自动检测并切换模式 (默认)\n\n示例 1 (去危险化):\n输入:\ndefang\nhttps://example.com/path\n\n输出:\nhXXps[://]example[.]com/path\n\n示例 2 (恢复):\n输入:\nrefang\nhXXps[://]example[.]com/path\n\n输出:\nhttps://example.com/path"
}
'''

def _defang_url(text):
    """将 URL 去危险化"""
    lines = text.split('\n')
    defanged_lines = []
    for line in lines:
        try:
            if not line:
                defanged_lines.append('')
            else:
                defanged = line.replace('.', '[.]').replace('http', 'hXXp').replace('https', 'hXXps').replace('://', '[://]')
                defanged_lines.append(defanged)
        except Exception:
            defanged_lines.append(line)
    return '\n'.join(defanged_lines)


def _refang_url(text):
    """将 URL 恢复正常"""
    lines = text.split('\n')
    refanged_lines = []
    for line in lines:
        try:
            if not line:
                refanged_lines.append('')
            else:
                refanged = line.replace('[.]', '.').replace('hXXp', 'http').replace('hXXps', 'https').replace('[://]', '://')
                refanged_lines.append(refanged)
        except Exception:
            refanged_lines.append(line)
    return '\n'.join(refanged_lines)


def _is_defanged(text):
    """检查 URL 是否已去危险化"""
    return '[.]' in text or 'hXXp' in text or 'hXXps' in text or '[://]' in text


def _toggle_url_defang(text):
    """自动切换 URL 去危险化/恢复模式"""
    if _is_defanged(text):
        return _refang_url(text)
    else:
        return _defang_url(text)


def run(text):
    """
    在 URL 防御格式和正常 URL 之间切换
    """
    lines = text.split('\n')
    first_line = lines[0].strip().lower()

    mode = 'toggle'
    text_to_process = text

    mode_map = {
        'defang': 'defang',
        'd': 'defang',
        'refang': 'refang',
        'r': 'refang',
        'toggle': 'toggle',
        't': 'toggle'
    }

    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_process = '\n'.join(lines[1:])

    if mode == 'defang':
        return _defang_url(text_to_process)
    elif mode == 'refang':
        return _refang_url(text_to_process)
    else:
        return _toggle_url_defang(text_to_process)


def main(state):
    """
    主函数，调用 run 函数处理输入文本
    """
    original = state.text.strip()
    lines = original.split('\n')
    first_line = lines[0].strip().lower()

    mode_map = {
        'defang': '→ Defang',
        'd': '→ Defang',
        'refang': '→ Refang',
        'r': '→ Refang',
        'toggle': '↔',
        't': '↔'
    }

    mode = first_line if first_line in mode_map else 'toggle'
    result = run(original)

    if result != original:
        state.text = result
        state.post_info(f"URL {mode_map.get(mode, '↔')}")
    else:
        state.post_info("URL 无变化")
