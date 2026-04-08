#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Compare Lines",
  "description": "比较两行文本的差异",
  "icon": "⚖️",
  "tags": ["compare","lines"],
  "help": "比较两行文本的差异\n\n示例:\n输入:\nhello world\nhello word\n\n输出:\n差异位置：7\n行 1: w\n行 2: d"
}"""


def _preprocess_text(text):
    """Preprocess text for comparison."""
    return [line.strip() for line in text.split('\n') if line.strip()]


def _compare_texts(lines1, lines2):
    """Compare two lists of lines and return differences."""
    diffs = []
    max_length = max(len(lines1), len(lines2))

    for i in range(max_length):
        line1 = lines1[i] if i < len(lines1) else None
        line2 = lines2[i] if i < len(lines2) else None

        if line1 is None and line2 is not None:
            diffs.append({'type': 'add', 'line_num1': None, 'line_num2': i + 1, 'content': line2})
        elif line1 is not None and line2 is None:
            diffs.append({'type': 'remove', 'line_num1': i + 1, 'line_num2': None, 'content': line1})
        elif line1 != line2:
            diffs.append({'type': 'change', 'line_num1': i + 1, 'line_num2': i + 1, 'content1': line1, 'content2': line2})

    # Categorize comparison result
    status = _categorize_comparison(lines1, lines2, diffs)

    return {
        'status': status,
        'diffs': diffs,
        'stats': {
            'lines1': len(lines1),
            'lines2': len(lines2),
            'diff_count': len(diffs)
        }
    }


def _categorize_comparison(lines1, lines2, diffs):
    """Categorize the comparison result."""
    if not diffs:
        return '完全一致'

    set1 = set(lines1)
    set2 = set(lines2)

    # Check if they have the same elements (different order)
    if set1 == set2:
        return '数据一致但顺序有差异'

    # Check if one is subset of another
    if set1.issubset(set2):
        return '数据 1 被包含在数据 2 中'
    if set2.issubset(set1):
        return '数据 2 被包含在数据 1 中'

    return '数据完全不同'


def _format_result(original_text, comparison_result, lines1, lines2):
    """Format the comparison result."""
    status = comparison_result['status']
    diffs = comparison_result['diffs']
    stats = comparison_result['stats']

    result = original_text + '\n\n'
    result += '=== 对比结果 ===\n'
    result += f'状态: {status}\n'
    result += f'文本1行数: {stats["lines1"]}\n'
    result += f'文本2行数: {stats["lines2"]}\n'
    result += f'差异行数: {stats["diff_count"]}\n\n'

    result += '=== 详细差异 ===\n'

    if not diffs:
        result += '无差异\n'
    else:
        result += '格式: [行号1]:[行号2] 内容\n'
        result += '符号: - 移除, + 添加, ~ 变更\n\n'

        for diff in diffs:
            if diff['type'] == 'remove':
                result += f'- {diff["line_num1"]}:     {diff["content"]}\n'
            elif diff['type'] == 'add':
                result += f'+     :{diff["line_num2"]} {diff["content"]}\n'
            elif diff['type'] == 'change':
                result += f'~ {diff["line_num1"]}:{diff["line_num2"]} {diff["content1"]} -> {diff["content2"]}\n'

    return result


def main(state):
    """Compare two text sections and show detailed differences."""
    text = state.text
    sections = text.split('\n' + '-' * 3 + '\n')

    if len(sections) != 2:
        state.post_error('Please provide two text sections separated by "\\n---\\n" (3 or more dashes)')
        return

    text1, text2 = sections
    lines1 = _preprocess_text(text1)
    lines2 = _preprocess_text(text2)

    comparison_result = _compare_texts(lines1, lines2)
    result_text = _format_result(text, comparison_result, lines1, lines2)

    state.text = result_text
