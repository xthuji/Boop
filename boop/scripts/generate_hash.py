"""
{
  "api": 1,
  "name": "Generate Hash",
  "description": "Compute hash of your text (SHA1/SHA256/SHA512)",
  "icon": "fingerprint",
  "tags": ["hash", "sha1", "sha256", "sha512"],
  "help": "Compute hash of your text.\n\nUsage: First line specifies algorithm (optional)\n  Format: algorithm\n\nParameters:\n  algorithm - Hash algorithm:\n              sha1/1    - SHA1 hash\n              sha256/256 - SHA256 hash (default)\n              sha512/512 - SHA512 hash\n\nExample:\n  sha256\n  hello world\n\n  Output:\nb94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
}
"""

import hashlib


def main(state):
    """Compute hash of text (SHA1/SHA256/SHA512)."""
    lines = state.text.split('\n')
    first_line = lines[0].strip().lower()

    # Check for help request
    if first_line in ('-h', '--help'):
        help_text = """
Compute Hash - 计算文本哈希值

用法：在第一行指定哈希算法（可选）
  格式：algorithm

参数说明：
  algorithm - 哈希算法：
              sha1/1    - SHA1 哈希
              sha256/256 - SHA256 哈希（默认）
              sha512/512 - SHA512 哈希

示例：
  sha1
  hello world

  将输出：
  2aae6c35c94fcfb415dbe95f408b9ce91ee846ed

  sha256
  hello world

  将输出：
  b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9

  sha512
  hello world

  将输出：
  309ecc489c12d6eb4cc40f50c902f2b4d0ed77ee511a7c7a9bcd3ca86d4cd86f989dd35bc5ff499670da34255b45b0cfd830e81f605dcf7dc5542e93ae9cd76f

  hello world

  将输出（默认 SHA256）：
  b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9
"""
        state.text = help_text + '\n' + '\n'.join(lines[1:])
        return

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
