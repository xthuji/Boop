# Boop 用户使用指南

## 简介

Boop 是一个文本处理工具，通过运行 Python 脚本来快速处理和转换文本。

**主要功能：**
- 🐍 Python 脚本支持
- ⌨️ 自定义快捷键
- 🔄 撤销/重做
- 📁 多脚本目录管理
- 🎯 跨平台（macOS/Windows/Linux）

---

## 快速开始

### 安装

**源码运行：**
```bash
pip install -r requirements.txt
python3 -m boop
```

**打包应用：** 下载对应平台的压缩包，解压后运行即可。

### 基本使用

1. **启动应用**：运行 `python3 -m boop` 或打开打包应用
2. **输入文本**：在编辑器中输入或粘贴文本
3. **运行脚本**：按 `Cmd+B`/`Ctrl+B` 打开脚本选择器，选择脚本后按 `Enter`
4. **查看结果**：处理结果立即显示

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Cmd+B` / `Ctrl+B` | 打开脚本选择器 |
| `Cmd+,` / `Ctrl+,` | 打开首选项 |
| `Cmd+Q` / `Ctrl+Q` | 退出应用 |
| `Cmd+Z` / `Ctrl+Z` | 撤销 |
| `Cmd+Shift+Z` / `Ctrl+Shift+Z` | 重做 |
| `Cmd+D` / `Ctrl+D` | 多光标选择 |
| `Cmd+A` / `Ctrl+A` | 全选 |

---

## 编写脚本

### 脚本模板

```python
'''
{
    "name": "脚本名称",
    "description": "功能描述",
    "tags": ["标签 1", "标签 2"],
    "icon": "★",
    "help": "详细使用说明",
    "dependencies": ["requests"]
}
'''

def main(state):
    text = state.text          # 获取文本
    state.text = text.upper()  # 设置结果
```

### 元数据字段

| 字段 | 说明 |
|------|------|
| `name` | 脚本名称 |
| `description` | 功能描述 |
| `tags` | 搜索标签 |
| `icon` | 图标（emoji 或字符） |
| `help` | 详细使用说明 |
| `dependencies` | 依赖包列表 |

### state API

| 方法 | 说明 |
|------|------|
| `state.text` | 获取/设置当前文本 |
| `state.full_text` | 获取/设置全部内容 |
| `state.insert(text)` | 在光标处插入 |
| `state.post_info(msg)` | 显示提示 |

### 安装依赖

1. 在脚本元数据中添加 `dependencies`
2. 打开首选项 → Scripts
3. 点击 **Install All Dependencies**

---

## 首选项

按 `Cmd+,` / `Ctrl+,` 打开首选项：

- **General**：窗口大小、字体设置
- **Scripts**：脚本目录、Python 解释器、依赖管理
- **Logs**：日志查看和清除

---

## 常见问题

**Q: 应用启动后闪退？**  
A: 安装 Tkinter：macOS 运行 `brew install python-tk`，Ubuntu 运行 `sudo apt-get install python3-tk`

**Q: 脚本无法运行？**  
A: 检查首选项 → Scripts 中的 Python 解释器路径是否正确

**Q: 如何添加脚本目录？**  
A: 首选项 → Scripts → Add，选择目录后 Save

**Q: 日志文件位置？**  
A: macOS: `~/Library/Logs/boop/` | Windows: `%APPDATA%/boop/logs/` | Linux: `~/.config/boop/logs/`

---

## 获取帮助

- 在 Help 菜单中选择 **User Guide** 查看本文档
- 查看项目中的 `README.md` 了解更多详情
