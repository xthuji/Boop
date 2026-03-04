"""
{
  "api": 1,
  "name": "Lines Shuffle Characters",
  "description": "Shuffles characters randomly for each line",
  "icon": "dice",
  "tags": ["shuffle", "random", "character", "char"],
  "help": "Shuffles characters randomly for each line.\n\nExample:\nInput:\nhello\nworld\n\nOutput:\nlehol (random)\nrowdl (random)"
}
"""

import random


def _shuffle_string(string):
    """Shuffle characters in a string."""
    chars = list(string)
    random.shuffle(chars)
    return ''.join(chars)


def main(state):
    """Shuffle characters randomly for each line."""
    lines = state.text.split('\n')
    shuffled_lines = [_shuffle_string(line) for line in lines]
    state.text = '\n'.join(shuffled_lines)
