'''
{
    "api": 1,
    "name": "移除空行",
    "description": "移除文本中的空行",
    "icon": "text",
    "tags": ["text", "remove", "empty", "lines"],
    "help": "移除文本中的空行\n\nExample:\nInput:\nhello\n\nworld\n\nOutput:\nhello\nworld"
}
'''

def run(text):
    """
    移除文本中的空行
    """
    lines = text.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("移除空行")
