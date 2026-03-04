#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Split Lines",
  "description": "将文本按分隔符分割成多行",
  "icon": "🧩",
  "tags": ["split","lines","separator","delimiter"],
  "help": "将文本按分隔符分割成多行\n\n首行参数格式:\ndelimiter[:quote[:escape]]\n\n参数说明:\n- delimiter: 分隔符 (默认 ',')\n- quote: 引号字符 (可选，如 '"' 或 "'")\n- escape: 是否启用转义 (code/true/t)\n\n示例 1 (默认分隔符):\n输入:\napple,banana,cherry\n\n输出:\napple\nbanana\ncherry\n\n示例 2 (自定义分隔符和引号):\n输入:\n;:":code\n"apple;pie","banana;bread"\n\n输出:\napple;pie\nbanana;bread"
}"""

import re


def main(state):
    """Split lines by delimiter with optional quote handling."""
    lines = state.text.split('\n')
    first_line = lines[0]

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
        if all(c in ',; \s' for c in trimmed):
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
