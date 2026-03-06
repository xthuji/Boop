#!/usr/bin/env python3
"""
NiceGUI 多光标编辑器示例
支持以下功能：
1. ⌘+d 选中文本相同的多个元素进行编辑
2. ⌃+⇧+上下方向键 添加多行光标进行多行编辑
"""

from nicegui import ui

class MultiCursorEditor:
    def __init__(self):
        self.content = """
# 示例代码
for i in range(10):
    print(f"Item {i}")
    print(f"Value {i}")
    print(f"Index {i}")
"""
        self.editor_id = "multi-cursor-editor"
        
    def create_editor(self):
        """创建支持多光标的编辑器"""
        # 嵌入 CodeMirror 编辑器
        content_escaped = self.content.replace('`', '\\`')
        
        # 添加 CodeMirror 库和样式
        ui.add_body_html('''
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/codemirror.min.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/theme/monokai.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/mode/python/python.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/selection/mark-selection.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/selection/active-line.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/selection/multiselect.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/search/search.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/search/jump-to-line.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/dialog/dialog.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.2/addon/dialog/dialog.min.css">
        ''')
        
        # 添加多光标功能实现
        ui.add_body_html('''
        <script>
            // 多光标功能实现
            CodeMirror.defineExtension('selectNextOccurrence', function() {{
                var cm = this;
                var selection = cm.getSelection();
                if (!selection) return;
                
                var cursor = cm.getCursor();
                var line = cursor.line;
                var ch = cursor.ch;
                
                // 从当前位置开始搜索
                var nextPos = cm.getSearchCursor(selection, {{line: line, ch: ch}});
                if (nextPos.findNext()) {{
                    // 获取当前所有选择
                    var selections = cm.listSelections();
                    // 添加新的选择
                    selections.push({{
                        anchor: nextPos.from(),
                        head: nextPos.to()
                    }});
                    // 设置所有选择
                    cm.setSelections(selections);
                }}
            }});
            
            CodeMirror.defineExtension('addCursorAbove', function() {{
                var cm = this;
                var cursors = cm.listSelections();
                var newCursors = [];
                
                for (var i = 0; i < cursors.length; i++) {{
                    var cursor = cursors[i];
                    if (cursor.from().line > 0) {{
                        newCursors.push({{
                            anchor: {{line: cursor.from().line - 1, ch: cursor.from().ch}},
                            head: {{line: cursor.from().line - 1, ch: cursor.to().ch}}
                        }});
                    }}
                }}
                
                if (newCursors.length > 0) {{
                    cm.setSelections(newCursors);
                }}
            }});
            
            CodeMirror.defineExtension('addCursorBelow', function() {{
                var cm = this;
                var cursors = cm.listSelections();
                var newCursors = [];
                var lastLine = cm.lastLine();
                
                for (var i = 0; i < cursors.length; i++) {{
                    var cursor = cursors[i];
                    if (cursor.from().line < lastLine) {{
                        newCursors.push({{
                            anchor: {{line: cursor.from().line + 1, ch: cursor.from().ch}},
                            head: {{line: cursor.from().line + 1, ch: cursor.to().ch}}
                        }});
                    }}
                }}
                
                if (newCursors.length > 0) {{
                    cm.setSelections(newCursors);
                }}
            }});
            
            CodeMirror.defineExtension('singleSelection', function() {{
                var cm = this;
                var cursor = cm.getCursor();
                cm.setSelection(cursor, cursor);
            }});
        </script>
        ''')
        
        # 创建编辑器容器
        with ui.card():
            ui.label('多光标编辑器').classes('text-xl font-bold mb-2')
            # 创建编辑器元素
            ui.html(f'<div id="{self.editor_id}" style="height: 400px; width: 100%;"></div>', sanitize=False)
            
            # 初始化编辑器
            ui.add_body_html(f'''
            <script>
                var editor = CodeMirror(document.getElementById('{self.editor_id}'), {{
                    mode: "python",
                    lineNumbers: true,
                    theme: "monokai",
                    indentUnit: 4,
                    tabSize: 4,
                    indentWithTabs: false,
                    lineWrapping: true,
                    styleActiveLine: true,
                    matchBrackets: true,
                    // 启用多光标支持
                    extraKeys: {{
                        // Mac 快捷键: ⌘+d 选择下一个匹配项
                        "Cmd-D": function(cm) {{
                            cm.selectNextOccurrence();
                        }},
                        // Windows/Linux 快捷键: Ctrl+d 选择下一个匹配项
                        "Ctrl-D": function(cm) {{
                            cm.selectNextOccurrence();
                        }},
                        // Mac 快捷键: ⌃+⇧+上箭头 添加光标到上一行
                        "Ctrl-Shift-Up": function(cm) {{
                            cm.addCursorAbove();
                        }},
                        // Mac 快捷键: ⌃+⇧+下箭头 添加光标到下一行
                        "Ctrl-Shift-Down": function(cm) {{
                            cm.addCursorBelow();
                        }},
                        // Windows/Linux 快捷键: Ctrl+Alt+上箭头 添加光标到上一行
                        "Ctrl-Alt-Up": function(cm) {{
                            cm.addCursorAbove();
                        }},
                        // Windows/Linux 快捷键: Ctrl+Alt+下箭头 添加光标到下一行
                        "Ctrl-Alt-Down": function(cm) {{
                            cm.addCursorBelow();
                        }},
                        // 取消多光标
                        "Esc": function(cm) {{
                            cm.singleSelection();
                        }}
                    }}
                }});
                
                // 设置初始内容
                editor.setValue(`{content_escaped}`);
                
                // 与 Python 通信
                window.editor = editor;
                
                // 当内容变化时更新 Python 端
                editor.on('change', function() {{
                    // 这里可以添加与 Python 端的通信逻辑
                }});
            </script>
            ''')
            
            # 添加操作按钮
            with ui.row():
                ui.button('获取内容', on_click=self.get_content)
                ui.button('清空', on_click=self.clear_content)
                ui.button('重置示例', on_click=self.reset_content)
        
    def get_content(self):
        """获取编辑器内容"""
        ui.run_javascript(f"window.editor.getValue()")
        ui.notify('内容已获取')
    
    def clear_content(self):
        """清空编辑器内容"""
        ui.run_javascript(f"window.editor.setValue('')")
        ui.notify('编辑器已清空')
    
    def reset_content(self):
        """重置为示例内容"""
        content_escaped = self.content.replace('`', '\\`')
        ui.run_javascript(f"window.editor.setValue(`{content_escaped}`)")
        ui.notify('已重置为示例内容')

def main():
    """主函数"""
    editor = MultiCursorEditor()
    
    @ui.page('/')
    def index():
        ui.markdown('# NiceGUI 多光标编辑器示例')
        ui.markdown('''
## 功能说明

- **⌘+d (Mac) 或 Ctrl+d (Windows/Linux)**：选中文本相同的多个元素
- **⌃+⇧+上下方向键 (Mac)**：添加多行光标进行多行编辑
- **Ctrl+Alt+上下方向键 (Windows/Linux)**：添加多行光标进行多行编辑
- **Esc**：取消多光标选择

## 示例用法

1. 选择一个单词，然后按 ⌘+d 选择所有相同的单词
2. 按住 ⌃+⇧ 同时按上下方向键添加多行光标
3. 开始编辑，所有光标位置会同时更新
''')
        editor.create_editor()
    
    # 运行应用
    ui.run(title='多光标编辑器', port=8080, reload=True)

if __name__ in {"__main__", "__mp_main__"}:
    main()
