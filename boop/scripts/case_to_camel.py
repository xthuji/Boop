'''
{
    "api": 1,
    "name": "转换为驼峰命名",
    "description": "将文本转换为驼峰命名格式",
    "icon": "type",
    "tags": ["format", "case", "camel"],
    "help": "将文本转换为驼峰命名格式\n\nExample:\nInput:\nhello world\n\nOutput:\nhelloWorld"
}
'''

import re

def run(text):
    """
    将文本转换为驼峰命名格式
    """
    # 移除所有非字母数字字符，将首字母小写，后续单词首字母大写
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 第一个单词小写，其余单词首字母大写
    camel_case = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
    return camel_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为驼峰命名")
