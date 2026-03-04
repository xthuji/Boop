#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "JSON to Code",
  "description": "在 JSON 和代码之间转换",
  "icon": "code",
  "tags": ["convert","json","code"],
  "help": "在 JSON 和 JavaScript 代码之间转换\n\n示例:\n输入:\n{\"name\": \"John\", \"age\": 30}\n\n输出:\nconst data = {\n  \"name\": \"John\",\n  \"age\": 30\n};"
}
'''

import json

def run(text):
    """
    在JSON和代码之间转换
    """
    try:
        # 尝试解析为JSON
        data = json.loads(text)
        # 转换为JavaScript对象
        code = "const data = "
        code += json.dumps(data, ensure_ascii=False, indent=2)
        code += ";"
        return code
    except json.JSONDecodeError:
        # 尝试从代码中提取JSON
        try:
            # 简单处理：查找大括号包围的内容
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                json_str = text[start:end+1]
                data = json.loads(json_str)
                return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            pass
    
    return text

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("JSON与代码转换")
