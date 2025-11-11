# agentype 安装说明

## 📦 包文件说明

本项目提供了两种安装包格式:

- **agentype-1.0.0-py3-none-any.whl** - Wheel 安装包 (4.0M)
  - 推荐格式,安装速度快
  - 适合直接使用 pip 安装

- **agentype-1.0.0.tar.gz** - 源码包 (3.8M)
  - 包含完整源代码
  - 兼容性好,适合需要查看源码的场景

## 🚀 快速安装

### 1. 基础安装 (核心功能)

```bash
# 使用 Wheel 包安装 (推荐)
pip install agentype-1.0.0-py3-none-any.whl

# 或使用源码包安装
pip install agentype-1.0.0.tar.gz
```

基础安装包含以下核心依赖:
- MCP 框架 (mcp, fastmcp)
- Web API 框架 (FastAPI, Uvicorn)
- 单细胞分析核心库 (scanpy, anndata)
- 数据处理库 (numpy, pandas, scipy)
- 基因富集分析 (gseapy)

## 🎯 完整功能安装

根据您的需求选择安装不同的可选功能模块:

### 2. 细胞类型注释功能

包含 CellTypist、SingleR、scType 等注释工具:

```bash
pip install agentype-1.0.0-py3-none-any.whl[annotation]
```

包含依赖:
- celltypist>=1.6.0
- rpy2>=3.5.0 (R 语言接口,用于 SingleR 和 scType)
- bioservices>=1.11.0 (NCBI API)
- biopython>=1.81

**注意**: 使用 SingleR 和 scType 需要先安装 R 语言环境 (R >= 4.0.0)

### 3. 机器学习增强

包含高级机器学习功能:

```bash
pip install agentype-1.0.0-py3-none-any.whl[ml]
```

包含依赖:
- scikit-learn>=1.3.0
- torch>=2.0.0
- numba>=0.58.0

### 4. 数据可视化

包含绘图和可视化功能:

```bash
pip install agentype-1.0.0-py3-none-any.whl[viz]
```

包含依赖:
- matplotlib>=3.8.0
- seaborn>=0.12.0
- plotly>=5.17.0

### 5. 性能优化

包含大规模数据处理优化:

```bash
pip install agentype-1.0.0-py3-none-any.whl[performance]
```

包含依赖:
- dask[complete]>=2023.12.0
- joblib>=1.3.0
- diskcache>=5.6.0

### 6. 部署相关

包含生产环境部署工具:

```bash
pip install agentype-1.0.0-py3-none-any.whl[deploy]
```

包含依赖:
- gunicorn>=21.2.0
- docker>=6.1.0

### 7. 一次性安装所有功能 (推荐)

如果您需要使用 agentype 的全部功能:

```bash
pip install agentype-1.0.0-py3-none-any.whl[annotation,ml,viz,performance,deploy]
```

## 🔧 系统要求

### Python 版本
- Python >= 3.8
- 推荐 Python 3.10 或更高版本

### R 语言环境 (可选)
如果需要使用 SingleR 或 scType 功能:
- R >= 4.0.0
- 必需的 R 包会在首次使用时自动安装

### 系统依赖
某些依赖可能需要系统级库:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential libhdf5-dev
```

**CentOS/RHEL:**
```bash
sudo yum groupinstall "Development Tools"
sudo yum install hdf5-devel
```

**macOS:**
```bash
brew install hdf5
```

## ✅ 验证安装

安装完成后,验证是否成功:

```bash
# 检查包版本
pip show agentype

# 测试导入
python -c "import agentype; print(agentype.__version__)"

# 查看命令行工具
celltype-manage --help
```

## 🎮 快速开始

### 启动 MCP 服务器

```bash
# 启动所有服务器
celltype-server

# 或使用管理工具
celltype-manage start
```

### Python 代码示例

```python
from agentype.mainagent import MainReactAgent
from agentype.dataagent import DataProcessorAgent
from agentype.appagent import CellTypeAnnotationAgent

# 初始化主 Agent
main_agent = MainReactAgent()

# 进行细胞类型注释
result = await main_agent.run(
    "请分析这个单细胞数据并进行细胞类型注释",
    data_path="/path/to/your/data.h5ad"
)
```

## 📝 配置

安装后,在项目目录创建配置文件:

```bash
# 复制示例配置
cp agentype_config.example.json agentype_config.json

# 编辑配置文件
vim agentype_config.json
```

主要配置项:
- **LLM 配置**: API 密钥、模型选择
- **数据路径**: 输入/输出目录
- **MCP 服务器**: 端口和地址配置
- **缓存设置**: 缓存目录和大小限制

## 🐛 常见问题

### Q1: 安装 rpy2 失败
**解决方案**: 确保已安装 R 语言环境,并设置 R_HOME 环境变量:
```bash
export R_HOME=/usr/lib/R  # Linux
export R_HOME=/Library/Frameworks/R.framework/Resources  # macOS
```

### Q2: numpy 版本冲突
**解决方案**: agentype 要求 numpy < 2.0,如遇冲突:
```bash
pip install "numpy>=1.24.0,<2.0" --force-reinstall
```

### Q3: h5py 安装失败
**解决方案**: 安装系统 HDF5 库后重试:
```bash
# Ubuntu/Debian
sudo apt-get install libhdf5-dev

# 重新安装
pip install h5py --no-binary h5py
```

### Q4: 找不到命令行工具
**解决方案**: 确保 pip 安装路径在 PATH 中:
```bash
export PATH="$HOME/.local/bin:$PATH"  # Linux
export PATH="$HOME/Library/Python/3.x/bin:$PATH"  # macOS
```

## 📚 更多资源

- **项目文档**: 查看 [README.md](README.md)
- **变更日志**: 查看 [CHANGELOG.md](CHANGELOG.md)
- **配置说明**: 查看 [CONFIG.md](CONFIG.md)
- **API 文档**: 查看 [README_API.md](README_API.md)

## 💡 开发安装

如果您需要修改源码或参与开发:

```bash
# 解压源码包
tar -xzf agentype-1.0.0.tar.gz
cd agentype-1.0.0

# 开发模式安装
pip install -e .[dev,annotation,ml,viz,performance]

# 运行测试
pytest tests/
```

## 📧 技术支持

如遇到安装问题:
- 邮件: contact@agentype.com
- GitHub Issues: https://github.com/agentype/celltype-agent/issues

---

**版本**: 1.0.0
**更新日期**: 2025-10-27
