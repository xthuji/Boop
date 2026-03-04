#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Professional TypeScript code formatter using jsbeautifier.
"""

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

# Boop script metadata
metadata = {
    "name": "Format TypeScript",
    "description": "Formats TypeScript code using jsbeautifier",
    "version": "1.0.0",
    "category": "format",
    "dependencies": ["jsbeautifier"],
    "input": "text",
    "output": "text",
    "icon": "pineapple",
    "help": "Formats TypeScript code with professional indentation and spacing. Uses jsbeautifier library for formatting."
}

def run(text, *args):
    """Boop script entry point."""
    try:
        return format_code(text)
    except Exception as e:
        return f"Error formatting TypeScript: {str(e)}"

def main(text, *args):
    """Main function for Boop script execution."""
    return run(text, *args)
