#!/bin/bash
# 运行新增算法测试的便捷脚本

echo "🧪 开始运行论文相关的四个核心算法测试"
echo "================================================"

echo ""
echo "1️⃣ 测试LLM驱动的意图识别算法 (4.2节)"
echo "-------------------------------------------"
python tests/test_enhanced_intent.py

echo ""
echo "2️⃣ 测试LLM驱动的智能参数补全策略 (4.3节)"
echo "-------------------------------------------"
python tests/test_smart_params.py

echo ""
echo "3️⃣ 测试知识图谱辅助的LLM模板匹配 (4.4节)"
echo "-------------------------------------------"
python tests/test_template_matching.py

echo ""
echo "4️⃣ 测试轻量级G代码验证机制 (4.5节)"
echo "-------------------------------------------"
python tests/test_simple_verification.py

echo ""
echo "✅ 所有算法测试完成！"
echo "================================================"
echo "💡 如需更详细的测试，可以运行："
echo "   - tests/test_gcode_verification.py (完整验证测试)"
echo "   - tests/test_simple_enhanced.py (增强功能测试)"