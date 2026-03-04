'''
{
    "api": 1,
    "name": "转换为Pascal命名",
    "description": "将文本转换为Pascal命名格式",
    "icon": "type",
    "tags": ["format", "case", "pascal"],
    "help": "将文本转换为Pascal命名格式\n\nExample:\nInput:\nhello world\n\nOutput:\nHelloWorld"
}
'''

import re

def run(text):
    """
    将文本转换为Pascal命名格式
    """
    # 移除所有非字母数字字符，将所有单词首字母大写
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 所有单词首字母大写
    pascal_case = ''.join(word.capitalize() for word in words)
    return pascal_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为Pascal命名")
