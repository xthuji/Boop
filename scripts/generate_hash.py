#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Generate Hash",
  "description": "计算文本的哈希值 (SHA1/SHA256/SHA512)",
  "icon": "📄",
  "tags": ["hash","sha1","sha256","sha512","code"],
  "help": "计算文本的哈希值\n\n用法：在第一行指定哈希算法 (可选)\n  格式：algorithm\n\n参数说明:\n  algorithm - 哈希算法:\n              sha1/1    - SHA1 哈希\n              sha256/256 - SHA256 哈希 (默认)\n              sha512/512 - SHA512 哈希\n\n示例:\n  sha1\n  hello world\n\n  将输出:\n  2aae6c35c94fcfb415dbe95f408b9ce91ee846ed"
}"""

import hashlib


def main(state):
    """Compute hash of text (SHA1/SHA256/SHA512)."""
    lines = state.text.split('\n')
    first_line = lines[0].strip().lower()

    algorithm = 'sha256'
    text_to_hash = state.text

    algorithm_map = {
        'sha1': 'sha1',
        '1': 'sha1',
        'sha256': 'sha256',
        '256': 'sha256',
        'sha512': 'sha512',
        '512': 'sha512'
    }

    if first_line in algorithm_map:
        algorithm = algorithm_map[first_line]
        text_to_hash = '\n'.join(lines[1:])

    try:
        text_bytes = text_to_hash.encode('utf-8')

        if algorithm == 'sha1':
            hash_result = hashlib.sha1(text_bytes).hexdigest()
        elif algorithm == 'sha256':
            hash_result = hashlib.sha256(text_bytes).hexdigest()
        elif algorithm == 'sha512':
            hash_result = hashlib.sha512(text_bytes).hexdigest()
        else:
            hash_result = hashlib.sha256(text_bytes).hexdigest()

        state.text = hash_result
    except Exception as e:
        state.post_error(f'计算哈希失败：{e}')
