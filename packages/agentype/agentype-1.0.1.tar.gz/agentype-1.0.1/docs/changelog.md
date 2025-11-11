# Changelog

All notable changes to CellType Agent will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-11

### 📦 PyPI 发布版本

这是 AgentType 的首个 PyPI 发布版本，包含文档重组和包结构优化。

### ✨ Changed - 变更

#### 文档重组
- 重新编写简洁的 README.md，突出核心特性和快速开始
- 将详细文档移至 `docs/` 目录：
  - docs/api.md - API 使用文档
  - docs/installation.md - 安装指南
  - docs/configuration.md - 配置说明
  - docs/package_info.md - 包信息
  - docs/changelog.md - 更新日志
- 完善系统依赖说明（Python、R、R 包）

#### 包配置优化
- 修复 MANIFEST.in 中的路径问题（celltypeAgent → agentype）
- 添加 docs 目录到包数据
- 添加 Prompts 模板文件包含规则
- 优化包数据清单结构

#### 文档改进
- 添加 PyPI 徽章
- 完善 R 环境安装说明
- 增加环境检查功能说明
- 优化示例代码说明

### 🔧 Fixed - 修复

- 修复包路径不一致问题
- 确保所有必要的非 Python 文件正确打包
- 修复文档链接

## [1.0.0] - 2025-01-26

### 🎉 首次正式发布

这是 CellType Agent 的首个正式版本，提供完整的细胞类型自动注释功能。

### ✨ Added - 新增功能

#### 核心架构
- **四大 Agent 系统**：MainAgent（主调度器）、SubAgent（基础服务）、DataAgent（数据处理）、AppAgent（应用注释）
- **MCP 协议集成**：基于 Model Context Protocol 的 Agent 间通信
- **React 模式**：LLM 驱动的推理-行动-观察循环

#### 数据处理能力
- 支持多种数据格式：RDS、H5AD、H5、CSV、JSON
- 自动数据格式转换和质量控制
- Marker 基因自动提取和分析
- 并行文件处理支持

#### 注释算法
- **SingleR** 注释支持（基于 R）
- **scType** 注释支持（基于 R）
- **CellTypist** 注释支持（基于 Python）
- 智能算法选择和参数优化

#### 物种识别
- 从 JSON marker 文件自动检测物种
- 从 H5AD 文件自动检测物种
- 从 RDS 文件自动检测物种
- 支持 Human 和 Mouse 物种

#### LLM 集成
- 统一的 LLM 客户端架构
- 完整支持 **DeepSeek Reasoner** 的 reasoning_content
- 流式和非流式输出支持
- 自动超时重试机制
- 幻觉检测（<observation> 标签检测）

#### Token 管理
- 实时 Token 消耗统计
- 多货币定价系统（CNY/USD）
- 分 Agent 成本追踪
- 自动成本估算
- 详细的使用报告

#### 日志系统
- 完整的 LLM 调用日志
- Session ID 追踪机制
- 分模块日志记录
- 控制台和文件双输出

#### 上下文管理
- 自动上下文总结（避免 Token 超限）
- 智能迭代控制
- 长对话压缩

#### 配置系统
- 全局配置管理器
- 环境变量支持
- 动态路径管理
- 统一的输出目录结构

#### API 和工具
- 简洁的 Python API
- 命令行工具（celltype-manage、celltype-server）
- 丰富的示例代码
- 完整的文档

### 🐛 Fixed - 修复问题

#### 核心修复
- 修复并行文件处理冲突问题
- 修复 MCP 服务器超时问题
- 解决上下文总结错误
- 修复配置文件路径查找

#### Token 和成本
- 修复 Token 计价错误
- 修复成本计算精度问题
- 修复 API base URL 匹配逻辑
- 完善多货币定价系统

#### 物种和数据
- 完善物种识别逻辑
- 优化物种信息传递机制
- 修复基因名称大小写处理

#### 输出和日志
- 修复推理内容输出格式
- 修复日志文件位置
- 优化流式输出显示

#### 其他
- 修复 Session ID 传递问题
- 修复项目目录处理
- 修复包构建配置

### 🔧 Changed - 变更

- 统一 LLM 请求接口
- 优化 Token 统计显示格式
- 改进错误处理和重试逻辑
- 简化配置文件结构
- 缩减不必要的控制台输出

### 📚 Documentation - 文档

- 完整的 README.md
- API 使用指南（README_API.md）
- 包信息说明（PACKAGE_INFO.md）
- 配置文档（CONFIG.md）
- 丰富的示例代码

### 🛠️ Technical Details - 技术细节

#### 依赖
- Python 3.8+
- FastAPI, Uvicorn
- Scanpy, AnnData
- MCP, FastMCP
- Pandas, NumPy
- CellTypist（可选）
- rpy2（可选，用于 R 接口）

#### 包大小
- Wheel: ~4.1 MB
- Source: ~3.9 MB

#### 许可证
- MIT License

---

## 未来计划

### [1.1.0] - 计划中

- [ ] 支持更多注释算法
- [ ] 增加批量处理模式
- [ ] Web UI 界面
- [ ] 性能优化和加速
- [ ] 更多物种支持
- [ ] 集成更多数据库

---

## 贡献

欢迎提交 Issue 和 Pull Request！

## 链接

- [GitHub 仓库](#)
- [PyPI 页面](#)
- [文档站点](#)
