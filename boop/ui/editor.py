"""
Editor Component - Text editor with line numbers and syntax highlighting
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, List, Dict, Any
from boop.core.shortcut_manager import shortcut_manager, CURRENT_PLATFORM_MODIFIERS
from boop.ui.editor_extensions import EditorExtensions
from boop.core.log import logger

class Editor:
    """带有行号和语法高亮功能的文本编辑器组件。"""

    def __init__(self, parent: tk.Widget, config):
        self.parent = parent
        self.config = config
        
        # UI 组件初始化
        self._text_widget: Optional[tk.Text] = None
        self._line_numbers: Optional[tk.Text] = None
        self._scrollbar: Optional[ttk.Scrollbar] = None
        
        # 撤销/重做历史
        self._history: List[str] = []
        self._history_index = -1
        
        # 脚本执行历史
        self._script_history: List[Dict[str, Any]] = []
        self._current_script_history_index = -1
        
        self._create_ui()
        
        # 初始化扩展与事件
        self.extensions = EditorExtensions(self._text_widget, self.config, self)
        self._bind_events()
        
        # 初始状态同步
        self._update_line_numbers()
        self._save_state()

    def _create_ui(self):
        """构建编辑器用户界面。"""
        frame = tk.Frame(self.parent)
        frame.pack(fill=tk.BOTH, expand=True)

        self._scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 行号栏配置
        self._line_numbers = tk.Text(
            frame, width=4, padx=5, pady=2,
            bg='#f0f0f0', fg='#666666',
            font=(self.config.font_family, self.config.font_size),
            state=tk.DISABLED, relief=tk.FLAT, takefocus=0
        )
        self._line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # 主文本框配置
        self._text_widget = tk.Text(
            frame, font=(self.config.font_family, self.config.font_size),
            wrap=tk.WORD, relief=tk.FLAT, undo=False, # 使用自定义撤销逻辑
            borderwidth=0, highlightthickness=0, padx=5, pady=2
        )
        self._text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 滚动联动
        self._scrollbar.config(command=self._sync_scroll)
        self._text_widget.config(yscrollcommand=self._scrollbar.set)
        self._line_numbers.config(yscrollcommand=self._scrollbar.set)

    def _move_to_start(self, event=None):
        """移动到文档开头。"""
        self._text_widget.mark_set(tk.INSERT, '1.0')
        return 'break'

    def _move_to_end(self, event=None):
        """移动到文档结尾。"""
        # 移动到文档的最后一个字符位置
        self._text_widget.mark_set(tk.INSERT, 'end-1c')
        return 'break'

    def _select_to_start(self, event=None):
        """选择到文档开头。"""
        # 确保选择包含当前行的内容，选择到当前行的结尾
        insert_pos = self._text_widget.index(tk.INSERT)
        # 移动到当前行的结尾
        line_end = self._text_widget.index('insert lineend')
        self._text_widget.tag_add(tk.SEL, '1.0', line_end)
        return 'break'

    def _select_to_end(self, event=None):
        """选择到文档结尾。"""
        # 确保选择包含当前行的内容
        insert_pos = self._text_widget.index(tk.INSERT)
        self._text_widget.tag_add(tk.SEL, insert_pos, 'end-1c')
        return 'break'

    def _paste(self, event=None):
        """处理粘贴操作。"""
        # 如果处于多光标模式，使用扩展的粘贴方法
        if hasattr(self.extensions, '_state') and len(self.extensions._state.selections) > 1:
            return self.extensions._handle_multi_cursor_paste()
        # 否则使用默认粘贴
        try:
            self._text_widget.event_generate('<<Paste>>')
        except Exception as e:
            pass
        return 'break'

    def _on_escape_key(self, event=None):
        """处理 Escape 键，兼容单光标和多光标模式。"""
        try:
            # 检查是否处于多光标模式
            if hasattr(self.extensions, '_state') and len(self.extensions._state.selections) > 1:
                # 多光标模式，清除多光标状态
                self.extensions._clear_multi_cursor_state()
                # 清除选区
                self._text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            else:
                # 单光标模式，清除选区并保持光标位置
                cursor_pos = self._text_widget.index(tk.INSERT)
                self._text_widget.tag_remove(tk.SEL, '1.0', tk.END)
                self._text_widget.mark_set(tk.INSERT, cursor_pos)
        except Exception as e:
            pass
        return 'break'

    def _bind_events(self):
        """绑定键盘、鼠标及自定义事件。"""
        tw = self._text_widget
        
        tw.bind('<<Modified>>', self._on_modified)

        # 统一绑定编辑器快捷键
        shortcut_configs = {
            'select_next_occurrence': { 'keys': ['Ctrl+d'], 'action': self._select_next_occurrence },
            'move_to_start': { 'keys': ['Ctrl+Home'], 'action': self._move_to_start },
            'move_to_end': { 'keys': ['Ctrl+End'], 'action': self._move_to_end },
            'select_to_start': { 'keys': ['Ctrl+Shift+Home'], 'action': self._select_to_start },
            'select_to_end': { 'keys': ['Ctrl+Shift+End'], 'action': self._select_to_end },
            'paste': { 'keys': ['Control+v'], 'action': self._paste },
            'undo': { 'keys': ['Control+z'], 'action': self._undo },
            'redo': { 'keys': ['Control+Shift+Z'], 'action': self._redo },
            'indent': { 'keys': ['Tab'], 'action': self._indent },
            'outdent': { 'keys': ['Shift+Tab'], 'action': self._outdent }
        }
        shortcut_manager.bind_editor_shortcuts(tw, self.config, shortcut_configs)
        
        # 方向键导航 (优化：统一处理逻辑)
        tw.bind('<Left>', lambda e: self._handle_nav_key(e, "start"))
        tw.bind('<Up>', lambda e: self._handle_nav_key(e, "start"))
        tw.bind('<Right>', lambda e: self._handle_nav_key(e, "end"))
        tw.bind('<Down>', lambda e: self._handle_nav_key(e, "end"))

        # 滚轮事件同步
        tw.bind('<MouseWheel>', self._on_mousewheel)
        self._line_numbers.bind('<MouseWheel>', self._on_mousewheel)

        # 扩展插件事件
        tw.bind('<Key>', self.extensions.on_key_press)
        
        # Escape 键清除选区并保持光标位置（绑定在通用 Key 事件之后，优先执行）
        tw.bind('<Escape>', self._on_escape_key)

    def _handle_nav_key(self, event, target_pos_type: str):
        """
        统一处理方向键逻辑。
        target_pos_type: "start" (左/上) 或 "end" (右/下)
        """
        # 如果处于多光标模式，清除状态
        if hasattr(self.extensions, '_state') and len(self.extensions._state.selections) > 1:
            self.extensions._clear_multi_cursor_state()
            # 清除选区
            self._text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            return None

        # 检查是否有选区
        try:
            sel_start = self._text_widget.index(tk.SEL_FIRST)
            sel_end = self._text_widget.index(tk.SEL_LAST)
            insert_pos = self._text_widget.index(tk.INSERT)
        except tk.TclError:
            # 无选区，正常移动
            self.extensions._clear_multi_cursor_state()
            return None

        # 如果按住 Shift，交给系统默认处理（扩展选区）
        if event.state & CURRENT_PLATFORM_MODIFIERS['Shift']:
            return None

        target_index = sel_start if target_pos_type == "start" else sel_end

        # 如果光标已经在目标边界，取消选区并正常移动
        if insert_pos == target_index:
            self._text_widget.tag_remove(tk.SEL, '1.0', tk.END)
            self.extensions._clear_multi_cursor_state()
            return None
        
        # 否则，移动光标到边界并拦截默认行为 (VSCode 风格)
        self._text_widget.mark_set(tk.INSERT, target_index)
        return 'break'

    def _sync_scroll(self, *args):
        """同步滚动条。"""
        self._text_widget.yview(*args)
        self._line_numbers.yview(*args)
        self._update_line_numbers()

    def _on_mousewheel(self, event):
        """处理鼠标滚轮。"""
        delta = -1 * (event.delta // 120)
        self._text_widget.yview_scroll(delta, 'units')
        self._line_numbers.yview_scroll(delta, 'units')
        self._update_line_numbers()
        return "break"

    def _on_modified(self, event):
        """当文本被修改时触发。"""
        if self._text_widget.edit_modified():
            self._update_line_numbers()
            self._save_state()
            self._text_widget.edit_modified(False)

    def _update_line_numbers(self):
        """更新行号显示。"""
        scroll_pos = self._text_widget.yview()[0]
        
        # 获取当前行数
        content = self._text_widget.get('1.0', 'end-1c')
        lines_count = content.count('\n') + 1
        
        line_numbers_str = '\n'.join(map(str, range(1, lines_count + 1)))
        
        # 只有在内容变化时才更新 Text 组件，减少闪烁
        if self._line_numbers.get('1.0', 'end-1c') != line_numbers_str:
            self._line_numbers.config(state=tk.NORMAL)
            self._line_numbers.delete('1.0', tk.END)
            self._line_numbers.insert('1.0', line_numbers_str)
            self._line_numbers.config(state=tk.DISABLED)
        
        self._line_numbers.yview_moveto(scroll_pos)

    def _save_state(self):
        """保存当前状态到历史记录（用于撤销/重做）。"""
        current_text = self.get_content()
        
        # 避免重复保存相同状态
        if self._history and current_text == self._history[self._history_index]:
            return

        # 如果在历史中间修改，切断未来的分支
        if self._history_index < len(self._history) - 1:
            self._history = self._history[:self._history_index + 1]
            
        self._history.append(current_text)
        self._history_index = len(self._history) - 1

    # --- 编辑操作 API ---

    def _undo(self, event=None):
        if self._history_index > 0:
            self._history_index -= 1
            self._apply_history_state(self._history[self._history_index])
        return 'break'

    def _redo(self, event=None):
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._apply_history_state(self._history[self._history_index])
        return 'break'

    def _apply_history_state(self, text: str):
        """应用历史状态。"""
        self._text_widget.delete('1.0', tk.END)
        self._text_widget.insert('1.0', text)
        self._update_line_numbers()
        # 设置修改状态为True，然后触发Modified事件
        self._text_widget.edit_modified(True)
        self._text_widget.event_generate('<<Modified>>')

    def get_content(self) -> str:
        return self._text_widget.get('1.0', 'end-1c')

    def set_content(self, text: str):
        self._text_widget.delete('1.0', tk.END)
        self._text_widget.insert('1.0', text)
        self._update_line_numbers()
        self._text_widget.event_generate('<<Modified>>')

    def get_cursor_position(self) -> tuple:
        line, col = map(int, self._text_widget.index(tk.INSERT).split('.'))
        return line, col

    def get_char_count(self) -> int:
        """获取当前文本的字符数。"""
        content = self._text_widget.get('1.0', 'end-1c')
        return len(content)

    def focus(self):
        self._text_widget.focus_set()

    def update_font(self, font_family: str, font_size: int):
        font_config = (font_family, font_size)
        self._text_widget.config(font=font_config)
        self._line_numbers.config(font=font_config)
        self._update_line_numbers()

    # --- 脚本历史管理 ---

    def record_script_execution(self, script_name: str):
        """记录脚本执行前后的状态。"""
        before_state = self.get_content()
        
        entry = {
            'script_name': script_name,
            'before': before_state,
            'after': None
        }
        
        # 处理历史分支
        if self._current_script_history_index < len(self._script_history) - 1:
            self._script_history = self._script_history[:self._current_script_history_index + 1]
            
        self._script_history.append(entry)
        self._current_script_history_index = len(self._script_history) - 1
        self._save_state()

    def update_script_execution_result(self, after_state: str):
        if self._script_history and self._current_script_history_index >= 0:
            self._script_history[self._current_script_history_index]['after'] = after_state

    def _select_next_occurrence(self, event):
        result = self.extensions.select_next_occurrence()
        self._update_line_numbers()
        return result

    def _indent(self, event):
        result = self.extensions._adjust_indent(False)
        self._update_line_numbers()
        return result

    def _outdent(self, event):
        result = self.extensions._adjust_indent(True)
        self._update_line_numbers()
        return result
