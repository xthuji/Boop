'''
{
    "api": 1,
    "name": "快速替换",
    "description": "快速替换文本中的内容",
    "icon": "text",
    "tags": ["text", "replace"],
    "help": "快速替换文本中的内容\n\nExample:\nInput:\nhello world\nold: hello\nnew: hi\n\nOutput:\nhi world"
}
'''

def run(text):
    """
    快速替换文本中的内容
    """
    lines = text.split('\n')
    if len(lines) < 3:
        return text
    
    content = '\n'.join(lines[:-2])
    old = ''
    new = ''
    
    for line in lines[-2:]:
        if line.startswith('old: '):
            old = line[5:]
        elif line.startswith('new: '):
            new = line[5:]
    
    if old:
        content = content.replace(old, new)
    
    return content

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("快速替换")
