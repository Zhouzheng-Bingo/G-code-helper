#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的参数提取功能
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def extract_params_from_message(message: str, param_list: list, param_types: dict) -> dict:
    """
    从用户消息中提取参数值 - 增强版，支持自然语言理解
    """
    params = {}
    
    # 智能参数提取规则
    param_patterns = {
        'Cn': [
            r'总共进(\d+)刀',
            r'进(\d+)刀',
            r'循环(\d+)次',
            r'Cn[是为=:]?\s*(\d+)',
        ],
        'L': [
            r'加工长度[是为:]?\s*(\d+(?:\.\d+)?)毫米',
            r'长度[是为:]?\s*(\d+(?:\.\d+)?)(?:毫米|mm)?',
            r'L[是为=:]?\s*(\d+(?:\.\d+)?)',
        ],
        'Tr': [
            r'每次进刀量[是为:]?\s*(\d+(?:\.\d+)?)毫米',
            r'进刀量[是为:]?\s*(\d+(?:\.\d+)?)毫米',
            r'Tr[是为=:]?\s*(\d+(?:\.\d+)?)',
        ],
        'Cr': [
            r'进刀量总共[是为:]?\s*(\d+(?:\.\d+)?)毫米',
            r'总进刀量[是为:]?\s*(\d+(?:\.\d+)?)毫米',
            r'Cr[是为=:]?\s*(\d+(?:\.\d+)?)',
        ],
        'F': [
            r'加工速度[是为:]?\s*(\d+(?:\.\d+)?)毫米每分',
            r'进给速度[是为:]?\s*(\d+(?:\.\d+)?)(?:毫米每分|mm/min)?',
            r'速度[是为:]?\s*(\d+(?:\.\d+)?)(?:毫米每分|mm/min)?',
            r'F[是为=:]?\s*(\d+(?:\.\d+)?)',
        ],
        'D': [
            r'直径[是为:]?\s*(\d+(?:\.\d+)?)(?:毫米|mm)?',
            r'D[是为=:]?\s*(\d+(?:\.\d+)?)',
        ],
        'S': [
            r'转速[是为:]?\s*(\d+)(?:转每分|rpm)?',
            r'主轴转速[是为:]?\s*(\d+)(?:转每分|rpm)?',
            r'S[是为=:]?\s*(\d+)',
        ]
    }
    
    # 对每个需要的参数进行智能提取
    for param in param_list:
        if param in param_patterns:
            for pattern in param_patterns[param]:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1)
                        param_type = param_types.get(param, float)
                        
                        if param_type == int:
                            params[param] = int(float(value))
                        elif param_type == float:
                            params[param] = float(value)
                        else:
                            params[param] = param_type(value)
                        
                        print(f"✅ 智能提取参数: {param} = {params[param]} (通过模式: {pattern})")
                        break
                    except (ValueError, IndexError):
                        continue
    
    return params

def test_enhanced_extraction():
    """测试增强后的参数提取功能"""
    user_input = "我要使用外圆工艺加工一个外圆，每次进刀量0.5毫米，总共进两刀，进刀量总共是一毫米，加工长度是100毫米，加工速度是300毫米每分"
    
    param_list = ['Cn', 'L', 'Tr', 'Cr', 'F']
    param_types = {'Cn': int, 'L': float, 'Tr': float, 'Cr': float, 'F': float}
    
    print("🧪 测试增强后的参数提取功能")
    print(f"用户输入: {user_input}")
    print("-" * 80)
    
    # 预期的参数提取结果
    expected_params = {
        "Cn": 2,       # 总共进两刀
        "L": 100.0,    # 加工长度是100毫米
        "Tr": 0.5,     # 每次进刀量0.5毫米
        "Cr": 1.0,     # 进刀量总共是一毫米
        "F": 300.0     # 加工速度是300毫米每分
    }
    
    print("🎯 预期参数:")
    for param, value in expected_params.items():
        print(f"  {param} = {value}")
    
    print("-" * 80)
    
    # 提取参数
    extracted = extract_params_from_message(user_input, param_list, param_types)
    
    print("-" * 80)
    print("📊 提取结果对比:")
    
    success_count = 0
    for param, expected_value in expected_params.items():
        actual_value = extracted.get(param, None)
        if actual_value == expected_value:
            print(f"✅ {param}: 成功 ({expected_value})")
            success_count += 1
        else:
            print(f"❌ {param}: 失败 (期望{expected_value}, 实际{actual_value})")
    
    print("-" * 80)
    print(f"🎉 提取成功率: {success_count}/{len(expected_params)} ({success_count/len(expected_params)*100:.1f}%)")
    
    if success_count == len(expected_params):
        print("🎊 所有参数提取成功！系统现在可以正确理解自然语言输入。")
        return True
    else:
        print("🔧 还有部分参数需要优化。")
        return False

if __name__ == "__main__":
    test_enhanced_extraction()