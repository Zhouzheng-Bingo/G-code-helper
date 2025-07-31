# 测试文件说明

这个文件夹包含了项目的所有测试和调试脚本。

## 主要测试文件

### 核心功能测试
- `test.py` - 主要的综合测试脚本
- `test_gcode_generation.py` - G代码生成功能测试
- `test_process_recognition.py` - 工艺识别测试

### 意图分类相关测试
- `test_intent_classifier.py` - 意图分类器测试
- `test_intent_simple.py` - 简单意图分类测试
- `test_intent_demo.py` - 意图分类演示
- `test_unified_intent_system.py` - 统一意图系统测试
- `test_llm_centric.py` - LLM中心意图分类测试
- `test_llm_simple.py` - 简单LLM测试

### 性能测试
- `test_performance.py` - 详细性能测试
- `test_preload.py` - 预加载功能测试
- `test_full_qa.py` - 完整问答流程测试
- `compare_performance.py` - 性能对比测试
- `quick_test.py` - 快速性能诊断

### 工具和修复
- `remove_sleep_delays.py` - 移除sleep延迟的工具
- `test_entity_error.py` - 实体错误测试
- `test_hello.py` - 问候功能测试

### UI测试
- `webui_test.py` - Web UI测试
- `direct_test.py` - 直接测试

## 新增算法测试 (论文相关)

### 四个核心算法的测试文件
- `test_enhanced_intent.py` - LLM驱动的意图识别算法测试 (4.2节)
- `test_smart_params.py` - LLM驱动的智能参数补全策略测试 (4.3节)
- `test_template_matching.py` - 知识图谱辅助的LLM模板匹配测试 (4.4节)
- `test_gcode_verification.py` - 轻量级G代码验证机制测试 (4.5节)
- `test_simple_enhanced.py` - 简化的增强功能测试
- `test_simple_verification.py` - 简化的验证功能测试

## 使用方法

```bash
# 运行主要测试
python tests/test.py

# 性能测试
python tests/test_performance.py

# 快速诊断
python tests/quick_test.py

# 新增算法测试 (推荐按顺序运行)
python tests/test_enhanced_intent.py     # 意图识别测试
python tests/test_smart_params.py        # 参数补全测试  
python tests/test_template_matching.py   # 模板匹配测试
python tests/test_simple_verification.py # 验证机制测试 (简化版)
```

## 注意事项

- 运行测试前确保已启动必要的服务（如Neo4j、Ollama等）
- 某些测试可能需要较长时间完成
- 性能测试结果会受当前系统负载影响