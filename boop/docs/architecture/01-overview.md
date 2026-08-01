# Boop Python — 架构与业务概览

> 由 `python-arch-doc` skill 基于代码勘察生成。所有结论附带文件证据。

## 1. 产品定位

Boop Python 是一个**跨平台桌面文本处理工具**，灵感来自 macOS 原生应用 [Boop](https://github.com/IvanMathy/Boop)。用户在编辑器中输入或粘贴文本，通过快捷键唤起脚本选择器，执行 Python 脚本对选中文本进行格式化、转换、统计、编解码等处理。

与原 Boop 的关键差异（证据：[README.md](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/README.md#L152-L160)）：

| 特性 | 原 Boop | Boop Python |
|------|---------|-------------|
| 脚本语言 | JavaScript | Python |
| 执行方式 | JavaScriptCore（进程内） | 子进程隔离 |
| UI | 原生 macOS (Swift) | Tkinter（跨平台） |
| 配置 | macOS Preferences | JSON 文件 |
| 平台 | 仅 macOS | macOS / Linux / Windows |

## 2. 业务目标与成功指标

| 目标 | 指标 | 目标值 | 数据来源 |
|------|------|--------|----------|
| 跨平台一致体验 | 支持平台数 | 3（macOS/Linux/Windows） | [build.sh](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L253-L297) |
| 脚本丰富度 | 内置脚本数 | 60+ | [scripts/](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/scripts) 目录 |
| 启动响应快 | 主窗口初始化耗时 | < 1s | [app/__main__.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/__main__.py#L16-L75) 已埋点 |
| 脚本执行安全 | 崩溃不影响主进程 | 100%（子进程隔离） | [app/core/utils.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/utils.py#L11-L94) |
| 分发包体积适中 | 安装包大小 | < 50 MB | PyInstaller `--onedir` + UPX 压缩 |

## 3. 干系人与用户画像

| 画像 | 角色 | 目标 | 痛点 |
|------|------|------|------|
| 开发者 | 写代码的工程师 | 快速对文本做格式化/转换，不打断编码流 | IDE 内置工具能力有限，切换浏览器工具成本高 |
| 脚本作者 | 扩展工具的用户 | 用 Python 编写自定义文本处理脚本 | 需要简单可测的脚本契约与依赖安装机制 |
| 运维者 | 打包分发的人 | 一键产出三平台安装包 | 跨平台依赖与图标处理繁琐 |

## 4. 业务能力（顶层）

- **CAP-1 文本编辑** — Tkinter 编辑器，支持撤销/重做、多光标、缩进、剪贴板（[app/ui/editor.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/ui/editor.py)）
- **CAP-2 脚本执行** — 子进程隔离执行用户脚本，超时控制，结果回传（[app/core/utils.py#run_script_in_subprocess](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/utils.py#L11-L94)）
- **CAP-3 脚本管理** — 多目录加载、元数据解析（docstring 内 JSON）、缓存（[app/core/script.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/script.py)、[app/core/script_metadata.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/script_metadata.py)）
- **CAP-4 脚本发现** — 模糊搜索选择器，按名称/描述/标签匹配（[app/ui/script_picker.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/ui/script_picker.py)）
- **CAP-5 快捷键** — 应用内绑定 + 系统级全局热键（[app/core/shortcut_manager.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/shortcut_manager.py)、[app/core/global_hotkey.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/global_hotkey.py)）
- **CAP-6 配置管理** — JSON 持久化配置，含字体/窗口/脚本目录/Python 路径（[app/config/settings.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/config/settings.py)）
- **CAP-7 偏好设置** — 多 Tab GUI：General / Scripts / Logs（[app/ui/preferences.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/ui/preferences.py)）
- **CAP-8 依赖安装** — 解析脚本声明的依赖并 pip 安装（[app/ui/preferences.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/ui/preferences.py) Scripts Tab）
- **CAP-9 可观测性** — 滚动日志文件（5MB×3）+ stdout（[app/core/log.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/log.py)）
- **CAP-10 事件通信** — 进程内发布订阅解耦组件（[app/core/event.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/event.py)）

## 5. 领域术语表（Ubiquitous Language）

| 术语 | 定义 | 同义词 |
|------|------|--------|
| Script | 用户编写的 Python 文本处理单元，须定义 `main(state)` | 脚本 |
| State | 脚本执行上下文，承载输入文本与输出，提供 `post_info`/`post_error` | state |
| ScriptMetadata | 从脚本 docstring 解析的 JSON 元数据（名称/描述/标签/依赖/图标） | 元数据 |
| ScriptPicker | 模糊搜索脚本的选择器弹窗 | 脚本选择器 |
| Preferences | 偏好设置面板 | 首选项 |
| GlobalHotkey | 系统级热键，应用未聚焦时也能触发 | 全局快捷键 |
| MetadataCache | 脚本元数据磁盘缓存，按文件 mtime 失效 | 缓存 |
| script_wrapper | 子进程入口脚本，读 stdin、exec 用户脚本、写 JSON 到 stdout | 脚本包装器 |

## 6. 范围边界

**范围内：**
- 桌面 GUI 文本处理（Tkinter）
- 用户自定义 Python 脚本的加载、执行、缓存
- 跨平台打包分发（DMG / tar.gz / zip）
- 应用内与系统级快捷键

**范围外：**
- 服务端 / Web API / 多用户协作
- 数据库持久化（仅 JSON 文件配置与缓存）
- 自动更新机制（未实现，需手动分发新版本）
- 移动端
- 网络 Accounts / 云同步

## 7. 文档导航

- [C4 系统上下文](./02-c4-context.md)
- [C4 容器图](./03-c4-containers.md)
- [C4 组件图](./04-c4-components.md)
- [模块与包映射](./06-module-map.md)
- [Python 工程特性分析](./07-python-specifics.md)
- [数据流](./08-data-flow.md)
- [架构决策记录 (ADR)](./decisions/README.md)
- [新人入职指南](./10-onboarding.md)
