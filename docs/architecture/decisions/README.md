# ADR 索引

| # | 标题 | 状态 | 日期 |
|---|------|------|------|
| [0001](./0001-use-subprocess-isolation-for-scripts.md) | 使用子进程隔离执行用户脚本 | Accepted | 2026-08-01 |
| [0002](./0002-flat-layout-with-app-package.md) | 采用 flat 布局与 `app` 包名 | Accepted | 2026-08-01 |
| [0003](./0003-pyinstaller-for-cross-platform-distribution.md) | 使用 PyInstaller 进行跨平台分发 | Accepted | 2026-08-01 |
| [0004](./0004-tkinter-for-cross-platform-gui.md) | 采用 Tkinter 作为 GUI 框架 | Accepted | 2026-08-01 |

## 待补充的决策

以下决策尚未记录为 ADR，建议后续补齐：

- **0005**：自研测试运行器 vs pytest（当前用自研 `run_tests.py`，见 [Python 特性分析 §10](../07-python-specifics.md#10-测试)）
- **0006**：同步模型 + threading for 全局热键（见 [Python 特性分析 §5](../07-python-specifics.md#5-异步模型)）
- **0007**：脚本元数据用 docstring 内 JSON 而非 sidecar 文件
- **0008**：是否引入 `pyproject.toml` 规范化打包（见 [Python 特性分析 §1](../07-python-specifics.md#1-打包与构建后端)）

## 模板

新增 ADR 时复制 [ADR 模板](../../methodology/adr-template.md)，编号取下一个未用数字。
