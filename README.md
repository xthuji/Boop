# Boop

基于 Python 的跨平台文本处理工具，灵感来自 macOS 原生应用 Boop。

> 🤖 **AI-Assisted Development** — 本项目主要由 AI 辅助编程完成（架构设计、代码实现、文档撰写均由 AI Agent 驱动，人类负责需求定义与代码审查）。

**特点：**
- 🐍 Python 脚本支持（70+ 内置脚本）
- ⌨️ 自定义快捷键 + 系统级全局热键
- 🔄 撤销/重做、多光标编辑
- 📁 多脚本目录管理（可配置多目录加载）
- 🎯 跨平台（macOS / Windows / Linux）
- 🔒 子进程隔离执行，脚本崩溃不影响主进程
- 🌐 一键打包发布，GitHub Actions 自动构建三平台产物

---

## 快速开始

### 安装运行

```bash
pip install -r requirements.txt
python3 -m app
```

### 环境要求

| 要求 | 版本 |
|------|------|
| Python | 3.9+ |
| Tkinter | 随 Python 附带（macOS: `brew install python-tk`；Ubuntu: `apt install python3-tk`） |

### 打包桌面应用

```bash
./run_tools.sh build          # 构建当前平台的桌面应用
./run_tools.sh                # 交互式菜单（回车默认 dev）
./release.sh --dry-run        # 预览发布命令（创建 tag 触发 CI）
```

**打包产物（按平台自动生成）：**

| 平台 | 产物 |
|------|------|
| macOS | `release/Boop_v{version}.dmg` |
| Windows | `release/Boop_v{version}_windows_amd64.zip` |
| Linux | `release/Boop_v{version}_linux_amd64.tar.gz` |

**CI/CD（GitHub Actions）：** 推送 `v*` 标签自动触发三平台并行构建，产物上传至 GitHub Release。

---

## 使用

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Cmd+B` / `Ctrl+B` | 打开脚本选择器 |
| `Cmd+,` / `Ctrl+,` | 打开首选项 |
| `Cmd+Q` / `Ctrl+Q` | 退出 |
| `Cmd+Z` / `Ctrl+Z` | 撤销 |
| `Cmd+Shift+Z` / `Ctrl+Shift+Z` | 重做 |
| `Cmd+D` / `Ctrl+D` | 选中下一个匹配项（多光标编辑） |
| `Escape` | 退出多光标编辑模式 |
| `Cmd+Home` / `Ctrl+Home` | 移动到文档开头 |
| `Cmd+End` / `Ctrl+End` | 移动到文档结尾 |
| `Cmd+Shift+Home` / `Ctrl+Shift+Home` | 选中到文档开头 |
| `Cmd+Shift+End` / `Ctrl+Shift+End` | 选中到文档结尾 |
| `Tab` | 增加缩进 |
| `Shift+Tab` | 减少缩进 |

### 基本流程

1. 输入或粘贴文本
2. 按 `Cmd+B` / `Ctrl+B` 打开脚本选择器
3. 搜索并选择脚本，按 `Enter` 运行
4. 查看处理结果

---

## 编写脚本

### 脚本模板

```python
'''
{
    "name": "脚本名称",
    "description": "功能描述",
    "tags": ["标签"],
    "icon": "★",
    "help": "使用说明",
    "dependencies": ["requests"]
}
'''

def main(state):
    text = state.text
    state.text = text.upper()  # 示例：转大写
```

### 元数据字段

| 字段 | 说明 |
|------|------|
| `name` | 脚本名称 |
| `description` | 功能描述 |
| `tags` | 搜索标签 |
| `icon` | 图标 |
| `help` | 帮助说明 |
| `dependencies` | 依赖包列表 |

### state API

| 方法 | 说明 |
|------|------|
| `state.text` | 获取/设置选中文本（主要输入输出接口） |
| `state.full_text` | 获取全部内容（只读，与 text 相同） |
| `state.selection` | 获取选中文本（只读，与 text 相同） |
| `state.insert(text)` | 在光标处插入文本（会替换 text） |
| `state.post_info(msg)` | 显示提示信息 |
| `state.post_error(msg)` | 显示错误信息 |

> 💡 **注意**: 运行时 State 类由 `app/core/script_wrapper.py` 提供，包含完整 API。`scripts/lib/base.py` 提供简化的 State 类供脚本导入使用（仅含 `text`、`post_info`、`post_error`）。

### 安装依赖

1. 在脚本元数据中添加 `dependencies`
2. 首选项 → Scripts → **Install All Dependencies**

---

## 配置

按 `Cmd+,` / `Ctrl+,` 打开首选项：

- **General**：窗口大小、字体、主题
- **Scripts**：脚本目录、Python 解释器路径、依赖管理
- **Logs**：日志查看和清除

---

## 项目结构

```
boop/
├── .github/workflows/release.yml   # CI 发布流程（三平台并行构建）
├── app/                            # 主包（运行入口）
│   ├── __main__.py                 # `python -m app` 入口
│   ├── config/                     # BoopConfig + JSON 持久化
│   ├── core/                       # 脚本管理 / 缓存 / 日志 / 热键 / 事件
│   └── ui/                         # MainWindow / Editor / ScriptPicker / Preferences
├── scripts/                        # 70+ 内置脚本（格式化、转换、编解码、行操作等）
├── data/config.json                # 默认配置样本
├── icons/                          # 图标资源（.icns / .ico / .png）
├── docs/                           # 架构与开发文档 + ADR
├── tests/                          # 脚本测试 + 编辑器测试
├── LICENSE                         # MIT License
├── run_tools.sh                    # 构建/运行/测试一体化工具（交互菜单或命令行）
├── release.sh                      # Git tag 发布辅助脚本
├── version.txt                     # 版本号（单一来源）
└── requirements.txt                # 依赖清单
```

---

## 构建与发布流程

### 本地构建

```bash
# 开发模式（直接 python -m app 运行）
./run_tools.sh dev

