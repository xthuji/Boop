#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Toggle HTML Entities",
  "description": "在 HTML 实体和文本之间转换",
  "icon": "🌐",
  "tags": ["html","entities","encode","decode"],
  "help": "在 HTML 实体和文本之间转换\n\n示例:\n输入:\nhello & world\n\n输出:\nhello &amp; world"
}
'''

import html

def run(text):
    """
    在HTML实体和字符之间切换
    """
    # 检查是否包含HTML实体
    if '&' in text:
        try:
            # 转换为字符
            decoded = html.unescape(text)
            if decoded != text:
                return decoded
        except Exception:
            pass
    
    # 转换为HTML实体
    try:
        encoded = html.escape(text)
        return encoded
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("HTML实体转换")
