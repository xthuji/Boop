'''
{
    "api": 1,
    "name": "对齐代码",
    "description": "对齐代码中的赋值语句",
    "icon": "code",
    "tags": ["format", "code", "align"],
    "help": "对齐代码中的赋值语句\n\nExample:\nInput:\na = 1\nbb = 2\nccc = 3\n\nOutput:\na   = 1\nbb  = 2\nccc = 3"
}
'''

import re

def run(text):
    """
    对齐代码中的赋值语句
    """
    lines = text.split('\n')
    
    # 找出所有包含赋值操作的行
    assignment_lines = []
    for i, line in enumerate(lines):
        match = re.search(r'\s*(.+?)\s*=', line)
        if match:
            assignment_lines.append((i, match.group(1)))
    
    if not assignment_lines:
        return text
    
    # 计算最长的变量名长度
    max_length = max(len(name) for _, name in assignment_lines)
    
    # 对齐赋值语句
    for i, name in assignment_lines:
        line = lines[i]
        # 替换原行
        new_line = re.sub(r'\s*(.+?)\s*=', f'{name.ljust(max_length)} =', line)
        lines[i] = new_line
    
    return '\n'.join(lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("对齐代码")
