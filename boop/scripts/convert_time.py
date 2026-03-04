'''
{
    "api": 1,
    "name": "时间格式转换",
    "description": "在不同时间格式之间转换",
    "icon": "time",
    "tags": ["convert", "time"],
    "help": "在不同时间格式之间转换\n\n支持的格式：\n- 时间戳（秒）\n- 日期时间字符串（如：2023-12-25 12:00:00）\n\nExample 1 (时间戳转日期时间):\nInput:\n1671979200\n\nOutput:\n日期时间: 2022-12-25 12:00:00\n时间戳(秒): 1671979200\n时间戳(毫秒): 1671979200000\n\nExample 2 (日期时间转时间戳):\nInput:\n2022-12-25 12:00:00\n\nOutput:\n时间戳(秒): 1671979200\n时间戳(毫秒): 1671979200000\n标准格式: 2022-12-25 12:00:00"
}
'''

import re
from datetime import datetime

def run(text):
    """
    时间格式转换
    """
    # 尝试解析为时间戳
    timestamp_match = re.search(r'\b(\d{9,13})\b', text)
    if timestamp_match:
        timestamp = int(timestamp_match.group(1))
        # 处理毫秒时间戳
        if timestamp > 10**12:
            timestamp = timestamp / 1000
        
        # 转换为日期时间
        dt = datetime.fromtimestamp(timestamp)
        result = f"日期时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"时间戳(秒): {int(timestamp)}\n"
        result += f"时间戳(毫秒): {int(timestamp * 1000)}"
        return result
    
    # 尝试解析为日期时间字符串
    date_formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S',
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%H:%M:%S'
    ]
    
    for fmt in date_formats:
        try:
            dt = datetime.strptime(text.strip(), fmt)
            timestamp = dt.timestamp()
            result = f"时间戳(秒): {int(timestamp)}\n"
            result += f"时间戳(毫秒): {int(timestamp * 1000)}\n"
            result += f"标准格式: {dt.strftime('%Y-%m-%d %H:%M:%S')}"
            return result
        except ValueError:
            continue
    
    return "无法解析的时间格式"

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("时间格式转换")
