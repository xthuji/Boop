'''
{
    "api": 1,
    "name": "十六进制编解码",
    "description": "在十六进制编码和解码之间切换",
    "icon": "lock",
    "tags": ["hex", "encode", "decode"],
    "help": "在十六进制编码和解码之间切换\n\n- 如果输入是编码后的十六进制，进行解码\n- 如果输入是未编码的文本，进行编码\n\nExample 1 (解码):\nInput:\n68656c6c6f20776f726c64\n\nOutput:\nhello world\n\nExample 2 (编码):\nInput:\nhello world\n\nOutput:\n68656c6c6f20776f726c64"
}
'''

def run(text):
    """
    在十六进制编码和解码之间切换
    """
    try:
        # 尝试解码
        # 移除可能的空格和0x前缀
        hex_str = text.replace(' ', '').replace('0x', '')
        decoded = bytes.fromhex(hex_str).decode('utf-8')
        return decoded
    except Exception:
        # 尝试编码
        try:
            encoded = text.encode('utf-8').hex()
            return encoded
        except Exception:
            return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("十六进制编解码")
