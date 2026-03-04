"""
{
  "api": 1,
  "name": "Remove Duplicate Lines",
  "description": "Remove duplicate lines (keep first occurrence)",
  "icon": "filtration",
  "tags": ["lines", "clean", "remove", "duplicate"],
  "help": "Removes duplicate lines, keeping only the first occurrence of each.\n\nExample:\nInput:\napple\nbanana\napple\ncherry\nbanana\n\nOutput:\napple\nbanana\ncherry"
}
"""


def main(state):
    """Remove duplicate lines, keeping first occurrence."""
    lines = state.text.split('\n')
    seen = set()
    unique_lines = []

    for line in lines:
        if line not in seen:
            seen.add(line)
            unique_lines.append(line)

    state.text = '\n'.join(unique_lines)
