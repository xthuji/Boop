# Boop 用户使用指南

## 简介

Boop 是一个跨平台（macOS / Windows / Linux）的文本处理桌面工具。用户在编辑器中输入或粘贴文本，通过快捷键唤起脚本选择器，执行 Python 脚本对选中文本进行格式化、转换、统计、编解码等处理。

## 快速开始

### 源码运行

```bash
cd 
pip install -r requirements.txt
python3 -m app
```

### 打包应用

从 Release 页面下载对应平台的压缩包（macOS DMG / Linux tar.gz / Windows zip），解压后运行即可。

### 首次启动

首次启动后，需要在 **偏好 → Scripts → Python Path** 中指定系统 Python 解释器路径（用于派生子进程执行用户脚本）。

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

## 基本使用流程

1. **启动应用**（源码：`python3 -m app`；打包：双击 .app）
2. **输入文本**：在编辑器中输入或粘贴文本
3. **运行脚本**：按 `Cmd+B`/`Ctrl+B` 打开脚本选择器，搜索并选择脚本后按 `Enter`
4. **查看结果**：处理结果立即显示在编辑器中

## 首选项

按 `Cmd+,` / `Ctrl+,` 打开：

- **General**：窗口大小、字体设置
- **Scripts**：脚本目录、Python 解释器路径、依赖管理
- **Logs**：日志查看和清除

## 编写自定义脚本

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
    text = state.text          # 获取当前选中文本
    state.text = text.upper()  # 设置处理结果
```

### 元数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 脚本名称（必填） |
| `description` | string | 功能描述（必填） |
| `tags` | list | 搜索标签 |
| `icon` | string | 图标（emoji 或字符） |
| `help` | string | 详细使用说明 |
| `dependencies` | list | 需要 pip 安装的第三方包 |

### State API

脚本通过 `state` 对象与主应用交互：

| 方法/属性 | 说明 |
|-----------|------|
| `state.text` | 获取/设置当前选中文本 |
| `state.full_text` | 获取/设置编辑器全部内容 |
| `state.insert(text)` | 在光标处插入文本 |
| `state.post_info(msg)` | 向用户显示提示信息 |
| `state.post_error(msg)` | 向用户显示错误信息 |

### 安装脚本依赖

1. 在脚本元数据的 `dependencies` 字段声明所需包（如 `["json5", "yaml"]`）
2. 打开首选项 → **Scripts**
3. 点击 **Install All Dependencies**

## 常见问题

**Q: 应用启动后闪退？**  
A: 缺少 Tkinter。macOS 运行 `brew install python-tk`，Ubuntu 运行 `sudo apt-get install python3-tk`。

**Q: 脚本无法运行？**  
A: 检查首选项 → Scripts 中的 Python 解释器路径是否正确；或查看日志文件。

**Q: 如何添加自定义脚本目录？**  
A: 首选项 → Scripts → Add，选择目录后 Save。

**Q: 日志文件位置？**  
A: macOS: `~/Library/Logs/.log` | Windows: `%APPDATA%/boop/logs/` | Linux: `~/.config/boop/logs/boop.log`

**Q: Python 解释器路径默认值是什么？**  
A: 首次启动为空，需在首选项中手动指定；也会尝试常见路径（如 miniconda / conda / pyenv）作为回退。

## 更多资料

- 架构与开发文档：[architecture/README.md](./architecture/README.md)
- 新人入职指南：[architecture/10-onboarding.md](./architecture/10-onboarding.md)
