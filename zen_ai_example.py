#!/usr/bin/env python3
"""
Zen AI 使用示例 - 展示如何在G-code项目中使用AI模型
"""

from zen_ai import ZenAI, ask_gemini, ask_o3

def basic_usage():
    """基本用法示例"""
    print("=== 基本用法 ===")
    
    # 快速问答
    answer = ask_gemini("什么是CNC编程?")
    print(f"Gemini回答: {answer[:200]}...")
    
    # 复杂推理
    solution = ask_o3("设计一个G代码优化思路")
    print(f"O3方案: {solution[:200]}...")

def advanced_usage():
    """高级用法示例"""
    print("\n=== 高级用法 ===")
    
    ai = ZenAI()
    
    # 使用特定模型
    response = ai.chat(
        "分析以下G代码的性能: G01 X10 Y20 F100", 
        model='gemini-2.5-pro'
    )
    print(f"深度分析: {response[:200]}...")
    
    # 对比不同模型
    models_to_test = ['gemini-2.5-flash', 'o3-mini']
    question = "什么是数控加工?"
    
    for model in models_to_test:
        response = ai.chat(question, model)
        print(f"\n{model} 回答:")
        print(response[:150] + "...")

if __name__ == "__main__":
    # 首先列出可用模型
    print("🔍 检查可用模型...")
    from zen_ai import list_models
    models = list_models()
    
    if models:
        print(f"\n✅ 发现 {len(models)} 个模型，开始测试...")
        basic_usage()
        advanced_usage()
    else:
        print("❌ 没有可用模型，请检查配置")
