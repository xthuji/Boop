# Boop Python 需求规格说明书

## 1. 项目概述

### 1.1 项目目标
Boop Python 是一个文本处理工具，灵感来自 macOS 的 Boop 应用。用户可以通过快捷键调用各种 Python 脚本来处理和转换文本。

### 1.2 核心原则
1. **单一窗口原则**: 应用启动后只创建一个主编辑窗口，所有操作都在此窗口内进行
2. **无模态交互**: 避免创建独立的模态对话框窗口
3. **即时反馈**: 所有操作结果直接在编辑器中显示
4. **轻量级**: 快速启动，低资源占用

---

## 2. 窗口管理架构

### 2.1 窗口层次结构

```
┌─────────────────────────────────────────────────────────────┐
│                    MainWindow (tk.Tk)                        │
│  唯一的主窗口实例，应用生命周期内只创建一个                  │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Menu Bar (tk.Menu)                                      │ │
│  │  - Scripts Menu                                          │ │
│  │  - Edit Menu                                             │ │
│  │  - Help Menu                                             │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Editor Area (tk.Text)                                   │ │
│  │  - 唯一的文本编辑区域                                    │ │
│  │  - 所有文本操作的唯一数据源                              │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Status Bar (ttk.Label)                                  │ │
│  │  - 显示操作状态和消息                                    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 弹出面板设计

所有辅助功能使用 `tk.Frame` 作为主窗口的子组件，而不是 `tk.Toplevel`：

```python
# ❌ 错误：创建独立窗口
dialog = tk.Toplevel(parent)

# ✅ 正确：创建子面板
popup = tk.Frame(parent)
popup.place(x=50, y=50, width=500, height=400)
```

### 2.3 面板类型

| 面板名称 | 用途 | 实现方式 |
|---------|------|---------|
| ScriptPickerPopup | 脚本选择器 | `tk.Frame` + `place()` |
| PreferencesPanel | 偏好设置 | `tk.Frame` + `pack()` |
| AboutPanel | 关于信息 | `tk.Frame` + `place()` |

---

## 3. 数据处理流程

### 3.1 数据流架构

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Editor     │────▶│  Script      │────▶│   Editor     │
│  (tk.Text)   │     │  Execution   │     │  (tk.Text)   │
│              │     │  (subprocess)│     │              │
└──────────────┘     └──────────────┘     └──────────────┘
      ▲                      │                    ▲
      │                      ▼                    │
      │              ┌──────────────┐             │
      └──────────────│  Result      │─────────────┘
                     │  Processing  │
                     └──────────────┘
```

### 3.2 文本数据获取

```python
class MainWindow:
    def __init__(self):
        self.editor = tk.Text(self.root)  # 唯一编辑器实例
    
    def _get_editor_text(self) -> tuple[str, Optional[str]]:
        """获取编辑器文本和选中文本"""
        text = self.editor.get("1.0", tk.END).rstrip('\n')
        selection = None
        try:
            sel_start = self.editor.index(tk.SEL_FIRST)
            sel_end = self.editor.index(tk.SEL_LAST)
            selection = self.editor.get(sel_start, sel_end)
        except tk.TclError:
            pass  # 没有选中文本
        return text, selection
```

### 3.3 脚本执行流程

```python
def _execute_script(self, script, text, selection):
    """执行脚本并更新编辑器"""
    # 1. 保存当前状态（用于撤销）
    self._save_state()
    
    # 2. 在子进程中执行脚本
    result = self.script_runner.run_script(script, text, selection)
    
    # 3. 更新编辑器内容
    if result.success:
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", result.full_text)
    
    # 4. 显示状态消息
    self._show_status_message(result)
```

### 3.4 ScriptExecution 数据类

```python
class ScriptExecution:
    """脚本执行时的数据上下文"""
    
    def __init__(self, text: str, selection: Optional[str], full_text: str):
        self._text = text or ""
        self._selection = selection
        self._full_text = full_text or text or ""
        self._messages = []
        self._insertions = []
    
    @property
    def text(self) -> str:
        """获取当前文本（选中优先）"""
        if self._selection is not None:
            return self._selection
        return self._full_text or ""
    
    @text.setter
    def text(self, value: str):
        """设置文本，同时更新 full_text"""
        if self._selection is not None:
            # 有选中时，同时更新选中和完整文本
            if self._selection in self._full_text:
                self._full_text = self._full_text.replace(self._selection, value, 1)
            else:
                self._full_text = value
            self._selection = value
        else:
            self._full_text = value
    
    @property
    def full_text(self) -> str:
        """获取完整文本"""
        return self._full_text or ""
```

---

## 4. 核心组件设计

### 4.1 MainWindow（主窗口）

