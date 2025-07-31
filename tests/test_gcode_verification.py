#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试G代码验证机制
"""

import os
import sys

os.environ['PY_ENVIRONMENT'] = 'local'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa.llm_gcode_verifier import get_gcode_verifier, verify_gcode, verify_and_fix_gcode
from qa.enhanced_gcode_generator import generate_gcode_intelligently


def test_basic_verification():
    """测试基础验证功能"""
    print("🧪 测试基础G代码验证")
    print("=" * 60)
    
    verifier = get_gcode_verifier()
    
    # 测试用例1：正常的G代码
    print("\n1️⃣ 测试正常G代码")
    normal_gcode = """
G21 (单位：毫米)
G90 (绝对坐标)
M03 S1000 (主轴正转)
G00 X0 Y0 Z5 (快速定位)
G01 Z-1 F100 (进给到深度)
G01 X50 F200 (切削)
G01 Y30
G00 Z5 (退刀)
M05 (主轴停止)
M30 (程序结束)
"""
    
    result = verifier.verify_gcode(normal_gcode, "外圆工艺", "外圆")
    print(f"验证结果: {result.summary}")
    print(f"评分: 安全性={result.safety_score}, 效率={result.efficiency_score}, 规范性={result.standard_score}")
    
    # 测试用例2：有安全问题的G代码
    print("\n\n2️⃣ 测试有安全隐患的G代码")
    unsafe_gcode = """
G00 X1000 Y1000 (超大距离快速移动)
G01 Z-50 F5000 (进给速度过快)
G01 X0 Y0
M30
"""
    
    result = verifier.verify_gcode(unsafe_gcode)
    print(f"验证结果: {result.summary}")
    print("发现的问题:")
    for issue in result.issues:
        print(f"  [{issue.level.value}] {issue.description}")
        if issue.suggestion:
            print(f"    建议: {issue.suggestion}")
    
    # 测试用例3：语法错误的G代码
    print("\n\n3️⃣ 测试语法错误的G代码")
    syntax_error_gcode = """
G21
这是错误的一行
G01 X Y Z (缺少坐标值)
F (缺少进给速度值)
M30
"""
    
    result = verifier.verify_gcode(syntax_error_gcode)
    print(f"验证结果: {result.summary}")
    print(f"是否有效: {result.is_valid}")


def test_verification_and_fix():
    """测试验证并修复功能"""
    print("\n\n🧪 测试G代码自动修复")
    print("=" * 60)
    
    # 有问题的G代码
    problematic_gcode = """
G00 X500 Y500 Z100 (距离过大)
G01 Z-20 F5000 (进给速度过快)
G01 X0 F8000 (进给速度超限)
没有结束指令
"""
    
    print("原始G代码:")
    print(problematic_gcode)
    
    # 验证并修复
    fixed_gcode, result = verify_and_fix_gcode(problematic_gcode, "外圆工艺", "外圆")
    
    print("\n修复后的G代码:")
    print(fixed_gcode)
    print(f"\n验证结果: {result.summary}")


def test_integrated_generation():
    """测试集成的G代码生成和验证"""
    print("\n\n🧪 测试集成的G代码生成+验证")
    print("=" * 60)
    
    # 测试参数
    test_cases = [
        {
            "process": "外圆工艺",
            "sub_process": "外圆",
            "params": {"Cn": 2, "L": 100.0, "F": 300.0},
            "description": "车削外圆，要求高精度"
        },
        {
            "process": "里孔工艺",
            "sub_process": "内圆",
            "params": {"D": 25.0, "L": 50.0, "F": 5000.0},  # 故意设置过高的进给速度
            "description": "镗孔加工"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 测试案例 {i}:")
        print(f"工艺: {test['process']} - {test['sub_process']}")
        print(f"参数: {test['params']}")
        
        # 生成G代码（会自动验证）
        gcode, explanation = generate_gcode_intelligently(
            test['process'],
            test['sub_process'],
            test['params'],
            test['description']
        )
        
        if gcode:
            print("\n生成的G代码:")
            print("-" * 40)
            print(gcode[:300] + "..." if len(gcode) > 300 else gcode)
            print("-" * 40)
            print(f"\n说明:\n{explanation}")


def test_verification_details():
    """测试验证结果的详细信息"""
    print("\n\n🧪 测试验证结果详细信息")
    print("=" * 60)
    
    # 生成一个G代码
    gcode = """
G21 (单位设置)
G90 (绝对坐标)
M03 S2000 (主轴启动)
G00 X0 Y0 Z10
G01 Z-5 F150
G02 X50 Y50 I25 J0 F200 (圆弧插补)
G01 X100 Y100 F250
G00 Z20
M05
M30
"""
    
    verifier = get_gcode_verifier()
    result = verifier.verify_gcode(gcode, "外圆工艺", "外圆弧")
    
    # 输出详细的验证结果
    print("验证结果详情:")
    print(f"  总体评价: {result.summary}")
    print(f"  是否有效: {'✅ 是' if result.is_valid else '❌ 否'}")
    print(f"\n各项评分:")
    print(f"  安全性: {'█' * int(result.safety_score)}{'░' * (10-int(result.safety_score))} {result.safety_score:.1f}/10")
    print(f"  效率性: {'█' * int(result.efficiency_score)}{'░' * (10-int(result.efficiency_score))} {result.efficiency_score:.1f}/10")
    print(f"  规范性: {'█' * int(result.standard_score)}{'░' * (10-int(result.standard_score))} {result.standard_score:.1f}/10")
    print(f"  总  分: {'█' * int(result.overall_score)}{'░' * (10-int(result.overall_score))} {result.overall_score:.1f}/10")
    
    # 转换为字典格式
    print("\n\nJSON格式输出:")
    import json
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))


def test_edge_cases():
    """测试边缘情况"""
    print("\n\n🧪 测试边缘情况")
    print("=" * 60)
    
    verifier = get_gcode_verifier()
    
    # 空G代码
    print("1. 空G代码:")
    result = verify_gcode("")
    print(f"  结果: {result.summary}")
    
    # 只有注释的G代码
    print("\n2. 只有注释:")
    result = verify_gcode("(这是注释)\n(另一个注释)")
    print(f"  结果: {result.summary}")
    
    # 极简G代码
    print("\n3. 极简G代码:")
    result = verify_gcode("G01 X10\nM30")
    print(f"  结果: {result.summary}")


if __name__ == "__main__":
    try:
        test_basic_verification()
        test_verification_and_fix()
        test_integrated_generation()
        test_verification_details()
        test_edge_cases()
        
        print("\n\n✅ 所有测试完成!")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()