# Python 模式检测清单

在为 Python 项目做工程特性分析时作为检查表使用。每张表给出检测标记与需要记录的内容。每项输出格式：

```
### N. <分类>

**现状：** <一句话陈述>
**证据：** <file:line 或标记>
**评估：** ✅ 对齐 / ⚠️ 偏离 / 🔴 风险 — <一句话理由>
**建议（仅当偏离/风险）：** <一句话行动>
```

仅评估行必填；证据与建议在适用时给出。

## 1. 项目布局

| 布局 | 标记 | 取舍 |
|------|------|------|
| **src 布局** | `src/<pkg>/__init__.py` | ✅ 推荐。强制安装式导入；避免从 CWD 误导入。 |
| **flat 布局** | 仓库根下 `<pkg>/__init__.py` | 旧库与简单库常见；有遮蔽 stdlib 或 site-packages 的风险。 |
| **monorepo** | 多个 `pyproject.toml` 或 workspace 文件 | 记录 workspace 工具与成员清单。 |
| **Django 项目** | `manage.py` + `<project>/settings.py` + `apps/` | 文档化 app 列表与 `INSTALLED_APPS`。 |
| **Notebook 项目** | `*.ipynb` + `nbstripout` 配置 | 标注缺乏包结构为风险。 |

## 2. 打包与构建后端

检测 `pyproject.toml` 中的 `[build-system]`：

| 后端 | `build-system.requires` 值 | 说明 |
|------|----------------------------|------|
| setuptools | `setuptools >= 61` | 旧默认；兼容广。 |
| hatchling | `hatchling` | 现代；PEP 621 原生。 |
| flit-core | `flit-core >= 3` | 轻量；适合纯 Python 库。 |
| poetry-core | `poetry-core >= 1` | 绑定 poetry 工作流。 |
| pdm-backend | `pdm-backend` | PEP 621 + PEP 582 友好。 |
| setuptools-rust | `setuptools-rust` | Rust/Python 混合扩展。 |
| maturin | `maturin` | Rust 扩展；ABI。 |
| scikit-build-core | `scikit-build-core` | 基于 CMake 的 C/C++/Fortran 扩展。 |

## 3. 依赖管理

| 工具 | 锁文件 | 说明 |
|------|--------|------|
| pip + pip-tools | 由 `requirements.in` 生成的 `requirements.txt` | 通过 `--generate-hashes` 固定哈希。 |
| uv | `uv.lock` | Rust 实现，极快；锁确定。 |
| poetry | `poetry.lock` | 锁含哈希。 |
| pdm | `pdm.lock` | PEP 582 `__pypackages__` 选项。 |
| pipenv | `Pipfile.lock` | 较老；无 TOML。 |
| conda / mamba | `environment.yml` / `conda-lock.yml` | 记录非 Python 依赖。 |

## 4. 环境管理

- `python -m venv`（stdlib）
- `uv venv`（Rust，极快）
- `virtualenv`（更快，自带 pip）
- `conda` / `mamba` / `micromamba`
- `pyenv`（Python 解释器版本）
- `asdf` / `mise`（多语言版本管理器）

## 5. 类型系统

| 信号 | 含义 |
|------|------|
| `from typing import ...` / PEP 585 `list[str]` / PEP 604 `X \| Y` | 已用类型注解。 |
| `[tool.mypy]` 严格标志（`strict = true`、`disallow_untyped_defs`） | 强制严格类型检查。 |
| `pyrightconfig.json` / `basedpyright` | 基于 Pyright 的检查。 |
| `from pydantic import BaseModel` | 运行时校验；区分 v1（`Config` 类）与 v2（`model_config`）。 |
| `@dataclass`、`from attrs import define` | 轻量值类型。 |

## 6. 异步模型

| 模式 | 标记 |
|------|------|
| asyncio | `import asyncio`、`async def`、`await` |
| trio | `import trio`、`async with trio.open_nursery()` |
| anyio | `import anyio`（后端无关） |
| 异步 Web | FastAPI、Starlette、Litestar、aiohttp、Sanic、Tornado |
| ASGI 服务器 | `uvicorn`、`hypercorn`、`daphne`、`granian`、`uvloop` |
| 任务队列 | Celery、RQ、Dramatiq、ARQ、TaskIQ、Huey |

