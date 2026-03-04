'''
{
    "api": 1,
    "name": "列表格式转换",
    "description": "在不同列表格式之间转换",
    "icon": "text",
    "tags": ["convert", "data", "list"],
    "help": "在不同列表格式之间转换\n\nExample:\nInput:\n- item1\n- item2\n- item3\n\nOutput:\n* item1\n* item2\n* item3"
}
'''

def run(text):
    """
    在不同列表格式之间转换
    """
    lines = text.split('\n')
    converted_lines = []
    
    for line in lines:
        if line.strip().startswith('- '):
            # 转换为星号格式
            converted_lines.append(line.replace('- ', '* ', 1))
        elif line.strip().startswith('* '):
            # 转换为减号格式
            converted_lines.append(line.replace('* ', '- ', 1))
        else:
            converted_lines.append(line)
    
    return '\n'.join(converted_lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("列表格式转换")
