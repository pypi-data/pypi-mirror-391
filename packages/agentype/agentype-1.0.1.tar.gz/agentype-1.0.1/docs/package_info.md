# CellType Agent - Python包使用指南

## 📦 包构建完成

恭喜！你的CellType Agent项目已成功打包为Python包。生成的包文件位于 `dist/` 目录下：

- **源码包**: `agentype-1.0.0.tar.gz` (348KB)
- **Wheel包**: `agentype-1.0.0-py3-none-any.whl` (445KB)

## 🚀 安装方式

### 本地安装
```bash
# 从wheel包安装（推荐）
pip install dist/agentype-1.0.0-py3-none-any.whl

# 或从源码包安装
pip install dist/agentype-1.0.0.tar.gz

# 本地开发安装（可编辑模式）
pip install -e .
```

### 可选依赖安装
```bash
# 安装细胞类型注释工具
pip install "agentype[annotation]"

# 安装可视化支持
pip install "agentype[viz]"

# 安装性能优化
pip install "agentype[performance]"

# 安装全部功能
pip install "agentype[all]"

# 开发依赖
pip install "agentype[dev]"
```

## 💡 使用方式

### 命令行工具

安装后，你将获得以下命令行工具：

```bash
# 项目管理工具
celltype-manage status      # 检查项目状态
celltype-manage config      # 查看配置
celltype-manage examples    # 运行示例
celltype-manage clean       # 清理输出目录

# MCP服务器启动器
celltype-server            # 启动所有服务器
celltype-server main       # 只启动MainAgent
celltype-server --concurrent  # 并发启动多个服务器
```

### Python API

```python
import agentype as cta

# 检查安装状态
cta.check_installation()

# 获取Agent实例
main_agent = cta.get_main_agent()
app_agent = cta.get_app_agent()
sub_agent = cta.get_sub_agent()
data_agent = cta.get_data_agent()

# 配置管理
config = cta.get_global_config()

# 启动服务器
cta.start_all_servers()
cta.start_single_server("main")
```

### 直接使用Agent类

```python
# 导入特定Agent
from celltypeAppAgent import CelltypeAnnotationAgent
from celltypeMainagent import MainReactAgent
from celltypeSubagent import CelltypeReactAgent
from celltypeDataAgent import DataProcessorAgent

# 实例化使用
app_agent = CelltypeAnnotationAgent()
main_agent = MainReactAgent()
```

## 📁 包内容

包含以下模块和资源：

### 主要模块
- **celltypeMainagent**: 主调度器
- **celltypeSubagent**: 基础数据服务
- **celltypeDataAgent**: 数据处理
- **celltypeAppAgent**: 应用级注释
- **agentype**: 统一入口包
- **config**: 配置管理
- **examples**: 示例代码

### 资源文件
- R脚本文件 (`*.R`)
- 国际化文件 (`locales/*.json`)
- 配置文件 (`*.json`)
- 项目管理工具 (`manage.py`)

## 🔧 开发和发布

### 重新构建包
```bash
# 清理之前的构建
rm -rf build/ dist/ *.egg-info/

# 构建新包
python setup.py sdist bdist_wheel

# 或使用build工具（如果setuptools版本足够新）
python -m build
```

### 上传到PyPI
```bash
# 安装上传工具
pip install twine

# 检查包
twine check dist/*

# 上传到测试PyPI
twine upload --repository testpypi dist/*

# 上传到正式PyPI
twine upload dist/*
```

## 📋 系统要求

- **Python**: 3.8+
- **操作系统**: Linux, macOS, Windows
- **R环境**: 可选（SingleR和scType功能需要）

### 核心依赖
- fastapi, uvicorn (Web API)
- pandas, numpy (数据处理)
- scanpy, anndata (单细胞分析)
- mcp, fastmcp (MCP框架)

### 可选依赖
- celltypist (CellTypist注释)
- rpy2 (R接口)
- matplotlib, seaborn (可视化)

## 🆘 故障排除

### 常见问题

1. **导入错误**：检查依赖是否完整安装
2. **R接口问题**：确保R环境已安装并配置正确
3. **权限问题**：使用`--user`参数安装或使用虚拟环境

### 获取帮助

```python
# 检查安装状态
import agentype
agentype.check_installation()

# 查看包信息
agentype.info()

# 使用管理工具诊断
celltype-manage status
```

## 🎉 恭喜

你的CellType Agent项目现在已经是一个完整的、可分发的Python包了！

可以与其他研究者分享，或上传到PyPI供全球用户使用。包含了完整的细胞类型分析功能、统一的API接口和友好的命令行工具。