'''
{
    "api": 1,
    "name": "ASCII转换",
    "description": "在ASCII码和字符之间切换",
    "icon": "text",
    "tags": ["ascii", "convert"],
    "help": "在ASCII码和字符之间切换\n\n- 如果输入是ASCII码，转换为字符\n- 如果输入是字符，转换为ASCII码\n\nExample 1 (ASCII码转字符):\nInput:\n104 101 108 108 111\n\nOutput:\nhello\n\nExample 2 (字符转ASCII码):\nInput:\nhello\n\nOutput:\n104 101 108 108 111"
}
'''

import re

def run(text):
    """
    在ASCII码和字符之间切换
    """
    # 检查是否是ASCII码序列
    ascii_match = re.findall(r'\b\d{1,3}\b', text)
    if ascii_match and len(ascii_match) > 0:
        try:
            # 转换为字符
            chars = []
            for code in ascii_match:
                code = int(code)
                if 0 <= code <= 127:
                    chars.append(chr(code))
            return ''.join(chars)
        except Exception:
            pass
    
    # 转换为ASCII码
    try:
        ascii_codes = [str(ord(c)) for c in text]
        return ' '.join(ascii_codes)
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("ASCII转换")