# 构建并运行桌面应用
./run_tools.sh run

# 打包当前平台
./run_tools.sh build
```

### CI 发布流程

```bash
# 1. 更新 version.txt 中的版本号
# 2. 创建 tag 并推送
./release.sh                          # 读取 version.txt
./release.sh --version=1.1.0          # 强制指定版本
./release.sh --version=1.1.0 --dry-run # 预览不执行
```

推送 `v{version}` 标签后，GitHub Actions 将自动：

1. 在 `macos-latest` / `ubuntu-latest` / `windows-latest` 三平台并行构建
2. 使用 PyInstaller 打包桌面应用
3. 生成 `.dmg` / `.tar.gz` / `.zip` 产物
4. 上传至 GitHub Release 对应 Tag

---

## 文档

完整架构与开发文档见 [docs/architecture.md](./docs/architecture.md)（产品定位、C4 架构图、数据流、模块分析、工程特性、已知问题）。

架构决策记录（ADR）见 [docs/decisions/README.md](./docs/decisions/README.md)。

---

## 与原 Boop 的区别

| 特性 | 原 Boop | Boop Python |
|------|---------|-------------|
| 脚本语言 | JavaScript | Python |
| 执行方式 | JavaScriptCore | 子进程隔离 |
| UI | 原生 macOS (Swift) | Tkinter (跨平台) |
| 配置 | macOS Preferences | JSON 文件 |
| 平台 | 仅 macOS | macOS / Windows / Linux |

---

## Contributing

### 环境准备

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate             # Windows
pip install -r requirements.txt
python3 -m app                     # 启动应用（包名是 app，不是 boop）
```

> ⚠️ 项目无 `pyproject.toml`，**不是可安装包**，不要 `pip install -e .`。
> 首次运行后需在 **偏好 → Scripts → Python Path** 指定解释器（用于派生子进程执行用户脚本）。

### 运行测试

```bash
# 脚本测试（自研运行器，并行执行）
cd tests/test_scripts && python3 run_tests.py

# 使用 run_tools.sh 运行测试（自动安装 pytest）
./run_tools.sh test

# 编辑器按键测试（需要图形环境）
python3 tests/test_editor_keys.py
python3 tests/test_key_states.py
```

> 💡 项目提供两种测试方式：自研测试运行器（tests/test_scripts/run_tests.py）和 pytest（通过 run_tools.sh test）。

### 代码质量检查

> 项目当前未配置 lint/format/type-check 工具，需先自行安装：

```bash
pip install ruff mypy
ruff check .                # lint
ruff format .               # format
mypy app/                   # type check
```

### 常见开发任务

**新增脚本** → 在 `scripts/` 下新建 `.py`，文件开头 docstring 写 JSON 元数据（`name`、`description` 必填），定义 `main(state)` 函数。若声明了 `dependencies`，在偏好设置 Scripts Tab 点击 **Install All Dependencies**。

**添加测试用例** → 在 `tests/test_scripts/test_cases_<category>.json` 中追加：
```json
{ "script": "my_script", "input": "hello", "expected": "HELLO" }
```

**打包分发**：

```bash
./run_tools.sh build       # 构建当前平台
./run_tools.sh run         # 构建并运行 App
./run_tools.sh dev         # 开发模式：python -m app
./run_tools.sh test        # 运行单元测试
./run_tools.sh clean       # 清理构建产物
```

> 💡 Python 解释器自动探测顺序：环境变量 `BOOP_PYTHON` → 当前已激活 venv → `command -v python3`。

### 排错

| 症状 | 修复 |
|------|------|
| `ModuleNotFoundError: No module named 'app'` | 在项目根目录运行 `python3 -m app` |
| 弹窗 "Python interpreter path is not set" | 偏好设置 → Scripts → 设 Python Path |
| 脚本执行无响应 | 等待 `script_timeout`（默认 10s）后自动终止 |
| `ModuleNotFoundError: No module named 'json5'` | 偏好设置 → Scripts → Install All Dependencies |
| 全局热键不生效 | 编辑 `config.json` 设 `enable_global_hotkeys: true`，重启 |
| macOS `pynput` 无权限 | 系统设置 → 隐私 → 辅助功能 → 勾选应用 |

### 深入阅读

- [架构与开发文档](./docs/architecture.md) — 模块依赖、分层违规、工程特性评估、已知问题
- [ADR 索引](./docs/decisions/README.md) — 架构决策记录

---

## License

[MIT](./LICENSE) © Boop Contributors

灵感来自原 Boop 项目，参见原 [LICENSE](https://github.com/IvanMathy/Boop/blob/main/LICENSE)。
