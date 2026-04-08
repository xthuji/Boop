#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
{
    "name": "Manage Todo",
    "description": "管理 Todo 服务",
    "icon": "🌐",
    "tags": ["todo","manage","code"],
    "dependencies": ["pywebview"],
    "help": "管理 Todo 服务\n\n打开Todo管理页面 http://127.0.0.1:3000/"
}
'''

import os
import subprocess
import time
import urllib.request
import urllib.error
import webview


def run(state):
    """
    管理 Todo 服务
    """
    script_path = os.path.expanduser("~/script/pythonScript/manage_todo.py")

    try:
        if not os.path.exists(script_path):
            state.post_error(f"外部脚本不存在: {script_path}")
            return
        
        # 动态导入外部脚本
        import sys
        import importlib.util
        
        spec = importlib.util.spec_from_file_location("todo_manager", script_path)
        todo_manager = importlib.util.module_from_spec(spec)
        sys.modules["todo_manager"] = todo_manager
        spec.loader.exec_module(todo_manager)
        
        # 调用外部脚本的管理功能
        state.post_info("启动 Todo 服务管理")
        todo_manager.main()
        
    except Exception as e:
        state.post_error(f"管理 Todo 服务失败: {e}")


def main(state):
    """
    主函数
    """
    state.post_info("管理 Todo 服务")
    run(state)

if __name__ == '__main__':
    import lib.base as base
    main(base.State(""))