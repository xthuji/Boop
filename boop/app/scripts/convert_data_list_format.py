#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Convert Data List Format",
  "description": "在列表格式 json/xml/yaml/csv/tsv/sql/md/html 之间转换",
  "icon": "📊",
  "tags": ["convert","data","list","json","xml","yaml","csv","tsv","sql","md","html"],
  "help": "在列表格式 json/xml/yaml/csv/tsv/sql/md/html 之间转换 (减号和星号格式)\n\n示例:\n输入:\n- item1\n- item2\n- item3\n\n输出:\n* item1\n* item2\n* item3"
}
'''

import json
import csv
import io
import re

def run(text):
    """
    在列表格式 json/xml/yaml/csv/tsv/sql/md/html 之间转换
    """
    lines = text.split('\n')
    target_format = 'json'
    table_name = 'table_name'
    multiline = True
    headerless = False
    text_to_convert = text
    
    # 处理首行自定义参数
    valid_formats = ['json', 'csv', 'xml', 'yaml', 'tabtext', 'tsv', 'sql', 'html', 'markdown', 'md']
    
    if lines:
        first_line = lines[0].strip()
        config_parts = first_line.split(':')
        
        if config_parts and config_parts[0]:
            format = config_parts[0].lower()
            if format in valid_formats:
                # 映射格式
                if format == 'tsv':
                    target_format = 'tabtext'
                elif format == 'md':
                    target_format = 'markdown'
                else:
                    target_format = format
                
                # 处理第二个参数
                if len(config_parts) >= 2 and config_parts[1]:
                    second_part = config_parts[1].strip().lower()
                    if second_part == 'headerless':
                        headerless = True
                    else:
                        table_name = config_parts[1].strip()
                
                # 处理第三个参数
                if len(config_parts) >= 3 and config_parts[2]:
                    third_part = config_parts[2].strip().lower()
                    if third_part == 'headerless':
                        headerless = True
                    else:
                        multiline = third_part == 'true'
                
                # 跳过配置行
                text_to_convert = '\n'.join(lines[1:]).strip()
    
    # 解析输入数据
    data = parse_input_auto(text_to_convert, headerless)
    
    if not data:
        return text
    
    # 根据目标格式转换
    if target_format == 'json':
        return format_to_json(data)
    elif target_format == 'csv':
        return format_to_csv(data, headerless)
    elif target_format == 'xml':
        return format_to_xml(data)
    elif target_format == 'yaml':
        return format_to_yaml(data)
    elif target_format == 'tabtext':
        return format_to_tabtext(data, headerless)
    elif target_format == 'sql':
        return format_to_sql_insert(data, table_name, multiline)
    elif target_format == 'html':
        return format_to_html(data)
    elif target_format == 'markdown':
        return format_to_markdown_table(data)
    else:
        return text

def parse_input_auto(input_str, headerless=False):
    """
    自动检测并解析输入格式
    """
    s = input_str.strip()
    if not s:
        return []
    
    # 尝试解析为 JSON
    if s.startswith('[') or s.startswith('{'):
        try:
            data = json.loads(s)
            return data if isinstance(data, list) else [data]
        except Exception:
            pass
    
    # 尝试解析为 SQL INSERT
    if re.match(r'^INSERT\s+INTO', s, re.IGNORECASE):
        return parse_sql_insert(s)
    
    # 尝试解析为 HTML 列表
    if s.startswith('<') and ('<ul>' in s or '<ol>' in s):
        return parse_html_list(s)
    
    # 尝试解析为 XML
    if s.startswith('<'):
        return parse_xml(s)
    
    # 尝试解析为 YAML
    if ':' in s and ('\n' in s or '\r\n' in s):
        return parse_yaml(s)
    
    # 尝试解析为 TSV
    if '\t' in s:
        return parse_csv(s, '\t', headerless)
    
    # 尝试解析为 CSV
    if ',' in s:
        return parse_csv(s, ',', headerless)
    
    # 默认为简单列表
    return [{'value': s}]

def parse_sql_insert(sql_str):
    """
    解析 SQL INSERT 语句
    """
    result = []
    insert_regex = re.compile(r'INSERT\s+INTO\s+([\w`]+)\s*\((.*?)\)\s*VALUES\s*([\s\S]+?)(?:;|$)', re.IGNORECASE)
    
    for match in insert_regex.finditer(sql_str):
        table_name = match.group(1).replace('`', '').replace("'", '').replace('"', '')
        columns = [c.strip().replace('`', '').replace("'", '').replace('"', '') for c in match.group(2).split(',')]
        values_content = match.group(3).strip()
        
        # 解析值组
        group_regex = re.compile(r'\(([\s\S]*?)\)(?:\s*,\s*|\s*;?\s*$)')
        for group_match in group_regex.finditer(values_content):
            row = {'table': table_name}
            raw_row_values = split_sql_values(group_match.group(1))
            
            for i, col in enumerate(columns):
                if i < len(raw_row_values):
                    row[col] = parse_simple_value(raw_row_values[i])
            result.append(row)
    
    return result

def split_sql_values(str):
    """
    分割 SQL 值
    """
    result = []
    current = ''
    in_quotes = False
    quote_char = ''
    
    for char in str:
        if (char == "'" or char == '"') and not in_quotes:
            in_quotes = True
            quote_char = char
        elif char == quote_char and in_quotes:
            in_quotes = False
        elif char == ',' and not in_quotes:
            result.append(current.strip())
            current = ''
        else:
            current += char
    
    if current:
        result.append(current.strip())
    return result

def parse_csv(csv_str, delimiter=',', headerless=False):
    """
    解析 CSV 格式
    """
    lines = csv_str.strip().split('\n')
    if not lines:
        return []
    
    if headerless:
        # 无表头模式
        return [[parse_simple_value(v) for v in line.split(delimiter)] for line in lines if line]
    
    # 有表头模式
    if len(lines) < 2:
        return []
    
    headers = [h.strip() for h in lines[0].split(delimiter)]
    result = []
    
    for line in lines[1:]:
        if not line:
            continue
        values = line.split(delimiter)
        row = {}
        for i, h in enumerate(headers):
            if i < len(values):
                row[h] = parse_simple_value(values[i])
        result.append(row)
    
    return result

def parse_xml(xml_str):
    """
    解析 XML 格式
    """
    result = []
    item_regex = re.compile(r'<item>([\s\S]*?)</item>', re.IGNORECASE)
    
    for match in item_regex.finditer(xml_str):
        item_content = match.group(1)
        row = {}
        field_regex = re.compile(r'<([a-zA-Z0-9_]+)>([\s\S]*?)</\1>', re.IGNORECASE)
        
        for field_match in field_regex.finditer(item_content):
            field_name = field_match.group(1)
            field_value = field_match.group(2).strip()
            row[field_name] = parse_simple_value(field_value)
        
        if row:
            result.append(row)
    
    return result

def parse_yaml(yaml_str):
    """
    解析 YAML 格式
    """
    lines = [line.strip() for line in yaml_str.split('\n') if line.strip()]
    result = []
    current_row = {}
    
    for line in lines:
        if line.startswith('-'):
            if current_row:
                result.append(current_row)
                current_row = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if key:
                current_row[key] = parse_simple_value(value)
    
    if current_row:
        result.append(current_row)
    
    return result

def get_headers(data):
    """
    获取数据的表头
    """
    headers = []
    seen = set()
    for row in data:
        for key in row:
            if key != 'table' and key not in seen:
                headers.append(key)
                seen.add(key)
    return headers

def parse_simple_value(v):
    """
    解析简单值
    """
    if not v:
        return None
    v = v.strip()
    lower_v = v.lower()
    
    if lower_v == 'null':
        return None
    if lower_v == 'true':
        return True
    if lower_v == 'false':
        return False
    
    if (v.startswith("'") and v.endswith("'") or v.startswith('"') and v.endswith('"')):
        return v[1:-1].replace("''", "'")
    
    try:
        return float(v) if '.' in v else int(v)
    except ValueError:
        pass
    
    return v

def format_value_by_type(v, type):
    """
    根据类型格式化值
    """
    if v is None:
        return 'NULL' if type == 'sql' else ''
    
    if type == 'sql' and isinstance(v, str):
        return "'" + v.replace("'", "''") + "'"
    
    if type == 'csv' and ',' in str(v):
        return '"' + str(v).replace('"', '\\"') + '"'
    
    if type == 'xml':
        return str(v).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    return str(v)

def format_to_json(data):
    """
    转换为 JSON 格式
    """
    return json.dumps(data, indent=2, ensure_ascii=False)

def format_to_csv(data, headerless=False):
    """
    转换为 CSV 格式
    """
    if headerless and isinstance(data, list) and data and isinstance(data[0], list):
        # 无表头模式
        rows = []
        for row in data:
            rows.append(','.join([format_value_by_type(v, 'csv') for v in row]))
        return '\n'.join(rows)
    
    # 有表头模式
    headers = get_headers(data)
    rows = [','.join(headers)]
    for row in data:
        rows.append(','.join([format_value_by_type(row.get(h), 'csv') for h in headers]))
    
    return '\n'.join(rows)

def format_to_tabtext(data, headerless=False):
    """
    转换为制表符分隔格式
    """
    if headerless and isinstance(data, list) and data and isinstance(data[0], list):
        # 无表头模式
        return '\n'.join(['\t'.join([format_value_by_type(v, 'csv') for v in row]) for row in data])
    
    # 有表头模式
    headers = get_headers(data)
    rows = [headers] + [[format_value_by_type(row.get(h), 'csv') for h in headers] for row in data]
    return '\n'.join(['\t'.join(row) for row in rows])

def format_to_yaml(data):
    """
    转换为 YAML 格式
    """
    keys = get_headers(data)
    yaml_lines = []
    
    for row in data:
        yaml_lines.append('-')
        for key in keys:
            if key in row:
                yaml_lines.append(f'  {key}: {row[key]}')
    
    return '\n'.join(yaml_lines)

def format_to_xml(data):
    """
    转换为 XML 格式
    """
    headers = get_headers(data)
    xml_lines = ['<data>']
    
    for row in data:
        xml_lines.append('  <item>')
        for h in headers:
            if h in row:
                xml_lines.append(f'    <{h}>{format_value_by_type(row[h], "xml")}</{h}>')
        xml_lines.append('  </item>')
    
    xml_lines.append('</data>')
    return '\n'.join(xml_lines)

def format_to_sql_insert(data, table_name='table_name', multiline=True):
    """
    转换为 SQL INSERT 语句
    """
    if not data:
        return ''
    
    headers = get_headers(data)
    if not headers:
        return ''
    
    if multiline:
        # 多行模式
        statements = []
        for row in data:
            values = [format_value_by_type(row.get(h), 'sql') for h in headers]
            statements.append("INSERT INTO " + table_name + " (" + ", ".join(headers) + ") VALUES (" + ", ".join(values) + ");")
        return '\n'.join(statements)
    else:
        # 单行模式
        values = []
        for row in data:
            row_values = [format_value_by_type(row.get(h), 'sql') for h in headers]
            values.append(f"({', '.join(row_values)})")
        return "INSERT INTO " + table_name + " (" + ", ".join(headers) + ") VALUES\n  " + ",\n  ".join(values) + ";"

def parse_html_list(html_str):
    """
    解析 HTML 列表
    """
    result = []
    li_regex = re.compile(r'<li>([\s\S]*?)</li>', re.IGNORECASE)
    
    for match in li_regex.finditer(html_str):
        value = match.group(1).strip()
        if value:
            result.append({'value': value})
    
    return result

def format_to_html(data):
    """
    转换为 HTML 格式
    """
    if not data:
        return '<ul></ul>'
    
    html_lines = ['<ul>']
    
    if isinstance(data, list):
        if data and isinstance(data[0], list):
            # 列表的列表
            for row in data:
                items = [format_value_by_type(item, 'xml') for item in row]
                html_lines.append(f'  <li>{", ".join(items)}</li>')
        elif data and isinstance(data[0], dict):
            # 字典的列表
            keys = list(data[0].keys())
            for item in data:
                values = [format_value_by_type(item.get(key), 'xml') for key in keys]
                html_lines.append(f'  <li>{", ".join(values)}</li>')
        else:
            # 简单列表
            for item in data:
                html_lines.append(f'  <li>{format_value_by_type(item, "xml")}</li>')
    
    html_lines.append('</ul>')
    return '\n'.join(html_lines)

def format_to_markdown_table(data):
    """
    转换为 Markdown 表格格式
    """
    if not data:
        return ''
    
    table_elements = []
    
    if isinstance(data, list):
        if data and isinstance(data[0], list):
            # 列表的列表
            table_elements = data
        elif data and isinstance(data[0], dict):
            # 字典的列表
            headers = get_headers(data)
            table_elements = [headers]
            for row in data:
                row_values = [str(row.get(h, '')) for h in headers]
                table_elements.append(row_values)
        else:
            # 简单列表
            table_elements = [['Value']] + [[str(item)] for item in data]
    
    if len(table_elements) < 2:
        return ''
    
    # 计算每列最大长度
    column_max_length = {}
    for i in range(len(table_elements[0])):
        max_len = 0
        for row in table_elements:
            if i < len(row):
                max_len = max(max_len, len(row[i]))
        column_max_length[i] = max(max_len, 2)  # 确保至少 2 个字符
    
    # 格式化表格
    formatted_table = []
    headers = table_elements[0]
    formatted_table.append('| ' + ' | '.join([h.ljust(column_max_length[i]) for i, h in enumerate(headers)]) + ' |')
    formatted_table.append('| ' + ' | '.join(['---'.ljust(column_max_length[i]) for i in range(len(headers))]) + ' |')
    
    for row in table_elements[1:]:
        formatted_row = []
        for i, cell in enumerate(row):
            if i < len(column_max_length):
                formatted_row.append(cell.ljust(column_max_length[i]))
            else:
                formatted_row.append(cell)
        formatted_table.append('| ' + ' | '.join(formatted_row) + ' |')
    
    return '\n'.join(formatted_table)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("列表格式 json/xml/yaml/csv/tsv/sql/md/html 转换")
