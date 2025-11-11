# CellType Agent - 简化API使用指南

## 🚀 快速开始

CellType Agent 现在提供了基于 examples 目录提取的4个核心API函数，让细胞类型分析变得更加简单。

### 安装

```bash
pip install agentype

# 安装全部功能
pip install agentype[all]
```

## 📚 核心API

### 1. 主工作流处理 - MainAgent

```python
import agentype as cta

# 异步版本
result = await cta.process_workflow(
    input_data="data.rds",           # 输入数据文件
    tissue_type="骨髓",              # 组织类型
    api_key="your-api-key",         # 可选，API密钥
    language="zh"                    # 可选，语言设置
)

# 同步版本
result = cta.process_workflow_sync("data.rds", "骨髓")

print(f"分析成功: {result['success']}")
print(f"输出文件: {result['output_file_paths']}")
```

### 2. 基因分析 - SubAgent

```python
# 分析基因列表
gene_list = ["CD3D", "CD4", "CD8A", "CD19", "CD14"]

# 异步版本
result = await cta.analyze_genes(
    gene_list=gene_list,            # 基因列表
    tissue_type="骨髓",             # 组织类型
    max_genes=100                   # 最大基因数量
)

# 同步版本
result = cta.analyze_genes_sync(gene_list, "骨髓")

print(f"推断细胞类型: {result['final_celltype']}")
print(f"分析基因数量: {result['gene_count']}")

# 从文件加载基因列表
result = await cta.analyze_genes("genes.txt", "骨髓")
```

### 3. 数据处理 - DataAgent

```python
# 数据格式转换和预处理
result = await cta.process_data(
    data_file="data.h5ad",          # 输入文件
    target_format="rds",            # 目标格式(可选)
    output_dir="results/"           # 输出目录(可选)
)

# 同步版本
result = cta.process_data_sync("data.h5ad")

print(f"处理成功: {result['success']}")
print(f"输出文件: {result['output_file_paths']}")

# 支持的格式
formats = await cta.get_supported_formats()
print(f"支持格式: {formats}")  # ['.rds', '.h5ad', '.h5', '.csv', '.json']
```

### 4. 细胞类型注释 - AppAgent

```python
# 使用多种注释方法
files = {
    'rds_file': 'data.rds',
    'h5ad_file': 'data.h5ad',
    'marker_genes_json': 'markers.json'
}

result = await cta.annotate_cells(
    files=files,                    # 输入文件字典
    tissue_description="骨髓",      # 组织描述
    species="Mouse",                # 物种: Human/Mouse
    language="zh"                   # 语言设置
)

# 同步版本
result = cta.annotate_cells_sync(files, "骨髓", "Mouse")

print(f"注释成功: {result['success']}")
print(f"使用方法: {result['annotation_methods']}")
print(f"输出文件: {result['output_file_paths']}")

# 便利函数 - 只使用特定方法
result = await cta.annotate_with_singleR("data.rds", "骨髓", "Mouse")
result = await cta.annotate_with_celltypist("data.h5ad", "骨髓", "Human")
```

## 🔧 高级用法

### Agent实例（完整功能）

```python
# 获取完整的Agent实例
main_agent = cta.get_main_agent()
app_agent = cta.get_app_agent()

# 或使用类别名
main_agent = cta.MainAgent()
app_agent = cta.AppAgent()
```

### MCP服务器

```python
# 启动所有MCP服务器
cta.start_all_servers()

# 启动特定服务器
cta.start_single_server("main")
```

### 配置管理

```python
# 获取全局配置
config = cta.get_global_config()
print(f"输出目录: {config.paths.outputs_dir}")
print(f"语言设置: {config.project.language}")
```

## 📋 完整示例

```python
import asyncio
import agentype as cta

async def analyze_my_data():
    # 1. 数据预处理
    data_result = await cta.process_data("raw_data.h5ad")
    if not data_result['success']:
        print(f"数据处理失败: {data_result['error']}")
        return

    processed_file = data_result['output_file_paths'].get('processed_data')

    # 2. 基因分析
    genes = ["CD3D", "CD4", "CD8A", "CD19", "CD14", "FCGR3A"]
    gene_result = await cta.analyze_genes(genes, "免疫系统")
    print(f"预测细胞类型: {gene_result['final_celltype']}")

    # 3. 详细注释
    files = {'h5ad_file': processed_file}
    annotation_result = await cta.annotate_cells(
        files=files,
        tissue_description="免疫系统",
        species="Human"
    )

    if annotation_result['success']:
        print("注释完成!")
        print(f"使用方法: {annotation_result['annotation_methods']}")
        print(f"结果文件: {annotation_result['output_file_paths']}")

# 运行分析
asyncio.run(analyze_my_data())

# 或使用同步版本
def analyze_my_data_sync():
    data_result = cta.process_data_sync("raw_data.h5ad")
    genes = ["CD3D", "CD4", "CD8A"]
    gene_result = cta.analyze_genes_sync(genes, "免疫系统")
    print(f"预测细胞类型: {gene_result['final_celltype']}")

analyze_my_data_sync()
```

## 🎯 API参数说明

### 通用参数

- `api_key`: OpenAI API密钥，默认从环境变量 `OPENAI_API_KEY` 读取
- `api_base`: API基础URL，默认使用配置文件设置
- `model`: 使用的模型，默认使用配置文件设置
- `language`: 语言设置，`"zh"` 或 `"en"`，默认为中文
- `enable_streaming`: 是否启用流式输出，默认 `True`

### 返回格式

所有API函数都返回统一的字典格式：

```python
{
    "success": bool,                    # 是否成功
    "total_iterations": int,            # 总迭代次数
    "output_file_paths": dict,          # 输出文件路径
    "analysis_log": list,               # 分析日志
    "error": str,                       # 错误信息(如果失败)
    # ... 其他特定字段
}
```

## 🔗 命令行工具

```bash
# 项目管理
celltype-manage status              # 检查状态
celltype-manage config              # 查看配置
celltype-manage examples            # 运行示例

# MCP服务器
celltype-server                     # 启动所有服务器
celltype-server main               # 启动特定服务器
celltype-server --concurrent       # 并发启动
```

## 💡 最佳实践

1. **使用同步版本**: 如果不熟悉 async/await，使用 `*_sync` 版本的函数
2. **错误处理**: 总是检查返回结果中的 `success` 字段
3. **配置API密钥**: 通过环境变量设置 `OPENAI_API_KEY`
4. **文件路径**: 使用绝对路径或确保文件存在
5. **日志查看**: 检查 `outputs/logs/` 目录下的详细日志

这样，你就可以用非常简单的API调用完成复杂的细胞类型分析任务了！