'''
{
    "api": 1,
    "name": "Unicode转换",
    "description": "在Unicode转义序列和字符之间切换",
    "icon": "text",
    "tags": ["unicode", "convert"],
    "help": "在Unicode转义序列和字符之间切换\n\n- 如果输入包含Unicode转义序列，转换为字符\n- 如果输入包含非ASCII字符，转换为Unicode转义序列\n\nExample 1 (Unicode转义序列转字符):\nInput:\n\\u4f60\\u597d\n\nOutput:\n你好\n\nExample 2 (字符转Unicode转义序列):\nInput:\n你好\n\nOutput:\n\\u4f60\\u597d"
}
'''

import re

def run(text):
    """
    在Unicode转义序列和字符之间切换
    """
    # 检查是否包含Unicode转义序列
    if '\\u' in text:
        try:
            # 转换为字符
            decoded = text.encode('utf-8').decode('unicode_escape')
            return decoded
        except Exception:
            pass
    
    # 转换为Unicode转义序列
    try:
        encoded = ''.join(f'\\u{ord(c):04x}' if ord(c) > 127 else c for c in text)
        return encoded
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("Unicode转换")
