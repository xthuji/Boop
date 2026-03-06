#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Join Lines",
  "description": "将多行文本合并为单行",
  "icon": "🧩",
  "tags": ["join","lines","separator","delimiter"],
  "help": "将多行文本合并为单行\n\n首行参数格式:\nseparator[:quote[:escape]]\n\n参数说明:\n- separator: 分隔符 (默认空字符串)\n- quote: 引号字符 (可选，如 '"' 或 "'")\n- escape: 是否转义制表符 (code/true/t)\n\n示例 1 (默认设置):\n输入:\nhello\nworld\n\n输出:\nhelloworld\n\n示例 2 (自定义分隔符):\n输入:\n, \napple\nbanana\ncherry\n\n输出:\napple, banana, cherry\n\n示例 3 (带引号):\n输入:\n, :"\napple\nbanana\n\n输出:\n"apple", "banana"
}"""


def main(state):
    """Join lines with configurable separator, quote, and escape options."""
    lines = state.text.split('\n')
    first_line = lines[0]

    separator = ''
    quote = ''
    escape_tabs = False
    text_to_join = state.text

    def is_config_line(line):
        trimmed = line.strip()
        if trimmed in ('', 'code', 'true', 't'):
            return True
        if trimmed in ('"', "'"):
            return True
        if all(c in ',; \t' for c in trimmed):
            return True
        if trimmed.startswith(':') and ('"' in trimmed or "'" in trimmed or 'code' in trimmed.lower()):
            return True
        return False

    if is_config_line(first_line):
        config_parts = first_line.split(':')
        separator = config_parts[0] if config_parts else ''
        text_to_join = '\n'.join(lines[1:])

        if len(config_parts) >= 2 and config_parts[1]:
            second_part = config_parts[1].strip().lower()
            if second_part in ('"', "'"):
                quote = second_part
            elif second_part in ('code', 'true', 't'):
                escape_tabs = True

        if len(config_parts) >= 3 and config_parts[2]:
            third_part = config_parts[2].strip().lower()
            if third_part in ('code', 'true', 't'):
                escape_tabs = True

        # If quote is set but separator is empty, default to comma
        if quote and separator == '':
            separator = ', '

    # Process the text
    process_lines = text_to_join.split('\n')

    if escape_tabs:
        # Escape leading tabs
        escaped_lines = []
        for line in process_lines:
            leading_tabs = len(line) - len(line.lstrip('\t'))
            escaped_line = '\\t' * leading_tabs + line.lstrip('\t')
            escaped_lines.append(escaped_line)

        if separator == '':
            state.text = '\\n'.join(escaped_lines)
        else:
            state.text = separator.join(escaped_lines)
    elif quote:
        # Wrap each line with quotes
        quoted_lines = [f'{quote}{line}{quote}' for line in process_lines]
        state.text = separator.join(quoted_lines)
    else:
        # Simple join with separator
        state.text = text_to_join.replace('\n', separator)
