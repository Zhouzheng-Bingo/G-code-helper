#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的批量参数收集功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qa.interaction import extract_params_from_message, PARAM_DESCRIPTIONS

def test_param_descriptions():
    """测试参数描述映射"""
    print("🧪 测试参数描述映射")
    print("=" * 60)
    
    test_params = ['Cn', 'L', 'Tr', 'Cr', 'F', 'D', 'S']
    
    for param in test_params:
        desc = PARAM_DESCRIPTIONS.get(param, param)
        print(f"✅ {param} -> {desc}")
    
    print()

def test_batch_extraction():
    """测试批量参数提取"""
    print("🧪 测试批量参数提取")
    print("=" * 60)
    
    # 测试场景1：用户一次性提供所有参数
    user_input1 = "我要使用外圆工艺加工一个外圆，每次进刀量0.5毫米，总共进两刀，进刀量总共是一毫米，加工长度是100毫米，加工速度是300毫米每分"
    param_list1 = ['Cn', 'L', 'Tr', 'Cr', 'F']
    param_types1 = {'Cn': int, 'L': float, 'Tr': float, 'Cr': float, 'F': float}
    
    print("场景1：用户一次性提供所有参数")
    print(f"用户输入: {user_input1}")
    extracted1 = extract_params_from_message(user_input1, param_list1, param_types1)
    print(f"提取结果: {extracted1}")
    print(f"成功率: {len(extracted1)}/{len(param_list1)} ({len(extracted1)/len(param_list1)*100:.1f}%)")
    print()
    
    # 测试场景2：用户只提供部分参数
    user_input2 = "加工速度300毫米每分，总共进2刀"
    param_list2 = ['Cn', 'L', 'Tr', 'Cr', 'F']
    param_types2 = {'Cn': int, 'L': float, 'Tr': float, 'Cr': float, 'F': float}
    
    print("场景2：用户只提供部分参数")
    print(f"用户输入: {user_input2}")
    extracted2 = extract_params_from_message(user_input2, param_list2, param_types2)
    print(f"提取结果: {extracted2}")
    
    # 模拟剩余参数
    remaining_params = [p for p in param_list2 if p not in extracted2]
    print(f"剩余参数: {remaining_params}")
    
    # 显示友好的参数提示
    print("需要提供以下参数：")
    for param in remaining_params:
        param_type = param_types2.get(param, float)
        param_desc = PARAM_DESCRIPTIONS.get(param, param)
        print(f"- {param_desc} ({param}): {param_type.__name__}类型")
    
    print()
    
    # 测试场景3：用户后续补充参数
    user_input3 = "每次进刀量0.5毫米，总进刀量1毫米，加工长度100毫米"
    
    print("场景3：用户后续补充参数")
    print(f"用户输入: {user_input3}")
    extracted3 = extract_params_from_message(user_input3, remaining_params, param_types2)
    print(f"提取结果: {extracted3}")
    
    # 合并所有参数
    all_params = {**extracted2, **extracted3}
    print(f"合并结果: {all_params}")
    print(f"最终成功率: {len(all_params)}/{len(param_list2)} ({len(all_params)/len(param_list2)*100:.1f}%)")
    
    return len(all_params) == len(param_list2)

def test_friendly_prompts():
    """测试友好的参数提示"""
    print("🧪 测试友好的参数提示")
    print("=" * 60)
    
    missing_params = ['F', 'Cn', 'L']
    param_types = {'F': float, 'Cn': int, 'L': float}
    
    print("缺失参数的友好提示：")
    for param in missing_params:
        param_desc = PARAM_DESCRIPTIONS.get(param, param)
        param_type = param_types.get(param, float)
        print(f"- {param_desc} ({param}): {param_type.__name__}类型")
    
    print("\n示例输入：")
    example_parts = []
    for param in missing_params:
        if param == 'F':
            example_parts.append("加工速度300毫米每分")
        elif param == 'Cn':
            example_parts.append("总共进2刀")
        elif param == 'L':
            example_parts.append("加工长度100毫米")
        else:
            param_desc = PARAM_DESCRIPTIONS.get(param, param)
            example_parts.append(f"{param_desc}=数值")
    
    print(f"'{', '.join(example_parts)}'")
    print()

if __name__ == "__main__":
    print("🚀 测试新的批量参数收集功能")
    print("=" * 80)
    
    # 测试参数描述
    test_param_descriptions()
    
    # 测试批量提取
    success = test_batch_extraction()
    
    # 测试友好提示
    test_friendly_prompts()
    
    print("=" * 80)
    if success:
        print("🎉 所有测试通过！新的批量参数收集功能工作正常。")
        print("📝 主要改进：")
        print("   1. 参数名称显示为自然语言描述")
        print("   2. 支持批量参数输入")
        print("   3. 智能的参数收集提示")
        print("   4. 减少交互轮次")
    else:
        print("⚠️ 部分测试失败，需要进一步调试。")