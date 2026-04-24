#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Generate Sum",
  "description": "计算文本数字的总和",
  "icon": "📄",
  "tags": ["calculate","sum","math","code"],
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
    numbers = _num_string_to_array(s)
    sum_output = sum(numbers)
    return str(int(sum_output) if sum_output.is_integer() else sum_output)
