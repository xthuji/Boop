'''
{
    "api": 1,
    "name": "修剪行空白",
    "description": "修剪每行文本的空白字符",
    "icon": "text",
    "tags": ["text", "trim", "whitespace"],
    "help": "修剪每行文本的空白字符\n\nExample:\nInput:\n  hello world  \n  test  \n\nOutput:\nhello world\ntest"
}
'''

def run(text):
    """
    修剪每行文本的空白字符
    """
    lines = text.split('\n')
    trimmed_lines = [line.strip() for line in lines]
    return '\n'.join(trimmed_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("修剪行空白")
