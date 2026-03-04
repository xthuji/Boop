#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional XML code formatter and minifier.
Optimized with pure Python implementation from Boop FormatXML.js.
"""

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

# Boop script metadata
metadata = {
    "name": "Format XML",
    "description": "Formats XML code with proper indentation and spacing",
    "version": "1.0.0",
    "category": "format",
    "dependencies": [],
    "input": "text",
    "output": "text",
    "icon": "pineapple",
    "help": "Formats XML code with professional indentation and spacing. Handles comments, CDATA sections, and processing instructions."
}

def run(text, *args):
    """Boop script entry point."""
    try:
        return format_code(text)
    except Exception as e:
        return f"Error formatting XML: {str(e)}"

def main(text, *args):
    """Main function for Boop script execution."""
    return run(text, *args)