```python
class MainWindow:
    """应用主窗口（单例）"""
    
    def __init__(self, config_manager: ConfigManager):
        self.root = tk.Tk()  # 唯一的 Tk 实例
        self.editor = tk.Text(self.root)  # 唯一的编辑器
        self.script_loader = ScriptLoader()
        self.script_runner = ScriptRunner(config)
        
    def _open_script_picker(self):
        """打开脚本选择器（Frame 面板）"""
        def on_script_selected(script):
            if script:
                text, selection = self._get_editor_text()
                self._execute_script(script, text, selection)
            self.editor.focus_set()
        
        ScriptPickerPopup(self.root, self.script_loader, on_script_selected, self.editor)
```

### 4.2 ScriptPickerPopup（脚本选择器）

```python
class ScriptPickerPopup:
    """脚本选择器弹出面板"""
    
    def __init__(self, parent: tk.Tk, loader: ScriptLoader,
                 on_script_selected: Callable, editor_widget: tk.Text):
        self.parent = parent
        self.loader = loader
        self.on_script_selected = on_script_selected
        self.editor = editor_widget
        
        # 创建 Frame 面板（不是 Toplevel）
        self.popup = tk.Frame(self.parent, bg='white', relief='solid', borderwidth=1)
        self.popup.place(x=50, y=50, width=500, height=400)
        
        self._create_ui()
        self._bind_events()
    
    def _close(self):
        """关闭面板"""
        self.popup.destroy()
```

### 4.3 ScriptRunner（脚本执行器）

```python
class ScriptRunner:
    """在子进程中执行脚本"""
    
    def run_script(self, script: LoadedScript, text: str, 
                   selection: Optional[str]) -> ScriptResult:
        """执行脚本并返回结果"""
        # 创建 wrapper 代码
        wrapper = self._create_wrapper(script, text, selection)
        
        # 在子进程中执行
        result = subprocess.run(
            [self.python_path, "-c", wrapper],
            capture_output=True, text=True
        )
        
        return self._parse_result(result)
```

---

## 5. 用户交互流程

### 5.1 脚本选择与执行

```
用户操作                      系统响应
─────────                    ─────────
1. 按 Cmd+B                  → 显示 ScriptPickerPopup（Frame 面板）
2. 搜索脚本                  → 实时过滤脚本列表
3. 选择脚本（Enter/双击）     → 关闭面板，执行脚本
4. 脚本执行中                → 状态栏显示 "Running: xxx"
5. 脚本执行完成              → 编辑器内容更新，状态栏显示结果
```

### 5.2 面板交互

```python
# 键盘绑定
self.parent.bind('<Escape>', lambda e: self._close())  # 关闭面板
self.tree.bind('<Return>', lambda e: self._on_select())  # 确认选择
self.tree.bind('<Double-Button-1>', lambda e: self._on_select())  # 双击选择
self.tree.bind('<Up>', lambda e: self._navigate(-1))  # 向上导航
self.tree.bind('<Down>', lambda e: self._navigate(1))  # 向下导航
```

---

## 6. 构建与分发

### 6.1 构建配置

```bash
# PyInstaller 参数
--name "Boop"
--windowed           # 无控制台窗口
--onedir             # 单目录模式
--icon icons/icon.icns
--hidden-import tkinter
--hidden-import boop.ui.main_window
--hidden-import boop.ui.script_picker
--hidden-import boop.ui.preferences
```

### 6.2 构建产物

```
dist/
├── Boop-1.0.0-macos.dmg    # DMG 安装包
└── Boop.app/                # 可直接运行的 App
    └── Contents/
        ├── Frameworks/      # 依赖库
        ├── MacOS/           # 可执行文件
        ├── Resources/       # 资源文件
        └── Info.plist       # 应用信息
```

---

## 7. 禁止事项

### 7.1 禁止创建新窗口的操作

```python
# ❌ 禁止：创建 Toplevel 窗口
dialog = tk.Toplevel(self.root)
dialog.transient(self.root)
self.root.wait_window(dialog)

# ✅ 推荐：使用 Frame 面板
popup = tk.Frame(self.root)
popup.place(x=50, y=50, width=500, height=400)
```

### 7.2 禁止的数据操作

```python
# ❌ 禁止：在脚本执行时创建新的编辑器实例
new_editor = tk.Text(self.root)

# ✅ 推荐：始终使用唯一的编辑器实例
self.editor.delete("1.0", tk.END)
self.editor.insert("1.0", result.full_text)
```

---

## 8. 测试要求

### 8.1 窗口管理测试

```python
def test_single_window():
    """确保只有一个主窗口"""
    app = MainWindow(config_manager)
    # 打开脚本选择器
    app._open_script_picker()
    # 验证：只有一个 Tk 实例
    assert len(tk._default_root._children) == 1
```

### 8.2 数据处理测试

