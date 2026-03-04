'''
{
    "api": 1,
    "name": "HTML实体转换",
    "description": "在HTML实体和字符之间切换",
    "icon": "code",
    "tags": ["html", "entity", "convert"],
    "help": "在HTML实体和字符之间切换\n\n- 如果输入是HTML实体，转换为字符\n- 如果输入是字符，转换为HTML实体\n\nExample 1 (HTML实体转字符):\nInput:\n&amp;lt;hello&amp;gt;\n\nOutput:\n<hello>\n\nExample 2 (字符转HTML实体):\nInput:\n<hello>\n\nOutput:\n&amp;lt;hello&amp;gt;"
}
'''

import html

def run(text):
    """
    在HTML实体和字符之间切换
    """
    # 检查是否包含HTML实体
    if '&' in text:
        try:
            # 转换为字符
            decoded = html.unescape(text)
            if decoded != text:
                return decoded
        except Exception:
            pass
    
    # 转换为HTML实体
    try:
        encoded = html.escape(text)
        return encoded
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("HTML实体转换")
