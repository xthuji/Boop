"""
Editor Extensions - 增强型多光标编辑插件
支持类似 VSCode 的 Ctrl+D 选中与同步编辑功能。
"""

import tkinter as tk
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from boop.core.log import logger

@dataclass
class MultiCursorState:
    """管理多光标编辑会话的状态。"""
    selections: List[Tuple[str, str]] = field(default_factory=list)
    search_term: str = ""       # 初始选中的查找基准文本
    active_input: str = ""      # 当前实时输入/修改后的文本内容
    original_text: str = ""     # 会话开始时的完整文本快照
    hint_shown: bool = False

    def reset(self):
        """重置状态，但保留 hint_shown 以避免重复弹窗。"""
        self.selections = []
        self.search_term = ""
        self.active_input = ""
        self.original_text = ""


class EditorExtensions:
    """
    编辑器扩展类。
    优化说明：
    1. 保持了与测试脚本 (test_editor_keys.py) 兼容的方法名入口。
    2. 引入了原子化更新逻辑，防止多光标编辑时的文本偏移。
    """

    def __init__(self, text_widget: tk.Text, config=None, editor=None):
        self.text_widget = text_widget
        self.config = config
        self.editor = editor
        self._state = MultiCursorState()
        
        # 绑定基础点击事件：点击任何地方即退出多光标模式
        self.text_widget.bind('<Button-1>', lambda e: self.clear_selections())

    def _clear_multi_cursor_state(self):
        self.clear_selections()

    def _handle_multi_cursor_paste(self):
        try:
            pasted_text = self.text_widget.clipboard_get()
            return self._apply_multi_edit(pasted_text)
        except tk.TclError:
            return 'break'

    def _handle_delete(self):
        # 删除最后一个字符
        return self._apply_multi_edit(self._state.active_input[:-1])

    def _handle_printable_character(self, char: str):
        # 多光标模式下，第一次输入替换整个选中的文本，后续输入累积字符
        if self._state.active_input == self._state.search_term:
            # 第一次输入，替换整个选中的文本
            new_text = char
        else:
            # 后续输入，累积字符
            new_text = self._state.active_input + char
        return self._apply_multi_edit(new_text)

    # --- 核心逻辑实现 ---

    def clear_selections(self):
        """重置多光标状态。"""
        self._state.reset()
        self.text_widget.tag_remove(tk.SEL, '1.0', tk.END)

    def select_next_occurrence(self):
        """选中下一个匹配项（Ctrl+D 逻辑）。"""
        tw = self.text_widget
        content = tw.get('1.0', 'end-1c')

        # 检查是否需要启动新的会话或内容是否已在外部被改变
        if not self._state.selections or (len(self._state.selections) > 1 and self._state.original_text != content):
            self._init_session(tw, content)
        
        if not self._state.search_term:
            return 'break'

        # 从最后一个选区的末尾开始查找
        last_end = self._state.selections[-1][1]
        next_idx = tw.search(self._state.search_term, last_end, stopindex=tk.END)
        
        if next_idx:
            next_end = tw.index(f"{next_idx} + {len(self._state.search_term)}c")
            self._state.selections.append((next_idx, next_end))
            self._update_ui_selection_display(next_end)
        
        return 'break'

    def _init_session(self, tw, content):
        """初始化多光标编辑会话。"""
        try:
            # 优先使用现有选区
            start, end = tw.index(tk.SEL_FIRST), tw.index(tk.SEL_LAST)
        except tk.TclError:
            # 如果没选中，则自动选中当前光标下的单词
            start, end = tw.index('insert wordstart'), tw.index('insert wordend')
        
        selected = tw.get(start, end)
        if selected:
            self._state.reset()
            self._state.search_term = selected
            self._state.active_input = selected
            self._state.original_text = content
            self._state.selections = [(start, end)]

    def _apply_multi_edit(self, new_text: str):
        """
        核心原子化更新：
        计算所有选区被替换后的最终文本，一次性写入，避免逐个操作导致的索引偏移。
        """
        self._state.active_input = new_text
        # 使用当前文本内容作为基础，而不是原始文本，以支持连续操作
        original = self.text_widget.get('1.0', 'end-1c')
        
        # 从选区直接获取位置，而不是通过搜索
        # 按照选区的结束位置从后往前排序，确保替换时不会影响前面的索引
        sorted_selections = sorted(self._state.selections, key=lambda x: self._get_absolute_position(x[1]), reverse=True)
        
        # 2. 从后往前替换，生成新的全量文本（逆序是为了不破坏前面的 index）
        working_content = original
        for start, end in sorted_selections:
            # 计算绝对位置
            start_pos = self._get_absolute_position(start)
            end_pos = self._get_absolute_position(end)
            # 替换文本
            working_content = working_content[:start_pos] + new_text + working_content[end_pos:]

        # 3. 计算替换后，各选区在全新内容中的新 line.col 坐标
        new_selections = []
        # 重新获取所有选区的位置（从前往后）
        temp_pos = 0
        for _ in range(len(self._state.selections)):
            temp_pos = working_content.find(new_text, temp_pos)
            if temp_pos == -1: break
            
            # 将绝对位置转换为 Tkinter 的 "line.column" 字符串
            prefix = working_content[:temp_pos]
            line = prefix.count('\n') + 1
            col = len(prefix.split('\n')[-1])
            
            new_s = f"{line}.{col}"
            new_e = f"{line}.{col + len(new_text)}"
            new_selections.append((new_s, new_e))
            temp_pos += len(new_text)

        # 4. 执行原子级更新
        self._update_widget_content(working_content, new_selections)
        # 更新搜索词为新文本，以便后续操作基于新内容
        self._state.search_term = new_text
        return 'break'


    def _adjust_indent(self, decrease=False):
        """
        增加或减少缩进。
        """
        tw = self.text_widget
        indent_char = '\t'
        
        try:
            # 获取当前选区
            has_selection = bool(tw.tag_ranges(tk.SEL))
            if has_selection:
                start_idx = tw.index(tk.SEL_FIRST)
                end_idx = tw.index(tk.SEL_LAST)
            else:
                # 无选区则针对当前行，并记录初始光标列位置
                start_idx = end_idx = tw.index(tk.INSERT)
    
            start_line = int(start_idx.split('.')[0])
            end_line = int(end_idx.split('.')[0])
            
            # 修正结束行：如果选中了下一行的开头(col 0)，不处理最后一行
            if has_selection and end_idx.split('.')[1] == '0' and end_line > start_line:
                end_line -= 1
    
            # 记录初始光标位置，用于后续恢复或偏移
            old_cursor_idx = tw.index(tk.INSERT)
            old_cursor_line, old_cursor_col = map(int, old_cursor_idx.split('.'))
    
            # 遍历每一行进行处理
            for line_num in range(start_line, end_line + 1):
                line_start = f"{line_num}.0"
                if not decrease:
                    # 增加缩进
                    tw.insert(line_start, indent_char)
                else:
                    # 减少缩进：删除行首的 \t 或 4个空格
                    line_text = tw.get(line_start, f"{line_start} lineend")
                    if line_text.startswith('\t'):
                        tw.delete(line_start, f"{line_start} + 1c")
                    elif line_text.startswith('    '):
                        tw.delete(line_start, f"{line_start} + 4c")
    
            # 处理选区恢复与光标位置
            if has_selection:
                # 重新选中完整的行（测试用例期望的行为）
                tw.tag_remove(tk.SEL, '1.0', tk.END)
                # 注意：测试期望 Step 18 的选区是 "\tLine 2\n\tLine 3"，即包含缩进但不包含最后的换行
                tw.tag_add(tk.SEL, f"{start_line}.0", f"{end_line}.end")
            else:
                # 无选区时，光标需要根据插入情况移动
                # 如果是在行中间插入，列号应该增加 len(indent_char)
                new_col = old_cursor_col + (len(indent_char) if not decrease else -1)
                new_col = max(0, new_col)
                tw.mark_set(tk.INSERT, f"{old_cursor_line}.{new_col}")
    
        except Exception as e:
            logger.error(f"缩进调整失败: {e}")
        finally:
            return "break"

    def _get_absolute_position(self, index):
        """
        将 Tkinter 的 line.column 索引转换为绝对位置
        """
        line, col = map(int, index.split('.'))
        content = self.text_widget.get('1.0', 'end-1c')
        lines = content.split('\n')
        pos = 0
        for i in range(line - 1):
            pos += len(lines[i]) + 1  # +1 for the newline
        pos += col
        return pos

    def _update_widget_content(self, content: str, selections: list):
        """更新文本组件内容并恢复选区。"""
        tw = self.text_widget
        # 记录当前滚动位置
        y_scroll = tw.yview()[0]
        
        tw.delete('1.0', tk.END)
        tw.insert('1.0', content)
        
        # 更新快照状态
        self._state.original_text = content
        self._state.selections = selections
        
        # 恢复高亮
        tw.tag_remove(tk.SEL, '1.0', tk.END)
        for s, e in selections:
            tw.tag_add(tk.SEL, s, e)
        
        # 移动主光标到最后一个选区的末尾并保持可见
        if selections:
            last_target = selections[-1][1]
            tw.mark_set(tk.INSERT, last_target)
            tw.see(last_target)
            
        # 恢复滚动位置，防止视觉跳动
        tw.yview_moveto(y_scroll)

    def on_key_press(self, event):
        """
        键盘事件分发器。
        如果当前处于多光标模式（选区 > 1），则拦截并处理。
        """
        if len(self._state.selections) <= 1:
            return None # 让 Tkinter 处理默认逻辑
        
        # 处理退出模式的按键 PageUp(Prior)、PageDown(Next)
        if event.keysym in ('Up', 'Down', 'Left', 'Right', 'Escape', 'Home', 'End', 'PageUp', 'PageDown', 'Prior', 'Next'):
            self.clear_selections()
            return None
        
        # 处理删除
        if event.keysym == 'BackSpace':
            return self._handle_delete()
        
        # 处理回车（换行）
        if event.keysym == 'Return':
            return self._apply_multi_edit('\n')
            
        # 处理普通可打印字符
        if event.char and event.char.isprintable():
            return self._handle_printable_character(event.char)
            
        return None

    def _update_ui_selection_display(self, focus_idx: str):
        """仅更新 UI 上的选中状态（不改变文本内容）。"""
        tw = self.text_widget
        tw.tag_remove(tk.SEL, '1.0', tk.END)
        for s, e in self._state.selections:
            tw.tag_add(tk.SEL, s, e)
        tw.mark_set(tk.INSERT, focus_idx)
        tw.see(focus_idx)

    def get_selections(self) -> List[Tuple[str, str]]:
        """获取当前所有选区的起始和结束位置。"""
        return self._state.selections