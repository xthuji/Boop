# Boop Python — 模块与包映射

> 基于 `Grep` 对 `^(from|import)\s+` 的扫描结果生成。

## 1. 顶层布局

```
boop/                                   # Python 项目根
├── requirements.txt                    # 依赖清单（无 pyproject.toml）
├── version.txt                         # 版本号 + PyInstaller 版本资源
├── build.sh                            # 跨平台打包脚本
├── test_app.sh                         # 测试入口
├── update_boop_scripts.sh              # 脚本更新工具
├── app/                                # 主包（flat layout）
│   ├── __init__.py                     # 版本元信息
│   ├── __main__.py                     # 入口：python -m app
│   ├── config/
│   │   ├── __init__.py                 # 重导出 BoopConfig
│   │   └── settings.py                 # BoopConfig dataclass + JSON 持久化
│   ├── core/
│   │   ├── __init__.py                 # 重导出 ScriptMetadata
│   │   ├── cache.py                    # MetadataCache
│   │   ├── event.py                   # EventSystem（发布订阅）
│   │   ├── global_hotkey.py           # GlobalHotkeyManager
│   │   ├── log.py                     # 日志配置 + 全局 logger
│   │   ├── path.py                    # 路径解析
│   │   ├── script.py                  # ScriptManager
│   │   ├── script_metadata.py         # ScriptMetadata 解析
│   │   ├── script_wrapper.py          # 子进程入口脚本
│   │   ├── shortcut_manager.py        # ShortcutManager
│   │   └── utils.py                    # run_script_in_subprocess 等
│   └── ui/
│       ├── __init__.py                 # 重导出 MainWindow 等
│       ├── editor.py                   # Editor
│       ├── editor_extensions.py        # EditorExtensions
│       ├── main.py                     # MainWindow
│       ├── preferences.py             # PreferencesPanel
│       └── script_picker.py           # ScriptPickerPopup
├── scripts/                            # 用户脚本包（60+ 脚本）
│   ├── __init__.py
│   ├── lib/base.py                    # State 基类
│   ├── format_*.py / convert_*.py / ... 
├── data/config.json                   # 默认配置样本
├── icons/                             # 图标资源 + convert_icons.py
└── tests/
    ├── test_editor_keys.py             # 编辑器按键测试
    ├── test_key_states.py              # 按键状态测试
    └── test_scripts/
        ├── run_tests.py               # 自研测试运行器
        ├── run_tests.sh
        └── test_cases_*.json          # 测试用例数据
```

**布局类型**：flat（`app/` 与 `scripts/` 直接位于项目根）
**根包名**：`app`

