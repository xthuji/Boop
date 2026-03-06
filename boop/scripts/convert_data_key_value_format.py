#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Convert Data Key Value Format",
  "description": "在键值对格式 json/url/cookie/kv 之间转换",
  "icon": "🎹",
  "tags": ["convert","data","json","url","cookie","kv","key","value"],
  "help": "在键值对格式 json/url/cookie/kv 之间转换\n\n用法：在第一行指定目标格式（可选）\n  格式：format\n\n参数说明：\n  format - 目标格式：json（默认）、url、cookie、kv（键值对）\n\n支持的输入格式：\n- JSON 格式：{\"key\": \"value\"}\n- URL 参数：key1=value1&key2=value2\n- Cookie 格式：key1=value1; key2=value2\n- 键值对格式：key1=value1\n\n示例:\n输入:\njson\nkey1=value1\nkey2=value2\n\n输出:\n{\n  \"key1\": \"value1\",\n  \"key2\": \"value2\"\n}"
}
'''

import json
import urllib.parse

def run(text):
    """
    在键值对格式 json/url/cookie/kv 之间转换
    """
    lines = text.split('\n')
    target_format = 'json'
    text_to_convert = text
    
    # 处理首行自定义参数
    format_map = {
        'json': 'json',
        'url': 'url',
        'cookie': 'cookie',
        'kv': 'kv',
        'keyvalue': 'kv',
        'key-value': 'kv'
    }
    
    if lines:
        first_line = lines[0].strip().lower()
        if first_line in format_map:
            target_format = format_map[first_line]
            text_to_convert = '\n'.join(lines[1:])
    
    # 检测输入格式
    input_format = detect_input_format(text_to_convert)
    
    try:
        # 解析输入
        json_data = parse_input(text_to_convert, input_format)
        
        # 根据目标格式转换
        if target_format == 'json':
            return format_to_json(json_data)
        elif target_format == 'url':
            return format_to_url(json_data)
        elif target_format == 'cookie':
            return format_to_cookie(json_data)
        elif target_format == 'kv':
            return format_to_key_value(json_data)
        else:
            return text
    except Exception as e:
        return text

def detect_input_format(text):
    """
    检测输入格式
    """
    trimmed = text.strip()
    
    if trimmed.startswith('{') or trimmed.startswith('['):
        return 'json'
    
    if '?' in trimmed or '&' in trimmed:
        return 'url'
    
    if '; ' in trimmed and '=' in trimmed:
        return 'cookie'
    
    if '=' in trimmed:
        return 'kv'
    
    return 'json'

def parse_input(text, format):
    """
    解析输入数据
    """
    if format == 'json':
        return json.loads(text)
    elif format == 'url':
        url_text = text
        if not text.startswith('http') and not text.startswith('?') and '&' not in text:
            url_text = 'http://example.com?' + text
        elif text.startswith('?'):
            url_text = 'http://example.com' + text
        
        parsed_url = urllib.parse.urlparse(url_text)
        url_data = {
            'url_path': parsed_url.scheme + '://' + parsed_url.netloc + parsed_url.path
        }
        
        params = urllib.parse.parse_qs(parsed_url.query)
        for key, values in params.items():
            if len(values) == 1:
                url_data[key] = values[0]
            else:
                url_data[key] = values
        
        return url_data
    elif format == 'cookie':
        cookies = {}
        parts = text.split('; ')
        
        for part in parts:
            if '=' in part:
                index = part.index('=')
                key = part[:index].strip()
                value = part[index+1:].strip()
                cookies[key] = value
        
        return cookies
    elif format == 'kv':
        kv_lines = text.split('\n')
        kv_data = {}
        
        for line in kv_lines:
            if '=' in line:
                key, *value_parts = line.split('=')
                if key:
                    kv_data[key.strip()] = '='.join(value_parts).strip()
        
        return kv_data
    else:
        return {}

def format_to_json(data):
    """
    转换为 JSON 格式
    """
    return json.dumps(data, indent=2, ensure_ascii=False)

def format_to_url(data):
    """
    转换为 URL 参数格式
    """
    url_path = ''
    query_params = []
    
    if 'url_path' in data:
        url_path = data['url_path']
        for key, value in data.items():
            if key != 'url_path':
                if isinstance(value, list):
                    for v in value:
                        query_params.append(f'{key}={urllib.parse.quote(str(v))}')
                else:
                    query_params.append(f'{key}={urllib.parse.quote(str(value))}')
    else:
        for key, value in data.items():
            if isinstance(value, list):
                for v in value:
                    query_params.append(f'{key}={urllib.parse.quote(str(v))}')
            else:
                query_params.append(f'{key}={urllib.parse.quote(str(value))}')
    
    param_str = '&'.join(query_params)
    if param_str:
        if '?' in url_path:
            return f'{url_path}&{param_str}'
        elif url_path:
            return f'{url_path}?{param_str}'
        else:
            return param_str
    else:
        return url_path

def format_to_cookie(data):
    """
    转换为 Cookie 格式
    """
    cookie_parts = []
    for key, value in data.items():
        if isinstance(value, list):
            for v in value:
                cookie_parts.append(f'{key}={v}')
        else:
            cookie_parts.append(f'{key}={value}')
    return '; '.join(cookie_parts)

def format_to_key_value(data):
    """
    转换为键值对格式
    """
    lines = []
    for key, value in data.items():
        if isinstance(value, list):
            for v in value:
                lines.append(f'{key}={v}')
        else:
            lines.append(f'{key}={value}')
    return '\n'.join(lines)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("键值对格式 json/url/cookie/kv 转换")
