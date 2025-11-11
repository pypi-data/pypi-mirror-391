# 配置说明

## 🔐 安全配置

为了保护您的 API 密钥安全，项目采用以下配置方式：

### 1. 环境变量配置（推荐）

最安全的方式是使用环境变量：

```bash
# 设置 API 密钥
export OPENAI_API_KEY="your-api-key-here"

# 可选：设置 API Base URL
export OPENAI_API_BASE="https://api.openai.com/v1"

# 可选：设置模型
export OPENAI_MODEL="gpt-4"
```

### 2. 配置文件方式

如果需要使用配置文件，请按照以下步骤操作：

1. **复制示例配置文件**：
   ```bash
   cp agentype_config.example.json agentype_config.json
   ```

2. **编辑配置文件**：
   打开 `agentype_config.json`，填入您的配置：
   ```json
   {
     "llm": {
       "api_base": "https://api.openai.com/v1",
       "api_key": "your-actual-api-key",
       "model": "gpt-4"
     }
   }
   ```

3. **注意**：
   - ⚠️ `agentype_config.json` 已经被加入 `.gitignore`，不会被提交到 Git
   - ⚠️ 永远不要将包含真实 API 密钥的配置文件提交到版本控制
   - ⚠️ 如果使用配置文件，环境变量会覆盖配置文件中的空值

## 📁 配置文件说明

- `agentype_config.example.json` - 配置文件模板（不含敏感信息，可以提交到 Git）
- `agentype_config.json` - 实际使用的配置文件（包含敏感信息，不应提交到 Git）
- `agentype_config.json.backup` - 配置文件备份（仅在本地，不应提交到 Git）

## 🔄 配置优先级

系统按照以下优先级读取配置：

1. **环境变量**（最高优先级）
   - `OPENAI_API_KEY`
   - `OPENAI_API_BASE`
   - `OPENAI_MODEL`

2. **配置文件** (`agentype_config.json`)
   - 如果配置文件中的值为空，会自动使用环境变量填充
   - 如果配置文件中有值，则使用配置文件的值

3. **默认值**（最低优先级）

## ✅ 验证配置

使用项目管理工具验证配置是否正确：

```bash
# 检查配置
python manage.py config

# 检查项目状态
python manage.py status
```

## 🛡️ 安全提醒

1. **不要硬编码 API 密钥**：永远不要在代码中直接写入 API 密钥
2. **使用环境变量**：在生产环境中，始终使用环境变量管理敏感信息
3. **定期轮换密钥**：定期更换 API 密钥以提高安全性
4. **检查 .gitignore**：确保敏感配置文件已被正确忽略
5. **如果密钥泄露**：
   - 立即在 API 提供商处撤销该密钥
   - 生成新的 API 密钥
   - 如果已推送到公开仓库，考虑使用 `git filter-branch` 或 BFG Repo-Cleaner 清理历史

## 📖 更多信息

详细使用说明请参考 [README.md](README.md)
