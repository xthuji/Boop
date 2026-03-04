'''
{
    "api": 1,
    "name": "制表符转空格",
    "description": "将制表符转换为空格",
    "icon": "code",
    "tags": ["format", "space", "tab"],
    "help": "将制表符转换为空格\n\n默认将1个制表符转换为4个空格\n\nExample:\nInput:\n\thello world\n\nOutput:\n    hello world"
}
'''

def run(text):
    """
    将制表符转换为空格
    """
    # 将制表符转换为4个空格
    return text.replace('\t', '    ')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("制表符转空格")
