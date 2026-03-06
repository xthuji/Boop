#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle URL Defang",
  "description": "对 URL 进行伪装处理",
  "icon": "↔️",
  "tags": ["url","defang","security"],
  "help": "对 URL 进行伪装处理 (用于安全分析)\n\n示例:\n输入:\nhttps://example.com/path\n\n输出:\nhxxps://example[.]com/path"
}
'''

def _defang_url(text):
    """将URL去危险化"""
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
    """将URL恢复正常"""
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
    """检查URL是否已去危险化"""
    return '[.]' in text or 'hXXp' in text or 'hXXps' in text or '[://]' in text


def _toggle_url_defang(text):
    """自动切换URL去危险化/恢复模式"""
    if _is_defanged(text):
        return _refang_url(text)
    else:
        return _defang_url(text)


def run(text):
    """
    在URL防御格式和正常URL之间切换
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
    else:  # toggle
        return _toggle_url_defang(text_to_process)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("URL防御转换")
