# 架构文档输出模板

下列模板供撰写架构文档时参考，所有 `<...>` 占位符需替换为项目实际内容。

## 业务概览（`01-overview.md`）

```markdown
# <项目名> — 架构与业务概览

## 1. 产品定位

<一段大白话描述系统做什么、服务谁。>

## 2. 业务目标与成功指标

| 目标 | 指标 | 目标值 | 数据来源 |
|------|------|--------|----------|
| <如：降低文本处理摩擦> | <首次处理耗时> | <30 s> | <分析数据源> |

## 3. 干系人与用户画像

| 画像 | 角色 | 目标 | 痛点 |
|------|------|------|------|
| <姓名> | <角色> | <目标> | <痛点> |

## 4. 业务能力

- **CAP-1** <能力名> — <一句话描述>
- **CAP-2** <能力名> — <一句话描述>

## 5. 领域术语表

| 术语 | 定义 | 同义词 |
|------|------|--------|
| <术语> | <定义> | <别名> |

## 6. 范围边界

**范围内：**
- <项>

**范围外：**
- <项>

## 7. 关联文档

- [C4 系统上下文](./02-c4-context.md)
- [容器图](./03-c4-containers.md)
- [组件图](./04-c4-components.md)
- [模块映射](./06-module-map.md)
- [Python 特性分析](./07-python-specifics.md)
- [数据流](./08-data-flow.md)
- [ADR](./decisions/README.md)
- [入职指南](./10-onboarding.md)
```

## 模块映射（`06-module-map.md`）

```markdown
# <项目名> — 模块与包映射

## 1. 顶层布局

<repo root>/
├── pyproject.toml          # 清单
├── src/<package>/          # 或根下 <package>/（flat 布局）
│   ├── __init__.py
│   └── ...
└── tests/

**布局类型：** `src` | `flat` | `monorepo`
**根包：** `<package>`
**所需 Python：** `<3.x>`（证据：`pyproject.toml` 的 `requires-python`）

## 2. 包目录

| 包 / 模块 | 用途 | 公共 API（`__all__`） | 入向依赖 | 被谁依赖 |
|-----------|------|------------------------|----------|----------|
| `<package>.<sub>` | <一句话> | <导出> | <导入> | <谁导入它> |

## 3. 分层

目标分层（上层依赖下层，禁止反向）：

1. **入口 / 接口** — `cli/`、`ui/`、`routers/`、`__main__.py`
2. **应用 / 用例** — `services/`、`use_cases/`
3. **领域** — `models/`、`domain/`
4. **基础设施** — `repositories/`、`adapters/`、`db/`

### 分层违规

| From → To | 严重度 | 建议修复 |
|-----------|--------|----------|
| `<pkg>.models → <pkg>.routers` | 🔴 严重 | <修复> |

（无违规则留空。）

## 4. 循环导入

| 循环 | 触发方式 | 建议修复 |
|------|----------|----------|
| `<A> → <B> → <A>` | <如何暴露> | <抽公共模块 / 懒加载> |

（无则留空。）

## 5. 入口点

| 名称 | 类型 | 位置 | 框架 |
|------|------|------|------|
| `<entry>` | CLI / GUI / WSGI / ASGI / worker | `<file>:<line>` | click / typer / FastAPI / ... |
```

## 数据流（`08-data-flow.md`）

```markdown
# <项目名> — 数据流

> 选 2–5 个代表性旅程。

## Journey 1: <如：用户提交文本处理>

### 参与者
- User
- GUI / CLI
- 脚本引擎
- 文件系统

### 序列图

sequenceDiagram
    participant U as User
    participant UI as GUI (tkinter)
    participant SE as Script engine
    participant FS as Scripts dir
    U->>UI: 选中文本，按快捷键
    UI->>SE: execute(script_name, text)
    SE->>FS: 加载并 exec 脚本
    FS-->>SE: 处理结果
    SE-->>UI: 返回处理后文本
    UI-->>U: 替换选区

### 标注
- 同步/异步边界：<全同步 | 第 N 步起异步>
- 事务边界：<无 | 第 X 步包在事务里>
- 重试/回退：<无 | 最多重试 3 次，带退避>
- 缓存：<无 | 按输入缓存结果>

---

## 横切观察

- **关键路径：** <哪个旅程在用户感知性能的关键路径上>
- **失败模式：** <第 X 步失败会怎样>
- **可观测性缺口：** <哪些旅程缺指标/追踪>
```

## 入职指南（`10-onboarding.md`）

```markdown
# <项目名> — 新人入职指南

## 1. 前置条件

| 要求 | 版本 | 检查命令 |
|------|------|----------|
| Python | `<3.x>` | `python --version` |
| OS | macOS / Linux / Windows | — |
| 系统依赖 | <如 Tk "8.6+"、libpq> | `<command>` |
| 工具链 | <uv / poetry / pip> | `<tool> --version` |

## 2. 克隆与搭建

git clone <repo-url>
cd <repo>

### 创建环境并安装依赖

**uv（现代首选）：**
uv sync
source .venv/bin/activate

**poetry：**
poetry install
poetry shell

**pip + venv（回退）：**
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## 3. 本地运行

python -m <package>                 # 通过 __main__.py 的入口

## 4. 跑测试

pytest                              # 全部
pytest tests/<dir>                  # 子集
pytest -k "<expression>"            # 按名过滤
pytest --cov=<package> --cov-report=html

## 5. 代码质量

ruff check .                       # lint
ruff format .                      # format
mypy app/                          # 类型检查
pre-commit run --all-files         # 全部钩子

## 6. 项目结构

详见 [模块映射](./06-module-map.md)。

## 7. 常见开发任务

### 加运行时依赖

pip install <pkg>                  # 或对应工具

### 加新端点 / 命令 / 文本处理

1. 在对应层加文件（见模块映射）。
2. 若是公共符号，加入 `__all__`。
3. 在 `tests/` 下镜像源路径加测试。
4. 跑 lint + 类型检查 + 测试。

### 加新 ADR

复制 [ADR 模板](../methodology/adr-template.md)，编号取下一个未用数字，更新 `decisions/README.md` 索引。

## 8. 排错

| 症状 | 可能原因 | 修复 |
|------|----------|------|
| `ModuleNotFoundError: No module named '<pkg>'` | 忘了 `pip install -e .` | 激活 venv 并重试 |

## 9. 下一步

- 阅读 [架构概览](./01-overview.md)
- 浏览 [C4 系统上下文](./02-c4-context.md)
- 看最近 [ADR](./decisions/README.md) 了解当前方向
```
