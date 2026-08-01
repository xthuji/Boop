# 0003. 使用 PyInstaller 进行跨平台分发

- **Status:** Accepted
- **Date:** 2026-08-01
- **Deciders:** Boop Python Team

## Context

需要将 Tkinter 桌面应用分发到 macOS / Linux / Windows 三个平台，目标用户无需预装 Python 即可运行。需选择打包方案。

## Decision Drivers

- 跨平台一致性（macOS/Linux/Windows）
- 单一工具链降低维护成本
- 产出自包含的可执行目录（无需用户装 Python）
- 体积可控

## Options Considered

### Option A: PyInstaller（采用）
- Pros：成熟；支持 `--onedir`/`--onefile`/`--windowed`；跨平台；可裁剪标准库模块；社区文档丰富
- Cons：体积偏大（含 Python 运行时）；启动稍慢；杀毒软件偶发误报

### Option B: Nuitka
- Pros：编译为 C，体积小，启动快
- Cons：编译慢；Tkinter 兼容性偶有问题；调试困难

### Option C: Briefcase (BeeWare)
- Pros：原生打包（macOS .app、MSI、deb）；PyPI 友好
- Cons：生态较新；Tkinter 支持不如 PyInstaller 成熟

### Option D: cx_Freeze
- Pros：跨平台
- Cons：社区较小；配置不如 PyInstaller 灵活

## Decision

选择 **Option A**：PyInstaller `--onedir --windowed`。配合 `--exclude-module` 精细裁剪不需要的标准库模块（[build.sh#L43-L77](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L43-L77)），用 UPX 压缩减小体积。

## Consequences

- **Positive**：单一脚本 `build.sh` 覆盖三平台；`--exclude-module` 列表使体积从全量 ~80MB 降至 ~30-40MB；`_MEIPASS` 机制使资源路径解析统一（[path.py#L19-L25](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/path.py#L19-L25)）。
- **Negative**：每次依赖升级需重新打包；杀毒软件偶发误报需代码签名（当前未实现）。
- **Risk**：🔴 [build.sh#L228](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L228) `clean_py_files` 删除 dist 下 `.py` 仅保留 `.pyc`，但保留 `scripts/` 与 `script_wrapper.py` 的 `.py`——若用户脚本 `from lib.base import State` 依赖 `.py` 存在，打包后可能失效。需验证 `lib/base.py` 是否也被保留。

## Compliance

- `build.sh` 是唯一构建入口
- `version.txt` 同时作为 PyInstaller 版本资源
- `data/`、`scripts/`、`script_wrapper.py` 通过 `--add-data` 打入包（[build.sh#L29-L33](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/build.sh#L29-L33)）

## Change Log

- 2026-08-01: Status Proposed → Accepted
