'''
{
    "api": 1,
    "name": "URL编解码",
    "description": "在URL编码和解码之间切换",
    "icon": "link",
    "tags": ["url", "encode", "decode"],
    "help": "在URL编码和解码之间切换\n\n- 如果输入是编码后的URL，进行解码\n- 如果输入是未编码的URL，进行编码\n\nExample 1 (解码):\nInput:\nhttps%3A%2F%2Fwww.example.com%2F\n\nOutput:\nhttps://www.example.com/\n\nExample 2 (编码):\nInput:\nhttps://www.example.com/\n\nOutput:\nhttps%3A%2F%2Fwww.example.com%2F"
}
'''

import urllib.parse

def run(text):
    """
    URL编码与解码
    """
    try:
        # 尝试解码
        decoded = urllib.parse.unquote(text)
        if decoded != text:
            return decoded
        # 尝试编码
        encoded = urllib.parse.quote(text)
        return encoded
    except Exception:
        return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("URL编解码")
