#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Slashes",
  "description": "在正斜杠和反斜杠之间切换",
  "icon": "↔️",
  "tags": ["slashes","toggle","path"],
  "help": "在正斜杠 (/) 和反斜杠 (\\) 之间切换\n\n示例:\n输入:\npath/to/file\n\n输出:\npath\\to\\file"
}
'''

def _add_slashes(text):
    """添加反斜杠转义"""
    lines = text.split('\n')
    escaped_lines = []
    for line in lines:
        # 转义引号和反斜杠
        escaped = line.replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'")
        # 转义 null 字符
        escaped = escaped.replace('\x00', '\\0')
        escaped_lines.append(escaped)
    return '\n'.join(escaped_lines)


def _remove_slashes(text):
    """移除反斜杠转义"""
    lines = text.split('\n')
    unescaped_lines = []
    for line in lines:
        # 处理转义字符
        unescaped = ''
        i = 0
        while i < len(line):
            if line[i] == '\\' and i + 1 < len(line):
                next_char = line[i + 1]
                if next_char == '\\':
                    unescaped += '\\'
                elif next_char == '0':
                    unescaped += '\x00'
                else:
                    unescaped += next_char
                i += 2
            else:
                unescaped += line[i]
                i += 1
        unescaped_lines.append(unescaped)
    return '\n'.join(unescaped_lines)


def _is_escaped(text):
    """检查文本是否已转义"""
    return '\\\\' in text or "\\'" in text or '\\"' in text or '\\0' in text


def _toggle_slashes(text):
    """自动切换转义/反转义模式"""
    if _is_escaped(text):
        return _remove_slashes(text)
    else:
        return _add_slashes(text)


def run(text):
    """
    在反斜杠转义和反转义之间切换
    """
    lines = text.split('\n')
    first_line = lines[0].strip().lower()
    
    mode = 'toggle'
    text_to_process = text
    
    mode_map = {
        'add': 'add',
        'a': 'add',
        'remove': 'remove',
        'r': 'remove',
        'toggle': 'toggle',
        't': 'toggle'
    }
    
    if first_line in mode_map:
        mode = mode_map[first_line]
        text_to_process = '\n'.join(lines[1:])
    
    if mode == 'add':
        return _add_slashes(text_to_process)
    elif mode == 'remove':
        return _remove_slashes(text_to_process)
    else:  # toggle
        return _toggle_slashes(text_to_process)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("切换斜杠")
