#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format Java",
  "description": "Professional Java code formatter and minifier.",
  "icon": "pineapple",
  "tags": ["java", "format", "minify"],
  "help": "Format or minify Java code with proper indentation and spacing.\n\nExample:\nInput:\npublic class Hello{public static void main(String[] args){System.out.println(\"Hello\");}}\n\nOutput:\npublic class Hello {\n    public static void main(String[] args) {\n        System.out.println(\"Hello\");\n    }\n}\n\nIf the code is already formatted, it will be minified."
}
"""

import re

CONFIG = {'INDENT': '    '}

STREAM_METHODS = ['filter', 'map', 'collect', 'flatMap', 'forEach', 'sorted', 'reduce']
KEYWORDS_WITH_SPACE = ['if', 'for', 'while', 'switch', 'catch', 'synchronized']

class TokenManager:
    def __init__(self):
        self.placeholders = []

    def protect(self, code):
        def add_token(m):
            idx = len(self.placeholders)
            token_id = '__J_TK_{}__'.format(idx)
            self.placeholders.append({'id': token_id, 'content': m.group(0)})
            return token_id

        code = re.sub(r'/\*[\s\S]*?\*/', add_token, code)
        code = re.sub(r'//.*$', add_token, code)
        code = re.sub(r'"(\\.|[^"\\])*"', add_token, code)
        code = re.sub(r'<[A-Za-z0-9_,\.\s\?<\>\[\]]+>', lambda m: add_token(m) if len(m.group(0)) > 3 else m.group(0), code)

        return code

    def restore(self, code):
        result = code
        for i in range(len(self.placeholders) - 1, -1, -1):
            result = result.replace(self.placeholders[i]['id'], self.placeholders[i]['content'])
        return result

class Engine:
    @staticmethod
    def preprocess(code):
        stream_regex = r'\.({})\('.format('|'.join(STREAM_METHODS))
        # 保护 for 循环括号内的内容
        def protect_for_loops(m):
            return m.group(0).replace(';', '___SEMICOLON___')
        code = re.sub(r'\bfor\s*\([^)]*\)', protect_for_loops, code)
        # 处理其他部分
        code = re.sub(r'\{', ' {\n', code)
        code = re.sub(r'\}', '\n}\n', code)
        code = re.sub(r';', ';\n', code)
        code = re.sub(r'(@\w+)\s+', r'\1\n', code)
        code = re.sub(r'\}\s*else', '} else', code)
        code = re.sub(r'else\s*\{', 'else {', code)
        code = re.sub(stream_regex, r'\n.\1(', code)
        # 恢复 for 循环括号内的分号
        code = code.replace('___SEMICOLON___', ';')
        return code

    @staticmethod
    def format_line(line):
        l = line.strip()
        if not l:
            return ''

        # 1. 处理数组参数空格 (String[] args)
        l = re.sub(r'(\w+)\[\](\w+)', r'\1[] \2', l)

        # 2. 基础关键词空格 (if, for...)
        keywords_pattern = r'\b({})\s*\('.format('|'.join(KEYWORDS_WITH_SPACE))
        l = re.sub(keywords_pattern, r'\1 (', l)

        # 3. 增强的操作符处理
        operators = ['==', '!=', '>=', '<=', '->', '&&', '||', '=', '\+', '-', '\*', '/', '%', '>', '<']
        for op in operators:
            # 匹配非空白字符与操作符之间缺失的空格
            op_pattern = r'([^\s\+\-\*\/\%&\|^!<>])({})([^\s\+\-\*\/\%&\|^!<>])'.format(re.escape(op))
            l = re.sub(op_pattern, r'\1 \2 \3', l)

            # 处理操作符左侧缺失空格：a> 0 -> a > 0
            left_pattern = r'([^\s\+\-\*\/\%&\|^!<>])({})\s+'.format(re.escape(op))
            l = re.sub(left_pattern, r'\1 \2 ', l)

            # 处理操作符右侧缺失空格：a >0 -> a > 0
            right_pattern = r'\s+({})([^\s\+\-\*\/\%&\|^!<>])'.format(re.escape(op))
            l = re.sub(right_pattern, r' \1 \2', l)

        # 4. 逗号空格
        l = re.sub(r',(?!\s)', ', ', l)

        # 5. for 循环条件中的分号空格
        if 'for' in l:
            l = re.sub(r'for\s*\(([^;]+);([^;]+);([^)]+)\)', r'for (\1; \2; \3)', l)

        # 6. 清理重复空格
        return re.sub(r'\s+', ' ', l)

def format_code(code):
    """Format Java code."""
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

        if line.startswith('}') or line.startswith(']'):
            level = max(0, level - 1)

        current_indent = level + 1 if line.startswith('.') else level
        content = Engine.format_line(line)

        formatted_lines.append(CONFIG['INDENT'] * current_indent + content)

        if line.endswith('{') or line.endswith('['):
            level += 1

    result = tokens.restore('\n'.join(formatted_lines))
    return post_process(result)

def post_process(code):
    """Post process the formatted code."""
    lines = code.split('\n')
    pkg = ''
    imports = []
    body = []

    for l in lines:
        t = l.strip()
        if t.startswith('package '):
            pkg = t
        elif t.startswith('import '):
            imports.append(t)
        elif t != '':
            body.append(l)

    output = []
    if pkg:
        output.append(pkg + '\n')
    if imports:
        output.append('\n'.join(sorted(imports)) + '\n')

    body_content = '\n'.join(body)
    body_content = re.sub(r'\n{3,}', '\n\n', body_content)
    output.append(body_content)

    return '\n'.join(output).strip() + '\n'


def main(state):
    """Format or minify Java text."""
    if not state.text or not state.text.strip():
        return
    
    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Java code formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error("Error formatting Java: {}".format(str(e)))
        else:
            print("Error formatting Java: {}".format(str(e)))

def is_minified(text):
    """Check if Java code is minified."""
    text = text.strip()
    return not '\n' in text and ('class' in text or 'public' in text or 'static' in text)

def minify_code(code):
    """Minify Java code."""
    if not code or not code.strip():
        return code
    
    # 移除注释
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    # 移除多余空格和换行
    code = re.sub(r'\s+', ' ', code)
    # 移除行尾分号
    code = re.sub(r';$', '', code)
    return code.strip()

def process_format_code(text):
    """Process Java code - format or minify based on input state."""
    if not text or not text.strip():
        return text
    
    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)