**需标注的隐患：**
- 异步函数内做阻塞 I/O 而未用 `run_in_executor` / `anyio.to_thread`。
- 在已运行的事件循环里再调 `asyncio.run`。
- Python 3.10 之后还在用 `asyncio.get_event_loop()`（已弃用）。

## 7. Web 框架

| 框架 | 标记 |
|------|------|
| Django | `django`、`manage.py`、`settings.py` |
| Flask | `flask`、`Flask(__name__)` |
| FastAPI | `fastapi`、`FastAPI()`、`@app.get` |
| Starlette | `starlette`、`Starlette()` |
| Litestar | `litestar`、`Litestar()` |
| aiohttp | `aiohttp.web` |

服务器（WSGI/ASGI）：`gunicorn`、`uwsgi`、`uvicorn`、`hypercorn`、`daphne`、`granian`。

## 8. 数据层

- ORM：Django ORM、SQLAlchemy 2.x、SQLModel、Tortoise、Peewee
- 迁移：Alembic（`alembic.ini`）、Django migrations、yoyo-migrations
- NoSQL：`motor`（Mongo）、`redis`、`aioredis`、`cassandra-driver`
- 缓存：`functools.lru_cache`、`cachetools`、`diskcache`、Redis、Memcached

## 9. CLI 框架

| 工具 | 标记 |
|------|------|
| argparse | `argparse.ArgumentParser`（stdlib） |
| click | `click.group()`、`@click.option` |
| typer | `typer.Typer()` |
| fire | `fire.Fire()` |

## 10. 配置与密钥

| 工具 | 标记 |
|------|------|
| pydantic-settings | `BaseSettings`、`SettingsConfigDict` |
| dynaconf | `dynaconf.Dynaconf` |
| python-dotenv | `load_dotenv()` |
| configparser / tomllib | stdlib 配置读取器 |
| 直接 `os.environ` | — |

**需标注**：`.env` 中提交了密钥（且无 `.gitignore` 保护）、`settings.py` 字面量里出现密钥。

## 11. 测试

| 运行器 | 标记 |
|--------|------|
| pytest | `conftest.py`、`test_*.py`、`pytest.ini` |
| unittest | `unittest.TestCase` |
| tox | `tox.ini` |
| nox | `noxfile.py` |

pytest 插件：`pytest-asyncio`、`pytest-cov`、`pytest-xdist`、`pytest-mock`、`hypothesis`。

## 12. 代码质量

| 工具 | 标记 |
|------|------|
| ruff | `[tool.ruff]`（lint + format，替代 flake8 + isort + black） |
| black | `[tool.black]` |
| isort | `[tool.isort]` |
| flake8 | `.flake8` |
| pre-commit | `.pre-commit-config.yaml` |

## 13. 可观测性

| 关注点 | 库 |
|--------|----|
| 日志 | `logging`（stdlib）、`structlog`、`loguru` |
| 指标 | `prometheus-client` |
| 链路追踪 | `opentelemetry-sdk`、`ddtrace` |
| 错误追踪 | `sentry-sdk` |
| 性能分析 | `py-spy`、`scalene`、`cProfile` |

## 14. 部署

| 目标 | 标记 |
|------|------|
| Docker / OCI | `Dockerfile`、`docker-compose.yml` |
| WSGI | gunicorn、waitress |
| ASGI | uvicorn、hypercorn、daphne |
| Serverless | `def lambda_handler` |
| 原生安装包 | PyInstaller（`.spec`）、cx_Freeze、Nuitka、Briefcase |
| systemd | `.service` 单元文件 |

## 15. 安全

| 关注点 | 工具 | 标记 |
|--------|------|------|
| 依赖漏洞扫描 | pip-audit、safety、osv-scanner | CI 任务或 pre-commit |
| 密钥扫描 | gitleaks、trufflehog、detect-secrets | pre-commit + CI |
| SAST | bandit、ruff `S` 规则、semgrep | 配置 + baseline |
