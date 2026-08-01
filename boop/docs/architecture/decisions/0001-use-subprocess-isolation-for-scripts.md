# 0001. 使用子进程隔离执行用户脚本

- **Status:** Accepted
- **Date:** 2026-08-01
- **Deciders:** Boop Python Team

## Context

Boop 的核心能力是执行用户编写的 Python 脚本对文本进行处理。用户脚本来源不可控，可能包含未处理的异常、死循环、`exit()`、甚至恶意操作。原版 Boop（macOS/Swift）使用 JavaScriptCore 进程内沙箱执行 JS 脚本；本项目的 Python 版本需要选择等价的隔离机制。

## Decision Drivers

- 脚本崩溃绝不能影响主 GUI 进程
- 必须支持超时终止长脚本
- 需要捕获脚本 stdout/stderr 与异常栈
- 实现成本要低（小项目）

## Options Considered

### Option A: 进程内 `exec()` 直接执行
- Pros：零 IPC 开销；可共享内存对象
- Cons：🔴 脚本崩溃会拖垮主进程；无法可靠超时；`exec` 污染主进程命名空间

### Option B: `subprocess.Popen` 派生子进程（采用）
- Pros：进程级隔离；`communicate(timeout=...)` 原生超时；stdout/stderr 天然分离
- Cons：每次执行启动 Python 解释器开销（~50-200ms）；需序列化输入输出

### Option C: 长驻 worker 子进程 + RPC
- Pros：避免每次启动解释器；可复用导入的脚本模块
- Cons：实现复杂；需自定义协议；worker 崩溃后需重启逻辑

## Decision

选择 **Option B**：通过 `subprocess.Popen` 派生子进程，入口为 `app/core/script_wrapper.py`。主进程通过 stdin 传入脚本路径与输入文本，子进程 `exec` 脚本后将结果以 JSON 写到 stdout。

## Consequences

- **Positive**：脚本崩溃被隔离在子进程；超时由 `subprocess.communicate(timeout=...)` 保证；实现仅 ~70 行（[script_wrapper.py](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/script_wrapper.py)）。
- **Negative**：每次执行有 ~50-200ms 解释器启动开销；UI 在执行期间阻塞（同步 `communicate`）。
- **Trade-off accepted**：桌面工具场景下，单次脚本执行延迟可接受；隔离性远重要于启动开销。
- **Action items**：未来可引入"脚本结果缓存"或"长驻 worker"作为优化（见变更触发条件）。

## Compliance

- [app/core/utils.py#run_script_in_subprocess](file:///Users/huji/work/MyProject/code_mine/gitee/boop/boop/app/core/utils.py#L11-L94) 是唯一脚本执行入口
- `script_timeout` 配置项控制超时（默认 10s）

## Change Log

- 2026-08-01: Status Proposed → Accepted
