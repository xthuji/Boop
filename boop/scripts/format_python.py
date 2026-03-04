#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format Python",
  "description": "Professional Python code formatter and minifier.",
  "icon": "pineapple",
  "tags": ["python", "format", "minify"],
  "help": "Format or minify Python code with proper indentation and spacing.\n\nExample:\nInput:\ndef hello():print(\"Hello\")\n\nOutput:\ndef hello():\n    print(\"Hello\")\n\nIf the code is already formatted, it will be minified."
}
"""

import re

CONFIG = {'INDENT': '    ', 'NEWLINE': '\n'}


class TokenManager:
    """Token manager for protecting strings, comments, and docstrings."""
    
    def __init__(self):
        self.tokens = []
    
    def protect(self, code):
        """Protect strings, docstrings, and comments with placeholders."""
        def placeholder(match):
            token_id = '___PY_TOK_{}___'.format(len(self.tokens))
            self.tokens.append(match.group(0) if isinstance(match, re.Match) else match)
            return token_id
        
        # Protect triple-quoted strings (docstrings) first
        processed = re.sub(r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\')', placeholder, code)
        # Protect regular strings (including f/r/b/u prefixed)
        processed = re.sub(r'[furb]?(?:"(\\.|[^"\\])*"|\'(\\.|[^\'\\])*\')', placeholder, processed)
        # Protect comments
        processed = re.sub(r'#.*', placeholder, processed)
        
        return processed
    
    def restore(self, code):
        """Restore protected tokens back to original content."""
        result = code
        for i in range(len(self.tokens) - 1, -1, -1):
            result = result.replace('___PY_TOK_{}___'.format(i), self.tokens[i])
        return result


def format_expression(line):
    """Format a single line of Python expression."""
    l = line.strip()
    if not l:
        return ''
    
    # 1. Handle async/await keywords
    l = re.sub(r'\b(async|await)\s+', r'\1 ', l)
    
    # 2. Add spaces around operators
    operators = ['==', '!=', '<=', '>=', '//', r'\+=', '-=', r'\*=', '/=', '%=', r'\+', '-', r'\*', '/', '%', '>', '<']
    op_regex = r'([^\s!<>])({})([^\s!<>])'.format('|'.join(operators))
    l = re.sub(op_regex, r'\1 \2 \3', l)
    
    # 3. Handle equals sign (distinguish assignment from default args)
    l = re.sub(r'([^!<>=])=([^!<>=])', r'\1 = \2', l)
    
    # Fix default parameters: (a = None) -> (a=None)
    def fix_default_param(match):
        return match.group(1) + '=' + match.group(2)
    l = re.sub(r'(\([^()]*?)\s=\s([^()]*?\))', fix_default_param, l)
    
    # 4. Normalize commas and colons
    l = re.sub(r',(?!\s)', ', ', l)
    l = re.sub(r'\s{2,}', ' ', l)
    l = re.sub(r'\s+:', ':', l)
    
    # 5. Fix type annotation spacing
    l = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*):([^\s])', r'\1: \2', l)
    
    # 6. Fix return type annotation arrows
    l = re.sub(r'-\s*>\s*', ' -> ', l)
    l = re.sub(r'\s*->\s*', ' -> ', l)
    
    return l


def process_imports(lines):
    """Sort and organize import statements."""
    imports = []
    others = []
    
    for line in lines:
        trimmed = line.strip()
        if trimmed.startswith('import ') or trimmed.startswith('from '):
            imports.append(trimmed)
        elif trimmed:
            others.append(trimmed)
    
    # Sort imports alphabetically
    imports.sort()
    return {'imports': imports, 'others': others}


def format_code(code):
    """Format Python code."""
    if not code or not code.strip():
        return code
    
    tokens = TokenManager()
    protected = tokens.protect(code)
    
    # Process imports
    import_data = process_imports(protected.split('\n'))
    
    level = 0
    formatted = []
    
    # Add import statements
    if import_data['imports']:
        for imp in import_data['imports']:
            formatted.append(imp)
        formatted.append('')  # Empty line after imports
    
    # Process other code lines
    for i, line in enumerate(import_data['others']):
        trimmed = line.strip()
        if not trimmed:
            continue
        
        # 1. Check if current line is a keyword that should decrease indent
        is_deindent = re.match(r'^(elif|else|except|finally)\b', trimmed)
        if is_deindent:
            level = max(0, level - 1)
        
        # 2. Format and apply current indent
        content = format_expression(trimmed)
        formatted.append(CONFIG['INDENT'] * level + content)
        
        # 3. Increase indent for lines ending with colon
        if trimmed.endswith(':'):
            level += 1
    
    result = tokens.restore('\n'.join(formatted))
    return result.strip() + CONFIG['NEWLINE']


def main(state):
    """Format or minify Python text."""
    if not state.text or not state.text.strip():
        return
    
    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Python code formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error("Error formatting Python: {}".format(str(e)))
        else:
            print("Error formatting Python: {}".format(str(e)))

def is_minified(text):
    """Check if Python code is minified."""
    text = text.strip()
    return not '\n' in text and ('def' in text or 'class' in text or 'import' in text)

def minify_code(code):
    """Minify Python code."""
    if not code or not code.strip():
        return code
    
    # 移除注释
    code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'"""[\s\S]*?"""', '', code, flags=re.DOTALL)
    code = re.sub(r"'''[\s\S]*?'''", '', code, flags=re.DOTALL)
    # 移除多余空格和换行
    code = re.sub(r'\s+', ' ', code)
    # 移除行尾分号
    code = re.sub(r';$', '', code)
    return code.strip()

def process_format_code(text):
    """Process Python code - format or minify based on input state."""
    if not text or not text.strip():
        return text
    
    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)


