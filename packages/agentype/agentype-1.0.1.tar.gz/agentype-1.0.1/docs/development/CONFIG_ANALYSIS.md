# CellType MCP Server 配置系统详细分析

> 本文档详细分析了 agentype 项目的配置系统架构、参数定义、加载流程和调用链路。

**版本**: 1.0.0
**最后更新**: 2025-10-28
**作者**: CellType Agent 开发团队

---

## 📑 目录

- [一、配置文件结构](#一配置文件结构)
- [二、配置参数定义](#二配置参数定义)
- [三、配置加载流程](#三配置加载流程)
- [四、配置参数调用链路图](#四配置参数调用链路图)
- [五、各 Agent 配置使用详解](#五各-agent-配置使用详解)
- [六、Common 模块配置使用](#六common-模块配置使用)
- [七、配置参数使用位置汇总表](#七配置参数使用位置汇总表)
- [八、配置使用最佳实践](#八配置使用最佳实践)
- [九、完整配置示例](#九完整配置示例)
- [十、总结](#十总结)

---

## 📁 一、配置文件结构

### 1.1 配置文件位置

```
celltype-mcp-server/
├── agentype_config.json              # ⭐ 主配置文件
├── agentype_config.example.json      # 配置模板
└── agentype/
    ├── config/                             # 全局配置模块
    │   ├── global_config.py               # 全局配置管理器（核心）
    │   ├── paths_config.py                # 路径配置管理器
    │   └── unified_logger.py              # 统一日志管理器
    │
    ├── mainagent/config/                   # MainAgent 配置
    │   ├── settings.py                    # MainAgent 设置
    │   ├── cache_config.py                # 缓存配置
    │   ├── session_config.py              # Session 配置
    │   └── prompts.py                     # 提示词
    │
    ├── subagent/config/                    # SubAgent 配置
    ├── dataagent/config/                   # DataAgent 配置
    └── appagent/config/                    # AppAgent 配置
```

### 1.2 主配置文件结构

**`agentype_config.json` 完整结构**:

```json
{
  "version": "1.0.0",
  "updated_at": "2025-10-26T16:21:47.261005",

  "paths": {
    "project_root": "/root/code/gitpackage/.../celltype-mcp-server",
    "outputs_dir": ".../outputs",
    "cache_dir": ".../outputs/cache",
    "logs_dir": ".../outputs/logs",
    "results_dir": ".../outputs/results",
    "downloads_dir": ".../outputs/downloads",
    "temp_dir": ".../outputs/temp"
  },

  "llm": {
    "api_base": null,                       // API 基础 URL
    "api_key": null,                        // API 密钥
    "model": "gpt-4",                       // 模型名称
    "max_tokens": 4000,                     // 最大 token 数
    "temperature": 0.3                      // 温度参数
  },

  "project": {
    "language": "zh",                       // 语言（zh/en）
    "enable_streaming": true,               // 流式输出
    "enable_logging": true,                 // 启用日志
    "max_parallel_tasks": 3,                // 最大并行任务
    "cache_expiry_days": 30,                // 缓存过期天数
    "auto_cleanup": true                    // 自动清理
  },

  "agents": {
    "celltypeMainagent": {
      "enabled": true,
      "max_retries": 3,
      "log_level": "INFO"
    },
    "celltypeSubagent": { ... },
    "celltypeDataAgent": { ... },
    "celltypeAppAgent": { ... }
  }
}
```

---

## 🔧 二、配置参数定义

### 2.1 全局配置类（`global_config.py`）

#### **PathConfig** - 路径配置

```python
@dataclass
class PathConfig:
    project_root: Path      # 项目根目录
    outputs_dir: Path       # 输出目录
    cache_dir: Path         # 缓存目录
    logs_dir: Path          # 日志目录
    results_dir: Path       # 结果目录
    downloads_dir: Path     # 下载目录
    temp_dir: Path          # 临时目录
```

**调用位置**:
- ✅ 所有 Agent 的缓存管理
- ✅ 日志系统
- ✅ 结果保存
- ✅ 临时文件处理

#### **LLMConfig** - LLM 配置

```python
@dataclass
class LLMConfig:
    api_base: Optional[str] = None          # API URL
    api_key: Optional[str] = None           # API 密钥
    model: str = "gpt-4"                    # 模型名称
    max_tokens: int = 4000                  # 最大 token
    temperature: float = 0.3                # 温度参数
```

**调用位置**:
- ✅ `common/llm_client.py` - LLM 客户端初始化
- ✅ 所有 Agent 的 ConfigManager

#### **ProjectConfig** - 项目配置

```python
@dataclass
class ProjectConfig:
    language: str = "zh"                    # 界面语言
    enable_streaming: bool = True           # 流式输出
    enable_logging: bool = True             # 日志开关
    max_parallel_tasks: int = 3             # 并行任务数
    cache_expiry_days: int = 30             # 缓存过期
    auto_cleanup: bool = True               # 自动清理
```

**调用位置**:
- ✅ React Agent 初始化（所有 Agent）
- ✅ 提示词语言选择
- ✅ 流式输出控制

#### **AgentConfig** - Agent 配置

```python
@dataclass
class AgentConfig:
    enabled: bool = True                    # 启用状态
    max_retries: int = 3                    # 重试次数
    log_level: str = "INFO"                 # 日志级别
```

**调用位置**:
- ✅ MainAgent 子 Agent 管理
- ✅ LLM 调用重试逻辑

### 2.2 各 Agent 特有配置

#### **MainAgent 配置** (`mainagent/config/settings.py`)

```python
@dataclass
class ConfigManager:
    # LLM配置
    openai_api_base: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = "gpt-4o"

    # MainAgent配置
    language: str = "zh"
    enable_streaming: bool = True
    max_parallel_tasks: int = 3

    # 缓存和日志配置
    cache_dir: Optional[str] = None
    log_dir: Optional[str] = None
    enable_logging: bool = True

    # 子Agent连接配置
    subagents: Dict[str, SubAgentConfig] = field(default_factory=dict)
```

#### **SubAgent 配置** (`subagent/config/settings.py`)

```python
class ConfigManager:
    def __init__(self,
                 openai_api_base: str = None,
                 openai_api_key: str = None,
                 openai_model: str = "gpt-4o",
                 proxy: str = None):
        # 基础 LLM 配置
        self.openai_api_base = openai_api_base
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model
        self.proxy = proxy
```

#### **DataAgent 配置** (`dataagent/config/settings.py`)

```python
class ConfigManager:
    def __init__(self, ...):
        # LLM 配置
        self.openai_api_base = openai_api_base
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model

        # 数据处理特有配置
        self.pval_threshold = 0.05           # p值阈值
        self.max_retries = 3                 # 最大重试次数

        # 使用统一配置系统
        self.cache_dir = str(get_cache_dir("celltypeDataAgent"))
        self.log_dir = "logs"
```

#### **AppAgent 配置** (`appagent/config/settings.py`)

```python
class ConfigManager:
    def __init__(self, ...):
        # LLM 配置
        self.openai_api_base = openai_api_base
        self.openai_api_key = openai_api_key
        self.openai_model = openai_model

        # 细胞类型注释工具配置
        self.singler_config = {
            "default_dataset": "HumanPrimaryCellAtlasData",
            "output_format": "json"
        }

        self.sctype_config = {
            "default_tissue": "Immune system",
            "output_format": "json"
        }

        self.celltypist_config = {
            "auto_detect_species": True,
            "default_model": None,
            "output_format": "json"
        }

        # 物种检测配置
        self.species_detection_config = {
            "confidence_threshold": 0.7,
            "default_species": "Human",
            "supported_species": ["Human", "Mouse"]
        }
```

---

## 🔄 三、配置加载流程

### 3.1 配置加载优先级（从高到低）

```
1. 环境变量 CELLTYPE_CONFIG_PATH      ← 最高优先级（用于子 Agent 继承）
   ↓
2. 环境变量 CELLTYPE_CONFIG_FILE
   ↓
3. 当前工作目录 agentype_config.json
   ↓
4. 默认配置（硬编码）
```

### 3.2 初始化流程

**核心代码**: `agentype/config/global_config.py:GlobalConfigManager._initialize()`

```python
def _initialize(self):
    # 步骤 1: 确定项目根目录
    env_root = os.getenv("CELLTYPE_PROJECT_ROOT")
    external_config = _detect_external_config()

    if env_root:
        project_root = Path(env_root)
    elif external_config:
        project_root = external_config.parent
    else:
        project_root = Path.cwd()

    # 步骤 2: 确定配置文件路径
    env_config = os.getenv("CELLTYPE_CONFIG_FILE")

    if env_config:
        config_file = Path(env_config)
    elif external_config:
        config_file = external_config
    else:
        config_file = project_root / "agentype_config.json"

    # 步骤 3: 设置环境变量供子 Agent 使用
    if config_file.exists():
        os.environ["CELLTYPE_CONFIG_PATH"] = str(config_file)

    # 步骤 4: 初始化路径配置
    self._init_paths()

    # 步骤 5: 加载或创建配置文件
    self._load_or_create_config()
```

### 3.3 配置策略：只读原则

```python
def _load_or_create_config(self):
    """
    配置策略：
    - 配置文件存在 → 仅读取，绝不写入
    - 配置文件不存在 → 创建默认配置并写入一次
    """
    config_file_existed = self._config_file.exists()

    if config_file_existed:
        # 只读取，不修改
        with open(self._config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        self._load_from_dict(config_data)
    else:
        # 创建新配置，仅写入一次
        self._create_default_config()
        self.save_config()
```

### 3.4 环境变量支持

**支持的环境变量列表**:

```bash
# 配置文件相关
CELLTYPE_CONFIG_PATH         # 配置文件路径（最高优先级）
CELLTYPE_CONFIG_FILE         # 配置文件路径（备选）
CELLTYPE_PROJECT_ROOT        # 项目根目录

# LLM 配置
OPENAI_API_BASE              # API 基础 URL
OPENAI_API_KEY               # API 密钥
OPENAI_MODEL                 # 模型名称

# 项目配置
CELLTYPE_LANGUAGE            # 语言设置
CELLTYPE_ENABLE_STREAMING    # 启用流式输出
CELLTYPE_ENABLE_LOGGING      # 启用日志

# 工作目录
CELLTYPE_WORK_DIR            # 子 Agent 工作目录
```

### 3.5 配置验证

```python
def _validate_config(self, is_newly_created: bool = False):
    """验证配置文件是否完整

    检查 API 配置：
    - api_key 不能为空
    - api_base 不能为空

    如果检测到配置不完整，抛出 ConfigurationIncompleteError
    """
    api_key_empty = not self._llm_config.api_key or \
                    str(self._llm_config.api_key).strip() == ""
    api_base_empty = not self._llm_config.api_base or \
                     str(self._llm_config.api_base).strip() == ""

    if api_key_empty and api_base_empty:
        # 显示友好的错误提示
        raise ConfigurationIncompleteError(
            f"配置文件{'已生成' if is_newly_created else '不完整'}: "
            f"{self._config_file}\n"
            f"请填写 llm.api_base 和 llm.api_key 后重新运行。"
        )
```

---

## 📊 四、配置参数调用链路图

### 4.1 LLM 配置调用链

```
agentype_config.json
    └─ llm { api_base, api_key, model, temperature, max_tokens }
        │
        ├─→ GlobalConfigManager.llm
        │   └─→ get_global_config().llm
        │       │
        │       ├─→ MainAgent.ConfigManager
        │       ├─→ SubAgent.ConfigManager
        │       ├─→ DataAgent.ConfigManager
        │       └─→ AppAgent.ConfigManager
        │
        └─→ common/llm_client.py:LLMClient
            ├─ _normalize_api_url()        ← 使用 api_base
            ├─ chat()                       ← 使用 api_key, model
            └─ chat_stream()                ← 使用 api_key, model
```

**具体调用位置**:

| 配置参数 | 调用文件 | 调用方法/类 |
|---------|---------|-----------|
| `api_base` | `common/llm_client.py` | `LLMClient._normalize_api_url()` |
| `api_key` | `common/llm_client.py` | `LLMClient.chat()` / `chat_stream()` |
| `model` | `common/llm_client.py` | `LLMClient.__init__()` |
| `temperature` | `mainagent/agent/main_react_agent.py` | `MainReactAgent.run()` |
| `max_tokens` | `mainagent/agent/main_react_agent.py` | `MainReactAgent.run()` |

### 4.2 路径配置调用链

```
agentype_config.json
    └─ paths { cache_dir, logs_dir, results_dir, temp_dir, downloads_dir }
        │
        ├─→ GlobalConfigManager.paths
        │   │
        │   ├─→ get_cache_dir(agent_name)
        │   │   └─→ mainagent/config/cache_config.py:CacheManager
        │   │   └─→ subagent/config/cache_config.py:CacheManager
        │   │   └─→ dataagent/config/cache_config.py:CacheManager
        │   │   └─→ appagent/config/cache_config.py:CacheManager
        │   │
        │   ├─→ get_logs_dir(agent_name)
        │   │   └─→ config/unified_logger.py:UnifiedOutputLogger
        │   │   └─→ common/llm_logger.py:LLMLogger
        │   │   └─→ 所有 Agent 的日志初始化
        │   │
        │   ├─→ get_results_dir()
        │   │   └─→ mainagent/tools/mapping_tools.py:adata_mapping()
        │   │   └─→ dataagent/tools/save_marker_genes.py
        │   │
        │   ├─→ get_temp_dir()
        │   │   └─→ dataagent/tools/data_converters.py
        │   │
        │   └─→ get_downloads_dir()
        │       └─→ subagent/tools/fetchers/* (数据库下载)
```

**详细调用位置表**:

| 路径类型 | 调用文件 | 调用场景 |
|---------|---------|---------|
| `cache_dir` | `*/config/cache_config.py` | 所有 Agent 的缓存管理 |
| `logs_dir` | `config/unified_logger.py` | 统一日志系统 |
| `logs_dir` | `common/llm_logger.py` | LLM 调用日志 |
| `results_dir` | `mainagent/tools/mapping_tools.py` | 保存映射结果 |
| `results_dir` | `dataagent/tools/save_marker_genes.py` | 保存 marker 基因 |
| `temp_dir` | `dataagent/tools/data_converters.py` | 临时文件转换 |
| `downloads_dir` | `subagent/tools/fetchers/*` | 数据库缓存 |

### 4.3 Project 配置调用链

```
agentype_config.json
    └─ project { language, enable_streaming, enable_logging, max_parallel_tasks }
        │
        ├─→ language
        │   └─→ 所有 Agent 的 __init__(language=...)
        │       ├─→ */config/prompts.py:get_system_prompt(language)
        │       └─→ common/token_statistics.py:TokenReporter(language)
        │
        ├─→ enable_streaming
        │   └─→ 所有 Agent 的 __init__(enable_streaming=...)
        │       └─→ common/llm_client.py:chat_stream() 开关
        │
        ├─→ enable_logging
        │   └─→ config/unified_logger.py:UnifiedOutputLogger
        │
        └─→ max_parallel_tasks
            └─→ mainagent/config/settings.py:ConfigManager
```

### 4.4 Agent 配置调用链

```
agentype_config.json
    └─ agents { celltypeMainagent, celltypeSubagent, ... }
        │
        ├─→ enabled
        │   └─→ mainagent/tools/subagent_tools.py (控制子 Agent 启用)
        │
        ├─→ max_retries
        │   └─→ */agent/*_react_agent.py (LLM 调用重试)
        │
        └─→ log_level
            └─→ config/unified_logger.py (日志级别)
```

---

## 🎯 五、各 Agent 配置使用详解

### 5.1 MainAgent 配置流程

**入口文件**: `agentype/mainagent/agent/main_react_agent.py`

```python
from agentype.config import get_logs_dir
from agentype.mainagent.config.settings import ConfigManager

class MainReactAgent:
    def __init__(self, config: Optional[ConfigManager] = None, ...):
        # 1. 使用传入配置或从环境变量创建
        self.config = config or ConfigManager.from_env()

        # 2. 使用全局配置的日志目录
        if log_dir is None:
            log_dir = str(get_logs_dir("llm/main_agent"))

        # 3. 初始化 LLM 客户端（使用 config）
        self.llm_logger = LLMLogger(log_dir)
        self.llm_client = LLMClient(
            config=self.config,
            logger_callbacks={...}
        )
```

**MCP Server 启动**: `agentype/mainagent/services/mcp_server.py`

```python
from agentype.mainagent.tools.subagent_tools import load_config_from_json

# 从全局配置加载
json_config = load_config_from_json()  # 读取 agentype_config.json

if json_config:
    llm_config = json_config.get('llm', {})
    project_config = json_config.get('project', {})

    # 创建 MainAgent 配置
    config = ConfigManager(
        openai_api_base=llm_config.get('api_base'),
        openai_api_key=llm_config.get('api_key'),
        openai_model=llm_config.get('model', 'gpt-4o'),
        language=project_config.get('language', 'zh'),
        enable_streaming=project_config.get('enable_streaming', True)
    )
```

### 5.2 SubAgent 配置流程

**API 入口**: `agentype/api/celltype_analysis.py`

```python
from agentype.config import get_global_config, check_and_update_config

async def analyze_genes(..., api_key=None, api_base=None, model=None):
    # 1. 获取全局配置
    global_config = get_global_config()

    # 2. 检查并更新配置（如果 API 参数传入）
    check_and_update_config(
        global_config,
        api_key=api_key,
        api_base=api_base,
        model=model,
        language=language,
        enable_streaming=enable_streaming,
    )

    # 3. 创建 SubAgent 配置（优先使用参数，否则使用全局配置）
    config = ConfigManager(
        openai_api_base=api_base or global_config.llm.api_base,
        openai_api_key=api_key or global_config.llm.api_key,
        openai_model=model or global_config.llm.model,
    )

    # 4. 创建 Agent
    agent = CellTypeReactAgent(
        config=config,
        language=language,
        enable_streaming=enable_streaming,
    )
```

### 5.3 DataAgent 配置流程

**配置初始化**: `agentype/dataagent/config/settings.py`

```python
from agentype.config import get_cache_dir

class ConfigManager:
    def __init__(self, ...):
        # 使用全局配置的缓存目录
        self.cache_dir = str(get_cache_dir("celltypeDataAgent"))
        self.log_dir = "logs"

        # DataAgent 特有配置
        self.pval_threshold = 0.05           # p 值阈值
        self.max_retries = 3                 # 最大重试次数
```

**调用位置**: `agentype/dataagent/tools/data_converters.py`

```python
from agentype.config import get_temp_dir

def convert_h5ad_to_rds(h5ad_file, ...):
    # 使用全局配置的临时目录
    temp_dir = get_temp_dir()
    ...
```

### 5.4 AppAgent 配置流程

**配置初始化**: `agentype/appagent/config/settings.py`

```python
from agentype.config import get_logs_dir

class ConfigManager:
    def __init__(self, ...):
        # 使用全局配置的 LLM 日志目录
        self.llm_log_dir = str(get_logs_dir("llm/app_agent"))

        # 细胞类型注释工具配置
        self.singler_config = {
            "default_dataset": "HumanPrimaryCellAtlasData",
            "output_format": "json"
        }

        self.sctype_config = {
            "default_tissue": "Immune system",
            "output_format": "json"
        }

        self.celltypist_config = {
            "auto_detect_species": True,
            "default_model": None,
            "output_format": "json"
        }

        # 物种检测配置
        self.species_detection_config = {
            "confidence_threshold": 0.7,
            "default_species": "Human",
            "supported_species": ["Human", "Mouse"]
        }
```

---

## 🔍 六、Common 模块配置使用

### 6.1 LLM Client

**文件**: `agentype/common/llm_client.py`

```python
class LLMClient:
    def __init__(self, config, logger_callbacks=None):
        """
        Args:
            config: 包含以下属性的配置对象
                - openai_api_key
                - openai_api_base
                - openai_model
        """
        self.config = config

    def _normalize_api_url(self) -> str:
        """标准化 API URL

        使用: self.config.openai_api_base
        """
        url = self.config.openai_api_base.strip()
        # 自动添加 https:// 和 /v1/chat/completions
        ...

    def chat(self, messages, temperature=0.7, max_tokens=4000, ...):
        """LLM 调用

        使用:
        - self.config.openai_api_key
        - self.config.openai_model
        """
        ...
```

### 6.2 Token Statistics

**文件**: `agentype/common/token_statistics.py`

```python
class TokenReporter:
    def __init__(self, language: str = "zh"):
        """
        Args:
            language: 从 global_config.project.language 传入
        """
        self.language = language

    def add_request(self, prompt_tokens, completion_tokens,
                   model_name, api_base):
        """记录 Token 使用

        Args:
            model_name: 从 config.openai_model 传入
            api_base: 从 config.openai_api_base 传入
        """
        # 根据 api_base 和 model_name 计算成本
        pricing = self.pricing_registry.get_pricing(model_name, api_base)
        ...
```

### 6.3 Unified Logger

**文件**: `agentype/config/unified_logger.py`

```python
from agentype.config import get_global_config

class UnifiedOutputLogger:
    def __init__(self, agent_name: str = "celltype_analysis", ...):
        # 使用全局配置的日志目录
        global_config = get_global_config()
        self.log_dir = global_config.get_logs_dir(agent_name)

        # 获取 session_id
        from ..mainagent.config.session_config import get_session_id
        session_id = get_session_id()

        # 生成日志文件名
        self.log_file = self.log_dir / f"{agent_name}_{session_id}.log"
```

---

## 📋 七、配置参数使用位置汇总表

### 7.1 LLM 配置参数

| 参数 | 定义位置 | 调用文件 | 调用方法 | 说明 |
|------|---------|---------|---------|------|
| `api_base` | `global_config.py:LLMConfig` | `common/llm_client.py` | `_normalize_api_url()` | 标准化 URL |
| `api_key` | `global_config.py:LLMConfig` | `common/llm_client.py` | `chat()` / `chat_stream()` | API 认证 |
| `model` | `global_config.py:LLMConfig` | `common/llm_client.py` | `__init__()` | 模型选择 |
| `temperature` | `global_config.py:LLMConfig` | `*/agent/*_react_agent.py` | `run()` | 控制随机性 |
| `max_tokens` | `global_config.py:LLMConfig` | `*/agent/*_react_agent.py` | `run()` | 限制输出长度 |

### 7.2 路径配置参数

| 路径类型 | 使用 Agent | 调用文件 | 用途 |
|---------|-----------|---------|------|
| `cache_dir` | 所有 | `*/config/cache_config.py` | 缓存管理 |
| `logs_dir` | 所有 | `config/unified_logger.py` | 统一日志 |
| `logs_dir` | 所有 | `common/llm_logger.py` | LLM 日志 |
| `results_dir` | MainAgent | `mainagent/tools/mapping_tools.py` | 保存映射结果 |
| `results_dir` | DataAgent | `dataagent/tools/save_marker_genes.py` | 保存 marker |
| `temp_dir` | DataAgent | `dataagent/tools/data_converters.py` | 临时转换 |
| `downloads_dir` | SubAgent | `subagent/tools/fetchers/*` | 数据库缓存 |

### 7.3 Project 配置参数

| 参数 | 使用位置 | 文件 | 说明 |
|------|---------|------|------|
| `language` | 所有 Agent | `*/config/prompts.py` | 提示词语言 |
| `language` | Token Reporter | `common/token_statistics.py` | 报告语言 |
| `enable_streaming` | 所有 Agent | `common/llm_client.py` | 流式输出 |
| `enable_logging` | 日志系统 | `config/unified_logger.py` | 日志开关 |
| `max_parallel_tasks` | MainAgent | `mainagent/config/settings.py` | 并行限制 |
| `cache_expiry_days` | Cache Manager | `*/config/cache_config.py` | 缓存过期 |
| `auto_cleanup` | Cache Manager | `*/config/cache_config.py` | 自动清理 |

### 7.4 Agent 配置参数

| 参数 | 使用位置 | 说明 |
|------|---------|------|
| `enabled` | `mainagent/tools/subagent_tools.py` | 控制子 Agent 启用 |
| `max_retries` | `*/agent/*_react_agent.py` | LLM 重试次数 |
| `log_level` | `config/unified_logger.py` | 日志级别 |

---

## 🎨 八、配置使用最佳实践

### 8.1 推荐的配置获取方式

```python
# ✅ 方式 1: 使用全局配置（推荐）
from agentype.config import get_global_config

global_config = get_global_config()
api_base = global_config.llm.api_base
api_key = global_config.llm.api_key
model = global_config.llm.model

# ✅ 方式 2: 使用便捷函数（推荐用于路径）
from agentype.config import (
    get_cache_dir,
    get_logs_dir,
    get_results_dir
)

cache_dir = get_cache_dir("your_agent_name")
logs_dir = get_logs_dir("your_agent_name")
results_dir = get_results_dir()

# ❌ 不推荐: 直接读取 JSON 文件
# with open("agentype_config.json") as f:
#     config = json.load(f)  # 不推荐，应使用全局配置管理器
```

### 8.2 配置文件管理原则

1. **只读原则**: 配置文件创建后保持只读状态
2. **单次写入**: 仅在配置文件不存在时创建并写入
3. **手动编辑**: 配置修改应通过手动编辑 JSON 文件
4. **环境变量**: 仅用于开发测试，生产环境使用配置文件

### 8.3 子 Agent 配置继承机制

```python
# MainAgent 启动时设置环境变量
os.environ["CELLTYPE_CONFIG_PATH"] = str(config_file_path)
os.environ["CELLTYPE_WORK_DIR"] = str(project_root)

# 子 Agent 自动从环境变量读取
external_config = _detect_external_config()  # 读取 CELLTYPE_CONFIG_PATH
# 所有子 Agent 共享同一个配置文件
```

### 8.4 配置验证建议

在使用配置前，建议进行验证：

```python
from agentype.config import get_global_config

global_config = get_global_config()

# 验证必要配置
assert global_config.llm.api_key, "API Key 未配置"
assert global_config.llm.api_base, "API Base URL 未配置"

# 验证路径存在
assert global_config.paths.outputs_dir.exists(), "输出目录不存在"
```

### 8.5 多环境配置管理

建议为不同环境创建不同的配置文件：

```bash
# 开发环境
agentype_config.dev.json

# 测试环境
agentype_config.test.json

# 生产环境
agentype_config.prod.json
```

通过环境变量指定使用哪个配置：

```bash
export CELLTYPE_CONFIG_FILE=agentype_config.prod.json
python your_script.py
```

---

## 📝 九、完整配置示例

### 9.1 生产环境配置示例

```json
{
  "version": "1.0.0",
  "updated_at": "2025-10-28T00:00:00.000000",

  "paths": {
    "project_root": "/path/to/your/project",
    "outputs_dir": "/path/to/your/project/outputs",
    "cache_dir": "/path/to/your/project/outputs/cache",
    "logs_dir": "/path/to/your/project/outputs/logs",
    "results_dir": "/path/to/your/project/outputs/results",
    "downloads_dir": "/path/to/your/project/outputs/downloads",
    "temp_dir": "/path/to/your/project/outputs/temp"
  },

  "llm": {
    "api_base": "https://api.siliconflow.cn/v1",
    "api_key": "sk-your-production-api-key-here",
    "model": "Pro/deepseek-ai/DeepSeek-V3",
    "max_tokens": 4000,
    "temperature": 0.3
  },

  "project": {
    "language": "zh",
    "enable_streaming": true,
    "enable_logging": true,
    "max_parallel_tasks": 3,
    "cache_expiry_days": 30,
    "auto_cleanup": true
  },

  "agents": {
    "celltypeMainagent": {
      "enabled": true,
      "max_retries": 3,
      "log_level": "INFO"
    },
    "celltypeSubagent": {
      "enabled": true,
      "max_retries": 3,
      "log_level": "INFO"
    },
    "celltypeDataAgent": {
      "enabled": true,
      "max_retries": 3,
      "log_level": "INFO"
    },
    "celltypeAppAgent": {
      "enabled": true,
      "max_retries": 3,
      "log_level": "INFO"
    }
  }
}
```

### 9.2 开发环境配置示例

```json
{
  "version": "1.0.0",
  "updated_at": "2025-10-28T00:00:00.000000",

  "paths": {
    "project_root": "/home/user/dev/celltype-mcp-server",
    "outputs_dir": "/home/user/dev/celltype-mcp-server/outputs",
    "cache_dir": "/home/user/dev/celltype-mcp-server/outputs/cache",
    "logs_dir": "/home/user/dev/celltype-mcp-server/outputs/logs",
    "results_dir": "/home/user/dev/celltype-mcp-server/outputs/results",
    "downloads_dir": "/home/user/dev/celltype-mcp-server/outputs/downloads",
    "temp_dir": "/home/user/dev/celltype-mcp-server/outputs/temp"
  },

  "llm": {
    "api_base": "https://api.openai.com/v1",
    "api_key": "sk-your-dev-api-key-here",
    "model": "gpt-4",
    "max_tokens": 4000,
    "temperature": 0.5
  },

  "project": {
    "language": "zh",
    "enable_streaming": true,
    "enable_logging": true,
    "max_parallel_tasks": 2,
    "cache_expiry_days": 7,
    "auto_cleanup": false
  },

  "agents": {
    "celltypeMainagent": {
      "enabled": true,
      "max_retries": 5,
      "log_level": "DEBUG"
    },
    "celltypeSubagent": {
      "enabled": true,
      "max_retries": 5,
      "log_level": "DEBUG"
    },
    "celltypeDataAgent": {
      "enabled": true,
      "max_retries": 5,
      "log_level": "DEBUG"
    },
    "celltypeAppAgent": {
      "enabled": true,
      "max_retries": 5,
      "log_level": "DEBUG"
    }
  }
}
```

---

## 🎯 十、总结

### 10.1 配置系统架构特点

1. **分层设计**: 全局配置 → Agent 配置 → 工具配置
2. **单例模式**: 全局配置管理器确保配置一致性
3. **只读原则**: 配置文件创建后只读，修改需手动编辑
4. **自动继承**: 子 Agent 通过环境变量自动继承主配置
5. **灵活扩展**: 各 Agent 可添加特有配置，共享核心配置

### 10.2 核心调用路径

```
agentype_config.json
    ↓
GlobalConfigManager (单例)
    ↓
    ├─→ LLM 配置 → LLMClient → 所有 Agent
    ├─→ 路径配置 → 缓存/日志/结果/临时目录
    ├─→ Project 配置 → 语言/流式输出/日志开关
    └─→ Agent 配置 → 启用状态/重试次数/日志级别
```

### 10.3 配置系统优势

1. **统一管理**: 所有配置集中在一个 JSON 文件中
2. **类型安全**: 使用 dataclass 提供类型检查
3. **验证机制**: 自动验证配置完整性
4. **环境隔离**: 支持多环境配置
5. **易于调试**: 清晰的配置加载日志

### 10.4 最佳实践总结

| 场景 | 推荐做法 |
|------|---------|
| 获取配置 | 使用 `get_global_config()` |
| 获取路径 | 使用便捷函数如 `get_cache_dir()` |
| 修改配置 | 手动编辑 JSON 文件 |
| 开发调试 | 使用环境变量临时覆盖 |
| 生产部署 | 使用配置文件，避免环境变量 |

### 10.5 常见问题

**Q: 如何修改配置？**
A: 直接编辑 `agentype_config.json` 文件，重启应用即可生效。

**Q: 环境变量和配置文件冲突时，哪个优先？**
A: 配置文件优先。环境变量仅用于指定配置文件路径。

**Q: 子 Agent 如何继承主配置？**
A: 通过 `CELLTYPE_CONFIG_PATH` 环境变量自动继承。

**Q: 如何为不同环境使用不同配置？**
A: 创建多个配置文件，通过 `CELLTYPE_CONFIG_FILE` 环境变量指定。

**Q: 配置文件被意外修改怎么办？**
A: 配置系统采用只读策略，一旦创建只会读取不会写入。

---

## 📚 附录

### A. 配置相关文件清单

```
agentype/
├── config/
│   ├── global_config.py          # 全局配置管理器（核心）
│   ├── paths_config.py            # 路径配置
│   ├── unified_logger.py          # 统一日志
│   └── __init__.py                # 导出接口
├── mainagent/config/
│   ├── settings.py                # MainAgent 配置
│   ├── cache_config.py            # 缓存配置
│   ├── session_config.py          # Session 配置
│   └── prompts.py                 # 提示词
├── subagent/config/
│   ├── settings.py                # SubAgent 配置
│   ├── cache_config.py            # 缓存配置
│   └── prompts.py                 # 提示词
├── dataagent/config/
│   ├── settings.py                # DataAgent 配置
│   ├── cache_config.py            # 缓存配置
│   └── prompts.py                 # 提示词
└── appagent/config/
    ├── settings.py                # AppAgent 配置
    ├── cache_config.py            # 缓存配置
    └── prompts.py                 # 提示词
```

### B. 配置相关 API

```python
# 全局配置
from agentype.config import (
    get_global_config,           # 获取全局配置实例
    check_and_update_config,     # 检查并更新配置
)

# 路径配置
from agentype.config import (
    get_paths,                   # 获取所有路径配置
    get_cache_dir,               # 获取缓存目录
    get_logs_dir,                # 获取日志目录
    get_results_dir,             # 获取结果目录
    get_downloads_dir,           # 获取下载目录
    get_temp_dir,                # 获取临时目录
)

# Session 配置
from agentype.mainagent.config.session_config import (
    get_session_id,              # 获取当前 session ID
    set_session_id,              # 设置 session ID
)
```

### C. 相关文档

- [项目 README](../README.md)
- [安装指南](../INSTALL.md)
- [API 文档](../docs/)
- [开发指南](../docs/development/)

---

**文档维护**: 本文档应随配置系统更新而更新
**反馈渠道**: 如有疑问或建议，请提交 Issue
**版本历史**: 见 Git 提交记录
