#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Convert Time Format",
  "description": "在不同时间格式之间转换",
  "icon": "⏰",
  "tags": ["convert","time","iso","date","datetime","dt","timestamp","ts"],
  "help": "在不同时间格式之间转换，支持多种时间格式\n\n首行参数格式:\n1. cycle 或 c (循环模式)\n2. output_format (仅指定输出格式)\n3. input_format:output_format (指定输入和输出格式)\n\n支持的格式:\n- iso: ISO 格式 (2022-12-25T12:00:00.000000+00:00)\n- date: 日期格式 (2022-12-25)\n- time: 时间格式 (12:00:00)\n- datetime: 日期时间格式 (2022-12-25 12:00:00)\n- datetime-ms: 带毫秒的日期时间格式\n- timestamp: 10位时间戳 (秒)\n- timestamp-ms: 13位时间戳 (毫秒)\n- slashes: 带斜杠的日期时间格式 (2022/12/25 12:00:00)\n- us: 美国格式 (12/25/2022 12:00:00)\n- eu: 欧洲格式 (25/12/2022 12:00:00)\n\n示例 1 (默认转换 - 时间戳转日期时间):\n输入:\n1671979200\n输出:\n2022-12-25 12:00:00\n\n示例 2 (指定输出格式 - 日期时间转13位时间戳):\n输入:\ntimestamp-ms\n2022-12-25 12:00:00\n输出:\n1671979200000\n\n示例 3 (循环模式):\n输入:\ncycle\n2022-12-25 12:00:00\n输出:\n1671979200"
}
'''

from datetime import datetime
import re

def run(text):
    """
    时间格式转换
    """
    lines = text.split('\n')
    output_format = None
    input_format = None
    text_to_convert = text
    cycle_mode = False
    
    # 定义格式映射
    formats = {
        'iso': '%Y-%m-%dT%H:%M:%S.%f%z',
        'date': '%Y-%m-%d',
        'time': '%H:%M:%S',
        'datetime': '%Y-%m-%d %H:%M:%S',
        'dt': '%Y-%m-%d %H:%M:%S',
        'datetime-ms': '%Y-%m-%d %H:%M:%S.%f',
        'timestamp': 'timestamp10',
        'ts': 'timestamp10',
        'timestamp-ms': 'timestamp13',
        'slashes': '%Y/%m/%d %H:%M:%S',
        'us': '%m/%d/%Y %H:%M:%S',
        'eu': '%d/%m/%Y %H:%M:%S',
        'hms': '%H:%M:%S'
    }
    
    # 循环格式顺序
    cycle_formats = [
        'datetime',
        'timestamp',
        'date',
        'time',
        'datetime-ms',
        'timestamp-ms',
        'slashes',
        'iso'
    ]
    
    # 格式别名
    format_aliases = {
        '1': 'timestamp',
        '2': 'datetime',
        '3': 'date',
        '4': 'time',
        '5': 'datetime-ms',
        '6': 'timestamp-ms',
        '7': 'slashes',
        '8': 'iso',
        'ts': 'timestamp',
        'dt': 'datetime',
        'd': 'date',
        't': 'time',
        'dms': 'datetime-ms',
        'tms': 'timestamp-ms',
        's': 'slashes',
        'i': 'iso'
    }
    
    # 处理首行自定义参数
    if lines and len(lines) > 1:
        first_line = lines[0].strip()
        
        if first_line == 'cycle' or first_line == 'c':
            cycle_mode = True
            text_to_convert = '\n'.join(lines[1:])
        elif ':' in first_line:
            parts = first_line.split(':')
            if len(parts) == 2:
                input_format = resolve_format_alias(parts[0].strip(), format_aliases)
                output_format = resolve_format_alias(parts[1].strip(), format_aliases)
                text_to_convert = '\n'.join(lines[1:])
        elif first_line in format_aliases or first_line in formats:
            output_format = resolve_format_alias(first_line, format_aliases)
            text_to_convert = '\n'.join(lines[1:])
    
    # 处理多行输入
    result = []
    for line in text_to_convert.split('\n'):
        line = line.strip()
        if not line:
            result.append('')
            continue
        
        # 检查是否包含行内格式指定
        if ':' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                time_str = ':'.join(parts[:-1])
                custom_format = parts[-1].strip()
                dt = parse_time(time_str)
                if dt:
                    fmt = formats.get(custom_format, custom_format)
                    converted = format_date(dt, fmt)
                    result.append(converted)
                    continue
        
        # 检测时间格式
        format_type = detect_time_format(line)
        
        # 处理时间与秒数的转换
        if format_type == 'hms':
            converted = str(time_to_seconds(line))
            result.append(converted)
            continue
        elif format_type == 'seconds':
            try:
                converted = seconds_to_time(int(line))
                result.append(converted)
                continue
            except ValueError:
                pass
        
        # 尝试解析时间
        dt = parse_time(line)
        if not dt:
            # 尝试使用更宽松的解析方式
            try:
                # 尝试解析为日期时间
                import dateutil.parser
                dt = dateutil.parser.parse(line)
            except Exception:
                result.append(line)
                continue
        
        # 处理输出格式
        if output_format:
            fmt = formats.get(output_format, output_format)
            converted = format_date(dt, fmt)
            result.append(converted)
        elif cycle_mode:
            current_format = detect_format_in_cycle(line, cycle_formats, formats)
            if current_format:
                next_format = get_next_format(current_format, cycle_formats)
                fmt = formats.get(next_format, next_format)
                converted = format_date(dt, fmt)
                result.append(converted)
            else:
                result.append(line)
        else:
            # 默认转换
            if format_type in ['timestamp10', 'timestamp13']:
                converted = format_date(dt, formats['datetime'])
            else:
                converted = format_date(dt, formats['timestamp'])
            result.append(converted)
    
    return '\n'.join(result)

def resolve_format_alias(alias, format_aliases):
    """
    解析格式别名
    """
    return format_aliases.get(alias, alias)

def parse_time(time_str):
    """
    解析时间字符串
    """
    trimmed = time_str.strip()
    
    # 尝试解析为时间戳
    if re.match(r'^\d+$', trimmed):
        num = int(trimmed)
        length = len(trimmed)
        
        if length == 10:
            return datetime.fromtimestamp(num)
        elif length == 13:
            return datetime.fromtimestamp(num / 1000)
        else:
            return datetime.fromtimestamp(num)
    
    # 尝试解析为日期时间字符串
    date_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f%z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S',
        '%m/%d/%Y %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%m/%d/%Y',
        '%d/%m/%Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(trimmed, fmt)
        except ValueError:
            continue
    
    # 尝试使用 ISO 格式解析
    try:
        return datetime.fromisoformat(trimmed)
    except ValueError:
        pass
    
    return None

def format_date(date, format_str):
    """
    格式化日期
    """
    if format_str == 'timestamp10':
        return str(int(date.timestamp()))
    elif format_str == 'timestamp13':
        return str(int(date.timestamp() * 1000))
    else:
        try:
            return date.strftime(format_str)
        except ValueError:
            return str(date)

def detect_time_format(time_str):
    """
    检测时间格式
    """
    trimmed = time_str.strip()
    
    if re.match(r'^\d{10}$', trimmed):
        return 'timestamp10'
    elif re.match(r'^\d{13}$', trimmed):
        return 'timestamp13'
    elif re.match(r'^\d{1,2}:\d{2}(:\d{2})?$', trimmed):
        return 'hms'
    elif re.match(r'^\d+$', trimmed):
        # 检查是否是 10 位时间戳
        if len(trimmed) == 10:
            return 'timestamp10'
        return 'seconds'
    else:
        return 'datestring'

def detect_format_in_cycle(time_str, cycle_formats, formats):
    """
    检测循环中的格式
    """
    trimmed = time_str.strip()
    
    if re.match(r'^\d{10}$', trimmed):
        return 'timestamp'
    elif re.match(r'^\d{13}$', trimmed):
        return 'timestamp-ms'
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', trimmed):
        return 'datetime'
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}$', trimmed):
        return 'datetime-ms'
    elif re.match(r'^\d{4}-\d{2}-\d{2}$', trimmed):
        return 'date'
    elif re.match(r'^\d{2}:\d{2}:\d{2}$', trimmed):
        return 'time'
    elif re.match(r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$', trimmed):
        return 'slashes'
    elif re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', trimmed):
        return 'iso'
    
    return None

def get_next_format(current_format, cycle_formats):
    """
    获取下一个格式
    """
    index = cycle_formats.index(current_format) if current_format in cycle_formats else -1
    if index == -1:
        return cycle_formats[0]
    next_index = (index + 1) % len(cycle_formats)
    return cycle_formats[next_index]

def time_to_seconds(duration_text):
    """
    将时间字符串转换为秒数
    """
    parts = str(duration_text).split(':')
    hours = int(parts[0]) if len(parts) > 0 else 0
    minutes = int(parts[1]) if len(parts) > 1 else 0
    seconds = int(parts[2]) if len(parts) > 2 else 0
    return hours * 3600 + minutes * 60 + seconds

def seconds_to_time(seconds):
    """
    将秒数转换为时间字符串
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return "{0}:{1:02d}:{2:02d}".format(hours, minutes, secs)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("时间格式转换")
