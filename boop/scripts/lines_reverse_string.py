"""
{
  "api": 1,
  "name": "Lines Reverse String",
  "description": "Reverses string for each line",
  "icon": "flip",
  "tags": ["reverse", "string", "transform"],
  "help": "Reverses each line of the input text.\n\nExample:\nInput:\nhello\nworld\n\nOutput:\nolleh\ndlrow"
}
"""


def main(state):
    """Reverse string for each line."""
    lines = state.text.split('\n')
    reversed_lines = [line[::-1] for line in lines]
    state.text = '\n'.join(reversed_lines)
