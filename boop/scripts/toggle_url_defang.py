'''
{
    "api": 1,
    "name": "URL防御转换",
    "description": "在URL防御格式和正常URL之间切换",
    "icon": "link",
    "tags": ["url", "defang", "convert"],
    "help": "在URL防御格式和正常URL之间切换\n\n- 如果输入是防御格式的URL，转换为正常URL\n- 如果输入是正常URL，转换为防御格式\n\nExample 1 (防御格式转正常URL):\nInput:\nhttp[:]//www[.]example[.]com\n\nOutput:\nhttp://www.example.com\n\nExample 2 (正常URL转防御格式):\nInput:\nhttp://www.example.com\n\nOutput:\nhttp[:]//www[.]example[.]com"
}
'''

def run(text):
    """
    在URL防御格式和正常URL之间切换
    """
    # 检查是否是防御格式的URL
    if '[:]' in text or '[.]' in text:
        # 转换为正常URL
        return text.replace('[:]', ':').replace('[.]', '.')
    else:
        # 转换为防御格式
        return text.replace(':', '[:]').replace('.', '[.]')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("URL防御转换")
