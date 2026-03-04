'''
{
    "api": 1,
    "name": "Sort Lines",
    "description": "Sort lines alphabetically",
    "icon": "sort",
    "tags": ["sort", "lines", "alphabetize"],
    "help": "Sorts all lines in the text alphabetically (A-Z).\nEmpty lines are preserved in their sorted position."
}
'''

def main(state):
    """Sort lines alphabetically"""
    lines = state.full_text.split('\n')
    sorted_lines = sorted(lines)
    state.full_text = '\n'.join(sorted_lines)
    state.post_info("Lines sorted")
