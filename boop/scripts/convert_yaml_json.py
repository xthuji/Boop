#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
    "name": "Convert YAML JSON",
    "description": "在 YAML 和 JSON 之间相互转换",
    "icon": "💊",
    "tags": ["convert","yaml","json","code","data"],
    "help": "在 YAML 和 JSON 之间相互转换\n\n首行参数格式:\nformat (指定转换模式)\n\n支持的模式:\n- json/j: 强制转换为 JSON\n- yaml/y: 强制转换为 YAML\n- toggle/t: 自动检测并切换格式 (默认)\n\n示例 1 (强制转换为 JSON):\n输入:\njson\nname: John\nage: 30\n\n输出:\n{\n  \"name\": \"John\",\n  \"age\": 30\n}\n\n示例 2 (强制转换为 YAML):\n输入:\nyaml\n{\"name\": \"John\", \"age\": 30}\n\n输出:\nname: John\nage: 30"
}
'''

import json
import yaml

def run(text):
    """
    在YAML和JSON之间相互转换
    """
    lines = text.split('\n')
    mode = 'toggle'
    text_to_convert = text
    
    # 模式映射
    mode_map = {
        'json': 'json',
        'j': 'json',
        'yaml': 'yaml',
        'y': 'yaml',
        'toggle': 'toggle',
        't': 'toggle'
    }
    
    # 处理首行自定义参数
    if lines:
        first_line = lines[0].strip().lower()
        if mode_map.get(first_line):
            mode = mode_map[first_line]
            text_to_convert = '\n'.join(lines[1:])
    
    try:
        if mode == 'json':
            # 强制转换为JSON
            data = yaml.safe_load(text_to_convert)
            return json.dumps(data, ensure_ascii=False, indent=2)
        elif mode == 'yaml':
            # 强制转换为YAML
            data = json.loads(text_to_convert)
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
        else:
            # 自动检测并切换格式
            input_format = detect_input_format(text_to_convert)
            if input_format == 'yaml':
                data = yaml.safe_load(text_to_convert)
                return json.dumps(data, ensure_ascii=False, indent=2)
            else:
                data = json.loads(text_to_convert)
                return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        return f"转换失败: {str(e)}"

def detect_input_format(text):
    """
    检测输入格式
    """
    trimmed = text.strip()
    
    # 检测是否为JSON格式
    if (trimmed.startswith('{') and trimmed.endswith('}')) or \
       (trimmed.startswith('[') and trimmed.endswith(']')):
        try:
            json.loads(trimmed)
            return 'json'
        except json.JSONDecodeError:
            # 不是有效的JSON，尝试检测为YAML
            pass
    
    # 检测是否为YAML格式
    if ':\n' in trimmed or ':\r\n' in trimmed or \
       (any('-' in line.strip() for line in trimmed.split('\n')) and ':' in trimmed):
        try:
            yaml.safe_load(trimmed)
            return 'yaml'
        except yaml.YAMLError:
            # 不是有效的YAML
            pass
    
    # 默认假设为YAML格式
    return 'yaml'

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("YAML与JSON转换")
