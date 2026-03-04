'''
{
    "api": 1,
    "name": "转换为小写",
    "description": "将文本转换为小写",
    "icon": "type",
    "tags": ["format", "case", "lower"],
    "help": "将文本转换为小写\n\nExample:\nInput:\nHELLO WORLD\n\nOutput:\nhello world"
}
'''

def run(text):
    """
    将文本转换为小写
    """
    return text.lower()

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为小写")
