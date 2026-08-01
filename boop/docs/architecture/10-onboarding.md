# Boop Python — 新人入职指南

> 本指南假设从干净克隆开始。项目根：`/Users/huji/work/MyProject/code_mine/gitee/boop/boop`

## 1. 前置条件

| 要求 | 版本 | 检查命令 |
|------|------|----------|
| Python | 3.9+ | `python3 --version` |
| Tkinter | 随 Python 附带 | `python3 -c "import tkinter"` |
| 操作系统 | macOS / Linux / Windows | — |
| pip | 任意 | `python3 -m pip --version` |
| PyInstaller（仅打包时） | `>=5.0` | `python3 -m PyInstaller --version` |
| Pillow（仅构建图标时） | `>=9.0` | `python3 -c "import PIL"` |

## 2. 克隆与环境准备

```bash
git clone <repo-url>
cd boop/boop   # 进入 Python 项目根
```

### 创建虚拟环境并安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows
pip install -r requirements.txt
```

> ⚠️ 项目无 `pyproject.toml`，**不是可安装包**，不要 `pip install -e .`（会失败）。直接以源码运行。

### 配置 Python 解释器路径

首次运行需在偏好设置中指定 Python 解释器路径（用于派生子进程执行用户脚本）：

1. 启动应用（见下节）
2. `Cmd+,` / `Ctrl+,` 打开偏好 → **Scripts** Tab
3. 设置 Python Path（如 `.venv/bin/python3` 或系统 `python3`）

或直接编辑用户数据目录下的 `config.json`（路径见 [path.py#get_user_data_dir](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/path.py#L8-L35)）。

## 3. 本地运行

```bash
# 从项目根 boop/boop/ 执行
python3 -m app
```

> ⚠️ **注意**：[README.md#L21](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/README.md#L21) 写作 `python3 -m boop`，但实际包名是 `app`（见 [ADR-0002](./decisions/0002-flat-layout-with-app-package.md)）。以本文档为准。

### 首次启动行为

- 在用户数据目录创建 `config.json`（首次启动，[app/__main__.py#L66-L68](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/__main__.py#L66-L68)）
- 若 `python_path` 未设置，弹窗提示去偏好设置（[app/__main__.py#L47-L60](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/__main__.py#L47-L60)）
- 加载默认 `scripts/` 目录下的脚本元数据

### 用户数据目录位置

| 环境 | 路径 |
|------|------|
| 开发模式 | `<project>/boop/data/` |
| PyInstaller 打包后 | `<_MEIPASS>/data/` |
| 沙箱/无写权限时 | `$TMPDIR/Boop/` |

## 4. 运行测试

### 脚本测试（自研运行器）

```bash
# 跑全部脚本测试用例
cd tests/test_scripts
python3 run_tests.py

# 或用 shell 脚本
./run_tests.sh
```

测试用例存于 `test_cases_*.json`（按类别分组：case / convert / format / lines / toggle）。运行器用 `concurrent.futures` 并行执行（[run_tests.py#L14](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/tests/test_scripts/run_tests.py#L14)）。

### 编辑器按键测试

```bash
# 需要图形环境
python3 tests/test_editor_keys.py
python3 tests/test_key_states.py
```

> ⚠️ 项目无 `pytest`、无覆盖率配置（见 [Python 特性分析 §10](./07-python-specifics.md#10-测试)）。

## 5. 代码质量检查

> ⚠️ 项目当前**未配置** lint / format / type-check 工具。以下为建议命令，需先自行安装：

```bash
pip install ruff mypy
ruff check .                # lint
ruff format .               # format
mypy app/                   # type check（注解已有，但未强制）
```

## 6. 项目结构速览

详见 [模块与包映射](./06-module-map.md)。快速定位：

```
boop/boop/
├── app/                # 主包
│   ├── __main__.py     # 入口
│   ├── config/         # BoopConfig
│   ├── core/           # 脚本管理、缓存、日志、热键、事件
│   └── ui/             # MainWindow、Editor、ScriptPicker、Preferences
├── scripts/            # 60+ 用户文本处理脚本
│   └── lib/base.py     # State 基类
├── data/config.json    # 默认配置样本
├── tests/              # 自研测试运行器 + 用例 JSON
├── build.sh            # 跨平台打包
└── requirements.txt    # 依赖
```

## 7. 常见开发任务

### 新增一个文本处理脚本

1. 在 `scripts/` 下新建 `my_script.py`
2. 文件开头 docstring 内写 JSON 元数据（必需字段 `name`、`description`）：

```python
'''
{
    "name": "My Script",
    "description": "做什么用的",
    "tags": ["tag1", "tag2"],
    "icon": "★",
    "help": "使用说明",
    "dependencies": ["some-package"]
}
'''

def main(state):
    text = state.text
    state.text = text.upper()
```

3. `state` 对象 API：`state.text`（get/set）、`state.full_text`、`state.insert(text)`、`state.post_info(msg)`、`state.post_error(msg)`（见 [scripts/lib/base.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/scripts/lib/base.py)）
4. 若声明了 `dependencies`，在偏好设置 Scripts Tab 点击 **Install All Dependencies**
5. 重启应用或刷新元数据缓存即可在选择器中看到新脚本

### 添加测试用例

在 `tests/test_scripts/test_cases_<category>.json` 中追加：

```json
{
  "script": "my_script",
  "input": "hello",
  "expected": "HELLO"
}
```

### 修改快捷键默认值

编辑 [app/config/settings.py#_get_default_shortcuts](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/config/settings.py#L13-L59)。注意：保存配置时刻意删除 `shortcuts` 键（[settings.py#L106-L108](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/config/settings.py#L106-L108)），即用户自定义不会被持久化——升级默认值会影响所有用户。

### 打包分发

```bash
./build.sh              # 自动检测当前平台
./build.sh --macos      # 仅 macOS（产出 .app + 可选 .dmg）
./build.sh --linux      # 仅 Linux（产出 .tar.gz）
./build.sh --windows    # 仅 Windows（产出 .zip）
./build.sh --clean      # 清理构建产物
```

> ⚠️ `build.sh` 读取 `~/common_config.json` 的 `python_path`（[build.sh#L23](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L23)），需先准备好该文件。

## 8. 排错

| 症状 | 可能原因 | 修复 |
|------|----------|------|
| `ModuleNotFoundError: No module named 'app'` | 未在 `boop/boop/` 目录运行 | `cd boop/boop && python3 -m app` |
| 弹窗 "Python interpreter path is not set" | `config.python_path` 未配置 | 偏好设置 → Scripts → 设 Python Path |
| 脚本执行无响应 | 脚本死循环，等待超时 | 等待 `script_timeout`（默认 10s）后自动终止 |
| `ModuleNotFoundError: No module named 'json5'` | 脚本依赖未安装 | 偏好设置 → Scripts → Install All Dependencies |
| 全局热键不生效 | `enable_global_hotkeys` 为 false | 编辑 `config.json` 设为 `true`，重启 |
| macOS 下 `pynput` 无权限 | 系统隐私设置未授权 | 系统设置 → 隐私 → 辅助功能 → 勾选应用 |

## 9. 下一步阅读

- [架构与业务概览](./01-overview.md)
- [C4 系统上下文](./02-c4-context.md)
- [模块与包映射](./06-module-map.md)
- [Python 工程特性分析](./07-python-specifics.md)（含已知问题清单）
- [ADR 索引](./decisions/README.md)
