# gvcode 集成方案

## 1. 方案概述

本方案旨在从 gvcode 源码中提取核心功能，集成到 Boop Go 项目中，实现一个轻量级、高性能的文本编辑器。

### 1.1 目标

- 提取 gvcode 的核心编辑功能到 boop-go 项目
- 保持代码结构清晰，便于维护和扩展
- 确保编辑器功能与 Boop 的其他功能无缝集成

### 1.2 技术栈

- **前端**：Gio GUI 框架
- **编辑器**：基于 gvcode 核心组件
- **后端**：Go 标准库

## 2. 目录结构设计

```
boop-go/
├── go.mod                        # 项目配置
├── go.sum                        # 依赖校验
├── main.go                       # 可执行入口
├── README.md                     # 项目说明
│
├── src/                          # 源代码目录
│   ├── core/                     # 核心功能模块
│   │   ├── script/               # 脚本处理
│   │   │   ├── executor.go       # 脚本执行器
│   │   │   ├── metadata.go       # 脚本元数据解析
│   │   │   └── manager.go        # 脚本管理
│   │   ├── config.go             # 配置管理
│   │   ├── paths.go              # 路径管理
│   │   ├── event.go              # 事件系统
│   │   └── logging.go            # 日志系统
│   │
│   ├── ui/                       # UI 模块
│   │   ├── main_window.go        # 主窗口
│   │   ├── script_picker.go      # 脚本选择器
│   │   ├── settings.go           # 设置窗口
│   │   └── status_bar.go         # 状态栏
│   │
│   ├── editor/                   # 编辑器模块
│   │   ├── editor.go             # 编辑器模块入口
│   │   ├── gvcode/               # gvcode 核心组件
│   │   │   ├── editor.go         # 编辑器核心实现
│   │   │   ├── textview/         # 文本视图渲染
│   │   │   ├── internal/         # 内部实现
│   │   │   │   ├── buffer/       # 文本缓冲区
│   │   │   │   ├── layout/       # 文本布局
│   │   │   │   └── painter/      # 文本绘制
│   │   │   ├── gutter/           # 行号和侧边栏
│   │   │   ├── color/            # 颜色方案
│   │   │   └── textstyle/        # 文本样式
│   │   └── config.go             # 编辑器配置
│   │
│   ├── utils/                    # 工具模块
│   │   ├── persistence.go        # 文件操作
│   │   ├── python_env.go         # Python 环境
│   │   ├── platform.go           # 平台特定功能
│   │   └── error.go              # 错误处理
│   │
│   ├── scripts/                  # Python 脚本资源
│   │   ├── __init__.py
│   │   ├── lib/
│   │   └── *.py                  # 内置脚本
│   │
│   ├── assets/                   # 静态资源
│   │   ├── fonts/                # 字体文件
│   │   └── icons/                # 图标文件
│   │
│   └── tests/                    # 测试
│       ├── integration/
│       └── unit/
│
└── design/                       # 设计文档
    ├── img/                      # UI截图
    ├── 技术设计.md
    ├── 实现与迁移.md
    ├── 构建指南.md
    ├── 目录结构.md
    └── gvcode集成方案.md        # 本方案文档
```

## 3. 核心组件提取

### 3.1 提取组件列表

| 组件 | 源文件 | 目标路径 | 说明 |
|------|--------|----------|------|
| 编辑器核心 | gvcode-main/editor.go | src/editor/gvcode/editor.go | 编辑器主要功能 |
| 文本视图 | gvcode-main/textview/ | src/editor/gvcode/textview/ | 文本渲染和光标管理 |
| 缓冲区 | gvcode-main/internal/buffer/ | src/editor/gvcode/internal/buffer/ | 文本存储和操作 |
| 布局 | gvcode-main/internal/layout/ | src/editor/gvcode/internal/layout/ | 文本布局计算 |
| 绘制 | gvcode-main/internal/painter/ | src/editor/gvcode/internal/painter/ | 文本绘制 |
| 行号 | gvcode-main/gutter/ | src/editor/gvcode/gutter/ | 行号和侧边栏 |
| 颜色 | gvcode-main/color/ | src/editor/gvcode/color/ | 颜色方案 |
| 文本样式 | gvcode-main/textstyle/ | src/editor/gvcode/textstyle/ | 文本样式和语法高亮 |
| 事件处理 | gvcode-main/event.go | src/editor/gvcode/event.go | 编辑器事件处理 |
| 命令 | gvcode-main/commands.go | src/editor/gvcode/commands.go | 编辑器命令 |
| 选项 | gvcode-main/option.go | src/editor/gvcode/option.go | 编辑器选项 |

### 3.2 提取策略

