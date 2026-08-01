# Boop Python — 架构文档

> 由 `python-arch-doc` skill 基于代码勘察生成（2026-08-01）。所有结论附文件证据。

本目录包含 Boop Python 项目的完整架构与业务文档，按 C4 模型 + ADR 组织，并补充 Python 工程特性分析。

## 文档清单

| # | 文档 | 说明 |
|---|------|------|
| 1 | [架构与业务概览](./01-overview.md) | 产品定位、业务目标、能力清单、术语表、范围边界 |
| 2 | [C4 L1 系统上下文](./02-c4-context.md) | 系统与外部参与者/系统的关系 |
| 3 | [C4 L2 容器图](./03-c4-containers.md) | 主进程 GUI 容器 + 脚本执行子进程容器 |
| 4 | [C4 L3 组件图](./04-c4-components.md) | app.ui / app.core / app.config 包级分解 |
| 5 | [模块与包映射](./06-module-map.md) | 内部依赖图、分层违规、循环导入、功能重复 |
| 6 | [Python 工程特性分析](./07-python-specifics.md) | 14 项工程维度评估 + 已知问题清单 |
| 7 | [数据流](./08-data-flow.md) | 4 个代表性用户旅程的序列图 |
| 8 | [ADR 索引](./decisions/README.md) | 架构决策记录列表 |
| 9 | [新人入职指南](./10-onboarding.md) | 环境搭建、运行、测试、打包、排错 |

## 快速结论

**架构风格**：单体 Tkinter 桌面应用 + 子进程隔离脚本执行。同步模型，单主线程 + 1 daemon 线程（全局热键）。

**Top 3 优势**
1. **进程级脚本隔离**——用户脚本崩溃不影响主应用（[ADR-0001](./decisions/0001-use-subprocess-isolation-for-scripts.md)）
2. **精细的 PyInstaller 裁剪**——`EXCLUDE_MODULES` 列表把体积控制在 ~30-40MB
3. **充分日志埋点**——`__main__.py` 与 `MainWindow` 各阶段耗时记录

**Top 3 风险**
1. **无 `pyproject.toml`**——非可安装包，依赖与构建元数据无单一来源（[Python 特性分析 §1](./07-python-specifics.md#1-打包与构建后端)）
2. **分层违规**——`core` ↔ `config` 双向依赖；`shortcut_manager` 在 core 却依赖 tkinter（[模块映射 §3](./06-module-map.md#3-分层与分层违规)）
3. **功能重复**——`utils.py` 与 `shortcut_manager.py` 四个快捷键函数完全重复（[模块映射 §6](./06-module-map.md#6-功能重复跨文件)）

## 与现有项目文档的关系

| 现有文档 | 状态 | 说明 |
|----------|------|------|
| [项目 README.md](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/README.md) | ⚠️ 部分过时 | "项目结构"小节写 `logging.py`（实际为 `log.py`）；启动命令写 `python3 -m boop`（实际为 `python3 -m app`）。本文档已修正，未改动原 README（遵守"不删除内容"原则）。 |
| [USER_GUIDE.md](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/USER_GUIDE.md) | ✅ 仍有效 | 用户使用指南，与架构文档互补 |
| [SIMPLIFIED_DESIGN.md](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/SIMPLIFIED_DESIGN.md) | ⚠️ 可能过时 | 早期技术设计；若与新文档冲突，以本目录文档为准，原文件标记为 `[OUTDATED]` 由后续维护决定 |

## 维护指引

- 新增 ADR：复制 [skill 模板](file:///Users/huji/work/MyProject/code_mine/gitee/boop/.trae/skills/python-arch-doc/references/adr-template.md)，编号取下一个未用数字，更新 [decisions/README.md](./decisions/README.md) 索引
- 重新生成全套文档：在 IDE 中触发 `python-arch-doc` skill
- 不删除既有内容：被取代的章节用 `> [OUTDATED — superseded by <link> on YYYY-MM-DD]` 标注

## 关联资源

- [python-arch-doc skill 定义](file:///Users/huji/work/MyProject/code_mine/gitee/boop/.trae/skills/python-arch-doc/SKILL.md)
- [C4 模型参考](file:///Users/huji/work/MyProject/code_mine/gitee/boop/.trae/skills/python-arch-doc/references/c4-model.md)
- [Python 模式检测清单](file:///Users/huji/work/MyProject/code_mine/gitee/boop/.trae/skills/python-arch-doc/references/python-patterns.md)
