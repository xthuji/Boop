#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
    "name": "Sort JSON",
    "description": "对 JSON 对象的键进行排序",
    "icon": "↕️",
    "tags": ["json","sort","code"],
    "help": "对 JSON 对象的键进行字母排序\n\n示例:\n输入:\n{\"z\": 1, \"a\": 2, \"m\": 3}\n\n输出:\n{\"a\": 2, \"m\": 3, \"z\": 1}"
}
'''

import json

def sort_json(obj):
    """
    递归排序JSON对象的键
    """
    if isinstance(obj, dict):
        return {k: sort_json(v) for k, v in sorted(obj.items())}
    elif isinstance(obj, list):
        return [sort_json(item) for item in obj]
    else:
        return obj

def run(text):
    """
    排序JSON对象的键
    """
    try:
        data = json.loads(text)
        sorted_data = sort_json(data)
        return json.dumps(sorted_data, ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return "无效的JSON格式"

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("排序JSON")
