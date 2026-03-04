#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Generate Sum",
  "description": "计算数字的总和",
  "icon": "➕",
  "tags": ["calculate","sum","math"],
  "help": "计算文本中所有数字的总和\n\n示例:\n输入:\n1\n2\n3\n4\n5\n\n输出:\n15"
}"""

import re


def _looks_like_fraction(s):
    """Check if string looks like a fraction."""
    return bool(re.match(r'^[\d.]+/[\d.]+$', s))


def _get_fraction(s):
    """Get fraction value."""
    frac = s.split('/')
    return float(frac[0]) / float(frac[1])


def _get_number(s):
    """Get number from string, handling fractions."""
    if _looks_like_fraction(s):
        return _get_fraction(s)
    try:
        return float(s)
    except ValueError:
        return None


def _num_string_to_array(s):
    """Convert string of numbers to array."""
    # Remove comments
    s = re.sub(r'//.*', '', s)
    # Split by various delimiters
    parts = re.split(r'[\n\s,;=]', s)
    # Convert to numbers, filtering out empty values
    return [n for n in (_get_number(p) for p in parts) if n is not None]


def main(state):
    """Sum up a list of numbers."""
    if not state.text.strip():
        state.post_error('')
        return

    result = _calculate(state.text)
    state.text = result


def _calculate(s):
    """Calculate sum and format output."""
    comment = '\t// '
    numbers = _num_string_to_array(s)

    sum_output = sum(numbers)

    # Build the comment showing addition
    if len(numbers) > 1:
        sum_output_str = f'{sum_output}{comment}{" + ".join(str(n) for n in numbers)}'
    else:
        sum_output_str = str(sum_output)

    # Process each line
    result_lines = []
    for line in re.split(r'[\n,;]', s):
        line = line.strip()
        num = _get_number(line)
        if line.startswith('=') or line == '' or (num is not None and str(num) == line):
            result_lines.append(line)
        elif num is not None:
            result_lines.append(f'{line}{comment}{num}')
        else:
            result_lines.append(line)

    result_lines.append(f'= {sum_output_str}')
    return '\n'.join(result_lines)
