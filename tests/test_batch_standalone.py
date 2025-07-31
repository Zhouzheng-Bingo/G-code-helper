#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立测试新的批量参数收集功能
"""

import re

# 参数名称到自然语言的映射
PARAM_DESCRIPTIONS = {
    'Cn': '进刀次数/循环次数',
    'L': '加工长度',
    'Tr': '每次进刀量', 
    'Cr': '总进刀量',
    'F': '加工速度/进给速度',
    'D': '直径',
    'S': '主轴转速',
    'X': 'X坐标',
    'Y': 'Y坐标', 
    'Z': 'Z坐标',
    'R': '半径',
    'P': '螺距',
    'T': '刀具号',
    'A': '角度',
    'H': '高度',
    'W': '宽度'
}

def extract_params_from_message(message: str, param_list: list, param_types: dict) -> dict:
    """
    从用户消息中提取参数值 - 增强版，支持自然语言理解
    """
    params = {}
    
    # 智能参数提取规则 - 支持中文数字
    param_patterns = {
        'Cn': [
            r'总共进([二两三四五六七八九十2３４５６７８９１０２３]\d*)刀',
            r'总共进(\d+)刀',
            r'进([二两三四五六七八九十2３４５６７８９１０２３]\d*)刀',
            r'进(\d+)刀',
            r'循环([二两三四五六七八九十2３４５６７８９１０２３]\d*)次', 
            r'循环(\d+)次',
            r'只要进刀([一二三四五六七八九十1１２３４５６７８９１０]\d*)次',
            r'只要进([一二三四五六七八九十1１２３４５６７８９１０]\d*)刀',
            r'进刀([一二三四五六七八九十1１２３４５６７８９１０]\d*)次',
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
            r'进刀量总共[是为:]?\s*([一二三四五六七八九十1１２３４５６７８９１０]\d*(?:\.\d+)?)毫米',
            r'总共[是为:]?\s*([一二三四五六七八九十1１２３４５６７８９１０]\d*(?:\.\d+)?)毫米',
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
    
    # 中文数字转换映射
    chinese_numbers = {
        '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
        '两': '2', '１': '1', '２': '2', '３': '3', '４': '4', 
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9', '１０': '10'
    }
    
    # 对每个需要的参数进行智能提取
    for param in param_list:
        if param in param_patterns:
            for pattern in param_patterns[param]:
                match = re.search(pattern, message, re.IGNORECASE)
                if match:
                    try:
                        value = match.group(1)
                        
                        # 转换中文数字
                        if value in chinese_numbers:
                            value = chinese_numbers[value]
                        
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

def simulate_param_collection_session():
    """模拟参数收集会话"""
    print("🎭 模拟批量参数收集会话")
    print("=" * 80)
    
    # 初始状态：用户输入部分参数
    print("👤 用户: 我要使用外圆工艺加工一个外圆，只要进刀一次")
    
    # 需要的参数列表
    required_params = ['Cn', 'L', 'Tr', 'Cr', 'F']
    param_types = {'Cn': int, 'L': float, 'Tr': float, 'Cr': float, 'F': float}
    
    # 第一次提取
    extracted1 = extract_params_from_message("只要进刀一次", required_params, param_types)
    remaining_params = [p for p in required_params if p not in extracted1]
    
    print(f"🤖 系统: 已识别参数：{extracted1}")
    print("🤖 系统: 需要提供以下参数：")
    for param in remaining_params:
        param_desc = PARAM_DESCRIPTIONS.get(param, param)
        param_type = param_types.get(param, float)
        print(f"   - {param_desc} ({param}): {param_type.__name__}类型")
    
    print("🤖 系统: 您可以一次性提供多个参数，例如：")
    print("   '加工速度300毫米每分，加工长度100毫米，每次进刀量0.5毫米，总进刀量1毫米'")
    print()
    
    # 第二次用户输入
    print("👤 用户: 加工速度300毫米每分，加工长度100毫米")
    extracted2 = extract_params_from_message("加工速度300毫米每分，加工长度100毫米", remaining_params, param_types)
    
    # 更新参数
    all_params = {**extracted1, **extracted2}
    remaining_params = [p for p in required_params if p not in all_params]
    
    print(f"🤖 系统: 已收集参数：{', '.join([f'{PARAM_DESCRIPTIONS.get(k, k)}({k})={v}' for k, v in extracted2.items()])}")
    
    if remaining_params:
        print("🤖 系统: 仍需提供以下参数：")
        for param in remaining_params:
            param_desc = PARAM_DESCRIPTIONS.get(param, param)
            param_type = param_types.get(param, float)
            print(f"   - {param_desc} ({param}): {param_type.__name__}类型")
        print()
        
        # 第三次用户输入
        print("👤 用户: 每次进刀量0.5毫米，总进刀量1毫米")
        extracted3 = extract_params_from_message("每次进刀量0.5毫米，总进刀量1毫米", remaining_params, param_types)
        
        # 最终合并
        all_params.update(extracted3)
        final_remaining = [p for p in required_params if p not in all_params]
        
        print(f"🤖 系统: 已收集参数：{', '.join([f'{PARAM_DESCRIPTIONS.get(k, k)}({k})={v}' for k, v in extracted3.items()])}")
        
        if not final_remaining:
            print("🤖 系统: ✅ 所有参数已收集完毕，正在生成G代码...")
            print(f"🤖 系统: 最终参数: {all_params}")
            return True
        else:
            print("🤖 系统: ❌ 仍有缺失参数，需要继续收集")
            return False
    else:
        print("🤖 系统: ✅ 所有参数已收集完毕，正在生成G代码...")
        return True

def test_param_descriptions():
    """测试参数描述映射"""
    print("🧪 测试参数描述映射")
    print("=" * 60)
    
    test_params = ['Cn', 'L', 'Tr', 'Cr', 'F', 'D', 'S']
    
    print("参数名称 -> 自然语言描述：")
    for param in test_params:
        desc = PARAM_DESCRIPTIONS.get(param, param)
        print(f"   {param:>3} -> {desc}")
    
    print()

def main():
    """主测试函数"""
    print("🚀 测试改进的参数收集系统")
    print("=" * 80)
    
    # 测试参数描述
    test_param_descriptions()
    
    # 模拟会话
    success = simulate_param_collection_session()
    
    print("=" * 80)
    if success:
        print("🎉 测试成功！改进的参数收集系统工作正常。")
        print()
        print("📝 主要改进点：")
        print("   1. ✅ 参数显示为自然语言描述 (如 F -> 加工速度/进给速度)")
        print("   2. ✅ 支持批量参数输入 (一次输入多个参数)")
        print("   3. ✅ 智能参数提取 (理解自然语言表达)")
        print("   4. ✅ 减少交互轮次 (避免逐个参数收集)")
        print("   5. ✅ 友好的用户提示 (提供输入示例)")
        print()
        print("🔧 现在系统可以：")
        print("   - 直接识别: 'F参数' 显示为 '加工速度/进给速度 (F): float类型'")
        print("   - 批量收集: 用户可以说 '加工速度300毫米每分，总共进2刀'")
        print("   - 智能补全: 缺少参数时提供具体的输入建议")
    else:
        print("⚠️ 测试失败，需要进一步调试。")

if __name__ == "__main__":
    main()