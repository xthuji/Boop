#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle URL Defang",
  "description": "对 URL 进行伪装处理",
  "icon": "🌐",
  "tags": ["url","defang","security"],
  "help": "对 URL 进行伪装处理 (用于安全分析)\n\n示例:\n输入:\nhttps://example.com/path\n\n输出:\nhxxps://example[.]com/path"
}
'''

def run(text):
    """
    在URL防御格式和正常URL之间切换
    """
    # 检查是否是防御格式的URL
    if '[:]' in text or '[.]' in text:
        # 转换为正常URL
        return text.replace('[:]', ':').replace('[.]', '.')
    else:
        # 转换为防御格式
        return text.replace(':', '[:]').replace('.', '[.]')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("URL防御转换")
