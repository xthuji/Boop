'''
{
    "api": 1,
    "name": "添加Markdown引号",
    "description": "为文本添加Markdown引号格式",
    "icon": "text",
    "tags": ["format", "markdown", "quotes"],
    "help": "为文本添加Markdown引号格式\n\nExample:\nInput:\nhello world\ntest\n\nOutput:\n> hello world\n> test"
}
'''

def run(text):
    """
    为文本添加Markdown引号格式
    """
    lines = text.split('\n')
    quoted_lines = ['> ' + line for line in lines]
    return '\n'.join(quoted_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("添加Markdown引号")
