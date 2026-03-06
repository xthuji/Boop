#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{
  "name": "Format YAML",
  "description": "格式化 YAML 文档",
  "icon": "✨",
  "tags": ["yaml","format","fmt","code"],
  "dependencies": ["pyyaml"],
  "help": "格式化 YAML 文档\n\n示例:\n输入:\nname: John\nage: 30\n\n输出:\nname: John\nage: 30"
}"""

import yaml

def format_code(text):
    """Format YAML text using PyYAML."""
    if not text or not text.strip():
        return text

    # 预处理：确保冒号后面有空格
    import re
    text = re.sub(r'([a-zA-Z0-9_]+):([^\s])', r'\1: \2', text)

    # Use PyYAML for YAML formatting
    try:
        data = yaml.safe_load(text)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, indent=2, sort_keys=False)
    except Exception as e:
        raise Exception("Error formatting YAML: {}".format(e))

def main(state):
    """Format YAML text."""
    if not state.text or not state.text.strip():
        return

    try:
        state.text = format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("YAML formatted")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))
        else:
            print("Error formatting YAML: {}".format(str(e)))
