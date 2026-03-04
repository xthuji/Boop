'''
{
    "api": 1,
    "name": "YAML与JSON转换",
    "description": "在YAML和JSON之间相互转换",
    "icon": "code",
    "tags": ["convert", "yaml", "json"],
    "help": "在YAML和JSON之间相互转换\n\n- 如果输入是YAML，转换为JSON\n- 如果输入是JSON，转换为YAML\n\nExample 1 (YAML to JSON):\nInput:\nname: John\nage: 30\n\nOutput:\n{\n  \"name\": \"John\",\n  \"age\": 30\n}\n\nExample 2 (JSON to YAML):\nInput:\n{\"name\": \"John\", \"age\": 30}\n\nOutput:\nname: John\nage: 30"
}
'''

import json
import yaml

def run(text):
    """
    在YAML和JSON之间相互转换
    """
    # 尝试解析为JSON
    try:
        data = json.loads(text)
        # 输入是JSON，转换为YAML
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    except json.JSONDecodeError:
        # 尝试解析为YAML
        try:
            data = yaml.safe_load(text)
            # 输入是YAML，转换为JSON
            return json.dumps(data, ensure_ascii=False, indent=2)
        except yaml.YAMLError:
            # 既不是JSON也不是YAML
            return "输入不是有效的JSON或YAML格式"

def main(state):
    """
    主函数，调用run函数处理输入文本
    """
    state.text = run(state.text)
    state.post_info("YAML与JSON转换")
