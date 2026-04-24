#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format Lua",
  "description": "格式化 Lua 代码",
  "icon": "✨",
  "tags": ["lua","format","fmt","code"],
  "dependencies": [],
  "help": "格式化 Lua 代码\n\n示例:\n输入:\nfunction hello()print(\"Hello\")end\n\n输出:\nfunction hello()\n    print(\"Hello\")\nend"
}"""

import re

CONFIG = {'INDENT': '    ', 'NEWLINE': '\n'}

KEYWORDS_WITH_SPACE = ['if', 'for', 'while', 'repeat', 'function', 'local', 'return', 'break', 'continue', 'and', 'or', 'not', 'in']


class TokenManager:
    """Token manager for protecting comments and strings."""

    def __init__(self):
        self.placeholders = []

    def protect(self, code):
        """Protect comments and strings with placeholders."""
        result = ''
        i = 0
        n = len(code)

        while i < n:
            char = code[i]

            # Handle long comments --[[
            if char == '-' and i + 1 < n and code[i + 1] == '-' and i + 2 < n and code[i + 2] == '[' and i + 3 < n and code[i + 3] == '[':
                j = i + 4
                while j < n and not (code[j] == ']' and j + 1 < n and code[j + 1] == ']'):
                    j += 1
                if j + 1 < n:
                    j += 2
                comment = code[i:j]
                token_id = self._add_token(comment)
                result += token_id
                i = j
            # Handle single-line comments --
            elif char == '-' and i + 1 < n and code[i + 1] == '-':
                j = i + 2
                while j < n and code[j] != '\n':
                    j += 1
                comment = code[i:j]
                token_id = self._add_token(comment)
                result += token_id
                i = j
            # Handle long strings [[
            elif char == '[' and i + 1 < n and code[i + 1] == '[':
                j = i + 2
                while j < n and not (code[j] == ']' and j + 1 < n and code[j + 1] == ']'):
                    j += 1
                if j + 1 < n:
                    j += 2
                string = code[i:j]
                token_id = self._add_token(string)
                result += token_id
                i = j
            # Handle single-quoted strings
            elif char == "'":
                j = i + 1
                while j < n and not (code[j] == "'" and code[j - 1] != '\\'):
                    j += 1
                if j < n:
                    j += 1
                string = code[i:j]
                token_id = self._add_token(string)
                result += token_id
                i = j
            # Handle double-quoted strings
            elif char == '"':
                j = i + 1
                while j < n and not (code[j] == '"' and code[j - 1] != '\\'):
                    j += 1
                if j < n:
                    j += 1
                string = code[i:j]
                token_id = self._add_token(string)
                result += token_id
                i = j
            else:
                result += char
                i += 1

        return result

    def _add_token(self, content):
        """Add a token to placeholders list."""
        idx = len(self.placeholders)
        token_id = '__LUA_TK_{}__'.format(idx)
        self.placeholders.append({'id': token_id, 'content': content})
        return token_id

    def restore(self, code):
        """Restore protected tokens back to original content."""
        result = code
        for i in range(len(self.placeholders) - 1, -1, -1):
            result = result.replace(self.placeholders[i]['id'], self.placeholders[i]['content'])
        return result


def format_code(code):
    """Format Lua code."""
    if not code or not code.strip():
        return code

    tokens = TokenManager()
    processed = tokens.protect(code)

    # Preprocessing: split control structures to new lines
    # Handle then: move content after then to next line
    processed = re.sub(r'\b(then)\s+(.+)', r'\1\n\2', processed)
    processed = re.sub(r'\b(do)\s+(.+)', r'\1\n\2', processed)
    # Handle control structure keywords
    processed = re.sub(r'\b(do|then)\s*\n?', r'\1\n', processed)
    # Handle elseif - keep condition on same line (must come before else handling)
    processed = re.sub(r'\b(elseif)\s+(.+?)\s+then', r'\n\1 \2 then\n', processed)
    # Handle else - use word boundary to avoid matching elseif
    processed = re.sub(r'\b(else)\b\s*\n?', r'\n\1\n', processed)
    # Handle until - keep condition on same line
    processed = re.sub(r'\b(until)\s+(.+)', r'\n\1 \2', processed)
    processed = re.sub(r'\bend\s*\n?', r'\nend\n', processed)

    lines = processed.split('\n')
    formatted_lines = []
    level = 0

    for line_idx, line in enumerate(lines):
        line = line.strip()

        # Skip empty lines
        if not line:
            continue

        # Decrease indent for end/until only
        if re.match(r'^(end|until)$', line):
            level = max(0, level - 1)

        # Operator and spacing handling
        line = re.sub(r'([^\s])(==|~=|<=|>=|\.\.)([^\s])', r'\1 \2 \3', line)
        line = re.sub(r'([^\s])(=|[+\-*/%])([^\s])', r'\1 \2 \3', line)
        line = re.sub(r'([^\s])([<>])([^\s])', r'\1 \2 \3', line)
        line = re.sub(r',(?!\s)', r', ', line)
        # Handle keyword spacing
        for kw in KEYWORDS_WITH_SPACE:
            pattern = r'\b(' + re.escape(kw) + r')\s*(?=[\(\{])'
            line = re.sub(pattern, r'\1 ', line)
        line = re.sub(r'\b(if|for|while|repeat)\s*(?=[\w])', r'\1 ', line)
        line = re.sub(r'\s{2,}', r' ', line)

        # Handle table structure multi-line formatting
        if '{' in line and '}' in line and line.index('{') < line.index('}'):
            content = line[line.index('{') + 1:line.rindex('}')].strip()
            if ',' in content or '=' in content:
                parts = line.split('{')
                before = parts[0].strip()
                inside = parts[1][:parts[1].rindex('}')].strip()

                formatted_lines.append(CONFIG['INDENT'] * level + before + ' {')

                elements = [elem.strip() for elem in inside.split(',') if elem.strip()]
                for i, elem in enumerate(elements):
                    if i < len(elements) - 1:
                        formatted_lines.append(CONFIG['INDENT'] * (level + 1) + elem + ',')
                    else:
                        formatted_lines.append(CONFIG['INDENT'] * (level + 1) + elem)

                formatted_lines.append(CONFIG['INDENT'] * level + '}')

                # Check if indent should be increased
                if re.match(r'^(function|local function|do|then|repeat)$', line) or \
                   (re.match(r'^(if|for|while|repeat)\b', line) and ('then' in line or 'do' in line)):
                    level += 1
                continue

        # Handle elseif/else - output at one level less than current (same as original if)
        if re.match(r'^(elseif|else)\b', line):
            formatted_lines.append(CONFIG['INDENT'] * max(0, level - 1) + line)
        else:
            formatted_lines.append(CONFIG['INDENT'] * level + line)

        # Increase indent for control structures
        # Note: elseif/else do NOT increase indent as they are part of the same block
        if re.match(r'^(function|local function)\b', line):
            level += 1
        elif re.match(r'^(do|then|repeat)$', line) or line.endswith('{'):
            level += 1
        elif re.match(r'^(if|for|while|repeat)\b', line):
            if 'then' in line or 'do' in line:
                level += 1

    result = '\n'.join(formatted_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    # Restore protected strings and comments
    result = tokens.restore(result)
    return result.strip()


def main(state):
    """Format or minify Lua text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Lua code formatted")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error("Error formatting Lua: {}".format(str(e)))
        else:
            print("Error formatting Lua: {}".format(str(e)))
