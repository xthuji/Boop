# Boop

基于 Python 的文本处理工具，灵感来自 macOS 原生应用 Boop。

**特点：**
- 🐍 Python 脚本支持
- ⌨️ 自定义快捷键
- 🔄 撤销/重做
- 📁 多脚本目录管理
- 🎯 跨平台（macOS/Windows/Linux）

---

## 快速开始

### 安装

```bash
pip install -r requirements.txt
python3 -m app
```

### 环境要求

- Python 3.9+
- Tkinter（通常随 Python 一起安装）

### 打包应用

```bash
./build.sh
```

输出：`dist/Boop-*.dmg` (macOS) / `*.tar.gz` (Linux) / `*.zip` (Windows)

---

## 使用

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Cmd+B` / `Ctrl+B` | 打开脚本选择器 |
| `Cmd+,` / `Ctrl+,` | 打开首选项 |
| `Cmd+Q` / `Ctrl+Q` | 退出 |
| `Cmd+Z` / `Ctrl+Z` | 撤销 |
| `Cmd+Shift+Z` / `Ctrl+Shift+Z` | 重做 |

### 基本流程

1. 输入或粘贴文本
2. 按 `Cmd+B` / `Ctrl+B` 打开脚本选择器
3. 搜索并选择脚本，按 `Enter` 运行
4. 查看处理结果

---

## 编写脚本

### 脚本模板

```python
'''
{
    "name": "脚本名称",
    "description": "功能描述",
    "tags": ["标签"],
    "icon": "★",
    "help": "使用说明",
    "dependencies": ["requests"]
}
'''

def main(state):
    text = state.text
    state.text = text.upper()  # 示例：转大写
```

### 元数据字段

| 字段 | 说明 |
|------|------|
| `name` | 脚本名称 |
| `description` | 功能描述 |
| `tags` | 搜索标签 |
| `icon` | 图标 |
| `help` | 帮助说明 |
| `dependencies` | 依赖包列表 |

### state API

| 方法 | 说明 |
|------|------|
| `state.text` | 获取/设置文本 |
| `state.full_text` | 获取/设置全部内容 |
| `state.insert(text)` | 在光标处插入 |
| `state.post_info(msg)` | 显示提示 |

### 安装依赖

1. 在脚本元数据中添加 `dependencies`
2. 首选项 → Scripts → **Install All Dependencies**

---

## 配置

配置文件：`config.json`

### 首选项

按 `Cmd+,` / `Ctrl+,` 打开：

- **General**：窗口大小、字体
- **Scripts**：脚本目录、Python 解释器、依赖
- **Logs**：日志查看和清除

---

## 项目结构

```
boop/
├── .github/workflows/release.yml   # CI 发布流程（PyInstaller 打包 macOS DMG）
├── app/                            # 主包（运行入口）
│   ├── __main__.py                 # `python -m app` 入口
│   ├── config/                     # BoopConfig + JSON 持久化
│   ├── core/                       # 脚本管理 / 缓存 / 日志 / 热键 / 事件
│   └── ui/                         # MainWindow / Editor / ScriptPicker / Preferences
├── scripts/                        # 60+ 内置脚本
├── data/config.json                # 默认配置样本
├── icons/                          # 图标资源
├── docs/                           # 用户指南 + 架构文档 + 方法论
├── tests/                          # 脚本测试 + 编辑器测试
├── build.sh                        # 跨平台打包（PyInstaller）
├── release.sh                      # Git tag 发布辅助脚本
├── test_app.sh                     # 应用启动测试
├── update_boop_scripts.sh          # 脚本更新工具
├── version.txt                     # 版本号（release.sh 读取）
└── requirements.txt                # 依赖清单
```

---

## 文档

完整项目文档见 [docs/](./docs/)：

- [用户指南](./docs/user-guide.md) — 使用说明与脚本编写
- [架构与业务概览](./docs/architecture/01-overview.md) — 产品定位、能力清单、术语表
- [C4 架构](./docs/architecture/README.md) — 系统上下文 / 容器 / 组件
- [模块映射](./docs/architecture/06-module-map.md) — 内部依赖、分层、循环导入
- [Python 工程特性分析](./docs/architecture/07-python-specifics.md) — 14 项工程维度评估
- [ADR 索引](./docs/architecture/decisions/README.md) — 架构决策记录
- [新人入职指南](./docs/architecture/10-onboarding.md) — 环境搭建、运行、测试、打包
- [架构文档方法论](./docs/methodology/README.md) — C4 参考 / ADR 模板 / Python 模式检测清单

---

## 与原 Boop 的区别

| 特性 | 原 Boop | Boop Python |
|------|---------|-------------|
| 脚本语言 | JavaScript | Python |
| 执行方式 | JavaScriptCore | 子进程隔离 |
| UI | 原生 macOS (Swift) | Tkinter (跨平台) |
| 配置 | macOS Preferences | JSON 文件 |

---

## License

灵感来自原 Boop 项目，参见原 [LICENSE](https://github.com/IvanMathy/Boop/blob/main/LICENSE)。
