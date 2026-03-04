'''
{
    "api": 1,
    "name": "执行JavaScript",
    "description": "执行JavaScript代码",
    "icon": "code",
    "tags": ["javascript", "eval"],
    "help": "执行JavaScript代码\n\nExample:\nInput:\n1 + 1\n\nOutput:\n2"
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
