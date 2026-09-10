# ADR 索引

| # | 标题 | 状态 | 日期 |
|---|------|------|------|
| [0001](./0001-use-subprocess-isolation-for-scripts.md) | 使用子进程隔离执行用户脚本 | Accepted | 2026-08-01 |
| [0002](./0002-flat-layout-with-app-package.md) | 采用 flat 布局与 `app` 包名 | Accepted | 2026-08-01 |
| [0003](./0003-pyinstaller-for-cross-platform-distribution.md) | 使用 PyInstaller 进行跨平台分发 | Accepted | 2026-08-01 |
| [0004](./0004-tkinter-for-cross-platform-gui.md) | 采用 Tkinter 作为 GUI 框架 | Accepted | 2026-08-01 |

## 待补充的决策

以下决策尚未记录为 ADR，建议后续补齐：

- **0005**：自研测试运行器 vs pytest（当前用自研 `run_tests.py`，见 [架构文档 §11.9](../architecture.md#119-测试)）
- **0006**：同步模型 + threading for 全局热键
- **0007**：脚本元数据用 docstring 内 JSON 而非 sidecar 文件
- **0008**：是否引入 `pyproject.toml` 规范化打包（见 [架构文档 §11.1](../architecture.md#111-打包与构建后端)）

## ADR 模板

新增 ADR 时按以下模板撰写，编号取下一个未用数字，完成后更新上方索引。

```markdown
# NNNN. <决策标题>

- **Status:** Proposed | Accepted | Deprecated | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Deciders:** <姓名或角色>
- **Supersedes:** <ADR-XXXX，若有>
- **Superseded by:** <ADR-YYYY，若有>

## Context（上下文）

我们面临什么问题？有哪些力量（技术、业务、进度、团队技能、合规）在起作用？

## Decision Drivers（决策驱动因素）

- <驱动 1>
- <驱动 2>

## Options Considered（考虑过的方案）

### Option A: <名称>
- **Pros:** ...
- **Cons:** ...
- **Cost / effort:** ...
- **Risk:** ...

### Option B: <名称>
（同结构）

## Decision（决策）

选择 **<Option X>**，因为 <绑定驱动因素的简短理由>。

## Consequences（后果）

- **Positive:** ...
- **Negative:** ...
- **Neutral / trade-off accepted:** ...
- **Action items:**（可选）

## Change Log

- YYYY-MM-DD: Status Proposed → Accepted（决策者姓名）。
```
