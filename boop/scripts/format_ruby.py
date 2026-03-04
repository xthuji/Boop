#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format Ruby",
  "description": "Professional Ruby code formatter and minifier.",
  "icon": "pineapple",
  "tags": ["ruby", "format", "minify"],
  "help": "Format or minify Ruby code with proper indentation and spacing.\n\nExample:\nInput:\ndef hello() puts \"Hello\" end\n\nOutput:\ndef hello()\n  puts \"Hello\"\nend\n\nIf the code is already formatted, it will be minified."
}
"""

import re


class TokenManager:
    """Token 管理器，保护注释和字符串"""

    def __init__(self, prefix: str = ''):
        self.prefix = prefix
        self.placeholders = []

    def _add_token(self, content: str) -> str:
        idx = len(self.placeholders)
        token_id = '__{}_TK_{}__'.format(self.prefix, idx)
        self.placeholders.append({'id': token_id, 'content': content})
        return token_id

    def protect(self, code: str, patterns: list) -> str:
        result = code
        for pattern, flags in patterns:
            if flags == 0:
                result = re.sub(pattern, lambda m: self._add_token(m.group(0)), result)
            else:
                result = re.sub(pattern, lambda m: self._add_token(m.group(0)), result, flags=flags)
        return result

    def restore(self, code: str) -> str:
        result = code
        for i in range(len(self.placeholders) - 1, -1, -1):
            result = result.replace(self.placeholders[i]['id'], self.placeholders[i]['content'])
        return result

    def reset(self):
        self.placeholders = []


class RubyFormatter:
    """Ruby 代码格式化器"""

    INDENT = '  '  # Ruby 使用 2 空格缩进

    KEYWORDS_WITH_SPACE = ['def', 'class', 'module', 'if', 'for', 'while', 'until',
                           'case', 'begin', 'elsif', 'else', 'when', 'rescue', 'ensure']
    OPERATORS = ['==', '!=', '<=', '>=', '=', '+', '-', '*', '/', '%', '>', '<']

    def format(self, code: str) -> str:
        """格式化 Ruby 代码"""
        if not code or not code.strip():
            return code

        # 保护 token
        tm = TokenManager(prefix='RUBY')
        patterns = [
            (r'=begin[\s\S]*?=end', 0),
            (r'#.*$', re.MULTILINE),
            (r"'(\\.|[^'\\])*'", 0),
            (r'"(\\.|[^"\\])*"', 0),
        ]
        processed = tm.protect(code, patterns)

        # 预处理：拆分控制结构
        processed = self._preprocess(processed)

        # 逐行格式化
        formatted_lines = self._format_lines(processed)

        # 恢复 token
        result = tm.restore('\n'.join(formatted_lines))

        # 后处理
        return self._post_process(result)

    def _preprocess(self, code: str) -> str:
        """预处理代码"""
        # def + 名字 + 可选括号，保持在同一行后换行
        code = re.sub(r'\b(def\s+[\w\!\?]+(\s*\([^)]*\))?)', r'\1\n', code)
        # class, module, begin, do 后换行
        code = re.sub(r'\b(class\s+[\w:]+|module\s+[\w:]+|begin|do)\b', r'\1\n', code)
        # then 后换行
        code = re.sub(r'\b(then)\b', r'\1\n', code)
        # else, elsif, rescue, ensure, end 前后换行
        code = re.sub(r'\b(else|elsif|rescue|ensure|end)\b', r'\n\1\n', code)
        return code

    def _format_line(self, line: str) -> str:
        """格式化单行"""
        l = line.strip()
        if not l:
            return ''

        # 关键词空格
        l = self._format_keywords(l, self.KEYWORDS_WITH_SPACE)

        # 操作符空格
        l = self._format_operators(l, self.OPERATORS)

        # 逗号空格
        l = re.sub(r',(?!\s)', ', ', l)

        # 清理重复空格
        return re.sub(r'\s+', ' ', l)

    def _format_operators(self, line: str, operators: list) -> str:
        """为操作符添加空格"""
        result = line
        sorted_operators = sorted(operators, key=len, reverse=True)
        for op in sorted_operators:
            escaped_op = re.escape(op)
            pattern = r'(?<!\s)({})(?!\s)'.format(escaped_op)
            if re.search(pattern, result):
                result = re.sub(r'([^\s])({})([^\s])'.format(escaped_op), r'\1 \2 \3', result)
                result = re.sub(r'(\s)({})([^\s])'.format(escaped_op), r'\1 \2 \3', result)
                result = re.sub(r'([^\s])({})(\s)'.format(escaped_op), r'\1 \2 \3', result)
        result = re.sub(r'\s+', ' ', result)
        return result

    def _format_keywords(self, line: str, keywords: list) -> str:
        """为关键词添加空格（在括号前）"""
        result = line
        for keyword in keywords:
            pattern = r'\b(' + re.escape(keyword) + r')\s*([({])'
            result = re.sub(pattern, r'\1 \2', result)
        return result

    def _format_lines(self, code: str) -> list:
        """格式化所有行并处理缩进"""
        lines = code.split('\n')
        formatted = []
        level = 0

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                if formatted and formatted[-1]:
                    formatted.append('')
                continue

            # 递减缩进
            if re.match(r'^(end|elsif|else|when|rescue|ensure|\})', trimmed):
                level = max(0, level - 1)

            formatted.append(self.INDENT * level + self._format_line(trimmed))

            # 递增缩进
            if re.match(r'^(def|class|module|if|for|while|until|case|begin|elsif|else|when|rescue|ensure)\b|.*\bdo$|\{$', trimmed):
                level += 1

        return formatted

    def _post_process(self, code: str) -> str:
        """后处理"""
        code = re.sub(r'\n\s*\n', '\n', code)
        return code.strip() + '\n'


def format_code(code: str) -> str:
    """格式化 Ruby 代码的便捷函数"""
    formatter = RubyFormatter()
    return formatter.format(code)


def main(state):
    """Format or minify Ruby text."""
    if not state.text or not state.text.strip():
        return
    
    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Ruby code formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(f"Error formatting Ruby: {str(e)}")
        else:
            print(f"Error formatting Ruby: {str(e)}")

def is_minified(text):
    """Check if Ruby code is minified."""
    text = text.strip()
    return not '\n' in text and ('def' in text or 'class' in text or 'module' in text)

def minify_code(code):
    """Minify Ruby code."""
    if not code or not code.strip():
        return code
    
    # 移除注释
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'=begin[\s\S]*?=end', '', code, flags=re.DOTALL)
    # 移除多余空格和换行
    code = re.sub(r'\s+', ' ', code)
    # 移除行尾分号
    code = re.sub(r';$', '', code)
    return code.strip()

def process_format_code(text):
    """Process Ruby code - format or minify based on input state."""
    if not text or not text.strip():
        return text
    
    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)


