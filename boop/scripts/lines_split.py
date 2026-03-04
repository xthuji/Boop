#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Split Lines",
  "description": "将文本按分隔符分割成多行",
  "icon": "✂️",
  "tags": ["text","split","lines"],
  "help": "将文本按分隔符分割成多行\n\n示例:\n输入:\napple,banana,cherry\n\n输出:\napple\nbanana\ncherry"
}"""

import re


def main(state):
    """Split lines by delimiter with optional quote handling."""
    lines = state.text.split('\n')
    first_line = lines[0]

    # Check for help request
    if first_line.strip() in ('-h', '--help'):
        help_text = """
Split Lines - 拆分行

用法：在第一行指定配置（可选）
  格式：delimiter:quote:escape

参数说明：
  delimiter - 分隔符（默认为逗号）
            特殊值：\\n 表示换行符
  quote     - 引号类型（可选）
            " 或 '  - 按引号拆分
  escape    - 转义处理（可选）
            code/t/true - 转义特殊字符

示例：
  ,
  item1,item2,item3

  将输出：
  item1
  item2
  item3

  ,:"
  "item1","item2","item3"

  将输出：
  item1
  item2
  item3

  ;
  item1;item2;item3

  将输出：
  item1
  item2
  item3

  item1,item2,item3

  将输出（默认配置）：
  item1
  item2
  item3
"""
        state.text = help_text + '\n' + '\n'.join(lines[1:])
        return

    delimiter = ','
    quote = ''
    escape = False
    text_to_split = state.text

    def is_config_line(line):
        trimmed = line.strip()
        if trimmed in ('', 'code', 'true', 't'):
            return True
        if trimmed in ('"', "'"):
            return True
        if all(c in ',;\\s' for c in trimmed):
            return True
        if trimmed.startswith(':') and ('"' in trimmed or "'" in trimmed or 'code' in trimmed.lower()):
            return True
        return False

    if is_config_line(first_line):
        config_parts = first_line.split(':')
        delimiter = config_parts[0] if config_parts else ','
        text_to_split = '\n'.join(lines[1:])

        if len(config_parts) >= 2 and config_parts[1]:
            second_part = config_parts[1].strip()
            if second_part in ('"', "'"):
                quote = second_part
            elif second_part in ('code', 'true', 't'):
                escape = True

        if len(config_parts) >= 3 and config_parts[2]:
            third_part = config_parts[2].strip()
            if third_part in ('code', 'true', 't'):
                escape = True

    # Handle special delimiter
    if delimiter == '\\n':
        delimiter = '\n'

    result_lines = []

    if quote:
        # Split by quotes and delimiter
        lines_to_process = [line for line in text_to_split.split('\n') if line.strip()]

        for line in lines_to_process:
            # Extract all quoted content
            pattern = re.compile(rf'[{re.escape(quote)}]([^ {re.escape(quote)}]*?)[{re.escape(quote)}]\s*[{re.escape(delimiter)}]\s*')
            items = []

            for match in pattern.finditer(line):
                items.append(match.group(1))

            # Handle last element
            if items:
                last_match_index = pattern.lastindex
                if pattern.lastindex and pattern.search(line, pos=pattern.end()):
                    last_item = line[pattern.end():].strip()
                    if last_item.startswith(quote) and last_item.endswith(quote):
                        items.append(last_item[1:-1])
                    elif last_item:
                        items.append(last_item)
            else:
                # If no quotes, split by delimiter normally
                for item in line.split(delimiter):
                    trimmed_item = item.strip()
                    if trimmed_item:
                        if trimmed_item.startswith(quote) and trimmed_item.endswith(quote):
                            items.append(trimmed_item[1:-1])
                        else:
                            items.append(trimmed_item)

            result_lines.extend(items)
    else:
        # Split by delimiter normally
        lines_to_process = [line for line in text_to_split.split('\n') if line.strip()]

        for line in lines_to_process:
            for item in line.split(delimiter):
                trimmed_item = item.strip()
                if trimmed_item:
                    # Auto-detect and remove quotes
                    if (trimmed_item.startswith('"') and trimmed_item.endswith('"')) or \
                       (trimmed_item.startswith("'") and trimmed_item.endswith("'")):
                        result_lines.append(trimmed_item[1:-1])
                    else:
                        result_lines.append(trimmed_item)

    state.text = '\n'.join(result_lines)
