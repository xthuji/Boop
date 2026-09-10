#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format/Minify JavaScript",
  "description": "格式化或压缩 JavaScript 代码",
  "icon": "✨",
  "tags": ["javascript","format","minify","fmt","code"],
  "dependencies": [],
  "help": "格式化或压缩 JavaScript 代码\n\n如果代码已格式化，将进行压缩。\n\n示例:\n输入:\nfunction hello(){console.log(\"Hello\")}\n\n输出:\nfunction hello() {\n    console.log(\"Hello\");\n}"
}"""

import re

CONFIG = {'INDENT': '    ', 'NEWLINE': '\n'}


class TokenManager:
    """Token manager for protecting comments, strings, and template literals."""

    def __init__(self):
        self.placeholders = []

    def protect(self, code):
        """Protect comments, strings, and template literals with placeholders."""
        def add_token(match):
            token_id = '__JS_TK_{}__'.format(len(self.placeholders))
            self.placeholders.append({'id': token_id, 'content': match.group(0)})
            return token_id

        # Protect multi-line comments
        code = re.sub(r'/\*[\s\S]*?\*/', add_token, code)
        # Protect single-line comments
        code = re.sub(r'//.*$', add_token, code, flags=re.MULTILINE)
        # Protect template literals
        code = re.sub(r'`(?:\\.|[^\\`])*`', add_token, code)
        # Protect single-quoted strings
        code = re.sub(r"'(?:\\.|[^\\'])*'", add_token, code)
        # Protect double-quoted strings
        code = re.sub(r'"(?:\\.|[^\\"])*"', add_token, code)
        # Protect regex literals
        code = re.sub(r'/(?:\\.|[^/])+/[gimuy]*', add_token, code)

        return code

    def restore(self, code):
        """Restore protected tokens back to original content."""
        result = code
        for i in range(len(self.placeholders) - 1, -1, -1):
            result = result.replace(self.placeholders[i]['id'], self.placeholders[i]['content'])
        return result


def format_code(code):
    """Format JavaScript code."""
    if not code or not code.strip():
        return code

    tokens = TokenManager()
    processed = tokens.protect(code)

    # 1. Preprocessing: add spaces and newlines
    processed = processed.replace('{', ' {\n')
    processed = processed.replace('}', '\n}\n')
    processed = processed.replace(';', ';\n')
    processed = re.sub(r'\}\s*else', '} else', processed)
    processed = re.sub(r'else\s*\{', 'else {', processed)

    # 2. Split into lines
    lines = processed.split('\n')
    formatted = []
    level = 0

    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue

        # Adjust indent level for closing braces and keywords
        if re.match(r'^(\}|else|catch|finally)', trimmed):
            level = max(0, level - 1)

        # Format current line
        formatted_line = CONFIG['INDENT'] * level + trimmed

        # Handle spacing for keywords
        formatted_line = re.sub(r'\b(function|if|for|while|switch|catch|try|async)\s*\(', r'\1 (', formatted_line)
        formatted_line = re.sub(r'\)\s*\{', ') {', formatted_line)
        formatted_line = re.sub(r'\belse\s*\{', 'else {', formatted_line)
        formatted_line = re.sub(r'\s*=>\s*', ' => ', formatted_line)
        # Fix arrow function spacing
        formatted_line = re.sub(r'\s*=\s*>\s*', ' => ', formatted_line)

        # Handle spacing around equals sign (but not ==, ===, !=, !==, or =>)
        # Exclude arrow functions
        formatted_line = re.sub(r'([^=!<>])(=)(?!>)', r'\1 \2 ', formatted_line)
        formatted_line = re.sub(r'([^\s=])(=)(?!>)', r'\1 \2 ', formatted_line)

        # Handle spacing around operators (exclude comparison operators already handled)
        formatted_line = re.sub(r'([^\s])\+([^\s])', r'\1 + \2', formatted_line)
        formatted_line = re.sub(r'([^\s])\-([^\s])', r'\1 - \2', formatted_line)
        formatted_line = re.sub(r'([^\s])\*([^\s])', r'\1 * \2', formatted_line)
        formatted_line = re.sub(r'([^\s])/([^\s])', r'\1 / \2', formatted_line)
        formatted_line = re.sub(r'([^\s])%([^\s])', r'\1 % \2', formatted_line)
        formatted_line = re.sub(r'([^\s])&&([^\s])', r'\1 && \2', formatted_line)
        formatted_line = re.sub(r'([^\s])\|\|([^\s])', r'\1 || \2', formatted_line)

        # Handle comparison operators
        formatted_line = re.sub(r'([^\s])(==|===|!=|!==|>=|<=)([^\s])', r'\1 \2 \3', formatted_line)
        formatted_line = re.sub(r'([^\s])([<>])([^\s])', r'\1 \2 \3', formatted_line)

        # Handle spacing around commas and colons
        formatted_line = re.sub(r',(?!\s)', ', ', formatted_line)
        formatted_line = re.sub(r':(?!\s)', ': ', formatted_line)

        formatted.append(formatted_line)

        # Adjust indent level for next line
        if trimmed.endswith('{'):
            level += 1

    # 3. Post-processing
    result = tokens.restore('\n'.join(formatted))

    # Fix import statements - handle already restored content
    def fix_import(match):
        content = match.group(1)
        items = ', '.join([item.strip() for item in content.split(',')])
        return 'import {{ {} }} from '.format(items)
    result = re.sub(r'import\s*\{\s*([^}]+)\s*\}\s*from\s*', fix_import, result)

    # Fix destructuring assignments (object) - add space after =
    def fix_destruct_obj(match):
        decl = match.group(1)
        content = match.group(2)
        items = ', '.join([item.strip() for item in content.split(',')])
        return '{} {{ {} }} = '.format(decl, items)
    result = re.sub(r'\b(const|let|var)\s*\{\s*([^}]+)\s*\}\s*=', fix_destruct_obj, result)

    # Fix destructuring assignments (array)
    def fix_destruct_arr(match):
        decl = match.group(1)
        content = match.group(2)
        items = ', '.join([item.strip() for item in content.split(',')])
        return '{} [{}] ='.format(decl, items)
    result = re.sub(r'\b(const|let|var)\s*\[\s*([^\]]+)\s*\]\s*=', fix_destruct_arr, result)

    # Fix object literals
    def fix_object_literal(match):
        decl = match.group(1)
        var_name = match.group(2)
        content = match.group(3)
        items = [item.strip() for item in content.split(',') if item.strip()]
        if len(items) <= 1:
            return '{} {} = {{ {} }}'.format(decl, var_name, ', '.join(items))
        inner = '\n'.join([CONFIG['INDENT'] + item + (',' if i < len(items) - 1 else '') for i, item in enumerate(items)])
        return '{} {} = {{\n{}\n}}'.format(decl, var_name, inner)
    result = re.sub(r'(const|let|var)\s+(\w+)\s*=\s*\{([^}]+)\}', fix_object_literal, result)

    # Fix arrow function spacing
    result = re.sub(r'\s*=\s*=>\s*', ' => ', result)
    # Additional fix for arrow function spacing
    result = re.sub(r'\s*=>\s*', ' => ', result)

    # Fix template string variable spacing
    result = re.sub(r'\$\{\s*([^}]+)\s*\}', r'${\1}', result)

    # Fix semicolon position
    result = re.sub(r'\}\s*\n\s*;', '};', result)

    # Fix else spacing
    result = re.sub(r'\}\s+else', '} else', result)

    # Fix catch block spacing
    result = re.sub(r'\}\s*\n\s*catch', '} catch', result)
    result = re.sub(r'\}\s*catch\s*\((\w+)\)\s*\{', r'} catch (\1) {', result)
    result = re.sub(r'catch\s*\((\w+)\)\s*\{\s*\n', r'catch (\1) {\n    ', result)

    # Ensure console.error statements end with semicolon
    result = re.sub(r'console\.error\((\w+)\)\s*\n', r'console.error(\1);\n', result)
    result = re.sub(r'console\.error\((\w+)\);\s*\n\s*\}', r'console.error(\1);\n    }', result)

    # Clean up extra blank lines
    result = re.sub(r'\n{3,}', '\n\n', result)

    return result.strip()


def main(state):
    """Format or minify JavaScript text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("JavaScript code formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(f"Error formatting JavaScript: {str(e)}")
        else:
            print(f"Error formatting JavaScript: {str(e)}")

def is_minified(text):
    """Check if JavaScript code is minified."""
    text = text.strip()
    return not '\n' in text

def minify_code(code):
    """Minify JavaScript code."""
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
    """Process JavaScript code - format or minify based on input state."""
    if not text or not text.strip():
        return text

    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)
