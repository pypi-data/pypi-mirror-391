# CellType MCP Server - 统一配置示例

这个目录包含了所有Agent的统一配置使用示例。所有示例都使用根目录的统一配置系统，输出文件统一保存在 `outputs/` 目录下。

## 📁 目录结构

```
outputs/
├── cache/          # 缓存文件
│   ├── celltypeMainagent/
│   ├── celltypeSubagent/
│   ├── celltypeDataAgent/
│   └── celltypeAppAgent/
├── logs/           # 日志文件
├── results/        # 分析结果
└── downloads/      # 下载的数据库文件
```

## 🚀 使用示例

### 1. MainAgent 示例 (main_example.py)
统一调度器，协调多个Agent完成复杂的细胞类型分析任务。

```bash
python examples/main_example.py
```

**功能特点:**
- 统一工作流编排
- 自动调用其他Agent
- 结果整合和输出管理

### 2. SubAgent 示例 (subagent_example.py)
基础数据服务，提供基因信息查询和细胞类型富集分析。

```bash
python examples/subagent_example.py
```

**功能特点:**
- NCBI基因信息查询
- CellMarker/PanglaoDB数据库查询
- 基因富集分析
- 自动物种检测

### 3. DataAgent 示例 (data_example.py)
数据处理专家，支持多种数据格式的转换和预处理。

```bash
python examples/data_example.py
```

**功能特点:**
- RDS/H5AD/H5/CSV/JSON格式支持
- 数据质量控制
- 格式转换和标准化

### 4. AppAgent 示例 (app_example.py)
应用级注释，集成多种细胞类型注释算法。

```bash
python examples/app_example.py
```

**功能特点:**
- SingleR注释 (R环境)
- scType注释 (R环境)
- CellTypist注释 (Python环境)
- 智能算法选择

## ⚙️ 配置说明

### 环境变量配置

```bash
# API密钥设置
export OPENAI_API_KEY="your-api-key-here"
export OPENAI_API_BASE="https://api.openai.com/v1"
export OPENAI_MODEL="gpt-4"

# 语言和行为设置
export CELLTYPE_LANGUAGE="zh"  # zh(中文) 或 en(英文)
export CELLTYPE_ENABLE_STREAMING="true"
export CELLTYPE_ENABLE_LOGGING="true"
```

### 配置文件

所有配置都保存在 `config/agentype_config.json` 中:

```json
{
  "llm": {
    "api_base": "https://api.openai.com/v1",
    "api_key": null,  // 通过环境变量设置
    "model": "gpt-4",
    "max_tokens": 4000,
    "temperature": 0.3
  },
  "project": {
    "language": "zh",
    "enable_streaming": true,
    "enable_logging": true,
    "cache_expiry_days": 30
  },
  "agents": {
    "celltypeMainagent": {"enabled": true, "timeout": 30},
    "celltypeSubagent": {"enabled": true, "timeout": 30},
    "celltypeDataAgent": {"enabled": true, "timeout": 30},
    "celltypeAppAgent": {"enabled": true, "timeout": 30}
  }
}
```

## 📊 输出管理

### 文件命名规范

- **日志文件**: `{agent_name}_{timestamp}.log`
- **结果文件**: `{agent_name}_{session_id}_{type}.{ext}`
- **缓存文件**: 按数据库和功能分类存储

### 目录结构示例

```
outputs/
├── cache/
│   ├── celltypeSubagent/
│   │   ├── cellmarker/
│   │   ├── panglaodb/
│   │   └── ncbi/
│   └── celltypeAppAgent/
│       ├── celldx/
│       ├── sctype/
│       └── celltypist/
├── logs/
│   ├── celltypeMainagent/
│   │   └── main_agent_2025-09-17_10-30-15.log
│   └── celltypeSubagent/
│       └── subagent_2025-09-17_10-32-20.log
└── results/
    ├── celltypeMainagent/
    │   └── session_abc123/
    │       ├── final_results.json
    │       └── annotation_summary.xlsx
    └── celltypeAppAgent/
        └── annotation_results_mouse_bone_marrow.h5ad
```

## 🔧 依赖要求

### Python依赖
```bash
pip install -e .
```

### R环境 (AppAgent需要)
```r
install.packages(c("SingleR", "scType", "celldex"))
```

### CellTypist (AppAgent需要)
```bash
pip install scanpy celltypist
```

## 🚨 注意事项

1. **API密钥安全**: 不要在代码中硬编码API密钥，使用环境变量
2. **文件权限**: 确保 `outputs/` 目录有写权限
3. **磁盘空间**: 数据库缓存可能占用较大空间，注意磁盘容量
4. **网络连接**: 首次运行需要下载数据库文件
5. **R环境**: AppAgent的某些功能需要R环境支持

## 📞 支持

如果遇到问题，请检查:
1. `outputs/logs/` 目录下的详细日志
2. `config/agentype_config.json` 配置是否正确
3. 环境变量是否已正确设置
4. 必要的依赖是否已安装

更多信息请查看项目根目录的 `README.md` 文件。