1. **保持原始结构**：尽量保持 gvcode 的原始目录结构，便于后续更新
2. **最小化修改**：只修改必要的部分，确保功能正常运行
3. **添加适配层**：在 src/editor/editor.go 中添加适配层，将 gvcode 与 Boop 的其他模块集成
4. **移除不必要的功能**：移除与 Boop 功能无关的部分，如高级语法高亮、代码补全等

## 4. 功能集成

### 4.1 编辑器集成

在 `src/editor/editor.go` 中实现适配层，将 gvcode 与 Boop 集成：

```go
package editor

import (
    "github.com/oligo/gvcode"
)

// Editor 封装 gvcode 编辑器

type Editor struct {
    gvcode *gvcode.Editor
    config *EditorConfig
}

// NewEditor 创建新的编辑器实例
func NewEditor() *Editor {
    editor := gvcode.NewEditor()
    return &Editor{
        gvcode: editor,
        config: DefaultEditorConfig(),
    }
}

// SetText 设置编辑器文本
func (e *Editor) SetText(text string) {
    e.gvcode.SetText(text)
}

// GetText 获取编辑器文本
func (e *Editor) GetText() string {
    return e.gvcode.Text()
}

// Layout 布局编辑器
func (e *Editor) Layout(gtx layout.Context, lt *text.Shaper) layout.Dimensions {
    return e.gvcode.Layout(gtx, lt)
}

// Update 更新编辑器状态
func (e *Editor) Update(gtx layout.Context) (gvcode.EditorEvent, bool) {
    return e.gvcode.Update(gtx)
}

// SetConfig 设置编辑器配置
func (e *Editor) SetConfig(config *EditorConfig) {
    e.config = config
    // 应用配置到 gvcode
}

// GetConfig 获取编辑器配置
func (e *Editor) GetConfig() *EditorConfig {
    return e.config
}
```

### 4.2 脚本执行集成

在 `core/script/executor.go` 中实现脚本执行功能，与编辑器集成：

```go
package script

import (
    "os/exec"
    "strings"
)

// ExecuteScript 执行 Python 脚本
func ExecuteScript(scriptPath string, inputText string) (string, error) {
    // 构建 Python 脚本
    wrapper := buildWrapperScript(scriptPath, inputText)
    
    // 执行脚本
    cmd := exec.Command("python3", "-c", wrapper)
    output, err := cmd.CombinedOutput()
    
    if err != nil {
        return "", err
    }
    
    return strings.TrimSpace(string(output)), nil
}

// buildWrapperScript 构建包装脚本
func buildWrapperScript(scriptPath string, inputText string) string {
    // 构建包装脚本，注入 State 对象
    return `
class State:
    def __init__(self, text):
        self.text = text
        self._info_messages = []
        self._error_messages = []

    def insert(self, text, position=None):
        if position is None:
            self.text += text
        else:
            self.text = self.text[:position] + text + self.text[position:]

    def post_info(self, message):
        self._info_messages.append(message)

    def post_error(self, message):
        self._error_messages.append(message)

import sys
import os

# 添加脚本目录到 Python 路径
sys.path.insert(0, os.path.dirname('` + scriptPath + `'))

# 导入脚本
import ` + getModuleName(scriptPath) + `

# 创建状态对象
state = State('` + escapeText(inputText) + `')

# 执行脚本
try:
    ` + getModuleName(scriptPath) + `.main(state)
except Exception as e:
    state.post_error(str(e))

# 打印结果
print(state.text)
`
}

// getModuleName 从脚本路径获取模块名
func getModuleName(scriptPath string) string {
    // 实现模块名提取逻辑
    return ""
}

// escapeText 转义文本中的特殊字符
func escapeText(text string) string {
    // 实现文本转义逻辑
    return text
}
```

### 4.3 UI 集成

在 `ui/main_window.go` 中集成编辑器到主窗口：

```go
package ui

import (
    "boop-go/editor"
    "gioui.org/layout"
    "gioui.org/widget"
)

// MainWindow 主窗口

type MainWindow struct {
    editor *editor.Editor
    // 其他字段
}

// NewMainWindow 创建新的主窗口
func NewMainWindow() *MainWindow {
    return &MainWindow{
        editor: editor.NewEditor(),
        // 初始化其他字段
    }
}

// Layout 布局主窗口
func (w *MainWindow) Layout(gtx layout.Context) layout.Dimensions {
    return layout.Flex{
        Axis: layout.Vertical,
    }.Layout(gtx,
        layout.Rigid(func(gtx layout.Context) layout.Dimensions {
            // 菜单栏
            return w.layoutMenuBar(gtx)
        }),
        layout.Flexed(1, func(gtx layout.Context) layout.Dimensions {
            // 编辑器
            return w.editor.Layout(gtx, w.shaper)
        }),
        layout.Rigid(func(gtx layout.Context) layout.Dimensions {
            // 状态栏
            return w.layoutStatusBar(gtx)
        }),
    )
}

// Update 更新主窗口状态
func (w *MainWindow) Update(gtx layout.Context) {
    // 处理事件
    w.editor.Update(gtx)
    // 处理其他更新
}
```

