# Zen MCP Server 使用指南

## 快速开始

本项目允许您在Claude Code对话中直接调用多个AI模型（O3、Gemini等），无需手动调用API。

### 使用方式

在Claude Code对话框中，直接用自然语言描述您的需求，Claude会自动调用相应的模型：

- **"用O3帮我设计一个排序算法"** → 自动调用O3模型
- **"让Gemini Pro深度分析这个项目架构"** → 自动调用Gemini 2.5 Pro
- **"用Gemini Flash快速解释什么是REST API"** → 自动调用Gemini 2.5 Flash
- **"让O3和Gemini协作优化这段代码"** → 多模型协作

### 当前可用模型

| 模型 | 用途 | 上下文窗口 | 适用场景 |
|------|------|------------|----------|
| **O3 Pro** | 复杂推理 | 200K tokens | 算法设计、数学问题、深度逻辑推理 |
| **O3-mini** | 平衡性能 | 200K tokens | 一般推理任务、更快响应 |
| **Gemini 2.5 Pro** | 长上下文分析 | 1M tokens | 深度分析、架构设计、处理大文档 |
| **Gemini 2.5 Flash** | 快速响应 | 1M tokens | 简单查询、快速总结、日常问答 |

## 配置管理

### 修改API密钥或添加新模型

所有模型配置都在 `custom_models.json` 文件中：

#### 1. 更换API密钥

```json
{
  "name": "yunwu-o3",
  "api_url": "https://yunwu.ai/v1",
  "api_key": "sk-您的新密钥"  // 👈 直接替换这里
}
```

#### 2. 添加新模型到现有提供商

在对应provider的models数组中添加：

```json
"models": [
  {
    "id": "o3",
    "name": "O3 Pro - 复杂推理",
    "context_window": 200000,
    "description": "用于复杂推理任务"
  },
  {
    "id": "o1",  // 👈 新增模型
    "name": "O1 - 最新推理模型",
    "context_window": 128000,
    "description": "OpenAI最新推理模型"
  }
]
```

#### 3. 添加新的API提供商

在providers数组中添加新的提供商配置：

```json
{
  "providers": [
    // ... 现有的提供商 ...
    {
      "name": "openai-direct",  // 👈 新提供商
      "api_url": "https://api.openai.com/v1",
      "api_key": "sk-openai的密钥",
      "models": [
        {
          "id": "gpt-4-turbo",
          "name": "GPT-4 Turbo",
          "context_window": 128000,
          "description": "OpenAI最强模型"
        }
      ]
    }
  ]
}
```

### 完整配置示例

```json
{
  "providers": [
    {
      "name": "yunwu-o3",
      "api_url": "https://yunwu.ai/v1",
      "api_key": "sk-xxx...",
      "models": [
        {
          "id": "o3",
          "name": "O3 Pro - 复杂推理",
          "context_window": 200000,
          "description": "用于复杂推理任务"
        }
      ]
    }
  ]
}
```

### 注意事项

- ✅ **修改后无需重启Claude**，直接使用即可
- ✅ **conf/目录下也有一个副本**，保持同步即可
- ⚠️ **确保JSON格式正确**（注意逗号、引号）
- ⚠️ **API密钥需要有对应模型的访问权限**
- 💡 **建议先小额度测试新配置**

## 常见用法示例

### 单模型使用
- "用O3分析这个算法的时间复杂度"
- "让Gemini Pro解释微服务架构的优缺点"
- "用Gemini Flash快速总结Python的特点"

### 多模型协作
- "我想优化一个搜索系统，让O3设计算法，Gemini Pro设计架构"
- "先用O3分析问题本质，再用Gemini Flash给出简洁总结"

### 模型选择建议
- **复杂推理/算法设计** → O3 Pro
- **需要快速结果** → O3-mini 或 Gemini Flash
- **深度分析/长文档** → Gemini 2.5 Pro
- **简单问答** → Gemini 2.5 Flash

## 故障排查

如果模型调用失败：
1. 检查API密钥是否正确
2. 确认API提供商服务是否正常
3. 查看是否有模型名称拼写错误
4. 确保JSON格式正确（可以用在线JSON验证工具检查）

## 项目文件说明

- `custom_models.json` - 模型配置文件（主要修改这个）
- `server.py` - MCP服务器主程序
- `config.py` - 配置管理
- `.env` - 环境变量（一般不需要修改）
- `.mcp.json` - MCP配置
- `tools/` - 各种AI工具实现
- `providers/` - AI提供商接口实现

---

**提示**：您只需要修改 `custom_models.json` 就能添加新模型或更换API密钥！