# Boop Python — Python 工程特性分析

> 评估准则：✅ 对齐主流 / ⚠️ 偏离主流 / 🔴 风险。每项附文件证据。

## 1. 打包与构建后端

**当前状态**：无 `pyproject.toml`，无 `setup.py`/`setup.cfg`。项目以 `requirements.txt` + `build.sh` 组织，**不是可安装的 Python 包**，而是直接以源码运行。
**证据**：项目根无 `pyproject.toml`（Glob 未命中）；[requirements.txt](file:///Users/huji/work/MyProject/code_mine/gitee/boop/requirements.txt) 仅列依赖；[build.sh](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh) 直接调 PyInstaller。
**评估**：🔴 风险。不符合 PEP 517/518/621 主流规范；无法 `pip install -e .`；无法发布到 PyPI；依赖与构建元数据无单一来源。
**建议**：补一份 `pyproject.toml`（`[build-system]` 用 `setuptools` 或 `hatchling`，`[project]` 块声明元数据与依赖），保留 `requirements.txt` 作为锁定文件。

## 2. 依赖管理

**当前状态**：`pip` + `requirements.txt`，**无锁文件**（无 `requirements.lock` / `uv.lock` / `poetry.lock`）。
**证据**：[requirements.txt](file:///Users/huji/work/MyProject/code_mine/gitee/boop/requirements.txt) 仅用 `>=` 下限约束；[build.sh#L359](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh#L359) `pip install -r requirements.txt`。
**评估**：⚠️ 偏离。无锁文件意味着构建不可重现；`>=` 下限允许次要版本漂移；脚本动态依赖（json5、yaml 等）完全未声明在 `requirements.txt`。
**建议**：用 `pip-tools` 生成 `requirements.lock`（含哈希），或将脚本依赖按 optional-dependencies 分组写入 `pyproject.toml`。

## 3. 环境管理

**当前状态**：依赖开发者自备 Python 环境（构建脚本读 `~/common_config.json` 中的 `python_path`，证据：[build.sh#L23](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh#L23)）。运行期允许用户在偏好设置中指定 Python 解释器路径（`config.python_path`）。
**证据**：[app/core/utils.py#L24-L49](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/utils.py#L24-L49) 列出常见 miniconda 路径作为回退；[data/config.json#L5](file:///Users/huji/work/MyProject/code_mine/gitee/boop/data/config.json#L5) 指向 `/Users/huji/miniconda3/envs/python39/bin/python3`。
**评估**：⚠️ 偏离。无 `venv`/`uv venv` 标准化流程；个人开发者机器路径被写进样本配置；新人难以复现。
**建议**：提供 `.python-version` + `Makefile`/`justfile` 目标统一创建 venv；`data/config.json` 中 `python_path` 应为空或占位符，避免泄露个人路径。

## 4. 类型系统

**当前状态**：**广泛使用类型注解**（`from typing import ...`、`Optional`、`List`、`Dict`、`Callable`），但**无类型检查器配置**（无 `mypy.ini`、`pyrightconfig.json`、`pyproject.toml [tool.mypy]`）。运行期验证用 `dataclasses`，未使用 Pydantic。
**证据**：[app/config/settings.py#L7-L8](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/config/settings.py#L7-L8)、[app/core/script_metadata.py#L9](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/script_metadata.py#L9)；项目根无 mypy/pyright 配置文件。
**评估**：⚠️ 偏离。注解存在但不被强制，易腐化。`typing.List/Optional/Dict` 用法可迁移到 PEP 585/604 字面量（`list[str] | None`），前提是 Python 3.9+。
**建议**：引入 `ruff`（含 `pyupgrade` 规则）+ `mypy --strict` 起步门槛；将 `List/Dict/Optional` 迁移到内建泛型。

## 5. 异步模型

**当前状态**：**全同步**，无 `async`/`await`、无 `asyncio`、无 ASGI。仅用 `threading` 跑全局热键监听 daemon 线程。
**证据**：Grep `async def` / `asyncio` 在 `app/` 中无命中；[app/core/global_hotkey.py#L5-L6](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/global_hotkey.py#L5-L6) 使用 `threading.Thread`；[build.sh#L55](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh#L55) 显式排除 `asyncio`/`concurrent`。
**评估**：✅ 对齐。桌面 GUI 以 Tk 主循环为主，同步模型正确；全局热键用 daemon 线程是合理选择。
**风险点**：[app/core/global_hotkey.py#L90-L92](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/global_hotkey.py#L90-L92) 监听线程通过 `self.main_window.root.after(0, callback)` 调度回主线程，正确做法（Tk 非线程安全，跨线程更新 UI 必须 `after`）。

## 6. Web 框架

**当前状态**：无。纯桌面 GUI 应用。
**评估**：✅ 不适用（无 Web 组件）。

## 7. 数据层

**当前状态**：无 ORM、无数据库。持久化全部走 JSON 文件：
- `config.json` —— 用户配置（[app/config/settings.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/config/settings.py)）
- `cache/metadata.json` —— 脚本元数据缓存（[app/core/cache.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/cache.py)）
- `logs/boop.log` —— 滚动日志（[app/core/log.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/log.py)）
**评估**：✅ 对齐。桌面工具用 JSON 文件恰当，无需引入数据库。
**风险点**：[app/core/cache.py#L78](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/cache.py#L78) `cached_data['mtime'] >= file_mtime` 用 `>=` 而非 `>`，文件同秒保存可能误判缓存有效；但 mtime 秒级精度通常够用。

## 8. CLI

**当前状态**：无 CLI 框架。`build.sh` 是 Bash 脚本提供构建 CLI；Python 端无 `argparse`/`click`/`typer` 入口。
**证据**：`app/__main__.py` 直接启动 GUI，无参数解析。
**评估**：⚠️ 轻微偏离。无 `--version`/`--help` 程序化入口；用户只能通过 GUI 操作。
**建议**：可选——为 `__main__.py` 加 `argparse` 支持 `--version`、`--script <name>` 直接执行脚本的非交互模式。

## 9. 配置与密钥

**当前状态**：自研 `BoopConfig` dataclass + `from_file`/`save` JSON 序列化；无 pydantic-settings、无 dynaconf。
**证据**：[app/config/settings.py#L61-L113](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/config/settings.py#L61-L113)。
**评估**：✅ 对齐（轻量级场景）。dataclass + JSON 对桌面工具够用。
**风险点**：
- 🔴 [data/config.json#L5](file:///Users/huji/work/MyProject/code_mine/gitee/boop/data/config.json#L5) 含开发者个人绝对路径 `/Users/huji/miniconda3/...`，作为样本文件提交不规范。
- 🟡 [settings.py#L93](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/config/settings.py#L93) `cls(**data)` 反序列化时若 JSON 含未知字段会抛 `TypeError`；建议加 `**kwargs` 容错或显式过滤。
- 🟡 [settings.py#L106-L108](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/config/settings.py#L106-L108) 保存时删除 `shortcuts` 键（不持久化快捷键），但加载时又依赖默认值——若默认值升级，旧配置的快捷键会被静默覆盖。

## 10. 测试

**当前状态**：**自研测试运行器** `tests/test_scripts/run_tests.py`，基于 `unittest` + `concurrent.futures` 并行执行；测试用例存于 `test_cases_*.json` 数据文件。无 `pytest`、无 `conftest.py`、无 `tox.ini`/`noxfile.py`、**无覆盖率配置**。
**证据**：[tests/test_scripts/run_tests.py#L10-L18](file:///Users/huji/work/MyProject/code_mine/gitee/boop/tests/test_scripts/run_tests.py#L10-L18)（`import unittest`/`concurrent.futures`，无 `pytest`）；项目根无 `pytest.ini`/`pyproject.toml [tool.pytest]`。
**评估**：⚠️ 偏离。自研运行器虽满足需求，但失去 pytest 生态（fixtures、插件、IDE 集成、覆盖率报告）。
**建议**：迁移到 `pytest`，保留 JSON 用例作为参数化数据（`@pytest.mark.parametrize`）；加 `pytest-cov` 设 `--cov-fail-under=60` 起步。

## 11. 代码质量

**当前状态**：**无任何 lint/format/type-check 配置**。无 `ruff.toml`、`.flake8`、`.pylintrc`、`mypy.ini`、`.pre-commit-config.yaml`。
**证据**：项目根与 `app/` 均无对应配置文件。
**评估**：🔴 风险。代码风格靠人工维持，长期会腐化（已出现 [utils.py 与 shortcut_manager.py 的功能重复](./06-module-map.md#6-功能重复跨文件)）。
**建议**：引入 `ruff`（lint+format，零配置起步）+ `pre-commit`，最低规则集 `E,F,I,UP,B,S`。

## 12. 可观测性

**当前状态**：stdlib `logging`，`RotatingFileHandler` 5MB×3 备份，`AbbreviatedPathFormatter` 缩写 logger 名。开发态 DEBUG，打包后 INFO。无结构化日志、无 metrics、无 tracing、无错误追踪服务。
**证据**：[app/core/log.py#L36-L69](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/log.py#L36-L69)。
**评估**：✅ 对齐（桌面工具场景）。日志埋点充分，`__main__.py` 与 `MainWindow` 均记录阶段耗时。
**小问题**：🟡 [log.py#L29](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/log.py#L29) 缩写逻辑判断 `record.name.startswith('boop.')`，但实际 logger 名是 `app.core.xxx`（包名是 `app` 不是 `boop`），缩写分支永远不触发——遗留 bug。

## 13. 部署

**当前状态**：PyInstaller `--onedir --windowed` + UPX 压缩；产出 macOS DMG / Linux tar.gz / Windows zip。无 Docker、无 serverless、无 systemd。
**证据**：[build.sh#L116-L158](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh#L116-L158)。
**评估**：✅ 对齐。桌面应用用 PyInstaller 是行业标准。
**亮点**：`EXCLUDE_MODULES` 列表（[build.sh#L43-L77](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh#L43-L77)）精细裁剪标准库，减小体积。
**风险点**：
- 🟡 [build.sh#L228](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh#L228) `clean_py_files` 删除 `dist` 下所有 `.py`（仅保留 `.pyc`），但 `scripts/` 与 `script_wrapper.py` 除外——若用户脚本依赖同目录 `.py` 文件存在（如 `from lib.base import State`），打包后可能失效。
- 🟡 [build.sh#L272](file:///Users/huji/work/MyProject/code_mine/gitee/boop/build.sh#L272) DMG 构建交互式 `read -p`，不利于 CI 自动化。

## 14. 安全

**当前状态**：无依赖扫描、无密钥扫描、无 SAST 配置。
**证据**：无 `pip-audit`/`safety`/`bandit`/`gitleaks` 配置。
**评估**：⚠️ 偏离。
**关键风险**：🔴 [app/core/script_wrapper.py#L46](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/script_wrapper.py#L46) `exec(script_code, script_namespace)` 执行用户脚本——这是**设计上的核心风险面**，但通过子进程隔离 + 超时缓解（见 [ADR-0001](./decisions/0001-use-subprocess-isolation-for-scripts.md)）。子进程仍继承主进程文件系统权限，恶意脚本可读写用户目录下文件。
**建议**：
- 引入 `pip-audit` 到 CI（若后续建 CI）。
- 文档化"只运行可信脚本"的安全前提。
- 考虑限制子进程工作目录或使用沙箱（如 `firejail`，Linux）。

## 已知问题汇总（按优先级）

| # | 问题 | 严重度 | 位置 |
|---|------|--------|------|
| 1 | 无 `pyproject.toml`，非可安装包 | 🔴 高 | 项目根 |
| 2 | `core` ↔ `config` 双向依赖 + `shortcut_manager` 在 core 却依赖 tkinter | 🔴 高 | [module-map §3](./06-module-map.md#3-分层与分层违规) |
| 3 | `utils.py` 与 `shortcut_manager.py` 四个函数完全重复 | 🔴 高 | [module-map §6](./06-module-map.md#6-功能重复跨文件) |
| ~~4~~ | ~~README 写 `python3 -m boop` 但实际包名是 `app`~~ | ✅ 已修复 | [README.md#L21](file:///Users/huji/work/MyProject/code_mine/gitee/boop/README.md#L21)（2026-09-10 已改为 `python3 -m app`） |
| 5 | `data/config.json` 含开发者个人绝对路径 | 🟡 中 | [data/config.json#L3-L5](file:///Users/huji/work/MyProject/code_mine/gitee/boop/data/config.json#L3-L5) |
| 6 | 无 lint/type-check/test 覆盖工具链 | 🟡 中 | 项目根 |
| 7 | `log.py` 缩写分支判断 `boop.` 但实际包名 `app.` | 🟡 中 | [log.py#L29](file:///Users/huji/work/MyProject/code_mine/gitee/boop/app/core/log.py#L29) |
| 8 | `manage_todo.py` 引入 `pywebview` 重依赖仅服务单脚本 | 🟢 低 | [scripts/manage_todo.py#L19](file:///Users/huji/work/MyProject/code_mine/gitee/boop/scripts/manage_todo.py#L19) |
