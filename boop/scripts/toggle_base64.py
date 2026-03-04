'''
{
    "api": 1,
    "name": "Base64编解码",
    "description": "在Base64编码和解码之间切换",
    "icon": "lock",
    "tags": ["base64", "encode", "decode"],
    "help": "在Base64编码和解码之间切换\n\n- 如果输入是编码后的Base64，进行解码\n- 如果输入是未编码的文本，进行编码\n\nExample 1 (解码):\nInput:\naGVsbG8gd29ybGQ=\n\nOutput:\nhello world\n\nExample 2 (编码):\nInput:\nhello world\n\nOutput:\naGVsbG8gd29ybGQ="
}
'''

import base64

def run(text):
    """
    在Base64编码和解码之间切换
    """
    try:
        # 尝试解码
        decoded = base64.b64decode(text).decode('utf-8')
        return decoded
    except Exception:
        # 尝试编码
        try:
            encoded = base64.b64encode(text.encode('utf-8')).decode('utf-8')
            return encoded
        except Exception:
            return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("Base64编解码")