> `[OUTDATED — 已修复 2026-09-10]` 旧 README 曾写 `python3 -m boop` 与实际包名 `app` 不一致，现已修正。
**Python 版本要求**：3.9+（依赖 `dataclasses` field 默认、typing 语法；证据：[README.md](file:///Users/huji/work/MyProject/code_mine/gitee/boop/README.md#L23)）

## 2. 内部依赖图

由 Grep 抽取的 `app.*` 内部导入关系（仅列内部依赖）：

```
app/__main__.py            → app.config.settings, app.ui.main, app.core.log, app.core.path
app/config/__init__.py     → app.config.settings
app/config/settings.py     → app.core.log
app/core/__init__.py       → app.core.script_metadata
app/core/cache.py          → app.core.path, app.core.log
app/core/event.py          → app.core.log
app/core/global_hotkey.py  → app.core.log, app.core.shortcut_manager
app/core/log.py            → app.core.path
app/core/script.py         → app.config.settings, app.core.cache, app.core.script_metadata, app.core.log
app/core/script_metadata.py→ app.core.log
app/core/shortcut_manager.py→ app.core.log
app/core/utils.py          → （模块级仅 stdlib；函数内懒加载 app.core.log、pynput、pyperclip）
app/ui/__init__.py         → app.ui.main, app.ui.script_picker, app.ui.preferences
app/ui/editor.py           → app.core.shortcut_manager, app.ui.editor_extensions, app.core.log
app/ui/editor_extensions.py→ app.core.log
app/ui/main.py             → app.config.settings, app.core.script, app.core.utils, app.core.shortcut_manager,
                             app.core.event, app.core.log, app.core.global_hotkey, app.ui.editor, app.ui.script_picker
app/ui/preferences.py      → app.config.settings, app.core.log, app.core.utils, app.core.path
app/ui/script_picker.py    → app.core.script, app.core.utils, app.core.log
```

## 3. 分层与分层违规

目标分层（上层依赖下层，禁止反向）：

1. **入口/界面层** — `app.ui`, `app/__main__.py`
2. **核心服务层** — `app.core`
3. **配置层** — `app.config`
4. **基础设施** — `app.core.path`, `app.core.log`（被所有层依赖）

### 分层违规清单

| 序号 | 违规 | 严重度 | 证据 | 建议 |
|------|------|--------|------|------|
| L1 | `app.core.script` 导入 `app.config.settings` —— core 反向依赖 config | 🔴 高 | [script.py#L6](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/script.py#L6) | 将 `BoopConfig` 移至 `app.core` 或下沉为独立 `app.model` 层；或让 `ScriptManager` 接收 `script_directories` 参数而非整个 config |
| L2 | `app.config.settings` 导入 `app.core.log` —— config 反向依赖 core | 🟡 中 | [settings.py#L9](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/config/settings.py#L9) | config 层应不依赖日志；改为返回错误码或让调用方注入 logger |
| L3 | `app.core.shortcut_manager` 导入 `tkinter` —— core 层依赖 UI 库 | 🔴 高 | [shortcut_manager.py#L5](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/shortcut_manager.py#L5) | `ShortcutManager` 含 Tk 绑定逻辑，应移至 `app.ui` 或拆分：纯解析逻辑留 core，Tk 绑定逻辑进 ui |

> L1 与 L2 共同构成 `app.core` ↔ `app.config` 的**双向依赖**：`script → settings → log`，虽不形成循环（`log` 不导入 `config`/`script`），但增加了边界模糊度。

## 4. 循环导入

**未检测到运行期循环导入。** 所有内部依赖形成有向无环图（DAG）：

```
app.ui.main → app.core.script → app.config.settings → app.core.log → app.core.path
                                                                            ↑（终止）
```

`app.core.path` 仅导入 stdlib（`sys`、`pathlib`、`typing`），是依赖链的终点。

## 5. 入口点

| 名称 | 类型 | 位置 | 调用方式 | 证据 |
|------|------|------|----------|------|
| `main()` | GUI 主进程入口 | `app/__main__.py#L14-L75` | `python -m app` | [__main__.py#L78-L79](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/__main__.py#L78-L79) |
| `script_wrapper` | 子进程入口 | `app/core/script_wrapper.py` | 由主进程 `subprocess.Popen` 启动，无 `__main__` guard | [utils.py#L62-L68](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/utils.py#L62-L68) |
| `run_tests.py` | 测试运行器 | `tests/test_scripts/run_tests.py` | `python run_tests.py` 或 `./run_tests.sh` | [run_tests.py#main](file:///Users/huji/work/MyProject/code_mine/gitee/boop/tests/test_scripts/run_tests.py) |
| `convert_icons.py` | 图标转换工具 | `icons/convert_icons.py` | 手动执行 | [icons/convert_icons.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/icons/convert_icons.py) |

## 6. 功能重复（跨文件）

| 重复功能 | 位置 A | 位置 B | 评估 |
|----------|--------|--------|------|
| `normalize_shortcut` | `app/core/utils.py#L110`（函数） | `app/core/shortcut_manager.py#L54`（方法） | 🔴 完全重复。`utils.py` 版本疑似遗留，`shortcut_manager` 已被 `main.py`/`editor.py` 采用 |
| `get_tk_shortcut` | `app/core/utils.py#L126` | `app/core/shortcut_manager.py#L77` | 🔴 同上 |
| `parse_hotkey_for_pynput` | `app/core/utils.py#L138` | `app/core/shortcut_manager.py#L87` | 🔴 同上 |
| `binding_hotkey_action` | `app/core/utils.py#L196` | `app/core/shortcut_manager.py#bind_hotkey#L140` | 🔴 同上 |
| `State` 类 | `app/core/script_wrapper.py#L18-L31`（`ScriptExecution`） | `scripts/lib/base.py#L4-L13`（`State`） | 🟡 两份相似的运行时上下文实现，名字不同字段相近。`script_wrapper` 内联了 `State` 逻辑而未复用 `lib/base.py` |

建议：删除 `utils.py` 中四个快捷键函数（确认无外部调用后），统一走 `shortcut_manager`。

## 7. 外部依赖足迹

### 运行时第三方依赖（证据：[requirements.txt](file:///Users/huji/work/MyProject/code_mine/gitee/boop/requirements.txt)）

| 依赖 | 版本约束 | 用途 | 使用点 | 关键路径 |
|------|----------|------|--------|----------|
| `pynput` | `>=1.7.6` | 全局键盘事件监听 | `app/core/global_hotkey.py`、`app/core/shortcut_manager.py` | 是 |
| `pyperclip` | `>=1.8.2` | 系统剪贴板访问 | `app/core/utils.py#get_clipboard_content`（懒加载） | 否 |
| `tkinter` | （stdlib） | GUI | 全部 `app/ui/*` | 是 |

### 构建期依赖

| 依赖 | 版本约束 | 用途 |
|------|----------|------|
| `pyinstaller` | `>=5.0` | 跨平台打包 |
| `Pillow` | `>=9.0` | 图标处理（`icons/convert_icons.py`） |

### 脚本动态依赖（声明在脚本 docstring 的 `dependencies` 字段，按需 pip 安装）

| 依赖 | 声明于 | 用途 |
|------|--------|------|
| `json5` | `scripts/format_json.py` | 宽松 JSON 解析 |
| `yaml`（PyYAML） | `scripts/format_yaml.py`、`scripts/convert_data_yaml_json.py` | YAML 解析 |
| `bs4`（BeautifulSoup4） | `scripts/format_html.py` | HTML 解析 |
| `lxml` | `scripts/format_html.py` | HTML 解析后端 |
| `jsbeautifier` | `scripts/format_typescript.py` | JS/TS 格式化 |
| `sqlparse` | `scripts/format_sql.py` | SQL 格式化 |
| `webview`（pywebview） | `scripts/manage_todo.py` | 待办事项 GUI |

> ⚠️ `webview`（pywebview）体积大、依赖系统 WebView 运行时，仅为单个 `manage_todo.py` 脚本使用。建议评估是否值得内置，或拆为可选脚本。

## 8. 标准库使用概览

scripts/ 与 app/ 中高频使用的标准库（基于 Grep）：

| 标准库 | 使用文件数 | 用途 |
|--------|-----------|------|
| `re` | ~25 | 文本正则处理（脚本主力） |
| `json` | ~8 | JSON 解析与序列化 |
| `hashlib` | 2 | MD5/哈希生成 |
| `base64` | 1 | Base64 编解码 |
| `csv`, `io`, `configparser` | 1 each | 数据格式转换 |
| `urllib.parse` | 2 | URL 编解码 |
| `random` | 3 | 字符打乱、占位文本生成 |
| `subprocess`, `threading`, `logging` | app 内 | 进程/线程/日志 |
