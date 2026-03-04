'''
{
    "api": 1,
    "name": "修复智能引号",
    "description": "将智能引号转换为普通引号",
    "icon": "text",
    "tags": ["text", "quotes", "fix"],
    "help": "将智能引号转换为普通引号\n\nExample:\nInput:\n“hello world”\n\nOutput:\n\"hello world\""
}
'''

def run(text):
    """
    将智能引号转换为普通引号
    """
    # 替换智能引号为普通引号
    smart_quotes = {
        '“': '"',  # 左双引号
        '”': '"',  # 右双引号
        '‘': "'",  # 左单引号
        '’': "'"   # 右单引号
    }
    
    for smart, normal in smart_quotes.items():
        text = text.replace(smart, normal)
    
    return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("修复智能引号")