## 5. 配置和初始化

### 5.1 编辑器配置

在 `editor/config.go` 中定义编辑器配置：

```go
package editor

// EditorConfig 编辑器配置
type EditorConfig struct {
    FontFamily string
    FontSize   int
    TabSize    int
    LineNumbers bool
    WordWrap   bool
    Theme      string
}

// DefaultEditorConfig 默认编辑器配置
func DefaultEditorConfig() *EditorConfig {
    return &EditorConfig{
        FontFamily: "Monaco",
        FontSize:   14,
        TabSize:    4,
        LineNumbers: true,
        WordWrap:   false,
        Theme:      "default",
    }
}
```

### 5.2 应用初始化

在 `main.go` 中初始化应用：

```go
package main

import (
    "boop-go/ui"
    "boop-go/core"
    "gioui.org/app"
    "gioui.org/io/system"
    "gioui.org/layout"
)

func main() {
    // 初始化配置
    config := core.LoadConfig()
    
    // 初始化主窗口
    window := ui.NewMainWindow()
    
    // 运行应用
    go func() {
        w := app.NewWindow(
            app.Title("Boop"),
            app.Size(800, 600),
        )
        
        if err := run(w, window); err != nil {
            panic(err)
        }
    }()
    
    app.Main()
}

func run(w *app.Window, window *ui.MainWindow) error {
    var ops op.Ops
    for {
        e := <-w.Events()
        switch e := e.(type) {
        case system.DestroyEvent:
            return e.Err
        case system.FrameEvent:
            gtx := layout.NewContext(&ops, e)
            window.Update(gtx)
            window.Layout(gtx)
            e.Frame(gtx.Ops)
        }
    }
}
```

## 6. 性能优化

### 6.1 启动优化

- **延迟加载**：脚本和配置延迟加载，加快启动速度
- **缓存**：缓存脚本元数据，避免重复解析
- **懒初始化**：首次使用时初始化编辑器组件

### 6.2 运行时优化

- **文本处理**：使用 gvcode 的高效文本处理算法
- **渲染优化**：只渲染可见部分，提高渲染性能
- **事件处理**：优化事件处理逻辑，减少不必要的计算

## 7. 测试策略

### 7.1 单元测试

- **编辑器功能**：测试基本编辑功能
- **脚本执行**：测试脚本执行功能
- **配置管理**：测试配置读写功能

### 7.2 集成测试

- **编辑器集成**：测试编辑器与 UI 的集成
- **脚本执行**：测试脚本执行与编辑器的集成
- **完整流程**：测试完整的文本处理流程

## 8. 实现步骤

### 8.1 第一步：提取 gvcode 核心组件

1. 创建 `src/editor/gvcode/` 目录
2. 复制 gvcode 的核心组件到该目录
3. 调整导入路径，确保编译通过

### 8.2 第二步：实现编辑器适配层

1. 创建 `src/editor/editor.go` 文件
2. 实现 Editor 结构体，封装 gvcode 编辑器
3. 实现必要的方法，如 SetText、GetText、Layout 等

### 8.3 第三步：集成脚本执行功能

1. 创建 `src/core/script/` 目录
2. 实现脚本执行引擎
3. 实现脚本元数据解析
4. 实现脚本管理器

### 8.4 第四步：实现 UI 组件

1. 创建 `src/ui/` 目录
2. 实现主窗口
3. 实现脚本选择器
4. 实现设置窗口
5. 实现状态栏

### 8.5 第五步：实现配置系统

1. 创建 `src/core/config.go` 文件
2. 实现配置结构定义
3. 实现配置读写功能
4. 实现配置默认值

### 8.6 第六步：优化和测试

1. 优化启动速度和运行性能
2. 编写单元测试和集成测试
3. 进行跨平台测试

## 9. 总结

本方案通过提取 gvcode 的核心功能，集成到 Boop Go 项目中，实现了一个轻量级、高性能的文本编辑器。通过保持 gvcode 的原始结构，最小化修改，添加适配层，确保了代码的可维护性和可扩展性。同时，通过性能优化和测试策略，确保了应用的稳定性和性能。

该方案不仅满足了 Boop 的功能需求，还为未来的扩展和优化提供了良好的基础。