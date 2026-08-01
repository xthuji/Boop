# 0004. 采用 Tkinter 作为 GUI 框架

- **Status:** Accepted
- **Date:** 2026-08-01
- **Deciders:** Boop Python Team

## Context

需为跨平台桌面文本处理工具选择 GUI 框架。原版 Boop 用 Swift 原生 macOS API，但本项目目标是 macOS/Linux/Windows 三平台。

## Decision Drivers

- 跨平台（macOS/Linux/Windows）
- Python 标准库优先，减少打包体积
- 简单文本编辑器与对话框即可，无需复杂动画/原生外观

## Options Considered

### Option A: Tkinter（采用）
- Pros：Python 标准库，零额外依赖；跨平台；体积小；文档充足
- Cons：外观非原生；多光标编辑需自实现；无现代控件

### Option B: PyQt5 / PySide2
- Pros：控件丰富；外观更现代；信号槽机制
- Cons：🔴 许可证复杂（PyQt GPL / PySide LGPL）；体积大（~50MB Qt 运行时）；`build.sh` 已显式排除（[build.sh#L76](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L76)）

### Option C: wxPython
- Pros：原生外观
- Cons：体积大；跨平台一致性不如 Tkinter

### Option D: pywebview + HTML/CSS
- Pros：UI 用 Web 技术栈，灵活
- Cons：引入 WebView 运行时依赖；体积大；与 Tkinter 混用增加复杂度

## Decision

选择 **Option A**：Tkinter。文本编辑器、选择器、偏好面板均用 `tkinter` + `ttk` 实现，多光标编辑自行在 [editor_extensions.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/ui/editor_extensions.py) 扩展。

## Consequences

- **Positive**：零额外运行时依赖；打包体积小；`build.sh` 仅需 `--hidden-import tkinter`。
- **Negative**：外观与原生 macOS 应用有差距；多光标、行号等需自实现（已存在于 `editor_extensions.py`）。
- **Trade-off accepted**：以外观代价换取体积与依赖最小化。

## Compliance

- 所有 UI 模块 `import tkinter as tk`
- `build.sh` `--exclude-module PyQt5 gi wx PySide2`（[build.sh#L76](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L76)）

## Change Log

- 2026-08-01: Status Proposed → Accepted
