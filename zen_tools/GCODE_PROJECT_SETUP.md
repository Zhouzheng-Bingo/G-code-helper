# 在G-code项目中使用Zen AI模型

## 初次设置（只需执行一次）

### 第1步：运行复制命令

在终端中运行（复制粘贴这行命令）：

```bash
cd /Users/zhouzheng/zen-mcp-server && ./copy_zen_to_project.sh "/Users/zhouzheng/Library/CloudStorage/OneDrive-个人/学习资源/实验室/个人论文/自纠错数控系统大模型/PaperWithCode/G-code-helper"
```

### 第2步：进入您的G-code项目

```bash
cd "/Users/zhouzheng/Library/CloudStorage/OneDrive-个人/学习资源/实验室/个人论文/自纠错数控系统大模型/PaperWithCode/G-code-helper"
```

### 第3步：测试是否成功

```bash
python zen_ai.py
```

如果看到模型列表，说明设置成功！

## 日常使用

### ⚠️ 重要：每次打开G-code项目时

**每次打开G-code项目时，都需要先运行一次：**

```bash
python zen_ai.py
```

这会显示可用的AI模型，确认服务正常。

### 在代码中使用

在任何Python文件中：

```python
from zen_ai import ask_gemini, ask_o3

# 使用Gemini快速回答
answer = ask_gemini("什么是CNC编程")
print(answer)

# 使用O3进行复杂推理
solution = ask_o3("设计一个G代码优化算法")
print(solution)
```

### 更多用法

```python
from zen_ai import ZenAI

# 创建AI实例
ai = ZenAI()

# 列出所有可用模型
ai.models()

# 使用特定模型
response = ai.chat("你的问题", model='gemini-2.5-pro')
```

## 可用模型

- **gemini-2.5-flash** - 快速响应，适合简单问题
- **gemini-2.5-pro** - 深度分析，适合复杂任务
- **o3** - 强大推理，适合算法设计
- **o3-mini** - 平衡性能，适合一般推理

## 常见问题

1. **如果提示找不到zen_ai.py**
   - 确保在G-code项目根目录运行
   - 重新执行第1步的复制命令

2. **如果API调用失败**
   - 检查网络连接
   - 确认API密钥是否有效

3. **想更新配置**
   - 编辑 `zen_tools/custom_models.json`
   - 可以添加新的模型或更换API密钥

## 优点

- ✅ 不需要配置MCP
- ✅ 不需要重启Claude
- ✅ 直接Python调用
- ✅ 完全独立运行