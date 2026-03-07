#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format AppleScript",
  "description": "格式化 AppleScript 代码",
  "icon": "✨",
  "tags": ["applescript","format","fmt","code"],
  "dependencies": [],
  "help": "格式化 AppleScript 代码\n\n示例:\n输入:\non hello() say \"Hello\"\nend hello\n\n输出:\non hello()\n    say \"Hello\"\nend hello"
}"""

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


class AppleScriptFormatter:
    """AppleScript 代码格式化器"""

    INDENT = '    '

    KEYWORDS_WITH_SPACE = ['if', 'then', 'else', 'end', 'tell', 'to', 'of', 'with', 'in',
                           'and', 'or', 'not', 'repeat', 'times', 'while', 'until', 'try',
                           'on', 'error', 'return', 'continue', 'exit', 'set', 'copy', 'as']

    def format(self, code: str) -> str:
        """格式化 AppleScript 代码"""
        if not code or not code.strip():
            return code

        # 保护 token
        tm = TokenManager(prefix='AS')
        patterns = [
            (r'\(\*[\s\S]*?\*\)', 0),
            (r'--.*$', re.MULTILINE),
            (r'"(\\.|[^"\\])*"', 0),
        ]
        processed = tm.protect(code, patterns)

        # 预处理：处理 if-then 和 tell-to 结构
        processed = self._preprocess(processed)

        # 逐行格式化
        formatted_lines = self._format_lines(processed)

        # 恢复 token
        result = tm.restore('\n'.join(formatted_lines))

        # 后处理
        return self._post_process(result)

    def _preprocess(self, code: str) -> str:
        """预处理代码"""
        # 处理 if...then 结构
        code = re.sub(r'\bif\s+(.+?)\s+then\s+(.+)', r'if \1 then\n\2\nend if', code)

        # 处理 tell 结构
        code = re.sub(r'\btell\s+(.+?)\s+to\s+(.+)', r'tell \1\n\2\nend tell', code)

        # 处理多行语句，确保每个语句都在单独的行上
        code = re.sub(r';\s*', '\n', code)

        return code

    def _format_line(self, line: str) -> str:
        """格式化单行"""
        l = line.strip()
        if not l:
            return ''

        # 操作符空格
        operators = ['==', '!=', '<=', '>=', '&', '|', '+', '-', '*', '/', '=']
        l = self._format_operators(l, operators)

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

    def _format_lines(self, code: str) -> list:
        """格式化所有行并处理缩进"""
        lines = code.split('\n')
        formatted = []
        level = 0

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # 递减缩进
            if re.match(r'^(end if|end tell|else|on error)', trimmed):
                level = max(0, level - 1)

            formatted.append(self.INDENT * level + self._format_line(trimmed))

            # 递增缩进
            if re.match(r'^if\b.*\bthen$', trimmed):
                level += 1
            elif re.match(r'^tell\b', trimmed):
                level += 1

        return formatted

    def _post_process(self, code: str) -> str:
        """后处理"""
        code = re.sub(r'\n{3,}', '\n\n', code)
        return code.strip()


def format_code(code: str) -> str:
    """格式化 AppleScript 代码的便捷函数"""
    formatter = AppleScriptFormatter()
    return formatter.format(code)


def main(state):
    """Format or minify AppleScript text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("AppleScript code formatted")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error("Error formatting AppleScript: {}".format(str(e)))
        else:
            print("Error formatting AppleScript: {}".format(str(e)))
