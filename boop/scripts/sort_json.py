'''
{
    "api": 1,
    "name": "排序JSON",
    "description": "排序JSON对象的键",
    "icon": "code",
    "tags": ["format", "json", "sort"],
    "help": "排序JSON对象的键\n\nExample:\nInput:\n{\"b\": 2, \"a\": 1}\n\nOutput:\n{\n  \"a\": 1,\n  \"b\": 2\n}"
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