```python
def test_reverse_string():
    """测试 reverse_string 脚本"""
    runner = ScriptRunner(config)
    script = loader.get_script('Reverse String')
    
    # 无选中
    result = runner.run_script(script, 'hello', None)
    assert result.full_text == 'olleh'
    
    # 有选中
    result = runner.run_script(script, 'hello world', 'world')
    assert result.full_text == 'hello dlrow'
```

---

## 9. 错误处理

### 9.1 脚本执行错误

```python
try:
    result = self.script_runner.run_script(script, text, selection)
    if result.success:
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", result.full_text)
        self.status_var.set(f"✓ {result.messages[0]['text']}")
    else:
        # 错误显示在状态栏，不弹窗
        self.status_var.set(f"✗ Error: {result.error_message}")
except Exception as e:
    self.status_var.set(f"✗ Error: {str(e)}")
```

### 9.2 面板关闭处理

```python
def _close(self):
    """安全关闭面板"""
    # 解绑事件
    try:
        self.parent.unbind('<Escape>')
    except:
        pass
    
    # 取消定时器
    if self._debounce_timer:
        self.parent.after_cancel(self._debounce_timer)
    
    # 销毁面板
    if self.popup and self.popup.winfo_exists():
        self.popup.destroy()
        self.popup = None
```

---

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2024-03-03 | 初始版本，修复窗口管理和数据处理问题 |
| 1.1.0 | 2024-03-03 | 完全重构，实现单一窗口架构 |
| 1.2.0 | 2026-03-03 | 优化界面设计，添加单元测试框架，改进脚本选择器 |

## 11. 未实现功能

### 11.1 高优先级功能

| 功能 | 描述 | 实现建议 |
|------|------|----------|
| **Esc 键关闭窗口** | 在脚本选择器和首选项窗口中支持 Esc 键关闭 | 使用 `bind_class` 为 Toplevel 窗口及其子组件绑定 Esc 键，实现两级行为：第一次清除焦点/选中状态，第二次关闭窗口 |
| 脚本编辑器 | 内置脚本编辑器，方便用户修改和创建脚本 | 使用 Tkinter 的 Text 组件或第三方库，支持语法高亮、代码补全和错误提示 |
| 编辑器语法高亮 | 为编辑器添加语法高亮功能 | 使用第三方库如 Pygments 实现语法高亮 |
| 编辑器行号显示 | 在编辑器左侧显示行号 | 实现自定义行号组件，与编辑器同步滚动 |

### 11.2 中优先级功能

| 功能 | 描述 | 实现建议 |
|------|------|----------|
| 脚本分类管理 | 对脚本进行分类和组织 | 在脚本元数据中添加分类字段，在脚本选择器中显示分类标签 |
| 脚本参数配置 | 为脚本提供运行时参数配置界面 | 根据脚本元数据中的参数定义，动态生成配置界面 |
| 脚本导入/导出 | 支持脚本的导入和导出功能 | 实现脚本文件的导入和导出，以及脚本包的管理 |
| 最近使用的脚本 | 在脚本选择器中优先显示最近使用的脚本 | 扩展脚本执行历史功能，在脚本选择器中添加最近使用标签 |
| 脚本收藏功能 | 允许用户收藏常用脚本 | 在脚本元数据中添加收藏标记，在脚本选择器中添加收藏标签 |

### 11.3 低优先级功能

| 功能 | 描述 | 实现建议 |
|------|------|----------|
| 多语言支持 | 支持多语言界面 | 实现国际化框架，支持语言文件的加载和切换 |
| 脚本执行进度条 | 显示脚本执行的进度 | 在状态栏或脚本选择器中添加进度条组件 |
| 拖放支持 | 支持拖放文件到应用中 | 实现 Tkinter 的拖放功能，支持文件和文本的拖放 |
| 剪贴板历史 | 管理剪贴板历史记录 | 实现剪贴板历史管理，允许用户查看和恢复历史剪贴板内容 |

## 12. 优化建议

### 12.1 页面布局和交互流程优化

1. **脚本选择器界面优化**
   - 添加脚本分类标签，允许用户按分类筛选脚本
   - 增强键盘导航功能，支持更丰富的快捷键操作

2. **编辑器界面优化**
   - 添加行号显示和语法高亮功能
   - 改进编辑器的滚动和选择体验

3. **状态栏优化**
   - 添加当前行号、列号、字符数等信息
   - 提供更详细的操作状态和错误信息

4. **响应式设计优化**
   - 改进布局，使其在不同屏幕尺寸下都能良好显示
   - 优化面板大小和位置的计算逻辑

### 12.2 框架设计优化

1. **脚本执行系统优化**
   - 使用线程池或进程池管理脚本执行，减少启动开销
   - 实现脚本执行缓存，避免重复执行相同的脚本

