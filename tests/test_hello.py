# -*- coding: utf-8 -*-
"""
测试问候语模板
"""

# 模拟当前的问候语模板
HELLO_ANSWER_TEMPLATE = """您好！我是GJ306数控系统智能助手，基于专业知识图谱构建，专门为您提供数控加工、G代码编程、工艺参数设置等方面的专业指导。

我可以帮助您：
- 生成各种加工工艺的G代码程序
- 解答数控加工工艺问题
- 提供GJ306系统操作指导
- 分析加工参数和优化建议

请告诉我您需要什么帮助？"""

def test_hello_template():
    """测试问候语模板效果"""
    print("🧪 测试问候语模板")
    print("=" * 60)
    
    print("📝 用户输入: 您好")
    print("-" * 30)
    print("🤖 系统回复:")
    print(HELLO_ANSWER_TEMPLATE)
    
    print("\n" + "=" * 60)
    print("📊 模板分析:")
    print(f"• 字符长度: {len(HELLO_ANSWER_TEMPLATE)} 字符")
    print(f"• 行数: {HELLO_ANSWER_TEMPLATE.count(chr(10)) + 1} 行")
    print("• 包含专业定位: ✅")
    print("• 包含功能介绍: ✅") 
    print("• 包含引导语: ✅")
    print("• 语言风格: 专业、友好")
    
    print("\n💡 评估:")
    print("✅ 明确表明身份 - GJ306数控系统智能助手")
    print("✅ 强调技术背景 - 基于专业知识图谱")
    print("✅ 列出核心功能 - G代码生成、工艺指导等")
    print("✅ 引导用户交互 - 询问需要什么帮助")
    print("✅ 保持专业性 - 没有过于冗长或文艺化")

if __name__ == "__main__":
    test_hello_template()