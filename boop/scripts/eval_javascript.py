#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Eval JavaScript",
  "description": "执行 JavaScript 代码",
  "icon": "⚡",
  "tags": ["javascript","eval","code","execute","cmd","command"],
  "help": "执行 JavaScript 代码并返回结果\n\n示例:\n输入:\n1 + 1\n\n输出:\n2"
}
'''

import subprocess
import json

def run(text):
    """
    执行JavaScript代码
    """
    try:
        # 使用Node.js执行JavaScript代码
        result = subprocess.run(
            ['node', '-e', f'console.log(JSON.stringify(eval({json.dumps(text)})))'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"错误: {result.stderr.strip()}"
    except Exception as e:
        return f"错误: {str(e)}"

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("执行JavaScript")
