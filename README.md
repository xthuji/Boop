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
python3 -m boop
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
├── __main__.py          # 入口
├── config/
│   └── settings.py      # 配置管理
├── core/
│   ├── script.py        # 脚本管理
│   ├── script_metadata.py
│   ├── cache.py         # 元数据缓存
│   ├── event.py         # 事件系统
│   ├── logging.py       # 日志
│   └── utils.py         # 工具
├── ui/
│   ├── main.py          # 主窗口
│   ├── editor.py        # 编辑器
│   ├── script_picker.py # 脚本选择器
│   └── preferences.py   # 首选项
└── scripts/             # 内置脚本
```

---

## 文档

- **USER_GUIDE.md** - 用户使用指南
- **SIMPLIFIED_DESIGN.md** - 技术设计文档

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
