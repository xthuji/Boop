"""
{
  "api": 1,
  "name": "Generate Placeholder Text",
  "description": "Generates Lorem Ipsum placeholder text",
  "icon": "roman",
  "tags": ["generate", "lorem", "ipsum", "text"],
  "help": "Generates 100 words of Lorem Ipsum placeholder text.\n\nExample:\nInput:\n(anything)\n\nOutput:\nLorem ipsum dolor sit amet..."
}
"""

import random


def main(state):
    """Generate Lorem Ipsum placeholder text."""
    words = [
        "ad", "adipisicing", "aliqua", "aliquip", "amet", "anim", "aute",
        "cillum", "commodo", "consectetur", "consequat", "culpa", "cupidatat",
        "deserunt", "do", "dolor", "dolore", "duis", "ea", "eiusmod", "elit",
        "enim", "esse", "est", "et", "eu", "ex", "excepteur", "exercitation",
        "fugiat", "id", "in", "incididunt", "ipsum", "irure", "labore",
        "laboris", "laborum", "Lorem", "magna", "minim", "mollit", "nisi",
        "non", "nostrud", "nulla", "occaecat", "officia", "pariatur", "proident",
        "qui", "quis", "reprehenderit", "sint", "sit", "sunt", "tempor",
        "ullamco", "ut", "velit", "veniam", "voluptate"
    ]

    sentence = ""
    for _ in range(100):
        pos = random.randint(0, len(words) - 2)
        sentence += words[pos] + " "

    # Capitalize first letter and add period
    sentence = sentence[0].upper() + sentence[1:].strip() + "."

    state.text = sentence
