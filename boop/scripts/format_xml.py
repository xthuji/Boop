#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format/Minify XML",
  "description": "格式化或压缩 XML 文档",
  "icon": "✨",
  "tags": ["xml","format","minify","fmt","code"],
  "dependencies": [],
  "help": "格式化或压缩 XML 文档\n\n如果文档已格式化，将进行压缩。\n\n示例:\n输入:\n<root><child>text</child></root>\n\n输出:\n<root>\n    <child>text</child>\n</root>"
}"""

import re

CONFIG = {'INDENT': '    ', 'NEWLINE': '\n'}


class TokenManager:
    """Token manager for protecting comments and strings."""

    def __init__(self):
        self.placeholders = []

    def protect(self, code):
        """Protect comments and strings with placeholders."""
        def add_token(match):
            token_id = '__XML_TK_{}__'.format(len(self.placeholders))
            self.placeholders.append({'id': token_id, 'content': match.group(0)})
            return token_id

        # Protect XML comments
        code = re.sub(r'<!--[\s\S]*?-->', add_token, code)
        # Protect CDATA sections
        code = re.sub(r'<!\[CDATA\[[\s\S]*?\]\]>', add_token, code)
        # Protect DOCTYPE
        code = re.sub(r'<!DOCTYPE[^>]*>', add_token, code)
        # Protect XML declaration
        code = re.sub(r'<\?xml[^>]*\?>', add_token, code)
        # Protect processing instructions
        code = re.sub(r'<\?[^>]*\?>', add_token, code)

        return code

    def restore(self, code):
        """Restore protected tokens back to original content."""
        result = code
        for i in range(len(self.placeholders) - 1, -1, -1):
            result = result.replace(self.placeholders[i]['id'], self.placeholders[i]['content'])
        return result


def format_code(code):
    """Format XML code."""
    if not code or not code.strip():
        return code

    tokens = TokenManager()
    processed = tokens.protect(code)

    # Add newlines around tags
    processed = re.sub(r'>\s*<', '>\n<', processed)

    # Split into lines
    lines = processed.split('\n')
    formatted = []
    level = 0

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # Check for closing tags - decrease indent first
        if re.match(r'^</', line):
            level = max(0, level - 1)

        # Check for self-closing tags - no indent change
        if re.match(r'^<[^>]+/>$', line):
            formatted.append(CONFIG['INDENT'] * level + line)
            continue

        # Check for opening tags (not closing, not processing instruction)
        if re.match(r'^<[^/!?][^>]*>$', line):
            formatted.append(CONFIG['INDENT'] * level + line)
            level += 1
            continue

        # Check for closing tags
        if re.match(r'^</', line):
            formatted.append(CONFIG['INDENT'] * level + line)
            continue

        # Check for processing instructions and declarations
        if re.match(r'^<\?', line):
            formatted.append(CONFIG['INDENT'] * level + line)
            continue

        # Default: add current indent
        formatted.append(CONFIG['INDENT'] * level + line)

    result = tokens.restore('\n'.join(formatted))
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip() + CONFIG['NEWLINE']


def main(state):
    """Format or minify XML text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("XML code formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error("Error formatting XML: {}".format(str(e)))
        else:
            print("Error formatting XML: {}".format(str(e)))

def is_minified(text):
    """Check if XML is minified."""
    return not '\n' in text and re.search(r'<[^>]+>', text)

def minify_code(text):
    """Minify XML."""
    if not text or not text.strip():
        return text

    # 移除注释
    text = re.sub(r'<!--[\s\S]*?-->', '', text)
    # 移除多余空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def process_format_code(text):
    """Process XML text - format or minify based on input state."""
    if not text or not text.strip():
        return text

    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)
