#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Convert JSON Code String",
  "description": "在 JSON/JS/Python/Lua/Php 代码之间转换",
  "icon": "💊",
  "tags": ["convert","json","code","js","javascript","py","python","lua","php"],
  "help": "在 JSON/JS/Python/Lua/Php 代码之间转换\n\n首行参数格式:\n1. output_format (仅指定输出格式)\n2. input_format:output_format (指定输入和输出格式)\n\n支持的格式:\n- json: JSON 格式\n- js/javascript: JavaScript 格式\n- py/python: Python 格式\n- lua: Lua 格式\n- php: PHP 格式\n\n示例 1 (JSON 转 JavaScript):\n输入:\njavascript\n{\"name\": \"John\", \"age\": 30}\n\n输出:\n{\n  \"name\": \"John\",\n  \"age\": 30\n};\n\n示例 2 (JavaScript 转 Python):\n输入:\njavascript:python\n{name: 'John', age: 30}\n\n输出:\n{'name': 'John', 'age': 30}"
}
'''

import json
import re

def run(text):
    """
    在JSON/JS/Python/Lua/Php 代码之间转换
    """
    lines = text.split('\n')
    output_format = 'javascript'
    text_to_convert = text
    
    # 处理首行自定义参数
    format_map = {
        'json': 'json',
        'js': 'javascript',
        'javascript': 'javascript',
        'py': 'python',
        'python': 'python',
        'lua': 'lua',
        'php': 'php'
    }
    
    if lines:
        first_line = lines[0].strip()
        parts = first_line.split(':')
        
        if len(parts) == 2 and parts[0] in format_map and parts[1] in format_map:
            output_format = format_map[parts[1]]
            text_to_convert = '\n'.join(lines[1:])
        elif first_line in format_map:
            output_format = format_map[first_line]
            text_to_convert = '\n'.join(lines[1:])
    
    try:
        # 尝试解析输入数据
        data = parse_input(text_to_convert)
        
        # 根据目标格式转换
        if output_format == 'json':
            return json.dumps(data, ensure_ascii=False, indent=4)
        elif output_format == 'javascript':
            return format_to_javascript(data)
        elif output_format == 'python':
            return format_to_python(data)
        elif output_format == 'lua':
            return format_to_lua(data)
        elif output_format == 'php':
            return format_to_php(data)
        else:
            return text
    except Exception as e:
        return text

def parse_input(text):
    """
    解析输入数据
    """
    # 尝试解析为JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # 尝试解析为JavaScript对象或列表
    try:
        # 检查是否是列表
        if text.strip().startswith('[') and text.strip().endswith(']'):
            # 修复JavaScript列表格式
            json_str = text.strip()
            # 替换单引号为双引号
            json_str = re.sub(r"'(\w+)'\s*:", r'"\1":', json_str)
            # 替换没有引号的键
            json_str = re.sub(r"(\w+)\s*:", r'"\1":', json_str)
            return json.loads(json_str)
        # 尝试解析为对象
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            # 修复JavaScript对象格式
            json_str = text[start:end+1]
            # 替换单引号为双引号
            json_str = re.sub(r"'(\w+)'\s*:", r'"\1":', json_str)
            # 替换没有引号的键
            json_str = re.sub(r"(\w+)\s*:", r'"\1":', json_str)
            return json.loads(json_str)
    except Exception:
        pass
    
    # 尝试解析为Python字典
    try:
        # 简单处理：查找大括号包围的内容
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            # 修复Python字典格式
            py_str = text[start:end+1]
            # 替换单引号为双引号
            py_str = re.sub(r"'(\w+)'\s*:", r'"\1":', py_str)
            return json.loads(py_str)
    except Exception:
        pass
    
    # 尝试解析为Lua表
    try:
        # 简单处理：查找大括号包围的内容
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            # 修复Lua表格式
            lua_str = text[start:end+1]
            # 替换等号为冒号
            lua_str = re.sub(r"(\w+)\s*=", r'"\1":', lua_str)
            return json.loads(lua_str)
    except Exception:
        pass
    
    # 尝试解析为PHP数组
    try:
        # 简单处理：查找方括号包围的内容
        start = text.find('[')
        end = text.rfind(']')
        if start != -1 and end != -1:
            # 修复PHP数组格式
            php_str = text[start:end+1]
            # 替换箭头为冒号
            php_str = re.sub(r"(\w+)\s*=>", r'"\1":', php_str)
            return json.loads(php_str)
    except Exception:
        pass
    
    # 默认为空对象
    return {}

def format_to_javascript(data):
    """
    转换为JavaScript对象格式
    """
    def format_value(value, level=0):
        indent = '    ' * level
        next_indent = '    ' * (level + 1)
        
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
        elif isinstance(value, list):
            if not value:
                return '[]'
            items = [next_indent + format_value(item, level + 1) for item in value]
            return '[' + '\n' + ',\n'.join(items) + '\n' + indent + ']'
        elif isinstance(value, dict):
            if not value:
                return '{}'
            items = [next_indent + k + ': ' + format_value(v, level + 1) for k, v in value.items()]
            return '{' + '\n' + ',\n'.join(items) + '\n' + indent + '}'
        else:
            return str(value)
    
    return format_value(data)

def format_to_python(data):
    """
    转换为Python字典格式
    """
    def format_value(value, level=0):
        indent = '    ' * level
        next_indent = '    ' * (level + 1)
        
        if value is None:
            return 'None'
        elif isinstance(value, bool):
            return 'True' if value else 'False'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return "'" + value.replace("'", "\\'") + "'"
        elif isinstance(value, list):
            if not value:
                return '[]'
            items = [next_indent + format_value(item, level + 1) for item in value]
            return '[' + '\n' + ',\n'.join(items) + '\n' + indent + ']'
        elif isinstance(value, dict):
            if not value:
                return '{}'
            items = [next_indent + format_value(k) + ': ' + format_value(v, level + 1) for k, v in value.items()]
            return '{' + '\n' + ',\n'.join(items) + '\n' + indent + '}'
        else:
            return str(value)
    
    return format_value(data)

def format_to_lua(data):
    """
    转换为Lua表格式
    """
    def format_value(value, level=0):
        indent = '    ' * level
        next_indent = '    ' * (level + 1)
        
        if value is None:
            return 'nil'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return '"' + value.replace('"', '\\"') + '"'
        elif isinstance(value, list):
            if not value:
                return '{}'
            items = [next_indent + format_value(item, level + 1) for item in value]
            return '{' + '\n' + ',\n'.join(items) + '\n' + indent + '}'
        elif isinstance(value, dict):
            if not value:
                return '{}'
            items = [next_indent + k + ' = ' + format_value(v, level + 1) for k, v in value.items()]
            return '{' + '\n' + ',\n'.join(items) + '\n' + indent + '}'
        else:
            return str(value)
    
    return format_value(data)

def format_to_php(data):
    """
    转换为PHP数组格式
    """
    def format_value(value, level=0):
        indent = '    ' * level
        next_indent = '    ' * (level + 1)
        
        if value is None:
            return 'null'
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return "'" + value.replace("'", "\\'") + "'"
        elif isinstance(value, list):
            if not value:
                return '[]'
            items = [next_indent + format_value(item, level + 1) for item in value]
            return '[' + '\n' + ',\n'.join(items) + '\n' + indent + ']'
        elif isinstance(value, dict):
            if not value:
                return '[]'
            items = [next_indent + format_value(k) + ' => ' + format_value(v, level + 1) for k, v in value.items()]
            return '[' + '\n' + ',\n'.join(items) + '\n' + indent + ']'
        else:
            return str(value)
    
    # 对于列表数据，确保输出嵌套数组格式
    if isinstance(data, list):
        # 检查列表中的元素是否都是字典
        all_dicts = all(isinstance(item, dict) for item in data)
        if all_dicts:
            # 对于包含字典的列表，每个字典都包装在数组中
            items = []
            indent = '    '
            next_indent = '        '
            for item in data:
                dict_items = [next_indent + format_value(k) + ' => ' + format_value(v, 2) for k, v in item.items()]
                dict_str = '[' + '\n' + ',\n'.join(dict_items) + '\n' + indent + ']'
                items.append(indent + dict_str)
            return '[' + '\n' + ',\n'.join(items) + '\n' + '];'
    
    # 对于非列表数据，直接返回
    return format_value(data) + ';'

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("JSON/JS/Python/Lua/Php 代码转换")
