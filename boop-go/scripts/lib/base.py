#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class State:
    def __init__(self, text: str):
        self.text = text
    
    def post_info(self, msg):
        print(f"--- INFO: {msg}")
        # pass # 生产环境通常重定向或忽略，避免干扰控制台
    
    def post_error(self, msg):
        print(f"--- ERROR: {msg}")
        # pass