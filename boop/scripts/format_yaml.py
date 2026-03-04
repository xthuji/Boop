#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format YAML",
  "description": "Professional YAML code formatter and minifier.",
  "icon": "pineapple",
  "tags": ["yaml", "format", "minify"],
  "dependencies": ["PyYAML"],
  "help": "Format or minify YAML text using PyYAML.\n\nExample:\nInput:\nname: John\nage: 30\n\nOutput:\nname: John\nage: 30\n\nIf the YAML is already formatted, it will be minified."
}
"""

import yaml
import re

def is_minified(text):
    """Check if YAML is minified."""
    text = text.strip()
    return not '\n' in text and (':' in text)

def minify_code(text):
    """Minify YAML text."""
    if not text or not text.strip():
        return text
    
    # 移除注释
    lines = text.split('\n')
    minified_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        minified_lines.append(stripped)
    return ' '.join(minified_lines)

def format_code(text):
    """Format YAML text using PyYAML."""
    if not text or not text.strip():
        return text
    
    # 预处理：确保冒号后面有空格
    text = re.sub(r'([a-zA-Z0-9_]+):([^\s])', r'\1: \2', text)
    
    # Use PyYAML for YAML formatting
    try:
        data = yaml.safe_load(text)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True, indent=2, sort_keys=False)
    except Exception as e:
        raise Exception("Error formatting YAML: {}".format(e))

def process_format_code(text):
    """Process YAML text - format or minify based on input state."""
    if not text or not text.strip():
        return text
    
    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)

def main(state):
    """Format or minify YAML text."""
    if not state.text or not state.text.strip():
        return
    
    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("YAML formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))
        else:
            print("Error formatting YAML: {}".format(str(e)))

def run(text, *args):
    """Boop script entry point."""
    try:
        return process_format_code(text)
    except Exception as e:
        return "Error formatting YAML: {}".format(str(e))
