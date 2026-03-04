#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format Go",
  "description": "格式化 Go 代码",
  "icon": "🐹",
  "tags": ["go","format"],
  "dependencies": [],
  "help": "格式化或压缩 Go 代码\n\n如果代码已格式化，将进行压缩。\n\n示例:\n输入:\nfunc main(){fmt.Println(\"Hello\")}\n\n输出:\nfunc main() {\n    fmt.Println(\"Hello\")\n}"
}"""

import re

CONFIG = {'INDENT': '    ', 'NEWLINE': '\n'}

KEYWORDS_WITH_SPACE = ['if', 'for', 'while', 'switch', 'case', 'default', 'defer', 'go', 'select', 'range']


class TokenManager:
    """Token manager for protecting comments and strings."""

    def __init__(self):
        self.placeholders = []

    def protect(self, code):
        """Protect comments and strings with placeholders."""
        def add_token(match):
            idx = len(self.placeholders)
            token_id = '__G_TK_{}__'.format(idx)
            self.placeholders.append({'id': token_id, 'content': match.group(0)})
            return token_id

        # Protect single-line comments
        code = re.sub(r'//.*$', add_token, code, flags=re.MULTILINE)
        # Protect multi-line comments
        code = re.sub(r'/\*[\s\S]*?\*/', add_token, code)
        # Protect double-quoted strings
        code = re.sub(r'"(\\.|[^"\\])*"', add_token, code)
        # Protect backtick strings
        code = re.sub(r'`[\s\S]*?`', add_token, code)

        return code

    def restore(self, code):
        """Restore protected tokens back to original content."""
        result = code
        for i in range(len(self.placeholders) - 1, -1, -1):
            result = result.replace(self.placeholders[i]['id'], self.placeholders[i]['content'])
        return result


def extract_package_and_imports(code):
    """Extract package declaration and import statements."""
    lines = code.split('\n')
    pkg_line = ''
    import_lines = []
    code_lines = []

    in_import = False
    import_block = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('package '):
            pkg_line = stripped
        elif stripped.startswith('import '):
            if stripped == 'import':
                in_import = True
                import_block.append(stripped)
            elif in_import and stripped == '}':
                import_block.append(stripped)
                import_lines.extend(import_block)
                import_block = []
                in_import = False
            elif in_import:
                import_block.append(line)
            else:
                import_lines.append(stripped)
        elif stripped:
            code_lines.append(line)

    return {'pkgLine': pkg_line, 'importLines': import_lines, 'codeBody': ' '.join(code_lines)}


def preprocess(code):
    """Preprocess Go code for formatting. Returns (processed_code, replacements_dict)."""
    # Store replacements for later restoration
    replacements = {}

    # Protect for loops with semicolons (only for keyword followed by condition with 2 semicolons)
    for_loops = []

    def save_for_loop(match):
        placeholder = '__G_PREPROCESS_{}__'.format(len(replacements))
        full_match = match.group(0)
        # Find the opening brace position
        brace_pos = full_match.find('{')
        if brace_pos == -1:
            return full_match
        # Extract condition part (between 'for ' and '{')
        condition = full_match[4:brace_pos].strip()  # Skip 'for '
        # Format condition with proper spacing around operators
        # First protect := and ++ and <-
        condition = condition.replace(':=', '___COLON_EQ___')
        condition = condition.replace('++', '___PLUS_PLUS___')
        condition = condition.replace('--', '___MINUS_MINUS___')
        # Add spacing around operators
        condition = re.sub(r'\s*;\s*', '; ', condition)
        condition = re.sub(r'([^\s])<([^\s])', r'\1 < \2', condition)
        condition = re.sub(r'([^\s])=([^\s])', r'\1 = \2', condition)
        # Restore protected operators with spacing
        condition = condition.replace('___COLON_EQ___', ' := ')
        condition = condition.replace('___PLUS_PLUS___', '++')
        condition = condition.replace('___MINUS_MINUS___', '--')
        # Clean up extra spaces
        condition = re.sub(r'\s+', ' ', condition).strip()
        replacements[placeholder] = 'for ' + condition
        return placeholder + ' {'

    # Match Go for loops: for followed by two semicolons and opening brace
    code = re.sub(r'\bfor\s+[^;{]+;[^;{]+;[^{]+\{', save_for_loop, code)

    # Protect if/switch statements with initialization (single semicolon before condition)
    if_statements = []

    def save_if_statement(match):
        placeholder = '__G_PREPROCESS_{}__'.format(len(replacements))
        full_match = match.group(0)
        # Find the opening brace position
        brace_pos = full_match.find('{')
        if brace_pos == -1:
            return full_match
        # Extract the keyword (if or switch)
        keyword_match = re.match(r'\s*(if|switch)\s+', full_match)
        if not keyword_match:
            return full_match
        keyword = keyword_match.group(1)
        # Extract condition part (between keyword and '{')
        condition = full_match[len(keyword_match.group(0)):brace_pos].strip()
        # Format condition with proper spacing
        condition = re.sub(r'\s*;\s*', '; ', condition)
        replacements[placeholder] = keyword + ' ' + condition
        return placeholder + ' {'

    # Match if/switch with semicolon: (if|switch) ... ; ... {
    code = re.sub(r'\b(if|switch)\s+[^;{]+;[^{]+\{', save_if_statement, code)

    # Handle braces
    code = code.replace('{', ' {\n')
    code = code.replace('}', '\n}\n')
    # Handle semicolons
    code = code.replace(';', ';\n')
    # Handle else statements
    code = re.sub(r'\}\s*else', '} else', code)
    code = re.sub(r'else\s*\{', 'else {', code)

    return code, replacements


def restore_preprocess(code, replacements):
    """Restore preprocess placeholders."""
    result = code
    for placeholder, content in replacements.items():
        result = result.replace(placeholder, content)
    return result


def process_structures(code):
    """Process struct and interface definitions."""
    def process_struct_or_interface(match):
        type_name = match.group(1)
        body_content = match.group(2)
        fields = [field.strip() for field in body_content.split(';') if field.strip()]
        indent = CONFIG['INDENT']
        fields_str = '\n'.join([indent + field for field in fields])
        return '{} {{\n{}\n}}'.format(type_name, fields_str)

    code = re.sub(r'(struct|interface)\s*\{([^}]*?)\}', process_struct_or_interface, code, flags=re.DOTALL)
    return code


def format_line(line):
    """Format a single line of Go code."""
    l = line.strip()
    if not l:
        return ''

    # 1. Handle keyword spacing
    keywords_pattern = r'\b({})\s*\('.format('|'.join(KEYWORDS_WITH_SPACE))
    l = re.sub(keywords_pattern, r'\1 (', l)

    # 2. Protect compound operators with placeholders
    l = re.sub(r':=', '___COLON_EQ___', l)
    l = re.sub(r'<-', '___LESS_EQ___', l)
    l = re.sub(r'\+\+', '___PLUS_PLUS___', l)
    l = re.sub(r'--', '___MINUS_MINUS___', l)

    # 3. Handle comparison operators
    for op in ['==', '!=', '>=', '<=']:
        regex = r'(?<!\s){}(?!\s)'.format(re.escape(op))
        l = re.sub(regex, ' {} '.format(op), l)

    # 4. Handle simple operators (but not compound ones)
    l = re.sub(r'(?<!\s)(?<!\+)(?<!:)(\+)(?!\+)(?!\s)', r' \1 ', l)
    l = re.sub(r'(?<!\s)(?<!-)(?<!<)(-)(?!\-)(?!\s)', r' \1 ', l)
    l = re.sub(r'(?<!\s)(?<!\*)(\*)(?!\*)(?!\s)', r' \1 ', l)
    l = re.sub(r'(?<!\s)(?<!/)(/)(?!/)(?!\s)', r' \1 ', l)
    l = re.sub(r'(?<!\s)(?<!%)(%)(?!%)(?!\s)', r' \1 ', l)
    l = re.sub(r'(?<!\s)(?<!:)(?<![=!<>])(=)(?![=<>])(?!\s)', r' \1 ', l)
    l = re.sub(r'(?<!\s)(?<![=!<>])(>)(?![=<>])(?!\s)', r' \1 ', l)
    l = re.sub(r'(?<!\s)(?<![=!<>])(<)(?![=<>-])(?!\s)', r' \1 ', l)

    # 5. Restore compound operators
    l = re.sub(r'___COLON_EQ___', ' := ', l)
    l = re.sub(r'___LESS_EQ___', ' <- ', l)
    l = re.sub(r'___PLUS_PLUS___', '++', l)
    l = re.sub(r'___MINUS_MINUS___', '--', l)

    # 6. Handle comma spacing
    l = re.sub(r',(?!\s)', ', ', l)

    # 7. Clean up duplicate spaces
    return re.sub(r'\s+', ' ', l)


def post_process(code):
    """Post-process the formatted Go code."""
    # Clean up extra blank lines
    code = re.sub(r'\n{3,}', '\n\n', code)

    # Clean up semicolons after struct fields
    code = re.sub(r'([a-zA-Z_][a-zA-Z0-9_]*\s+[a-zA-Z_][a-zA-Z0-9_]*);', r'\1', code)

    # Clean up extra spaces before braces
    code = re.sub(r'\s+\{', ' {', code)

    # Re-process indentation
    lines = code.split('\n')
    formatted_lines = []
    level = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            formatted_lines.append('')
            continue

        # Adjust indent level
        if stripped.startswith('}') or stripped.startswith(']'):
            level = max(0, level - 1)
        if stripped.startswith('else'):
            level = max(0, level - 1)

        formatted_lines.append(CONFIG['INDENT'] * level + stripped)

        # Increase indent level
        if stripped.endswith('{') or stripped.endswith('['):
            level += 1

    return '\n'.join(formatted_lines)


def format_code(code):
    """Format Go code."""
    if not code or not code.strip():
        return code

    # Extract package and imports
    data = extract_package_and_imports(code)
    pkg_line = data['pkgLine']
    import_lines = data['importLines']
    code_body = data['codeBody']

    # Preprocess first (before token protection)
    processed, preprocess_replacements = preprocess(code_body)

    # Process code body with token protection
    tokens = TokenManager()
    protected = tokens.protect(processed)
    protected = process_structures(protected)

    # Format code lines
    code_lines_processed = protected.split('\n')
    formatted_code = []
    level = 0

    for line in code_lines_processed:
        stripped = line.strip()
        if not stripped:
            continue

        # Adjust indent level
        if stripped.startswith('}') or stripped.startswith(']'):
            level = max(0, level - 1)
        if stripped.startswith('else'):
            level = max(0, level - 1)

        # Format current line
        formatted_line = format_line(stripped)
        formatted_code.append(CONFIG['INDENT'] * level + formatted_line)

        # Increase indent level
        if stripped.endswith('{') or stripped.endswith('['):
            level += 1

    # Build final result
    result = []
    if pkg_line:
        result.append(pkg_line)
    if import_lines:
        result.append('')  # Empty line after package
        result.extend(import_lines)
    if import_lines and formatted_code:
        result.append('')  # Empty line after imports
    result.extend(formatted_code)

    # Restore tokens first, then preprocess placeholders
    final_result = tokens.restore('\n'.join(result))
    final_result = restore_preprocess(final_result, preprocess_replacements)
    return post_process(final_result).strip() + CONFIG['NEWLINE']


def main(state):
    """Format or minify Go code."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("Go code formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))

def is_minified(text):
    """Check if Go code is minified."""
    text = text.strip()
    return not '\n' in text and ('func' in text or 'package' in text or 'import' in text)

def minify_code(code):
    """Minify Go code."""
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
    """Process Go code - format or minify based on input state."""
    if not text or not text.strip():
        return text

    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)
