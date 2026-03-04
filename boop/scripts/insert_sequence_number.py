"""
{
  "api": 1,
  "name": "Insert Sequence Number",
  "description": "Insert sequence numbers (arabic/chinese/upper/lower)",
  "icon": "sort-numbers",
  "tags": ["insert", "sequence", "number"],
  "help": "Insert sequence numbers at the beginning of each line.\n\nUsage: First line specifies configuration (optional)\n  Format: start:step:type:sep:width\n\nParameters:\n  start  - Start value (number or letter)\n  step   - Step value (number)\n  type   - Sequence type:\n           1/n/num     - Arabic numbers (default)\n           2/c/zh      - Chinese numbers\n           a/u/upper   - Uppercase letters\n           b/l/lower   - Lowercase letters\n  sep    - Separator (default: space)\n  width  - Number width (zero-padded, e.g., 02 for 2 digits)\n\nExamples:\n  1:1:n: :02\n  item1\n  item2\n\n  Output:\n  01 item1\n  02 item2\n\n  A:1:upper:-\n  item1\n  item2\n\n  Output:\n  A-item1\n  B-item2"
}
"""


def _number_to_chinese(num):
    """Convert Arabic number to Chinese number representation."""
    chinese_digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    num_str = str(num)
    result = ''
    for digit in num_str:
        result += chinese_digits[int(digit)]
    return result


def _generate_incremental_values(start, step, format_type, count, placeholder_format):
    """Generate incremental values based on format."""
    current = start if isinstance(start, int) else ord(start)
    result = []

    for _ in range(count):
        value = ''

        if format_type == 'arabic':
            num = int(current)
            if placeholder_format:
                # Parse format like %02d
                import re
                match = re.search(r'\d+', placeholder_format)
                if match:
                    width = int(match.group())
                    value = str(num).zfill(width)
                else:
                    value = str(num)
            else:
                value = str(num)
        elif format_type == 'chinese':
            value = _number_to_chinese(int(current))
        elif format_type == 'english_upper':
            value = chr(current)
        elif format_type == 'english_lower':
            value = chr(current)

        current += step
        result.append(value)

    return result


def main(state):
    """Insert sequence numbers at the beginning of each line."""
    lines = state.text.split('\n')
    first_line = lines[0]

    # Check for help request
    if first_line.strip() in ('-h', '--help'):
        help_text = """
Insert Sequence - 插入序列

用法：在第一行指定配置（可选）
  格式：start:step:type:sep:width

参数说明：
  start  - 起始值（数字或字母）
  step   - 步长（数字）
  type   - 序列类型：
           1/n/num     - 阿拉伯数字（默认）
           2/c/zh      - 中文数字
           a/u/upper   - 大写字母
           b/l/lower   - 小写字母
  sep    - 分隔符（默认为空格）
  width  - 数字宽度（自动补零，如 02 表示 2 位）

示例：
  1:1:n: :02
  item1
  item2

  将输出：
  01 item1
  02 item2

  A:1:upper:-
  item1
  item2

  将输出：
  A-item1
  B-item2

  1:2:c: :3
  item1
  item2
  item3

  将输出：
  一 item1
  三 item2
  五 item3

  item1
  item2

  将输出（默认配置）：
  1 item1
  2 item2
"""
        state.text = help_text + '\n' + '\n'.join(lines[1:])
        return

    start = 1
    step = 1
    format_type = 'arabic'
    separator = ' '
    placeholder_format = None
    text_to_process = state.text

    config_parts = first_line.split(':')
    first_part = config_parts[0].strip() if config_parts else ''
    is_first_part_number = first_part.isdigit()
    is_first_part_letter = len(first_part) == 1 and first_part.isalpha()

    if is_first_part_number or is_first_part_letter:
        # Parse start value
        if is_first_part_number:
            start = int(first_part)
        else:
            start = first_part.upper() if first_part.isupper() else first_part.lower()

        # Parse step
        if len(config_parts) >= 2 and config_parts[1]:
            step_str = config_parts[1].strip()
            if step_str.isdigit():
                step = int(step_str)

        # Parse type
        if len(config_parts) >= 3 and config_parts[2]:
            type_str = config_parts[2].strip().lower()
            type_map = {
                '1': 'arabic', 'n': 'arabic', 'num': 'arabic',
                '2': 'chinese', 'c': 'chinese', 'zh': 'chinese',
                'a': 'english_upper', 'u': 'english_upper', 'upper': 'english_upper',
                'b': 'english_lower', 'l': 'english_lower', 'lower': 'english_lower'
            }
            format_type = type_map.get(type_str, 'arabic')

        # Parse separator
        if len(config_parts) >= 4:
            separator = config_parts[3]

        # Parse width
        if len(config_parts) >= 5 and config_parts[4]:
            width_str = config_parts[4].strip()
            if width_str.isdigit():
                width = int(width_str)
                placeholder_format = f'%0{width}d'

        text_to_process = '\n'.join(lines[1:])

    # Count lines to process
    count = len([l for l in text_to_process.split('\n') if l.strip()])
    if count == 0:
        count = len(text_to_process.split('\n'))

    # Generate values
    values = _generate_incremental_values(start, step, format_type, count, placeholder_format)

    # Insert values
    process_lines = text_to_process.split('\n')
    result_lines = []
    for i, line in enumerate(process_lines):
        if i < len(values):
            result_lines.append(f'{values[i]}{separator}{line}')
        else:
            result_lines.append(line)

    state.text = '\n'.join(result_lines)
