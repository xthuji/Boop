#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format SQL",
  "description": "格式化 SQL 查询语句",
  "icon": "✨",
  "tags": ["sql","format","fmt","code"],
  "dependencies": ["sqlparse"],
  "help": "格式化 SQL 查询语句\n\n示例:\n输入:\nSELECT * FROM users WHERE id=1\n\n输出:\nSELECT *\nFROM users\nWHERE id = 1"
}"""

import sqlparse
import re

def format_code(code):
    """Format SQL code using sqlparse with custom tweaks."""
    if not code or not code.strip():
        return code

    try:
        # 先用 sqlparse 进行初步格式化
        formatted_sql = sqlparse.format(
            code,
            reindent=True,
            indent_width=4,
            keyword_case='upper'
        )

        # 然后进行自定义微调
        formatted_sql = custom_tweaks(formatted_sql)
        return formatted_sql
    except Exception as e:
        raise Exception("Error formatting SQL: {}".format(e))

def custom_tweaks(code):
    """Custom tweaks to improve sqlparse formatting."""
    # 确保操作符周围的空格
    code = re.sub(r'(\*)(?!\s)', r' \1 ', code)
    code = re.sub(r'(=)(?!\s)', r' \1 ', code)
    code = re.sub(r'(<)(?!\s)', r' \1 ', code)
    code = re.sub(r'(>)(?!\s)', r' \1 ', code)
    code = re.sub(r'(<=)(?!\s)', r' \1 ', code)
    code = re.sub(r'(>=)(?!\s)', r' \1 ', code)
    code = re.sub(r'(!=)(?!\s)', r' \1 ', code)

    # 移除多余的空格
    code = re.sub(r'\s+', ' ', code)

    # 确保括号内的参数之间有空格
    code = re.sub(r'\(([^)]*)\)', lambda m: '(' + re.sub(r',\s*', ', ', m.group(1)) + ')', code)

    # 确保表名和括号之间有空格
    code = re.sub(r'(CREATE TABLE\s+[\w]+)(\()', r'\1 \2', code)
    code = re.sub(r'(INSERT INTO\s+[\w]+)(\()', r'\1 \2', code)

    # 确保 UPDATE 和 SET 之间只有一个空格
    code = re.sub(r'UPDATE\s+([\w]+)\s+SET', r'UPDATE \1 SET', code)

    # 确保 SELECT * FROM 格式正确
    code = re.sub(r'SELECT\s+\*\s+FROM', r'SELECT * FROM', code)
    code = re.sub(r'SELECT\s+\*', r'SELECT *', code)
    code = re.sub(r'SELECT\*', r'SELECT *', code)

    # 确保 VALUES 关键字后有空格
    code = re.sub(r'VALUES\s*\(', r'VALUES (', code)

    # 确保 SET 部分和 WHERE 之间有空格
    code = re.sub(r'([^\s])WHERE', r'\1 WHERE', code)

    # 处理 JOIN 语句的换行
    code = re.sub(r'\bJOIN\b', '\nJOIN', code)
    # 处理 JOIN 语句后的 WHERE 语句换行
    code = re.sub(r'(JOIN.*)WHERE', r'\1\nWHERE', code)
    # 处理 ORDER BY 语句的换行
    code = re.sub(r'\bORDER BY\b', '\nORDER BY', code)

    # 处理简单查询的 WHERE 语句（不换行）
    # 对于没有 JOIN 的 SELECT 语句
    code = re.sub(r'(SELECT.*FROM.*)(?!.*JOIN)\nWHERE', r'\1 WHERE', code)
    # 对于 UPDATE 语句
    code = re.sub(r'(UPDATE.*SET.*)\nWHERE', r'\1 WHERE', code)
    # 对于 DELETE 语句
    code = re.sub(r'(DELETE.*FROM.*)\nWHERE', r'\1 WHERE', code)

    # 处理 CREATE TABLE 语句的列定义
    code = format_create_table(code)

    # 处理 SELECT 语句的多行格式化
    code = format_select(code)

    # 处理布尔值为小写
    code = re.sub(r'\bTRUE\b', 'true', code)
    code = re.sub(r'\bFALSE\b', 'false', code)

    return code

def format_create_table(code):
    """Format CREATE TABLE statements."""
    def format_create_table_match(match):
        table_name = match.group(1)
        columns = match.group(2)
        # 格式化列定义
        column_lines = []
        # 使用逗号分割列定义
        for column in re.split(r',\s*', columns):
            column = column.strip()
            if column:
                column_lines.append('    ' + column)
        formatted_columns = ',\n'.join(column_lines)
        return 'CREATE TABLE ' + table_name + ' (\n' + formatted_columns + '\n);'

    code = re.sub(r'CREATE TABLE\s+([\w]+)\s*\(([^;]*)\);', format_create_table_match, code)
    return code

def format_select(code):
    """Format SELECT statements."""
    def format_select_match(match):
        select_part = match.group(1)
        rest = match.group(2)
        # 处理 SELECT 部分
        if ',' in select_part:
            select_items = [item.strip() for item in select_part.split(',')]
            formatted_select = 'SELECT\n    ' + ',\n    '.join(select_items)
            # 对于复杂查询，FROM 关键字换行
            rest = re.sub(r'\bFROM\b', '\nFROM', rest)
        else:
            formatted_select = 'SELECT ' + select_part
            # 对于简单查询，FROM 关键字不换行
            rest = re.sub(r'\nFROM', ' FROM', rest)
        # 处理简单查询的 WHERE 语句（不换行）
        if 'JOIN' not in rest and 'ORDER BY' not in rest:
            rest = re.sub(r'\nWHERE', ' WHERE', rest)
        return formatted_select + rest

    code = re.sub(r'SELECT\s+([^FROM]+)(FROM.*)', format_select_match, code)
    return code


def main(state):
    """Format SQL text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("SQL code formatted")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(f"Error formatting SQL: {str(e)}")
        else:
            print(f"Error formatting SQL: {str(e)}")
