#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format Shell",
  "description": "格式化 Shell 脚本",
  "icon": "✨",
  "tags": ["shell","bash","format","fmt","code"],
  "dependencies": [],
  "help": "格式化 Shell 脚本\n\n示例:\n输入:\nif [ true ];then echo \"Hello\";fi\n\n输出:\nif [ true ]; then\n    echo \"Hello\"\nfi"
}"""

import re

CONFIG = {'INDENT': '    '}


class TokenManager:
    def __init__(self):
        self.placeholders = []

    def protect(self, code):
        def add_token(m):
            idx = len(self.placeholders)
            token_id = '__SH_TK_{}__'.format(idx)
            self.placeholders.append({'id': token_id, 'content': m.group(0)})
            return token_id

        # 特殊处理 Shebang，确保其后有换行
        if code.startswith('#!'):
            shebang_end = code.find('\n')
            if shebang_end == -1:
                space_pos = code.find(' ')
                if space_pos != -1:
                    code = code[:space_pos] + '\n' + code[space_pos:]
                else:
                    code = code + '\n'
            else:
                shebang_line = code[:shebang_end]
                if ' ' in shebang_line and not shebang_line.strip().endswith('\\'):
                    space_pos = shebang_line.find(' ')
                    code = shebang_line[:space_pos] + '\n' + shebang_line[space_pos:] + code[shebang_end:]

        # 保护注释和字符串
        code = re.sub(r'#.*', add_token, code)
        code = re.sub(r'"(\\.|[^"\\])*"', add_token, code)
        code = re.sub(r"'(\\.|[^'\\])*'", add_token, code)
        code = re.sub(r'`[^`]*`', add_token, code)
        code = re.sub(r'\$[({][^)}]*[)}]', add_token, code)

        return code

    def restore(self, code):
        result = code
        for i in range(len(self.placeholders) - 1, -1, -1):
            result = result.replace(self.placeholders[i]['id'], self.placeholders[i]['content'])
        return result


class Engine:
    @staticmethod
    def preprocess(code):
        # 结构化拆分逻辑
        # A. 在 fi, done, else, elif 之前换行，并移除它们前面可能存在的冗余分号
        code = re.sub(r';?\s*\b(fi|done|else|elif)\b', r'\n\1', code)
        # B. 在 then, do, else 之后如果紧跟代码，则换行 (保留 ; then 在行尾)
        code = re.sub(r'\b(then|do|else)\b\s+([^\s\n])', r'\1\n\2', code)
        # C. 精确处理函数定义和花括号块
        code = re.sub(r'(\bfunction\s+\w+\s*\(\s*\)|\w+\s*\(\s*\))\s*\{', r'\1 {', code)
        code = re.sub(r'\{\s+', r'{\n', code)
        code = re.sub(r'\s+\}', r'\n}', code)
        return code

    @staticmethod
    def format_line(line):
        l = line.strip()
        if not l:
            return ''

        # 清理多余的分号
        l = re.sub(r';+$', '', l)

        # 清理重复空格
        return re.sub(r'\s+', ' ', l)


def format_code(code):
    """Format Shell script code."""
    if not code or not code.strip():
        return code

    tokens = TokenManager()
    processed = tokens.protect(code)
    processed = Engine.preprocess(processed)

    lines = processed.split('\n')
    formatted_lines = []
    level = 0

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue

        # 递减当前行的缩进：如果行首是回退关键字
        if re.match(r'^(fi|done|else|elif|esac|\})', line):
            level = max(0, level - 1)

        content = Engine.format_line(line)
        formatted_lines.append(CONFIG['INDENT'] * level + content)

        # 决定下一行的缩进级别：如果当前行开启了代码块
        if re.search(r'\b(then|do|else|elif)\b$|\{$', line):
            level += 1
        elif re.match(r'^(if|for|while|until|case)\b', line) and not re.search(r'\b(then|do)\b', line):
            level += 1

    result = tokens.restore('\n'.join(formatted_lines))
    return post_process(result)


def post_process(code):
    """Post process the formatted code."""
    # 移除行末空格和多余的分号，并合并重复空行
    code = re.sub(r'[ \t]*;+\n', r'\n', code)
    code = re.sub(r'[ \t]+\n', r'\n', code)
    code = re.sub(r'\n\s*\n', '\n', code)

    return code.strip()


def main(state):
    """Format Shell text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Shell code formatted")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(f"Error formatting Shell: {str(e)}")
        else:
            print(f"Error formatting Shell: {str(e)}")
