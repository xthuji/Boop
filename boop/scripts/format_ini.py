#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
{
  "api": 1,
  "name": "Format INI",
  "description": "Professional INI file formatter and minifier.",
  "icon": "pineapple",
  "tags": ["ini", "format", "minify"],
  "help": "Format or minify INI file using configparser.\n\nExample:\nInput:\n[Section]\nkey=value\n\nOutput:\n[Section]\nkey = value\n\nIf the file is already formatted, it will be minified."
}
"""

import configparser

def format_code(text):
    """Format INI file using configparser."""
    if not text or not text.strip():
        return text
    
    # Use configparser for INI formatting
    try:
        cfg = configparser.ConfigParser()
        cfg.read_string(text)
        
        # Format the output
        import io
        output = io.StringIO()
        cfg.write(output)
        result = output.getvalue()
        
        # Remove default section header if it was not in the original
        import re
        if not re.search(r'^\s*\[DEFAULT\]', text, re.IGNORECASE | re.MULTILINE):
            result = re.sub(r'^\[DEFAULT\]\s*\n', '', result, flags=re.IGNORECASE)
        
        return result
    except Exception as e:
        raise Exception("Error formatting INI: {}".format(e))

def is_minified(text):
    """Check if INI is minified."""
    text = text.strip()
    return not '\n' in text and ('[' in text or '=' in text)

def minify_code(text):
    """Minify INI file."""
    if not text or not text.strip():
        return text
    
    # 移除注释
    lines = text.split('\n')
    minified_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped.startswith('!'):
            continue
        minified_lines.append(stripped)
    return ' '.join(minified_lines)

def process_format_code(text):
    """Process INI text - format or minify based on input state."""
    if not text or not text.strip():
        return text
    
    if is_minified(text):
        return format_code(text)
    else:
        return minify_code(text)

def main(state):
    """Format or minify INI file."""
    if not state.text or not state.text.strip():
        return
    
    try:
        state.text = process_format_code(state.text)
        if hasattr(state, 'post_info'):
            state.post_info("INI formatted or minified")
    except Exception as e:
        if hasattr(state, 'post_error'):
            state.post_error(str(e))

def run(text, *args):
    """Boop script entry point."""
    try:
        return process_format_code(text)
    except Exception as e:
        return "Error formatting INI: {}".format(str(e))
