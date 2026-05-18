# G代码生成助手 🤖

> 基于具身智能的自然语言驱动G代码编程系统

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 项目概述

G代码生成助手是一个以大语言模型（LLM）为核心的具身智能CNC编程系统。通过自然语言交互，用户可以轻松生成专业的G代码程序，无需掌握复杂的CNC编程知识。

### ✨ 核心特性

- 🧠 **LLM驱动**：以大语言模型为核心，其他技术辅助增强
- 💬 **自然对话**：支持中文自然语言输入和语音交互
- 🔍 **智能识别**：准确识别加工意图和工艺类型
- ⚡ **批量收集**：一次性收集多个参数，减少交互轮次
- 🎯 **精准生成**：生成符合GJ306标准的G代码程序
- ✅ **自动验证**：三层验证机制确保代码质量
- 📱 **友好界面**：现代化Web界面，支持文本复制

## 🏗️ 系统架构

```
┌─────────────────────────────────────────┐
│              用户界面层                  │
│  Gradio WebUI + FastAPI + 语音输入      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│              核心LLM层                  │
│  意图识别 → 参数补全 → 模板选择 → 验证  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│             辅助增强层                   │
│  BERT + 知识图谱 + RAG检索              │
└─────────────────────────────────────────┘
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Neo4j (可选，用于知识图谱)
- 支持的LLM服务：Ollama、智谱AI、千问等

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-username/G-code-helper.git
cd G-code-helper
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 设置环境变量
export PY_ENVIRONMENT=local
export KMP_DUPLICATE_LIB_OK=TRUE
```

4. **启动服务**
```bash
# 启动完整服务（API + WebUI）
python app.py

# 或分别启动
python api_backend.py  # 仅API服务
python webui.py        # 仅WebUI
```

5. **访问界面**
- WebUI: http://localhost:7860
- API文档: http://localhost:18881/docs

## 📖 使用指南

### 基本使用

1. **访问WebUI界面**：打开 http://localhost:7860
2. **输入加工需求**：使用自然语言描述你的加工需求
3. **参数确认**：系统会智能收集所需参数
4. **生成G代码**：获得完整的G代码程序
5. **复制使用**：直接复制代码到你的CNC系统

### 示例对话

```
用户：我要使用外圆工艺加工一个外圆，每次进刀量0.5毫米，总共进两刀，进刀量总共是一毫米，加工长度是100毫米，加工速度是300毫米每分

助手：识别到工艺类型：外圆工艺 → 外圆
已收集参数：
- 加工速度/进给速度 (F) = 300.0
- 进刀次数/循环次数 (Cn) = 2
- 加工长度 (L) = 100.0
- 每次进刀量 (Tr) = 0.5
- 总进刀量 (Cr) = 1.0

生成的G代码程序：
N10 G00 X100 Z5
N20 G01 X99 F300
N30 G01 Z-100
N40 G01 X100
N50 G00 Z5
N60 M30
```

### 支持的工艺类型

- **外圆工艺**：外圆、外锥面、外圆弧
- **端面工艺**：端面、切槽、内端面  
- **里孔工艺**：内圆、内锥面、内槽、内弧、中心孔
- **锥面工艺**：各种内外锥面加工
- **螺纹工艺**：内外螺纹加工
- **倒角工艺**：各种倒角操作

## 🔧 配置说明

### LLM配置

系统支持多种LLM服务，在 `config/config-local.yaml` 中配置：

```yaml
llm:
  provider: "ollama"  # 或 zhipu, qwen, deepseek
  model: "qwen2.5:7b"
  base_url: "http://localhost:11434"
  api_key: "your-api-key"
```

### 服务端口配置

```yaml
server:
  api_port: 18881    # API服务端口
  ui_port: 7860      # WebUI端口
  ui_share: false    # 是否公网访问
```

## 🧪 测试

### 运行测试套件

```bash
# 运行所有测试
python tests/test.py

# 运行特定测试
python tests/test_intent_classifier.py     # 意图识别测试
python tests/test_param_extraction.py      # 参数提取测试
python tests/test_gcode_generation.py      # G代码生成测试
```

### 性能测试

```bash
# 批量参数收集测试
python tests/test_batch_param_collection.py

# 意图识别准确率测试
python tests/test_enhanced_intent.py
```

## 📁 项目结构

```
G-code-helper/
├── app.py                 # 主应用入口
├── api_backend.py         # FastAPI后端服务
├── webui.py              # Gradio Web界面
├── config/               # 配置文件
│   ├── config.py
│   └── config-local.yaml
├── qa/                   # 核心算法模块
│   ├── llm_centric_classifier.py    # LLM意图识别
│   ├── llm_parameter_agent.py       # 智能参数补全
│   ├── llm_template_selector.py     # 模板选择
│   ├── llm_gcode_verifier.py       # 代码验证
│   └── interaction.py               # 主交互逻辑
├── lang_chain/           # LLM客户端
│   └── client/          # 多厂商LLM支持
├── model/               # 模型管理
├── dao/                # 数据访问层
├── tests/              # 测试文件
└── data/               # 数据文件
    ├── corpus/         # 文档语料
    └── model/          # 训练模型
```

## 🔬 核心算法

### 1. LLM驱动的意图识别
- **自反思机制**：低置信度时自动重新分析
- **BERT增强**：提供语义相似度参考
- **置信度融合**：LLM主导(90%) + 辅助技术(10%)

### 2. 智能参数补全策略
- **语义理解**：LLM理解参数含义和关系
- **批量收集**：一次询问多个相关参数
- **自然交互**：生成符合上下文的问询语句

### 3. 知识图谱辅助模板匹配
- **多维评分**：LLM评分(50%) + 参数匹配(20%) + 语义相似度(20%) + 使用频率(10%)
- **智能解释**：生成选择理由和优化建议

### 4. 三层验证机制
- **基础验证**：语法规则检查
- **参数验证**：数值范围和安全检查
- **智能验证**：LLM深度语义验证

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| 意图识别准确率 | 95%+ | 引入自反思机制后 |
| 参数提取成功率 | 100% | 支持多种中文表达 |
| G代码生成成功率 | 90%+ | 符合GJ306标准 |
| 平均交互轮次 | 2轮 | 批量参数收集优化 |
| 响应时间 | <3秒 | 包含LLM推理时间 |

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 开发环境设置

1. Fork本项目
2. 创建特性分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 提交Pull Request

### 代码规范

- 遵循PEP 8代码风格
- 添加必要的注释和文档字符串
- 确保所有测试通过

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 🔗 相关链接

- [项目详细介绍](PROJECT_OVERVIEW.md)
- [算法实现总结](algorithm_implementations_summary.md)
- [API文档](http://localhost:18881/docs)

## 📞 联系方式

- 项目作者：[Zheng Zhou]
- 邮箱：[zhouzheng18@mails.ucas.ac.cn]
- 项目主页：https://github.com/Zhouzheng-Bingo/G-code-helper

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和研究者！

---

⭐ **如果这个项目对你有帮助，请给个Star支持一下！**
