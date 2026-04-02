#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
  "name": "Convert Number Base",
  "description": "在不同进制之间转换数字",
  "icon": "🔢",
  "tags": ["convert","number","2","8","10","16"],
  "help": "在不同进制之间转换数字，支持2-36进制\n\n首行参数格式:\nfrom_base:to_base:uppercase\n\n参数说明:\n- from_base: 输入数字的进制 (2-36)\n- to_base: 输出数字的进制 (2-36)\n- uppercase: 是否使用大写字母 (true/false，默认true)\n\n示例:\n1. 默认转换（十进制转十六进制）:\n输入:\n10\n输出:\nA\n\n2. 自定义转换（二进制转八进制）:\n输入:\n2:8\n1010\n输出:\n12\n\n3. 自定义转换（十进制转十六进制，小写）:\n输入:\n10:16:false\n255\n输出:\nff"
}
'''

def run(text):
    """
    数字进制转换
    """
    lines = text.split('\n')
    from_base = 10
    to_base = 16
    uppercase = True
    text_to_convert = text
    
    # 处理首行自定义参数
    if lines:
        first_line = lines[0].strip()
        config_parts = first_line.split(':')
        
        if len(config_parts) >= 1 and config_parts[0]:
            try:
                from_base = int(config_parts[0].strip())
                if from_base < 2 or from_base > 36:
                    from_base = 10
            except ValueError:
                pass
        
        if len(config_parts) >= 2 and config_parts[1]:
            try:
                to_base = int(config_parts[1].strip())
                if to_base < 2 or to_base > 36:
                    to_base = 16
            except ValueError:
                pass
        
        if len(config_parts) >= 3 and config_parts[2]:
            uppercase = config_parts[2].strip().lower() == 'true'
        
        # 跳过配置行
        if config_parts and config_parts[0]:
            text_to_convert = '\n'.join(lines[1:]).strip() or text
    
    # 处理多行输入
    result = []
    for line in text_to_convert.split('\n'):
        line = line.strip()
        if not line:
            result.append('')
            continue
        
        try:
            # 转换为十进制
            decimal = int(line, from_base)
            
            # 转换为目标进制
            if to_base == 10:
                converted = str(decimal)
            else:
                # 使用内置函数转换进制
                converted = ""
                if decimal == 0:
                    converted = "0"
                else:
                    # Python 3.10+ 支持直接使用 int.to_bytes 或 format，但这里使用传统方法确保兼容性
                    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
                    temp = decimal
                    while temp > 0:
                        converted = digits[temp % to_base] + converted
                        temp = temp // to_base
            
            # 处理大小写
            if uppercase:
                converted = converted.upper()
            else:
                converted = converted.lower()
            
            result.append(converted)
        except ValueError:
            result.append(line)
    
    return '\n'.join(result)

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("数字进制转换")