2. **脚本加载机制优化**
   - 实现脚本缓存机制，提高启动速度
   - 优化脚本元数据的解析和存储

3. **配置系统优化**
   - 改进配置系统，支持更复杂的配置选项
   - 实现配置的版本管理和迁移

4. **错误处理优化**
   - 增强错误处理，提供更详细的错误信息和恢复建议
   - 实现错误日志的收集和分析

5. **模块化设计优化**
   - 进一步解耦模块，提高代码可维护性
   - 实现依赖注入机制，减少模块间的耦合

## 13. 技术架构改进

### 13.1 模块拆分

- 将 `script_execution.py` 拆分为更小的模块，提高可维护性
- 增加 `ui/components` 目录，用于存放可复用的 UI 组件

### 13.2 依赖注入

- 实现依赖注入机制，减少模块间的耦合
- 使用工厂模式创建核心组件

### 13.3 事件系统

- 实现事件系统，使组件间通信更加灵活
- 支持自定义事件和监听器

### 13.4 插件系统

- 实现插件系统，允许扩展应用功能
- 支持第三方插件的加载和管理

### 13.5 测试覆盖

- 增加单元测试和集成测试的覆盖范围
- 实现自动化测试流程

## 14. 性能优化

1. **脚本执行优化**
   - 使用进程池或线程池管理脚本执行
   - 实现脚本执行缓存，避免重复执行相同的脚本

2. **界面响应优化**
   - 使用异步操作处理耗时任务
   - 实现界面更新的节流和防抖

3. **内存管理**
   - 优化脚本加载机制，减少内存使用
   - 及时释放不再使用的资源

4. **启动速度优化**
   - 实现脚本缓存，避免每次启动都重新加载
   - 延迟加载非核心功能

## 15. 实现优先级

建议的优先级顺序：
1. **高优先级**：脚本编辑器、编辑器语法高亮和行号显示
2. **中优先级**：脚本分类管理、脚本参数配置、脚本导入/导出
3. **低优先级**：多语言支持、脚本执行进度条、拖放支持

通过有计划地实施这些改进，可以使 BoopPython 成为一个功能完整、性能优异的文本处理工具，满足用户的各种文本处理需求。

## 附录 B：重构检查清单

### B.1 窗口管理检查

- [ ] 整个应用只有一个 `tk.Tk()` 实例
- [ ] 所有弹出面板使用 `tk.Frame` 而非 `tk.Toplevel`
- [ ] 没有使用 `wait_window()` 阻塞主窗口
- [ ] 所有面板使用 `place()` 或 `pack()` 作为主窗口子组件

### B.2 数据处理检查

- [ ] 只有一个编辑器实例 (`self.editor`)
- [ ] 脚本执行时直接从编辑器获取文本
- [ ] 脚本结果直接更新到原编辑器
- [ ] `ScriptExecution.text` setter 正确更新 `_full_text`

### B.3 代码模式检查

```python
# ✅ 正确的窗口创建模式
class MyPopup:
    def __init__(self, parent: tk.Tk):
        self.popup = tk.Frame(parent)  # Frame, not Toplevel
        self.popup.place(...)

# ✅ 正确的编辑器访问模式
def _execute_script(self, script, text, selection):
    result = self.script_runner.run_script(script, text, selection)
    if result.success:
        self.editor.delete("1.0", tk.END)  # 更新唯一编辑器
        self.editor.insert("1.0", result.full_text)
```

---

## 附录 A：关键代码模式

### A.1 创建弹出面板的标准模式

```python
class MyPopup:
    def __init__(self, parent: tk.Tk, on_action: Callable):
        self.parent = parent
        self.on_action = on_action
        
        # 创建 Frame
        self.popup = tk.Frame(parent, bg='white', relief='solid', borderwidth=1)
        self.popup.place(relx=0.5, rely=0.5, anchor='center', 
                         relwidth=0.8, relheight=0.6)
        self.popup.lift()
        
        # 创建 UI
        self._create_ui()
        
        # 绑定事件
        parent.bind('<Escape>', lambda e: self._close())
        
        # 聚焦
        self.popup.focus_set()
    
    def _close(self):
        """关闭面板"""
        self.parent.unbind('<Escape>')
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()
```

### A.2 脚本执行的标准模式

```python
def _execute_script(self, script, text, selection):
    """执行脚本的标准流程"""
    # 1. 保存状态
    self._save_state()
    
    # 2. 执行
    result = self.script_runner.run_script(script, text, selection)
    
    # 3. 更新
    if result.success:
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", result.full_text)
        for msg in result.messages:
            prefix = "⚠ " if msg.get('is_error') else "✓ "
            self.status_var.set(f"{prefix}{msg.get('text', '')}")
    else:
        self.status_var.set(f"✗ Error: {result.error_message}")
    
    # 4. 聚焦
    self.editor.focus_set()
```
