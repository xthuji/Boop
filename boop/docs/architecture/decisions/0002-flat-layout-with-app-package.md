# 0002. 采用 flat 布局与 `app` 包名

- **Status:** Accepted
- **Date:** 2026-08-01
- **Deciders:** Boop Python Team

## Context

项目需选择 Python 包结构。主流有两种：`src` layout（`src/<pkg>/`）与 flat layout（`<pkg>/` 直接位于项目根）。包名也需确定——项目目录叫 `boop`，但若包名也叫 `boop`，会与项目根目录名混淆，且 `boop` 在 PyPI 已被占用。

## Decision Drivers

- 项目以 PyInstaller 打包为主，非 PyPI 发布的库
- 简单的导入路径（`from app.core import ...`）
- 避免与项目目录名 `boop` 冲突

## Options Considered

### Option A: `src/boop/` (src layout + boop 包名)
- Pros：符合 PEP 推荐的 src layout；包名与产品名一致
- Cons：`boop` 在 PyPI 已被占用；`src` 增加一层目录；需配置 `pyproject.toml`

### Option B: `app/` flat layout（采用）
- Pros：导入路径短（`from app.ui.main import MainWindow`）；无 `src` 冗余；与项目目录名 `boop` 区分
- Cons：⚠️ flat layout 有从 CWD 误导入风险；`app` 包名过于通用，未来发布到 PyPI 会冲突

### Option C: `src/boop_python/` (src layout + 带后缀包名)
- Pros：最规范；PyPI 友好
- Cons：包名冗长；小项目过度工程化

## Decision

选择 **Option B**：flat layout + `app` 包名。理由：本项目定位为桌面应用而非可分发库，PyInstaller 直接打 `app/__main__.py`，无需可安装包语义。

## Consequences

- **Positive**：导入路径简洁；PyInstaller hidden-imports 配置直观（`--hidden-import app.ui.main`，见 [build.sh#L145-L151](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L145-L151)）。
- **Negative**：🔴 [README.md#L21](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/README.md#L21) 写 `python3 -m boop`，与实际包名 `app` 不一致，新人会困惑。
- **Trade-off accepted**：放弃了 PyPI 可发布性，换取开发简洁。

## Compliance

- 所有内部导入以 `app.` 开头（见 [module-map §2](../06-module-map.md#2-内部依赖图)）
- `build.sh` 的 `--hidden-import` 列表使用 `app.*`

## Change Log

- 2026-08-01: Status Proposed → Accepted
