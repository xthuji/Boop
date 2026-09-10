# ADR 模板与规范

**架构决策记录**（ADR）捕获单个决策及其上下文、备选方案与后果。ADR 是版本化的，一旦 Accepted 即不可变（用新 ADR 取而代之），以纯 Markdown 存储。

参考：Michael Nygard 的原始 ADR 模式（<https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>）。

## 文件命名

```
docs/architecture/decisions/NNNN-kebab-case-title.md
```

- `NNNN`：从 `0001` 起的零填充序号。
- 标题：简短、决策导向（如 `use-uv-for-dependency-management`、`adopt-fastapi-over-flask`）。
- 序号**永不复用**。取代性决策取下一个空号并回链被取代的 ADR。

## 状态语义

| 状态 | 含义 |
|------|------|
| `Proposed` | 已起草，待评审。 |
| `Accepted` | 已批准，现约束力。 |
| `Deprecated` | 不再相关；不要遵循。 |
| `Superseded` | 被后续 ADR 取代（需链接）。 |
| `Rejected` | 考虑后否决（留档）。 |

状态变更采用追加方式：不重写历史。在文件底部加 `## Change Log` 小节，记录日期 + 作者 + 状态迁移。

## 模板

```markdown
# NNNN. <决策标题>

- **Status:** Proposed | Accepted | Deprecated | Superseded | Rejected
- **Date:** YYYY-MM-DD
- **Deciders:** <姓名或角色>
- **Supersedes:** <ADR-XXXX，若有>
- **Superseded by:** <ADR-YYYY，若有>

## Context（上下文）

我们面临什么问题？有哪些力量（技术、业务、进度、团队技能、合规）
在起作用？陈述问题，不要陈述方案。

纳入事实：库版本、规模估算、合规约束、上下游耦合。尽量引用证据
（文件、链接、指标）。

## Decision Drivers（决策驱动因素）

- <驱动 1，如"P99 延迟 < 200 ms">
- <驱动 2，如"团队已熟悉框架 X">
- <驱动 3，如"避免厂商锁定">

## Options Considered（考虑过的方案）

### Option A: <名称>

- **Pros:** ...
- **Cons:** ...
- **Cost / effort:** ...
- **Risk:** ...

### Option B: <名称>

（同结构。）

## Decision（决策）

选择 **<Option X>**，因为 <绑定驱动因素的简短理由>。

## Consequences（后果）

- **Positive:** ...
- **Negative:** ...
- **Neutral / trade-off accepted:** ...
- **Action items:**（谁在何时前做什么 — 可选）
- **Retro trigger:** 在何种条件下应重新审视本 ADR？

## Compliance（合规）

如何验证决策被遵循？

- Lint 规则 / pre-commit 钩子：...
- 评审 checklist 项：...
- 架构测试（如 import-linter 契约）：...

## Change Log

- YYYY-MM-DD: Status Proposed → Accepted（决策者姓名）。
```

## ADR 索引格式

维护 `docs/architecture/decisions/README.md` 作为表格：

```markdown
| # | 标题 | 状态 | 日期 |
|---|------|------|------|
| 0001 | 采用 FastAPI | Accepted | 2026-08-01 |
| 0002 | 采用 uv | Superseded by 0007 | 2026-08-01 |
| 0007 | 迁移到 uv workspace | Accepted | 2026-09-10 |
```

新增 ADR 或状态变更时同步更新该索引。
