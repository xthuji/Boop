# Boop 用户使用指南

## 简介

Boop 是一个文本处理工具，通过运行 Python 脚本来快速处理和转换文本。

**主要功能：**
- 🐍 Python 脚本支持
- ⌨️ 自定义快捷键
- 🔄 撤销/重做
- 📁 多脚本目录管理
- 🎯 跨平台（macOS/Windows/Linux）
- 📝 实时文本编辑
- 🖥️ 系统级全局热键

---

## 快速开始

### 安装

**源码运行：**
```bash
# 克隆仓库
git clone https://gitee.com/yourusername/boop.git
cd boop/boop-go

# 安装依赖
go mod tidy

# 运行应用
./test_app.sh
```

**打包应用：** 下载对应平台的压缩包，解压后运行即可。

### 基本使用

1. **启动应用**：运行 `./test_app.sh` 或打开打包应用
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
| `Cmd+Y` / `Ctrl+Y` | 重做（备选） |
| `Cmd+C` / `Ctrl+C` | 复制 |
| `Cmd+V` / `Ctrl+V` | 粘贴 |
| `Cmd+A` / `Ctrl+A` | 全选 |
| `Cmd+Home` / `Ctrl+Home` | 移动到文本开始 |
| `Cmd+End` / `Ctrl+End` | 移动到文本结束 |

---

## 脚本管理

### 脚本目录

Boop 默认使用 `scripts` 目录存放脚本。你可以在首选项中添加自定义脚本目录。

### 脚本格式

Boop 使用 Python 脚本进行文本处理，脚本需要包含元数据和 `main` 函数：

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

---

## 首选项

按 `Cmd+,` / `Ctrl+,` 打开首选项：

- **General**：窗口大小、字体设置、全局热键开关
- **Scripts**：脚本目录、Python 解释器路径、依赖管理
- **Logs**：日志查看和清除

---

## 常见问题

**Q: 应用启动后闪退？**  
A: 检查是否安装了 Go 环境，以及 Python 解释器路径是否正确。

**Q: 脚本无法运行？**  
A: 检查首选项 → Scripts 中的 Python 解释器路径是否正确，以及脚本是否有语法错误。

**Q: 如何添加脚本目录？**  
A: 首选项 → Scripts → Add，选择目录后 Save

**Q: 日志文件位置？**  
A: macOS: `~/Library/Logs/boop/` | Windows: `%APPDATA%/boop/logs/` | Linux: `~/.config/boop/logs/`

**Q: 全局热键不工作？**  
A: 在 macOS 上，需要在系统偏好设置 → 安全性与隐私 → 辅助功能中允许 Boop 控制您的电脑。

---

## 构建应用

### 构建脚本

使用项目中的 `build.sh` 脚本构建应用：

```bash
# 构建当前平台版本
./build.sh

# 构建 macOS 版本
./build.sh --macos

# 构建 Linux 版本
./build.sh --linux

# 构建 Windows 版本
./build.sh --windows
```

### 构建产物

构建完成后，产物会生成在 `dist` 目录中：
- macOS: `Boop-<版本>-macos.dmg`
- Linux: `Boop-<版本>-linux.tar.gz`
- Windows: `Boop-<版本>-windows.zip`

---

## 获取帮助

- 在 Help 菜单中选择 **User Guide** 查看本文档
- 查看项目中的 `README.md` 了解更多详情
