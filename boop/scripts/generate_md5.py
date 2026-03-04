"""
{
  "api": 1,
  "name": "Generate MD5",
  "description": "Computes the MD5 checksum of your text (Hex encoded)",
  "icon": "fingerprint",
  "tags": ["md5", "hash", "checksum"],
  "help": "Computes the MD5 checksum of your text.\n\nExample:\nInput:\nhello world\n\nOutput:\n5eb63bbbe01eeed093cb22bb8f5acdc3"
}
"""

import hashlib


def main(state):
    """Compute MD5 checksum of text."""
    text_bytes = state.text.encode('utf-8')
    md5_hash = hashlib.md5(text_bytes).hexdigest()
    state.text = md5_hash
    state.post_info("MD5 computed")
