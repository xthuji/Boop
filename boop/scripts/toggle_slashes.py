'''
{
    "api": 1,
    "name": "切换斜杠",
    "description": "在反斜杠和正斜杠之间切换",
    "icon": "text",
    "tags": ["text", "slashes", "convert"],
    "help": "在反斜杠和正斜杠之间切换\n\n- 如果输入包含反斜杠，转换为正斜杠\n- 如果输入包含正斜杠，转换为反斜杠\n\nExample 1 (反斜杠转正斜杠):\nInput:\nC:\\Users\\huji\n\nOutput:\nC:/Users/huji\n\nExample 2 (正斜杠转反斜杠):\nInput:\nC:/Users/huji\n\nOutput:\nC:\\Users\\huji"
}
'''

def run(text):
    """
    在反斜杠和正斜杠之间切换
    """
    # 检查是否包含反斜杠
    if '\\' in text:
        # 转换为正斜杠
        return text.replace('\\', '/')
    else:
        # 转换为反斜杠
        return text.replace('/', '\\')

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("切换斜杠")
