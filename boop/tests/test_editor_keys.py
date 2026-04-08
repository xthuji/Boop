#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化后的编辑器自动化测试框架
- 采用动态分发模式简化逻辑
- 补全了多光标、剪贴板及所有断言操作
- 支持原有的 test_cases.json 格式
"""

import time
import os
import sys
import tkinter as tk
import json
import argparse
from abc import ABC, abstractmethod

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 假设这些模块在您的环境中已正确配置
from app.ui.editor import Editor
from app.config.settings import BoopConfig
from app.core.shortcut_manager import shortcut_manager, CURRENT_PLATFORM_MODIFIERS
from app.core.log import logger

test_cases_file = os.path.join(os.path.dirname(__file__), 'test_cases.json')
# --- 模拟事件类 ---
class MockEvent:
    def __init__(self, keysym, char='', state=0):
        self.keysym = keysym
        self.char = char
        self.state = state

# --- 操作执行器 ---
class EditorOperationExecutor:
    """封装编辑器操作，方法名与 JSON 中的 action 对应"""
    def __init__(self, editor, results_text, root):
        self.editor = editor
        self.text_widget = editor._text_widget
        self.results_text = results_text
        self.root = root
        # 修饰键到state值的映射
        self.modifier_map = CURRENT_PLATFORM_MODIFIERS

    def _update_ui_log(self, msg):
        self.results_text.insert(tk.END, f"{msg}\n")
        self.results_text.see(tk.END)
        self.root.update()
        time.sleep(0.05)

    def _get_event(self, step):
        # 处理修饰键
        modifiers = step.get('modifiers', [])
        state = 0
        for mod in modifiers:
            if mod in self.modifier_map:
                state |= self.modifier_map[mod]
        return MockEvent(
            step.get('keysym', ''), 
            step.get('char', ''), 
            state
        )

    def _get_shotcut_str(self, step):
        modifiers = step.get('modifiers', [])
        keysym = step.get('keysym', '')
        return '+'.join(modifiers + [keysym])

    # 基础内容操作
    def set_content(self, step):
        text = step.get('text', '')
        self.editor.set_content(text)
        self._update_ui_log(f"📝 设置内容: \n{'-'*20}\n{text}\n{'-'*20}")

    def move_cursor(self, step):
        position = step.get('position', '1.0')
        self.text_widget.mark_set(tk.INSERT, position)
        self._update_ui_log(f"👆 移动光标至: {position}")

    def select_text(self, step):
        start = step.get('start', '1.0')
        end = step.get('end', '1.0')
        # 先清除旧的选择范围
        self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)
        # 添加新的选择范围
        self.text_widget.tag_add(tk.SEL, start, end)
        # 将光标设置到选择的结束位置，确保按方向键时的行为正确
        self.text_widget.mark_set(tk.INSERT, end)
        self._update_ui_log(f"↔️ 选择区域: {start} 到 {end} (光标位置: {end})")

    def clear_selection(self, step=None):
        self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)
        self._update_ui_log("🆖 清除选择")

    def set_clipboard(self, step):
        content = step.get('content', '')
        self.text_widget.clipboard_clear()
        self.text_widget.clipboard_append(content)
        self._update_ui_log(f"📋 设置剪贴板: '{content}'")

    # 方向键与编辑操作
    def on_key_press(self, step): 
        event = self._get_event(step)
        # 直接触发编辑器文本框的键盘事件
        self.text_widget.event_generate(f'<Key>', keysym=event.keysym, state=event.state)
        shortcut_str = self._get_shotcut_str(step)
        self._update_ui_log(f"⌨️🚀 按键操作: {shortcut_str}    {shortcut_str.replace('Command', '⌘').replace('Control', '^').replace('Shift', '⇧').replace('Alt', '⌥').replace('Escape', '⎋').replace('Up', '⬆️').replace('Down', '⬇️').replace('Left', '⬅️').replace('Right', '➡️')}")
    def clear_multi_cursor_state(self, step=None):
        self.editor.extensions._clear_multi_cursor_state()
        self._update_ui_log("🔄 重置多光标状态")

    def on_paste(self, step):
        """处理粘贴操作"""
        # result = self.editor.extensions._handle_multi_cursor_paste()
        # self._update_ui_log(f"📋 粘贴操作: {event.keysym} (状态: {event.state})")
        self.on_key_press(step)
        result = 'break'
        return result

    # 断言类方法 (返回 tuple: success, message)
    def assert_content(self, step):
        actual = self.editor.get_content()
        expected = step.get('expected', '')
        success = actual == expected
        return success, f"{'✅' if success else '❌'} 内容校验: {'正确' if success else f'错误 (实际: {repr(actual)})'}"

    def assert_selection(self, step):
        try: actual = self.text_widget.selection_get()
        except tk.TclError: actual = ""
        expected = step.get('expected', '')
        success = actual == expected
        return success, f"{'✅' if success else '❌'} 选中校验: {'正确' if success else f'错误 (实际: {repr(actual)})'}"

    def assert_multi_cursor_selections(self, step):
        actual_count = len(self.editor.extensions.get_selections())
        expected_count = step.get('expected_count', 0)
        success = actual_count == expected_count
        return success, f"{'✅' if success else '❌'} 多光标数: {actual_count}/{expected_count}"

    def assert_shortcut(self, step):
        event = self._get_event(step)
        # 根据 modifiers 和 keysym 构建 shortcut 字符串
        modifiers = step.get('modifiers', [])
        keysym = step.get('keysym', '')
        # 构建快捷键字符串
        shortcut_parts = modifiers + [keysym]
        shortcut = '+'.join(shortcut_parts)
        res = shortcut_manager.is_shortcut_pressed(event, shortcut)
        exp = step.get('expected', True)
        success = res == exp
        return success, f"{'✅' if success else '❌'} 快捷键 {shortcut} 校验: {'正确' if success else '错误'}"

    def assert_cursor_position(self, step):
        actual = self.text_widget.index(tk.INSERT)
        expected = step.get('expected', '1.0')
        success = actual == expected
        return success, f"{'✅' if success else '❌'} 光标位置校验: {'正确' if success else f'错误 (实际: {actual})'}"

    def assert_char_count(self, step):
        actual = self.editor.get_char_count()
        expected = step.get('expected', 0)
        success = actual == expected
        return success, f"{'✅' if success else '❌'} 字符计数校验: {actual}/{expected}"

# --- 测试用例逻辑 ---
class TestCase(ABC):
    def __init__(self, name):
        self.name = name
        self.passed = 0
        self.failed = 0

    @abstractmethod
    def run(self, editor, results_text, root): pass

class ConfigurableTestCase(TestCase):
    def __init__(self, name, test_config):
        super().__init__(name)
        self.test_config = test_config
        self.failures = []

    def run(self, editor, results_text, root):
        self._log(results_text, f"\n\n{'='*50}\n🧪🔬 测试 {self.name}...\n", root)
        executor = EditorOperationExecutor(editor, results_text, root)
        # 添加调试信息，显示初始内容
        self._log(results_text, f"初始内容: '{executor.editor.get_content()}'", root)

        for i, step in enumerate(self.test_config.get('steps', [])):
            action = step.get('action')
            handler = getattr(executor, action, None)

            if handler:
                if action.startswith('assert_'):
                    success, msg = handler(step)
                    # Extract expected and actual values for failure reporting
                    expected = step.get('expected')
                    actual = None
                    if action == 'assert_content':
                        actual = executor.editor.get_content()
                    elif action == 'assert_selection':
                        try:
                            actual = executor.text_widget.selection_get()
                        except tk.TclError:
                            actual = ""
                    elif action == 'assert_multi_cursor_selections':
                        actual = len(executor.editor.extensions.get_selections())
                    elif action == 'assert_cursor_position':
                        actual = executor.text_widget.index(tk.INSERT)
                    self._update_counters(success, step, actual, expected, i+1)
                    self._log(results_text, msg, root)
                elif action == 'handle_multi_cursor_paste':
                    res = handler(step)
                    if 'expected_result' in step:
                        success = (res == step['expected_result'])
                        self._update_counters(success, step, res, step['expected_result'], i+1)
                        self._log(results_text, f"粘贴返回校验: {res}", root)
                else:
                    try:
                        handler(step)
                    except Exception as e:
                        # 捕获并记录执行操作时的异常
                        self.failed += 1
                        failure_info = {
                            'step': action,
                            'step_number': i+1,
                            'expected': None,
                            'actual': f"执行异常: {str(e)}",
                            'details': step.get('text', '')
                        }
                        self.failures.append(failure_info)
                        self._log(results_text, f"❌: 执行 {action} 时发生异常: {str(e)}", root)
            elif action == 'comment':
                self._log(results_text, f"ℹ️: {step.get('text', '')}", root)
            else:
                # 记录未识别的操作
                self._log(results_text, f"⚠️: 未识别的操作: {action}", root)
        
        return self.passed, self.failed

    def _update_counters(self, success, step=None, actual=None, expected=None, step_number=None):
        if success:
            self.passed += 1
        else:
            self.failed += 1
            if step:
                failure_info = {
                    'step': step.get('action'),
                    'step_number': step_number,
                    'expected': expected,
                    'actual': actual,
                    'details': step.get('text', '')
                }
                self.failures.append(failure_info)

    def _log(self, widget, msg, root):
        widget.insert(tk.END, f"{msg}\n")
        widget.see(tk.END)
        root.update()

# --- 主运行器 ---
class TestRunner:
    def __init__(self):
        self.test_cases = []
        self.results_text = None

    def create_ui(self):
        root = tk.Tk()
        root.title("Boop 自动化测试框架 (优化版)")
        root.geometry("1100x800")
        
        pw = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        pw.pack(fill=tk.BOTH, expand=True)

        # 左侧：编辑器
        e_frame = tk.Frame(pw); pw.add(e_frame, width=600)
        # 右侧：结果
        r_frame = tk.Frame(pw, bg="#f8f9fa"); pw.add(r_frame, width=500)
        
        tk.Label(r_frame, text="测试控制台", font=('Arial', 12, 'bold')).pack(pady=5)
        self.results_text = tk.Text(r_frame, font=('Consolas', 10), wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 初始化编辑器
        config = BoopConfig()
        editor = Editor(e_frame, config)
        editor.focus()
        
        return root, editor

    def run_all(self):
        root, editor = self.create_ui()
        total_p = total_f = 0
        all_failures = []
        
        for case in self.test_cases:
            p, f = case.run(editor, self.results_text, root)
            total_p += p; total_f += f
            if case.failures:
                all_failures.append((case.name, case.failures))
            time.sleep(0.5)

        summary = f"\n测试汇总\n{'-'*30}\n通过: {total_p}\n失败: {total_f}\n"
        self.results_text.insert(tk.END, summary)
        print(summary)

        # Print detailed failure information
        if total_f > 0:
            failure_details = "\n失败详情:\n" + "-"*50 + "\n"
            for case_name, failures in all_failures:
                failure_details += f"测试用例: {case_name}\n"
                for i, failure in enumerate(failures, 1):
                    step_info = f"步骤 {failure.get('step_number', '?')}" if 'step_number' in failure else f"失败 {i}"
                    failure_details += f"  {step_info}: {failure['step']}\n"
                    if failure['expected'] is not None:
                        failure_details += f"    期望: {repr(failure['expected'])}\n"
                    if failure['actual'] is not None:
                        failure_details += f"    实际: {repr(failure['actual'])}\n"
                    if failure['details']:
                        failure_details += f"    详情: {failure['details']}\n"
                failure_details += "\n"
            self.results_text.insert(tk.END, failure_details)
            print(failure_details)
        else:
            self.results_text.insert(tk.END, "\n✓ 所有测试已通过！")
        
        root.after(1000, root.destroy)
        root.mainloop()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cases', nargs='*', help='指定要运行的测试用例名')
    args = parser.parse_args()

    if not os.path.exists(test_cases_file):
        print(f"错误: 找不到 {test_cases_file} 配置文件")
        return

    with open(test_cases_file, 'r', encoding='utf-8') as f:
        all_configs = json.load(f)

    runner = TestRunner()
    selected = args.cases if args.cases else all_configs.keys()
    
    for name in selected:
        if name in all_configs:
            runner.test_cases.append(ConfigurableTestCase(name, all_configs[name]))

    runner.run_all()

if __name__ == "__main__":
    main()