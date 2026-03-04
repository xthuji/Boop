'''
{
    "api": 1,
    "name": "转换为SNAKE_CASE",
    "description": "将文本转换为SNAKE_CASE大写命名格式",
    "icon": "type",
    "tags": ["format", "case", "snake", "upper"],
    "help": "将文本转换为SNAKE_CASE大写命名格式\n\nExample:\nInput:\nhello world\n\nOutput:\nHELLO_WORLD"
}
'''

import re

def run(text):
    """
    将文本转换为SNAKE_CASE大写命名格式
    """
    # 移除所有非字母数字字符，将所有单词转为大写并以下划线连接
    words = re.findall(r'[a-zA-Z0-9]+', text)
    if not words:
        return text
    
    # 所有单词大写，以下划线连接
    snake_upper_case = '_'.join(word.upper() for word in words)
    return snake_upper_case

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("转换为SNAKE_CASE")
