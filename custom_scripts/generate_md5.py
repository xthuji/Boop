#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Generate MD5",
  "description": "计算文本的 MD5 哈希值",
  "icon": "📄",
  "tags": ["hash","md5","code"],
  "help": "计算文本的 MD5 哈希值\n\n示例:\n输入:\nhello world\n\n输出:\n5eb63bbbe01eeed093cb22bb8f5acdc3"
}"""

import hashlib


def main(state):
    """Compute MD5 checksum of text."""
    text_bytes = state.text.encode('utf-8')
    md5_hash = hashlib.md5(text_bytes).hexdigest()
    state.text = md5_hash
    state.post_info("MD5 computed")
