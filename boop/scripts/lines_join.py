"""
{
  "api": 1,
  "name": "Join Lines",
  "description": "Join lines with configurable separator, quote, and escape options",
  "icon": "collapse",
  "tags": ["join", "lines"],
  "help": "Join lines with configurable options.\n\nUsage: First line specifies configuration (optional)\n  Format: separator:quote:escapeTabs\n\nParameters:\n  separator - Separator (default: empty, meaning direct concatenation)\n              Special value: \\n for newline\n  quote     - Quote type (optional)\n              \" or '  - Wrap each line with quotes\n  escapeTabs - Escape tabs (optional)\n              code/t/true - Escape tabs as \\t\n\nExamples:\n  ,\n  item1\n  item2\n\n  Output: item1,item2\n\n  ,:\" \n  item1\n  item2\n\n  Output: \"item1\",\"item2\""
}
"""


def main(state):
    """Join lines with configurable separator, quote, and escape options."""
    lines = state.text.split('\n')
    first_line = lines[0]

    # Check for help request
    if first_line.strip() in ('-h', '--help'):
        help_text = """
Join Lines - 合并行

用法：在第一行指定配置（可选）
  格式：separator:quote:escapeTabs

参数说明：
  separator - 分隔符（默认为空，表示直接合并）
            特殊值：\\n 表示换行符
  quote     - 引号类型（可选）
            " 或 '  - 用引号包裹每行
  escapeTabs - 转义制表符（可选）
            code/t/true - 将制表符转义为\\t

示例：
  ,
  item1
  item2

  将输出：
  item1,item2

  ,:"
  item1
  item2

  将输出：
  "item1","item2"

  \\n:code
  item1
  item2

  将输出：
  item1\\nitem2

  ;:'
  item1
  item2

  将输出：
  'item1';'item2'

  item1
  item2

  将输出（默认配置）：
  item1item2
"""
        state.text = help_text + '\n' + '\n'.join(lines[1:])
        return

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
