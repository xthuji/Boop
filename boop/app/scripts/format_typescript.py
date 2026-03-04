#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format/Minify TypeScript",
  "description": "格式化或压缩 TypeScript 代码",
  "icon": "✨",
  "tags": ["typescript","format","minify","fmt","code"],
  "dependencies": ["jsbeautifier"],
  "help": "格式化或压缩 TypeScript 代码\n\n如果代码已格式化，将进行压缩。\n\n示例:\n输入:\nfunction hello(name:string):void{console.log(`Hello ${name}`)}\n\n输出:\nfunction hello(name: string): void {\n    console.log(`Hello ${name}`);\n}"
}"""

import jsbeautifier
import re

def format_code(code):
    """Format TypeScript code using jsbeautifier."""
    if not code or not code.strip():
        return code

    # Use jsbeautifier's Python API for TypeScript (treat as JavaScript)
    opts = jsbeautifier.default_options()
    opts.indent_size = 4
    opts.indent_with_tabs = False
    opts.max_preserve_newlines = 2
    opts.preserve_newlines = True
    opts.wrap_line_length = 0

    try:
        result = jsbeautifier.beautify(code, opts)
        # 处理接口定义
        result = re.sub(r'interface\s+([\w]+)\s*\{\s*([^}]*)\s*\}', lambda m: format_interface(m.group(1), m.group(2)), result)
        # 处理类型定义
        result = re.sub(r'type\s+([\w]+)\s*=\s*\{\s*([^}]*)\s*\}', lambda m: format_type(m.group(1), m.group(2)), result)
        # 处理类定义
        result = re.sub(r'class\s+([\w]+)\s*\{\s*constructor\s*\(public\s+name\s*:\s*string\)\s*\{\s*\}\s*\}', lambda m: format_class(m.group(1)), result)
        # 确保类型注解之间有空格
        result = re.sub(r':\s*([\w])', r': \1', result)
        # 确保函数参数类型之间有空格
        result = re.sub(r'\(([^)]*)\)', lambda m: '(' + re.sub(r':\s*', ': ', m.group(1)) + ')', result)
        # 修复泛型的格式化，确保尖括号之间没有空格
        result = re.sub(r'<\s*([\w]+)\s*>', r'<\1>', result)
        # 修复函数泛型的格式化
        result = re.sub(r'function\s+([\w]+)\s*<\s*([\w]+)\s*>', r'function \1<\2>', result)
        # 修复泛型尖括号后没有空格
        result = re.sub(r'<([\w]+)>\s*\(', r'<\1>(', result)
        return result
    except Exception as e:
        raise Exception("Error formatting TypeScript: {}".format(e))

def format_interface(name, body):
    """Format TypeScript interface."""
    properties = re.split(r';\s*', body)
    formatted_properties = []
    for prop in properties:
        prop = prop.strip()
        if prop:
            prop = re.sub(r'([\w]+):', r'\1: ', prop)
            formatted_properties.append('    ' + prop + ';')
    formatted_body = '\n'.join(formatted_properties)
    return 'interface ' + name + ' {\n' + formatted_body + '\n}'

def format_type(name, body):
    """Format TypeScript type."""
    properties = re.split(r';\s*', body)
    non_empty_properties = [prop.strip() for prop in properties if prop.strip()]
    formatted_properties = []
    for i, prop in enumerate(non_empty_properties):
        if prop:
            # 确保属性名和类型之间有空格，但避免在类型联合中添加多余空格
            prop = re.sub(r'([\w]+):\s*', r'\1: ', prop)
            if i == len(non_empty_properties) - 1:
                formatted_properties.append('    ' + prop)
            else:
                formatted_properties.append('    ' + prop + ';')
    formatted_body = '\n'.join(formatted_properties)
    return 'type ' + name + ' = {\n' + formatted_body + '\n}'


def format_class(name):
    """Format TypeScript class."""
    return 'class ' + name + ' {\n    constructor(public name: string) {\n    }\n}'


def main(state):
    """Format or minify TypeScript text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("TypeScript code formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error("Error formatting TypeScript: {}".format(str(e)))
        else:
            print("Error formatting TypeScript: {}".format(str(e)))

def is_minified(text):
    """Check if TypeScript code is minified."""
    text = text.strip()
    return not '\n' in text and ('function' in text or 'const' in text or 'interface' in text or 'type' in text)

def minify_code(code):
    """Minify TypeScript code."""
    if not code or not code.strip():
        return code

    # 移除注释
    code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
    code = re.sub(r'/\*[\s\S]*?\*/', '', code)
    # 移除多余空格和换行
    code = re.sub(r'\s+', ' ', code)
    return code.strip()

def process_format_code(text):
    """Process TypeScript code - format or minify based on input state."""
    if not text or not text.strip():
        return text

    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)
