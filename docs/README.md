# Boop 项目文档

本目录包含 Boop 文本处理工具的完整项目文档，分为三大板块：

| 板块 | 目录 | 内容 |
|------|------|------|
| **用户文档** | [user-guide.md](./user-guide.md) | 面向终端用户：使用说明、快捷键、脚本编写、常见问题 |
| **架构与开发** | [architecture/README.md](./architecture/README.md) | 面向开发者：C4 架构图、模块映射、数据流、工程特性、ADR、入职指南 |
| **架构文档方法论** | [methodology/README.md](./methodology/README.md) | 面向架构文档作者：C4 参考、ADR 模板、Python 模式检测清单、输出模板 |

## 推荐阅读顺序

- **想快速上手** → 先读 [user-guide.md](./user-guide.md)
- **想了解项目全貌** → [architecture/01-overview.md](./architecture/01-overview.md) → [02-c4-context.md](./architecture/02-c4-context.md) → [10-onboarding.md](./architecture/10-onboarding.md)
- **准备修改代码** → 从 [06-module-map.md](./architecture/06-module-map.md) 和 [decisions/README.md](./architecture/decisions/README.md) 切入
- **想为项目写架构文档** → [methodology/README.md](./methodology/README.md)

## 顶层入口

- 项目根 README：[../README.md](../README.md)
- 应用根 README：[../boop/README.md](../boop/README.md)
