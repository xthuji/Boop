#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle Slashes",
  "description": "在正斜杠和反斜杠之间切换",
  "icon": "➡️",
  "tags": ["slashes","toggle","path"],
  "help": "在正斜杠 (/) 和反斜杠 (\\) 之间切换\n\n示例:\n输入:\npath/to/file\n\n输出:\npath\\to\\file"
}
'''

def run(text):
    """
    在反斜杠和正斜杠之间切换
    """
    # 检查是否包含反斜杠
    if '\\' in text:
        # 转换为正斜杠
        return text.replace('\\', '/')
    else:
        # 转换为反斜杠
        return text.replace('/', '\\')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("切换斜杠")
