'''
{
    "api": 1,
    "name": "Count Lines",
    "description": "Count the number of lines in your text",
    "icon": "counter",
    "tags": ["count", "lines", "stats"],
    "help": "Count the number of lines in your text.\n\nExample:\nInput:\nHello\nWorld\n\nOutput:\n2"
}
'''

def main(state):
    """Count the number of lines"""
    if not state.full_text:
        line_count = 0
    else:
        lines = state.full_text.split('\n')
        line_count = len(lines)
    state.text = str(line_count)
    state.post_info(f"{line_count} lines")
