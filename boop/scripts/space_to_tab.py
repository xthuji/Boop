'''
{
    "api": 1,
    "name": "空格转制表符",
    "description": "将空格转换为制表符",
    "icon": "code",
    "tags": ["format", "space", "tab"],
    "help": "将空格转换为制表符\n\n默认将4个连续空格转换为1个制表符\n\nExample:\nInput:\n    hello world\n\nOutput:\n\thello world"
}
'''

def run(text):
    """
    将空格转换为制表符
    """
    # 将4个连续空格转换为制表符
    return text.replace('    ', '\t')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("空格转制表符")
