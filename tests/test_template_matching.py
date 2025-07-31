#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试LLM驱动的模板匹配
"""

import os
import sys

os.environ['PY_ENVIRONMENT'] = 'local'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa.llm_template_selector import get_template_selector
from qa.enhanced_gcode_generator import EnhancedGCodeGenerator, generate_gcode_intelligently


def test_template_selection():
    """测试模板选择功能"""
    print("🧪 测试LLM模板选择器")
    print("=" * 60)
    
    selector = get_template_selector()
    
    # 测试用例
    test_cases = [
        {
            "process": "外圆工艺",
            "sub_process": "外圆",
            "params": {"Cn": 2, "L": 100.0, "F": 300.0},
            "description": "车削一个外圆，要求表面光滑"
        },
        {
            "process": "里孔工艺", 
            "sub_process": "内圆",
            "params": {"D": 25.0, "L": 50.0},
            "description": "镗一个内孔，直径25毫米"
        },
        {
            "process": "端面工艺",
            "sub_process": "切槽",
            "params": {"depth": 5.0, "L": 3.0},
            "description": "在端面切一个槽"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}:")
        print(f"工艺: {test['process']} - {test['sub_process']}")
        print(f"参数: {test['params']}")
        print(f"描述: {test['description']}")
        
        template_code, explanation, suggestions = selector.select_best_template(
            test['process'],
            test['sub_process'],
            test['params'],
            test['description']
        )
        
        if template_code:
            print(f"✅ 找到模板")
            print(f"📄 解释: {explanation}")
            if suggestions:
                print(f"💡 建议: {suggestions}")
        else:
            print(f"❌ 未找到模板: {explanation}")


def test_intelligent_generation():
    """测试智能G代码生成"""
    print("\n\n🧪 测试智能G代码生成")
    print("=" * 60)
    
    generator = EnhancedGCodeGenerator()
    
    # 测试完整参数
    print("\n1️⃣ 完整参数测试")
    gcode, explanation = generator.generate_with_intelligence(
        "外圆工艺",
        "外圆",
        {"Cn": 2, "L": 100.0, "Tr": 0.5, "Cr": 1.0, "F": 300.0},
        "车削外圆，精度要求高"
    )
    
    if gcode:
        print("生成的G代码:")
        print("-" * 40)
        print(gcode)
        print("-" * 40)
        print(f"说明: {explanation}")
        
        # 分析代码质量
        quality = generator.analyze_gcode_quality(gcode)
        print(f"\n质量评分:")
        print(f"  安全性: {quality.get('safety_score', 'N/A')}/10")
        print(f"  效率: {quality.get('efficiency_score', 'N/A')}/10")
        print(f"  规范性: {quality.get('standard_score', 'N/A')}/10")
        
        if quality.get('issues'):
            print(f"  问题: {', '.join(quality['issues'])}")
        if quality.get('improvements'):
            print(f"  改进建议: {', '.join(quality['improvements'])}")
    
    # 测试部分参数
    print("\n\n2️⃣ 部分参数测试")
    gcode, explanation = generator.generate_with_intelligence(
        "里孔工艺",
        "内圆",
        {"D": 30.0, "L": 40.0},  # 缺少进给速度等参数
        "镗孔加工"
    )
    
    if gcode:
        print("生成的G代码:")
        print("-" * 40)
        print(gcode[:200] + "..." if len(gcode) > 200 else gcode)
        print("-" * 40)
        print(f"说明: {explanation}")


def test_template_comparison():
    """测试模板比较功能"""
    print("\n\n🧪 测试模板比较")
    print("=" * 60)
    
    # 使用便捷函数
    params = {"Cn": 3, "L": 150.0, "F": 250.0}
    
    print("测试不同描述对模板选择的影响:")
    
    descriptions = [
        "普通外圆加工",
        "高精度外圆加工，表面粗糙度要求Ra0.8",
        "粗加工外圆，效率优先"
    ]
    
    for desc in descriptions:
        print(f"\n描述: {desc}")
        gcode, explanation = generate_gcode_intelligently(
            "外圆工艺", "外圆", params, desc
        )
        
        if gcode:
            # 只显示前几行G代码
            lines = gcode.strip().split('\n')[:3]
            print(f"G代码预览: {lines}")
            print(f"说明: {explanation}")


def test_error_handling():
    """测试错误处理"""
    print("\n\n🧪 测试错误处理")
    print("=" * 60)
    
    # 测试不存在的工艺
    print("1. 不存在的工艺:")
    gcode, explanation = generate_gcode_intelligently(
        "未知工艺", "未知子工艺", {}, "测试错误"
    )
    print(f"结果: {explanation}")
    
    # 测试空参数
    print("\n2. 空参数:")
    gcode, explanation = generate_gcode_intelligently(
        "外圆工艺", "外圆", {}, "测试空参数"
    )
    print(f"结果: {explanation}")


if __name__ == "__main__":
    try:
        test_template_selection()
        test_intelligent_generation()
        test_template_comparison()
        test_error_handling()
        
        print("\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()