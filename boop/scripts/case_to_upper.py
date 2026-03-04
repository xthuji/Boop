'''
{
    "api": 1,
    "name": "转换为大写",
    "description": "将文本转换为大写",
    "icon": "type",
    "tags": ["format", "case", "upper"],
    "help": "将文本转换为大写\n\nExample:\nInput:\nhello world\n\nOutput:\nHELLO WORLD"
}
'''

def run(text):
    """
    将文本转换为大写
    """
    return text.upper()

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为大写")
