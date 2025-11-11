# Token统计和定价计算系统详解

> **Author**: cuilei
> **Version**: 1.0
> **Last Updated**: 2025-01-25

---

## 📋 目录

- [1. 系统概述](#1-系统概述)
- [2. 核心组件](#2-核心组件)
- [3. 定价系统](#3-定价系统)
- [4. 统计收集机制](#4-统计收集机制)
- [5. 使用示例](#5-使用示例)
- [6. 技术亮点](#6-技术亮点)
- [7. 最佳实践](#7-最佳实践)

---

## 1. 系统概述

### 1.1 设计目标

CellType Agent 的 Token 统计和定价计算系统旨在解决以下核心问题:

- ✅ **跨进程统计**: 在 MCP (Model Context Protocol) 架构下,多个 Agent 运行在不同进程中,需要统一收集 token 使用数据
- ✅ **多货币定价**: 支持不同 API 提供商的定价策略 (人民币/美元, 百万tokens/千tokens)
- ✅ **成本透明**: 为用户提供清晰的成本估算和使用报告
- ✅ **易于扩展**: 便于添加新的模型和定价配置

### 1.2 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Token 统计系统                          │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  MainAgent   │  │  SubAgent    │  │  DataAgent   │      │
│  │              │  │              │  │              │      │
│  │ LLMClient ───┼──┼─ LLMClient ──┼──┼─ LLMClient ──┼──┐   │
│  │              │  │              │  │              │  │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │   │
│         │                 │                 │          │   │
│         │  记录到日志      │                 │          │   │
│         ▼                 ▼                 ▼          ▼   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         LLM 日志文件 (JSONL 格式)                     │  │
│  │  - llm/main_agent/llm_requests_session_{id}.jsonl   │  │
│  │  - llm/sub_agent/llm_requests_session_{id}.jsonl    │  │
│  │  - llm/data_agent/llm_requests_session_{id}.jsonl   │  │
│  │  - llm/app_agent/llm_requests_session_{id}.jsonl    │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         │ 解析                               │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           LogTokenParser (日志解析器)                 │  │
│  │  - 按 session_id 查找日志文件                         │  │
│  │  - 提取 usage 数据                                    │  │
│  │  - 提取 api_base 和 model_name                        │  │
│  │  - 生成 TokenStatistics 对象                         │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         │ 汇总                               │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         PricingRegistry (定价注册表)                  │  │
│  │  - SiliconFlow API 定价 (CNY/百万tokens)             │  │
│  │  - DeepSeek API 定价 (CNY/百万tokens)                │  │
│  │  - OpenAI API 定价 (USD/千tokens)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│                         │                                    │
│                         │ 计算成本                            │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         TokenReporter (报告生成器)                    │  │
│  │  - 简要报告 (single line)                             │  │
│  │  - 详细报告 (multi-agent breakdown)                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 模块位置

所有核心模块位于 `agentype/common/` 目录下:

```
agentype/common/
├── __init__.py
├── llm_client.py           # 统一 LLM 客户端 (集成 token 统计)
├── token_statistics.py     # Token 统计数据类、定价注册表、报告生成器
└── log_token_parser.py     # 日志解析器 (从 JSONL 文件提取统计)
```

---

## 2. 核心组件

### 2.1 TokenStatistics 类

**文件**: `agentype/common/token_statistics.py`

```python
@dataclass
class TokenStatistics:
    """Token统计数据类"""

    # 基础统计
    prompt_tokens: int = 0           # 输入 token 数
    completion_tokens: int = 0       # 输出 token 数
    total_tokens: int = 0            # 总 token 数
    request_count: int = 0           # API 请求次数

    # 元数据
    model_name: str = ""             # 模型名称
    agent_name: str = ""             # Agent 名称
    api_base: Optional[str] = None   # API 基础 URL (从日志中提取)
    start_time: Optional[str] = None # 开始时间
    last_updated: Optional[str] = None # 最后更新时间
```

#### 核心方法

| 方法 | 功能 | 返回值 |
|------|------|--------|
| `add_usage(usage_data)` | 添加一次 API 调用的 token 使用统计 | None |
| `get_estimated_cost(api_base)` | 估算成本 (支持多货币) | `(成本, 货币单位)` |
| `get_efficiency_score()` | 计算效率分数 (completion/total) | `0.0-1.0` |
| `get_summary(include_cost, api_base)` | 获取统计摘要 | `Dict` |
| `merge(other)` | 合并两个统计对象 | `TokenStatistics` |
| `to_dict()` / `to_json()` | 序列化 | `Dict` / `str` |

#### 使用示例

```python
from agentype.common.token_statistics import TokenStatistics

# 创建统计对象
stats = TokenStatistics(agent_name="MainAgent", model_name="deepseek-chat")

# 添加 API 调用的 usage 数据
usage_data = {
    "prompt_tokens": 1500,
    "completion_tokens": 500,
    "total_tokens": 2000
}
stats.add_usage(usage_data)

# 获取成本估算 (自动根据 api_base 和 model_name 选择定价)
cost, currency = stats.get_estimated_cost(api_base="https://api.deepseek.com")
print(f"成本: {currency} {cost:.4f}")  # 输出: 成本: CNY 0.0015

# 获取摘要
summary = stats.get_summary(include_cost=True)
print(summary)
# {
#   "agent_name": "MainAgent",
#   "total_tokens": 2000,
#   "estimated_cost": 0.0015,
#   "currency": "CNY",
#   ...
# }
```

---

### 2.2 PricingRegistry 类

**文件**: `agentype/common/token_statistics.py`

```python
class PricingRegistry:
    """模型定价注册表

    管理所有API的模型定价信息，支持根据api_base和model_name查询定价。
    """
```

#### 定价数据结构

```python
@dataclass
class ModelPricing:
    """模型定价信息"""
    prompt_price: float          # 输入token价格
    completion_price: float      # 输出token价格
    currency: str                # 货币单位：'CNY' 或 'USD'
    price_per_million: bool = True  # True: 按百万tokens计价, False: 按千tokens计价
```

#### 核心方法

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `get_pricing(model_name, api_base)` | 获取模型定价 | model_name, api_base | `ModelPricing` |
| `calculate_cost(prompt_tokens, completion_tokens, model_name, api_base)` | 计算成本 | tokens, model, api | `(成本, 货币)` |

#### 使用示例

```python
from agentype.common.token_statistics import _pricing_registry

# 查询定价
pricing = _pricing_registry.get_pricing(
    model_name="Pro/deepseek-ai/DeepSeek-V3",
    api_base="https://api.siliconflow.cn/v1"
)
print(pricing)
# ModelPricing(prompt_price=2.0, completion_price=8.0, currency='CNY', price_per_million=True)

# 计算成本
cost, currency = _pricing_registry.calculate_cost(
    prompt_tokens=1_000_000,   # 100万输入tokens
    completion_tokens=500_000,  # 50万输出tokens
    model_name="Pro/deepseek-ai/DeepSeek-V3",
    api_base="https://api.siliconflow.cn/v1"
)
print(f"{currency} {cost}")  # CNY 6.0 (2.0 + 4.0)
```

---

### 2.3 TokenReporter 类

**文件**: `agentype/common/token_statistics.py`

```python
class TokenReporter:
    """Token统计报告生成器"""

    def __init__(self, language: str = "zh"):
        """初始化报告生成器 (支持中英文)"""
        self.language = language
```

#### 核心方法

| 方法 | 功能 | 返回值 |
|------|------|--------|
| `generate_simple_report(stats, api_base)` | 生成简洁的单行报告 | `str` |
| `generate_detailed_report(total_stats, agent_stats, api_base)` | 生成详细的多 Agent 报告 | `str` |

#### 报告示例

**简要报告**:
```
📊 Token消耗: 125,430 tokens (估算成本: ¥0.3514) | 15次请求 | 效率: 32.5%
```

**详细报告**:
```markdown
### 📊 Token消耗统计

**总消耗**: 125,430 tokens (预估成本: ¥0.3514)

**分Agent统计**:
- SubAgent: 45,200 tokens (5次请求)
- DataAgent: 32,100 tokens (4次请求)
- AppAgent: 28,800 tokens (3次请求)

**效率指标**: 输出效率 32.5%
Token使用效率良好
```

---

### 2.4 LogTokenParser 类

**文件**: `agentype/common/log_token_parser.py`

```python
class LogTokenParser:
    """LLM 日志 Token 统计解析器

    从保存在文件系统中的 JSONL 格式日志文件中解析 token 使用统计。
    解决 MCP 架构下跨进程的统计收集问题。
    """
```

#### 日志文件格式

日志文件为 JSONL (JSON Lines) 格式,每行一条记录:

```jsonl
{"timestamp": "2025-01-25T10:30:45", "request": {"url": "https://api.deepseek.com/chat/completions", ...}, "response": "...", "success": true, "extra_info": {"usage": {"prompt_tokens": 1500, "completion_tokens": 500, "total_tokens": 2000}, "model_used": "deepseek-chat"}}
```

#### 日志文件命名规范

```
outputs/logs/llm/{agent_dir}/llm_requests_session_{session_id}.jsonl
```

例如:
- `outputs/logs/llm/main_agent/llm_requests_session_20250125_103045_abc123.jsonl`
- `outputs/logs/llm/sub_agent/llm_requests_session_20250125_103045_abc123.jsonl`

#### 核心方法

| 方法 | 功能 | 参数 | 返回值 |
|------|------|------|--------|
| `parse_agent_logs(agent_name, session_id)` | 解析单个 Agent 的日志 | agent_name, session_id | `TokenStatistics` |
| `parse_all_agents(session_id, include_agents)` | 解析所有 Agent 的日志 | session_id, agents | `Dict[str, TokenStatistics]` |
| `get_log_file_info(session_id)` | 获取日志文件信息 (调试) | session_id | `Dict` |

#### 使用示例

```python
from agentype.common.log_token_parser import LogTokenParser

# 初始化解析器
parser = LogTokenParser(log_base_dir="/app/data/outputs/logs/llm")

# 解析单个 Agent
stats = parser.parse_agent_logs(
    agent_name="SubAgent",
    session_id="20250125_103045_abc123"
)
print(f"SubAgent 消耗: {stats.total_tokens} tokens")

# 解析所有 Agent
all_stats = parser.parse_all_agents(
    session_id="20250125_103045_abc123",
    include_agents=["MainAgent", "SubAgent", "DataAgent", "AppAgent"]
)

for agent_name, stats in all_stats.items():
    print(f"{agent_name}: {stats.total_tokens} tokens")
```

---

### 2.5 LLMClient 中的 Token 统计集成

**文件**: `agentype/common/llm_client.py`

`LLMClient` 是统一的 LLM API 客户端,在每次 API 调用时自动记录 token 使用数据到日志文件。

```python
class LLMClient:
    """统一的 LLM API 客户端

    特性:
    - 支持流式和非流式调用
    - 完整支持 DeepSeek Reasoner 的 reasoning_content
    - 统一的日志记录接口 (通过回调函数)
    - 统一的 token 统计接口
    - 自动错误处理和重试逻辑 (最多3次)
    """
```

#### Token 统计流程

```python
async def call_api(
    self,
    messages: List[Dict],
    timeout: int = 270,
    stream: bool = False,
    request_type: str = "main",
    token_stats = None,        # 可选的 TokenStatistics 对象 (实时统计)
    llm_logger = None,         # 必需的 LLMLogger 对象 (日志记录)
    console_logger = None
) -> str:
    # ... API 调用逻辑 ...

    # 提取 usage 数据
    usage_data = data.get("usage", {})

    # 1️⃣ 实时统计 (可选, 目前未使用)
    if usage_data and token_stats:
        token_stats.add_usage(usage_data)

    # 2️⃣ 记录到日志文件 (主要方式)
    if llm_logger:
        extra_info = {
            "usage": usage_data,           # ⭐ 关键: 将 usage 保存到日志
            "model_used": data.get("model"),
            "reasoning_content": reasoning_content,
            "reasoning_length": len(reasoning_content)
        }

        llm_logger.log_request_response(
            request_type=request_type,
            request_data=request_data,
            response_data=content,
            success=True,
            extra_info=extra_info         # ⭐ 包含 usage 的额外信息
        )

    return content
```

**关键点**:
- ✅ 每次 LLM 调用都会将 `usage_data` 记录到 JSONL 日志文件的 `extra_info.usage` 字段
- ✅ 日志文件按 `session_id` 命名,确保同一次会话的所有调用都记录在同一个文件中
- ✅ `LogTokenParser` 从日志文件中提取 `usage` 数据,汇总生成 `TokenStatistics`

---

## 3. 定价系统

### 3.1 支持的 API 和模型定价

#### 3.1.1 SiliconFlow API

**API Base**: `https://api.siliconflow.cn/v1`
**货币**: 人民币 (CNY)
**计价单位**: 百万 tokens

| 模型名称 | 输入价格 (¥/百万tokens) | 输出价格 (¥/百万tokens) |
|---------|------------------------|------------------------|
| `Pro/deepseek-ai/DeepSeek-V3` | 2.0 | 8.0 |
| `deepseek-ai/DeepSeek-V3` | 2.0 | 8.0 |
| `Pro/deepseek-ai/DeepSeek-R1` | 4.0 | 16.0 |
| `deepseek-ai/DeepSeek-R1` | 4.0 | 16.0 |
| `Pro/deepseek-ai/DeepSeek-V3.1-Terminus` | 4.0 | 12.0 |
| `deepseek-ai/DeepSeek-V3.1-Terminus` | 4.0 | 12.0 |
| `Pro/deepseek-ai/DeepSeek-V3.2-Exp` | 2.0 | 3.0 |
| `deepseek-ai/DeepSeek-V3.2-Exp` | 2.0 | 3.0 |

#### 3.1.2 DeepSeek API

**API Base**: `https://api.deepseek.com`
**货币**: 人民币 (CNY)
**计价单位**: 百万 tokens

| 模型名称 | 输入价格 (¥/百万tokens) | 输出价格 (¥/百万tokens) |
|---------|------------------------|------------------------|
| `deepseek-chat` | 2.0 | 3.0 |
| `deepseek-reasoner` | 2.0 | 3.0 |

#### 3.1.3 OpenAI API (默认定价)

**API Base**: `https://api.openai.com/v1`
**货币**: 美元 (USD)
**计价单位**: 千 tokens

| 模型名称 | 输入价格 ($/千tokens) | 输出价格 ($/千tokens) |
|---------|---------------------|---------------------|
| `gpt-4` | 0.03 | 0.06 |
| `gpt-4o` | 0.03 | 0.06 |
| `gpt-3.5` | 0.001 | 0.002 |
| `gpt-3.5-turbo` | 0.001 | 0.002 |

### 3.2 定价查询算法

```python
def get_pricing(self, model_name: str, api_base: Optional[str] = None) -> Optional[ModelPricing]:
    """获取模型定价 - 三层查询策略"""

    # 1️⃣ 第一层: 如果提供了 api_base, 使用模糊匹配查找 API 特定定价
    if api_base:
        for registered_url, api_pricing in self._pricing_map.items():
            if registered_url in api_base or api_base.startswith(registered_url):
                # 在该 API 的定价表中查找模型
                if model_name in api_pricing:
                    return api_pricing[model_name]

    # 2️⃣ 第二层: 在默认定价中查找 (按模型名称的关键字匹配)
    model_lower = model_name.lower()
    for key, pricing in self._default_pricing.items():
        if key in model_lower:
            return pricing

    # 3️⃣ 第三层: 如果都找不到, 返回默认的 GPT-4 定价 (兜底策略)
    return ModelPricing(0.03, 0.06, "USD", False)
```

**匹配优先级**:
1. **精确匹配**: `api_base` + `model_name` 完全匹配
2. **关键字匹配**: 模型名称包含默认定价表中的关键字
3. **兜底定价**: GPT-4 定价 (避免返回 None)

### 3.3 成本计算方法

```python
def calculate_cost(
    self,
    prompt_tokens: int,
    completion_tokens: int,
    model_name: str,
    api_base: Optional[str] = None
) -> Tuple[float, str]:
    """计算成本 - 支持多货币和多计价单位"""

    # 获取定价
    pricing = self.get_pricing(model_name, api_base)

    # 根据计价单位计算
    if pricing.price_per_million:
        # 按百万 tokens 计价
        prompt_cost = (prompt_tokens / 1_000_000) * pricing.prompt_price
        completion_cost = (completion_tokens / 1_000_000) * pricing.completion_price
    else:
        # 按千 tokens 计价
        prompt_cost = (prompt_tokens / 1000) * pricing.prompt_price
        completion_cost = (completion_tokens / 1000) * pricing.completion_price

    total_cost = prompt_cost + completion_cost
    return (total_cost, pricing.currency)
```

**计算示例**:

```python
# 示例 1: DeepSeek-V3 (CNY, 百万tokens)
cost, currency = calculate_cost(
    prompt_tokens=1_500_000,     # 150万输入tokens
    completion_tokens=500_000,   # 50万输出tokens
    model_name="Pro/deepseek-ai/DeepSeek-V3",
    api_base="https://api.siliconflow.cn/v1"
)
# 计算: (1.5 * 2.0) + (0.5 * 8.0) = 3.0 + 4.0 = ¥7.0

# 示例 2: GPT-4 (USD, 千tokens)
cost, currency = calculate_cost(
    prompt_tokens=10_000,   # 1万输入tokens
    completion_tokens=5_000, # 5千输出tokens
    model_name="gpt-4",
    api_base="https://api.openai.com/v1"
)
# 计算: (10 * 0.03) + (5 * 0.06) = 0.3 + 0.3 = $0.6
```

---

## 4. 统计收集机制

### 4.1 统计收集流程

```
┌─────────────────────────────────────────────────────────────┐
│               Token 统计收集完整流程                          │
└─────────────────────────────────────────────────────────────┘

1️⃣ API 调用阶段
   ┌──────────────┐
   │  MainAgent   │
   │  调用 LLM    │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────────────────────────┐
   │  LLMClient.call_api()                │
   │  - 发送请求到 LLM API                │
   │  - 接收响应 (包含 usage_data)        │
   └──────┬───────────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────────┐
   │  LLMLogger.log_request_response()    │
   │  - 将 usage_data 写入日志文件        │
   │    extra_info: {                     │
   │      usage: {                        │
   │        prompt_tokens: 1500,          │
   │        completion_tokens: 500,       │
   │        total_tokens: 2000            │
   │      },                               │
   │      model_used: "deepseek-chat"     │
   │    }                                  │
   └──────┬───────────────────────────────┘
          │
          ▼
   📁 logs/llm/main_agent/llm_requests_session_{id}.jsonl
   (日志文件累积记录)

2️⃣ 子 Agent 调用阶段
   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
   │  SubAgent    │     │  DataAgent   │     │  AppAgent    │
   │  调用 LLM    │     │  调用 LLM    │     │  调用 LLM    │
   └──────┬───────┘     └──────┬───────┘     └──────┬───────┘
          │                    │                    │
          │  (同样通过 LLMClient 和 LLMLogger)      │
          │                    │                    │
          ▼                    ▼                    ▼
   📁 sub_agent/*.jsonl  📁 data_agent/*.jsonl  📁 app_agent/*.jsonl

3️⃣ 统计收集阶段 (任务完成时)
   ┌──────────────────────────────────────┐
   │  MainAgent._collect_all_token_stats()│
   │  - 获取当前 session_id               │
   │  - 初始化 LogTokenParser             │
   └──────┬───────────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────────┐
   │  LogTokenParser.parse_all_agents()   │
   │  - 查找所有 Agent 的日志文件         │
   │  - 逐行解析 JSONL                    │
   │  - 提取 usage_data                   │
   │  - 提取 api_base, model_name         │
   └──────┬───────────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────────┐
   │  生成 TokenStatistics 对象 (每个 Agent)│
   │  - MainAgent: TokenStatistics        │
   │  - SubAgent: TokenStatistics         │
   │  - DataAgent: TokenStatistics        │
   │  - AppAgent: TokenStatistics         │
   └──────┬───────────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────────┐
   │  merge_token_stats()                 │
   │  - 合并所有 Agent 的统计             │
   │  - 生成总统计对象                    │
   └──────┬───────────────────────────────┘
          │
          ▼
   ┌──────────────────────────────────────┐
   │  TokenReporter.generate_report()     │
   │  - 简要报告                          │
   │  - 详细报告 (分 Agent)               │
   └──────┬───────────────────────────────┘
          │
          ▼
   📊 最终输出到用户
```

### 4.2 Session ID 传递机制

为了确保所有 Agent 的日志文件使用相同的 session_id,系统实现了跨进程的 session_id 传递:

```python
# 1️⃣ MainAgent 生成 session_id
from agentype.mainagent.config.session_config import generate_session_id, set_session_id

session_id = generate_session_id()  # 例如: "20250125_103045_abc123"
set_session_id(session_id)

# 2️⃣ MainAgent 调用子 Agent 时传递 session_id
from agentype.subagent.agent.celltype_react_agent import CellTypeReactAgent

sub_agent = CellTypeReactAgent(
    config=config,
    session_id=session_id  # ⭐ 传递 session_id
)

# 3️⃣ 子 Agent 接收并设置 session_id
# (在 SubAgent/DataAgent/AppAgent 的 __init__ 中)
if session_id:
    from agentype.mainagent.config.session_config import set_session_id
    set_session_id(session_id)
    print(f"✅ SubAgent使用传入的session_id: {session_id}")

# 4️⃣ 所有 Agent 的日志文件使用相同的 session_id 命名
# - logs/llm/main_agent/llm_requests_session_20250125_103045_abc123.jsonl
# - logs/llm/sub_agent/llm_requests_session_20250125_103045_abc123.jsonl
# - logs/llm/data_agent/llm_requests_session_20250125_103045_abc123.jsonl
# - logs/llm/app_agent/llm_requests_session_20250125_103045_abc123.jsonl
```

### 4.3 多 Agent 统计汇总

```python
async def _collect_all_token_stats(self) -> Dict[str, Any]:
    """收集所有Agent的token统计信息"""

    # 1️⃣ 获取当前 session_id
    from agentype.mainagent.config.session_config import get_session_id
    current_session_id = get_session_id()

    # 2️⃣ 初始化日志解析器
    log_parser = LogTokenParser(log_base_dir="/app/data/outputs/logs/llm")

    # 3️⃣ 解析每个 Agent 的日志
    agents_to_query = ["MainAgent", "SubAgent", "DataAgent", "AppAgent"]
    all_agent_stats = {}

    for agent_name in agents_to_query:
        stats = log_parser.parse_agent_logs(agent_name, current_session_id)
        all_agent_stats[agent_name] = stats

    # 4️⃣ 分离 MainAgent 和子 Agent
    main_agent_stats = all_agent_stats.get("MainAgent")
    sub_agent_stats = {k: v for k, v in all_agent_stats.items() if k != "MainAgent"}

    # 5️⃣ 合并所有 token 统计
    total_stats = merge_token_stats(list(all_agent_stats.values()))
    total_stats.agent_name = "Total"

    # 6️⃣ 生成报告
    simple_report = self.token_reporter.generate_simple_report(total_stats)
    detailed_report = self.token_reporter.generate_detailed_report(total_stats, sub_agent_stats)

    # 7️⃣ 返回完整统计
    return {
        "main_agent": main_agent_stats.get_summary(),
        "sub_agents": {name: stats.get_summary() for name, stats in sub_agent_stats.items()},
        "total": total_stats.get_summary(),
        "simple_report": simple_report,
        "detailed_report": detailed_report
    }
```

---

## 5. 使用示例

### 5.1 基础使用: 创建和更新统计

```python
from agentype.common.token_statistics import TokenStatistics

# 创建统计对象
stats = TokenStatistics(
    agent_name="MainAgent",
    model_name="deepseek-chat",
    api_base="https://api.deepseek.com"
)

# 模拟多次 API 调用
for i in range(3):
    usage_data = {
        "prompt_tokens": 1000 + i * 100,
        "completion_tokens": 500 + i * 50,
        "total_tokens": 1500 + i * 150
    }
    stats.add_usage(usage_data)

# 查看统计结果
print(f"总请求: {stats.request_count}")           # 3
print(f"总 tokens: {stats.total_tokens}")         # 5100
print(f"输入 tokens: {stats.prompt_tokens}")      # 3300
print(f"输出 tokens: {stats.completion_tokens}")  # 1800

# 计算成本
cost, currency = stats.get_estimated_cost()
print(f"估算成本: {currency} {cost:.4f}")  # CNY 0.0102
```

### 5.2 日志解析: 从文件中提取统计

```python
from agentype.common.log_token_parser import LogTokenParser

# 初始化解析器
parser = LogTokenParser(log_base_dir="/app/data/outputs/logs/llm")

# 解析单个 Agent 的日志
stats = parser.parse_agent_logs(
    agent_name="SubAgent",
    session_id="20250125_103045_abc123"
)

print(f"SubAgent 统计:")
print(f"  - 总 tokens: {stats.total_tokens}")
print(f"  - 请求次数: {stats.request_count}")
print(f"  - 模型: {stats.model_name}")
print(f"  - API: {stats.api_base}")

# 解析所有 Agent
all_stats = parser.parse_all_agents(session_id="20250125_103045_abc123")

for agent_name, stats in all_stats.items():
    if stats.total_tokens > 0:
        print(f"{agent_name}: {stats.total_tokens:,} tokens")
```

### 5.3 报告生成: 创建用户友好的报告

```python
from agentype.common.token_statistics import TokenStatistics, TokenReporter, merge_token_stats

# 创建多个 Agent 的统计
main_stats = TokenStatistics(agent_name="MainAgent", total_tokens=50000, request_count=5)
sub_stats = TokenStatistics(agent_name="SubAgent", total_tokens=30000, request_count=3)
data_stats = TokenStatistics(agent_name="DataAgent", total_tokens=20000, request_count=2)

# 合并统计
total_stats = merge_token_stats([main_stats, sub_stats, data_stats])
total_stats.agent_name = "Total"
total_stats.model_name = "deepseek-chat"
total_stats.api_base = "https://api.deepseek.com"

# 生成报告
reporter = TokenReporter(language="zh")

# 简要报告
simple = reporter.generate_simple_report(total_stats)
print(simple)
# 📊 Token消耗: 100,000 tokens (估算成本: ¥0.2000) | 10次请求 | 效率: 30.0%

# 详细报告
agent_stats = {"SubAgent": sub_stats, "DataAgent": data_stats}
detailed = reporter.generate_detailed_report(total_stats, agent_stats)
print(detailed)
# ### 📊 Token消耗统计
# **总消耗**: 100,000 tokens (预估成本: ¥0.2000)
# **分Agent统计**:
# - SubAgent: 30,000 tokens (3次请求)
# - DataAgent: 20,000 tokens (2次请求)
# ...
```

### 5.4 成本估算: 不同模型和 API

```python
from agentype.common.token_statistics import _pricing_registry

# 示例 1: SiliconFlow DeepSeek-V3
cost1, currency1 = _pricing_registry.calculate_cost(
    prompt_tokens=2_000_000,
    completion_tokens=1_000_000,
    model_name="Pro/deepseek-ai/DeepSeek-V3",
    api_base="https://api.siliconflow.cn/v1"
)
print(f"{currency1} {cost1:.4f}")  # CNY 12.0000

# 示例 2: DeepSeek API
cost2, currency2 = _pricing_registry.calculate_cost(
    prompt_tokens=1_000_000,
    completion_tokens=500_000,
    model_name="deepseek-reasoner",
    api_base="https://api.deepseek.com"
)
print(f"{currency2} {cost2:.4f}")  # CNY 3.5000

# 示例 3: OpenAI GPT-4
cost3, currency3 = _pricing_registry.calculate_cost(
    prompt_tokens=50_000,
    completion_tokens=25_000,
    model_name="gpt-4",
    api_base="https://api.openai.com/v1"
)
print(f"{currency3} {cost3:.4f}")  # USD 3.0000
```

### 5.5 完整工作流示例

```python
from agentype.common.token_statistics import TokenStatistics, TokenReporter
from agentype.common.log_token_parser import LogTokenParser

async def analyze_token_usage(session_id: str):
    """分析指定会话的 token 使用情况"""

    # 1️⃣ 初始化解析器
    parser = LogTokenParser(log_base_dir="/app/data/outputs/logs/llm")

    # 2️⃣ 解析所有 Agent 的日志
    all_stats = parser.parse_all_agents(session_id=session_id)

    # 3️⃣ 打印每个 Agent 的统计
    print("\n=== Agent 统计 ===")
    for agent_name, stats in all_stats.items():
        if stats.total_tokens > 0:
            cost, currency = stats.get_estimated_cost()
            print(f"{agent_name}:")
            print(f"  Tokens: {stats.total_tokens:,}")
            print(f"  Requests: {stats.request_count}")
            print(f"  Cost: {currency} {cost:.4f}")

    # 4️⃣ 合并统计
    from agentype.common.token_statistics import merge_token_stats
    total_stats = merge_token_stats(list(all_stats.values()))
    total_stats.agent_name = "Total"

    # 5️⃣ 生成报告
    reporter = TokenReporter(language="zh")

    print("\n=== 简要报告 ===")
    print(reporter.generate_simple_report(total_stats))

    print("\n=== 详细报告 ===")
    sub_agents = {k: v for k, v in all_stats.items() if k != "MainAgent"}
    print(reporter.generate_detailed_report(total_stats, sub_agents))

    # 6️⃣ 返回完整统计
    return {
        "session_id": session_id,
        "total_tokens": total_stats.total_tokens,
        "total_cost": total_stats.get_estimated_cost()[0],
        "currency": total_stats.get_estimated_cost()[1],
        "agents": {name: stats.to_dict() for name, stats in all_stats.items()}
    }

# 使用示例
result = await analyze_token_usage("20250125_103045_abc123")
print(f"\n总消耗: {result['total_tokens']:,} tokens")
print(f"总成本: {result['currency']} {result['total_cost']:.4f}")
```

---

## 6. 技术亮点

### 6.1 跨进程统计收集

**问题**: MCP 架构下,每个 Agent 运行在独立的进程中,内存中的统计对象无法共享。

**解决方案**:
- ✅ 所有 LLM 调用都通过 `LLMLogger` 记录到文件系统 (JSONL 格式)
- ✅ 使用统一的 `session_id` 标识同一次分析任务
- ✅ `LogTokenParser` 在任务结束时解析所有日志文件,汇总统计

**优势**:
- 🎯 **可靠性**: 即使 Agent 进程崩溃,日志文件依然保留
- 🎯 **可追溯**: 每次调用都有完整的日志记录,便于调试
- 🎯 **灵活性**: 可以事后分析任意历史会话的 token 使用

### 6.2 多货币和多计价单位支持

**问题**: 不同 API 提供商使用不同的货币 (CNY/USD) 和计价单位 (百万tokens/千tokens)。

**解决方案**:
- ✅ `ModelPricing` 数据类包含 `currency` 和 `price_per_million` 字段
- ✅ `PricingRegistry` 根据 `api_base` 自动选择正确的定价策略
- ✅ 成本计算时自动处理单位转换

**优势**:
- 🎯 **准确性**: 避免单位换算错误 (例如将百万tokens误当作千tokens)
- 🎯 **透明性**: 用户看到的成本直接对应 API 提供商的账单
- 🎯 **可扩展**: 轻松添加新的 API 和定价策略

### 6.3 灵活的定价配置

**三层查询策略**:

```python
# 1️⃣ 精确匹配: api_base + model_name
pricing = registry.get_pricing(
    model_name="Pro/deepseek-ai/DeepSeek-V3",
    api_base="https://api.siliconflow.cn/v1"
)

# 2️⃣ 关键字匹配: 模型名称包含关键字
pricing = registry.get_pricing(
    model_name="gpt-4-turbo-preview",  # 包含 "gpt-4"
    api_base=None
)

# 3️⃣ 兜底策略: 返回默认的 GPT-4 定价
pricing = registry.get_pricing(
    model_name="unknown-model",
    api_base=None
)
```

**优势**:
- 🎯 **容错性**: 即使遇到未知模型,也能提供合理的成本估算
- 🎯 **易用性**: 大多数情况下只需提供模型名称即可
- 🎯 **精确性**: 支持 `api_base` 时可以精确匹配特定 API 的定价

### 6.4 统一的 API 接口

所有 Agent 共享相同的组件和接口:

```python
# 所有 Agent 都使用统一的 LLMClient
from agentype.common.llm_client import LLMClient

llm_client = LLMClient(config=config, logger_callbacks={...})
response = await llm_client.call_api(messages, llm_logger=llm_logger)

# 所有 Agent 都使用统一的 TokenStatistics
from agentype.common.token_statistics import TokenStatistics

stats = TokenStatistics(agent_name="MainAgent")
stats.add_usage(usage_data)

# 所有 Agent 都使用统一的 TokenReporter
from agentype.common.token_statistics import TokenReporter

reporter = TokenReporter(language="zh")
report = reporter.generate_simple_report(stats)
```

**优势**:
- 🎯 **一致性**: 所有 Agent 的统计方式完全一致
- 🎯 **可维护性**: 只需在一个地方修改代码,所有 Agent 自动同步
- 🎯 **可测试性**: 统一的接口便于编写单元测试

### 6.5 DeepSeek Reasoner 支持

`LLMClient` 完整支持 DeepSeek Reasoner 的 `reasoning_content` 特性:

```python
# 流式输出时实时显示推理过程 (灰色)
if 'reasoning_content' in delta:
    reasoning_chunk = delta['reasoning_content']
    print(f"\033[90m{reasoning_chunk}\033[0m", end='', flush=True)
    reasoning_content += reasoning_chunk

# 记录到日志
extra_info = {
    "reasoning_content": reasoning_content,
    "reasoning_length": len(reasoning_content),
    "usage": usage_data
}
```

**优势**:
- 🎯 **用户体验**: 用户可以实时看到 AI 的思考过程
- 🎯 **可追溯**: 推理内容也记录到日志,便于调试和分析
- 🎯 **透明度**: 完整展示 AI 的推理链路

---

## 7. 最佳实践

### 7.1 如何添加新的模型定价

```python
# 文件: agentype/common/token_statistics.py

class PricingRegistry:
    def _setup_default_pricing(self):
        # ... 现有配置 ...

        # 添加新的 API 定价
        new_api_pricing = {
            "new-model-v1": ModelPricing(1.0, 2.0, "CNY", True),
            "new-model-v2": ModelPricing(1.5, 3.0, "CNY", True),
        }
        self._pricing_map["https://api.newprovider.com/v1"] = new_api_pricing
```

### 7.2 如何在新 Agent 中集成 Token 统计

```python
class NewAgent:
    def __init__(self, config, session_id=None):
        # 1️⃣ 设置 session_id
        if session_id:
            from agentype.mainagent.config.session_config import set_session_id
            set_session_id(session_id)

        # 2️⃣ 初始化 LLM 客户端
        from agentype.common.llm_client import LLMClient
        self.llm_client = LLMClient(config=config, logger_callbacks={...})

        # 3️⃣ 初始化 LLM 日志记录器
        from agentype.{agent}/llm.logger import LLMLogger
        self.llm_logger = LLMLogger(log_dir="/path/to/logs/llm/new_agent")

        # 4️⃣ 初始化 Token 统计和报告器
        from agentype.common.token_statistics import TokenStatistics, TokenReporter
        self.token_stats = TokenStatistics(agent_name="NewAgent")
        self.token_reporter = TokenReporter(language="zh")

    async def call_llm(self, messages):
        # 调用 LLM 并自动记录 token 统计
        response = await self.llm_client.call_api(
            messages=messages,
            llm_logger=self.llm_logger,  # ⭐ 关键: 传递 llm_logger
            console_logger=self.console_logger
        )
        return response
```

### 7.3 如何优化 Token 使用效率

```python
from agentype.common.token_statistics import TokenStatistics

def analyze_efficiency(stats: TokenStatistics):
    """分析 token 使用效率并提供优化建议"""

    efficiency = stats.get_efficiency_score()

    if efficiency < 0.2:
        print("⚠️  Token 使用效率较低 (输出/总计 < 20%)")
        print("建议:")
        print("  - 检查是否有过多的系统提示或上下文")
        print("  - 考虑总结过长的对话历史")
        print("  - 使用更小的模型处理简单任务")
    elif efficiency > 0.5:
        print("⚠️  Token 使用效率异常高 (输出/总计 > 50%)")
        print("建议:")
        print("  - 检查是否提示词过于简短")
        print("  - 确认输出没有不必要的冗余")
    else:
        print("✅ Token 使用效率正常")

    # 分析单次请求平均 token 数
    avg_tokens = stats.total_tokens / stats.request_count if stats.request_count > 0 else 0

    if avg_tokens > 10000:
        print("⚠️  单次请求平均 token 数较高")
        print("建议:")
        print("  - 启用上下文总结功能")
        print("  - 减少单次请求的上下文长度")
```

### 7.4 如何调试 Token 统计问题

```python
from agentype.common.log_token_parser import LogTokenParser

def debug_token_stats(session_id: str):
    """调试 token 统计问题"""

    parser = LogTokenParser(log_base_dir="/app/data/outputs/logs/llm")

    # 1️⃣ 检查日志文件是否存在
    log_info = parser.get_log_file_info(session_id)

    print("=== 日志文件状态 ===")
    for agent_name, info in log_info.items():
        if info['exists']:
            print(f"✅ {agent_name}: {info['path']}")
            print(f"   大小: {info['size_kb']} KB")
            print(f"   修改时间: {info['modified']}")
        else:
            print(f"❌ {agent_name}: 日志文件不存在")
            print(f"   期望路径: {info['path']}")

    # 2️⃣ 解析日志并检查统计
    all_stats = parser.parse_all_agents(session_id)

    print("\n=== Token 统计 ===")
    for agent_name, stats in all_stats.items():
        print(f"{agent_name}:")
        print(f"  Total tokens: {stats.total_tokens}")
        print(f"  Requests: {stats.request_count}")
        print(f"  Model: {stats.model_name}")
        print(f"  API base: {stats.api_base}")

        if stats.total_tokens == 0:
            print(f"  ⚠️  警告: {agent_name} 没有 token 消耗记录")
```

---

## 附录: 常见问题 (FAQ)

### Q1: 为什么使用日志文件而不是内存共享?

**A**: MCP 架构下,每个 Agent 运行在独立的进程中,无法直接共享内存。日志文件提供了:
- ✅ 跨进程的数据持久化
- ✅ 即使进程崩溃也能保留数据
- ✅ 便于事后分析和调试

### Q2: 如何确保所有 Agent 使用相同的 session_id?

**A**: MainAgent 在初始化时生成 session_id,并通过构造函数参数传递给子 Agent:

```python
sub_agent = SubAgent(config=config, session_id=session_id)
```

子 Agent 在 `__init__` 中接收并设置 session_id:

```python
if session_id:
    from agentype.mainagent.config.session_config import set_session_id
    set_session_id(session_id)
```

### Q3: 如果日志文件损坏或缺失怎么办?

**A**: `LogTokenParser` 具有完善的错误处理:
- ✅ 如果日志文件不存在,返回空统计对象 (token=0)
- ✅ 如果 JSON 解析失败,跳过该行并继续解析
- ✅ 所有错误都会打印警告信息,但不会中断流程

### Q4: 如何验证成本估算的准确性?

**A**: 可以对比日志中的 `usage_data` 和 API 提供商的定价:

```python
# 从日志中提取 usage
usage = {"prompt_tokens": 1000000, "completion_tokens": 500000}

# 手动计算 (DeepSeek-V3: ¥2/百万输入, ¥8/百万输出)
expected_cost = (1.0 * 2.0) + (0.5 * 8.0)  # ¥6.0

# 使用系统计算
cost, currency = stats.get_estimated_cost(api_base="https://api.siliconflow.cn/v1")

assert abs(cost - expected_cost) < 0.0001
```

### Q5: 为什么有时 token 统计为 0?

**可能原因**:
1. ❌ Agent 没有实际调用 LLM
2. ❌ `llm_logger` 未正确初始化或传递
3. ❌ session_id 不匹配 (日志文件无法找到)
4. ❌ 日志文件权限问题

**调试步骤**:
```python
# 1. 检查日志文件是否存在
parser = LogTokenParser(log_base_dir="/app/data/outputs/logs/llm")
log_info = parser.get_log_file_info(session_id)
print(log_info)

# 2. 检查日志文件内容
with open(log_file, 'r') as f:
    for line in f:
        data = json.loads(line)
        print(data.get('extra_info', {}).get('usage'))

# 3. 检查 session_id 是否一致
from agentype.mainagent.config.session_config import get_session_id
print(f"Current session_id: {get_session_id()}")
```

---

## 总结

CellType Agent 的 Token 统计和定价计算系统是一个**设计精良、功能完善**的模块,具有以下特点:

✅ **跨进程统计**: 通过日志文件解决 MCP 架构下的统计收集问题
✅ **多货币支持**: 灵活处理不同 API 的定价策略 (CNY/USD, 百万/千tokens)
✅ **统一接口**: 所有 Agent 共享相同的统计组件和方法
✅ **用户友好**: 自动生成简要和详细报告,成本透明
✅ **易于扩展**: 便于添加新模型、新 API 和新定价策略
✅ **可靠性高**: 完善的错误处理和兜底策略

通过本文档,开发者可以:
- 🎯 理解 token 统计的完整流程
- 🎯 学会如何添加新模型的定价配置
- 🎯 掌握在新 Agent 中集成统计功能的方法
- 🎯 了解如何调试和优化 token 使用

---

**文档维护**: 如有疑问或发现错误,请联系项目维护者。
