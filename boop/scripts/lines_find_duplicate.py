"""
{
  "api": 1,
  "name": "Find Duplicate Lines",
  "description": "Finds and displays duplicate lines from the text",
  "icon": "filtration",
  "tags": ["lines", "duplicate", "find"],
  "help": "Finds duplicate lines and shows how many times each appears.\n\nExample:\nInput:\napple\nbanana\napple\ncherry\nbanana\n\nOutput:\napple (2 occurrences)\nbanana (2 occurrences)"
}
"""

from collections import Counter


def main(state):
    """Find and display duplicate lines."""
    lines = state.text.split('\n')
    line_count = Counter(lines)

    duplicates = []
    for line, count in line_count.items():
        if count > 1:
            duplicates.append(f"{line} ({count} occurrences)")

    if not duplicates:
        state.text = 'No duplicate lines found.'
    else:
        state.text = '\n'.join(duplicates)
