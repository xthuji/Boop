'''
{
    "api": 1,
    "name": "切换引号",
    "description": "在不同引号之间切换",
    "icon": "text",
    "tags": ["text", "quotes", "toggle"],
    "help": "在不同引号之间切换\n\n- 如果输入包含双引号，转换为单引号\n- 如果输入包含单引号，转换为双引号\n\nExample 1 (双引号转单引号):\nInput:\n\"hello world\"\n\nOutput:\n'hello world'\n\nExample 2 (单引号转双引号):\nInput:\n'hello world'\n\nOutput:\n\"hello world\""
}
'''

def run(text):
    """
    在不同引号之间切换
    """
    # 检查是否包含双引号
    if '"' in text:
        # 转换为单引号
        return text.replace('"', "'")
    else:
        # 转换为双引号
        return text.replace("'", '"')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("切换引号")
