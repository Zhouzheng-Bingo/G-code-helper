#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试LLM驱动的智能参数补全
"""

import os
import sys

os.environ['PY_ENVIRONMENT'] = 'local'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa.llm_parameter_agent import get_parameter_agent
from qa.enhanced_session import enhanced_session


def test_parameter_agent():
    """测试参数代理的各项功能"""
    print("🧪 测试LLM参数代理")
    print("=" * 60)
    
    agent = get_parameter_agent()
    
    # 测试1：分析所需参数
    print("\n1️⃣ 测试参数需求分析")
    params = agent.analyze_required_params("外圆工艺", "外圆")
    print(f"外圆加工所需参数：")
    for name, info in params.items():
        print(f"  - {name}: {info.description} ({'必需' if info.required else '可选'})")
    
    # 测试2：生成自然问题
    print("\n2️⃣ 测试自然语言问题生成")
    context = {"Cn": 2, "L": 100.0}
    question = agent.generate_natural_question("F", context)
    print(f"参数F的询问: {question}")
    
    # 测试3：解析用户回答
    print("\n3️⃣ 测试用户回答解析")
    test_answers = [
        ("300", "F"),
        ("大概50左右", "L"),
        ("20毫米", "D"),
        ("进给速度用300吧", "F"),
        ("不知道", "S")
    ]
    
    for answer, param in test_answers:
        value = agent.parse_user_answer(answer, param, float)
        print(f"  '{answer}' -> {param} = {value}")
    
    # 测试4：参数推理
    print("\n4️⃣ 测试参数推理")
    known = {"L": 100.0, "D": 20.0}
    all_params = {
        "L": agent.param_knowledge["L"],
        "D": agent.param_knowledge["D"],
        "F": agent.param_knowledge["F"],
        "S": agent.param_knowledge["S"]
    }
    inferred = agent.infer_related_params(known, all_params)
    print(f"已知参数: {known}")
    print(f"推理参数: {inferred}")


def test_enhanced_session():
    """测试增强的会话管理"""
    print("\n\n🧪 测试增强会话管理")
    print("=" * 60)
    
    # 初始化会话
    enhanced_session.init_session("外圆工艺", "外圆", ["Cn", "L", "Tr", "Cr", "F"])
    
    print("📝 模拟对话流程：")
    
    # 获取第一个问题
    question = enhanced_session.get_next_question()
    print(f"\n助手: {question}")
    
    # 模拟用户回答
    test_responses = [
        "2个",           # Cn
        "长度100毫米",   # L  
        "0.5就行",       # Tr
        "退回半径1",     # Cr
        "进给300"        # F
    ]
    
    for i, response in enumerate(test_responses):
        print(f"用户: {response}")
        
        all_done, next_msg = enhanced_session.add_param_value_smart(response)
        print(f"助手: {next_msg}")
        
        if all_done:
            print(f"\n✅ 参数收集完成！")
            print(f"最终参数: {enhanced_session.param_values}")
            break
    
    # 清理会话
    enhanced_session.clear()


def test_intelligent_completion():
    """测试智能补全场景"""
    print("\n\n🧪 测试智能参数补全场景")
    print("=" * 60)
    
    from qa.llm_centric_classifier import llm_centric_parse_process_type
    
    # 测试用例：部分参数的输入
    test_cases = [
        "我要车一个外圆，长度100",
        "加工内孔，直径25毫米，进给速度200",
        "切槽，深度5mm"
    ]
    
    for test_input in test_cases:
        print(f"\n📝 输入: {test_input}")
        
        # 1. 意图识别
        process_info = llm_centric_parse_process_type(test_input)
        print(f"识别结果: {process_info['main_process']} - {process_info['sub_process']}")
        
        # 2. 参数提取和补全
        if process_info['main_process'] != "NO_PROCESS":
            agent = get_parameter_agent()
            
            # 获取已提取的参数
            extracted = process_info.get('parameters', {})
            print(f"已提取参数: {extracted}")
            
            # 分析所需参数
            required = agent.analyze_required_params(
                process_info['main_process'],
                process_info['sub_process']
            )
            
            # 智能推理缺失参数
            inferred = agent.infer_related_params(extracted, required)
            if inferred:
                print(f"智能推理: {inferred}")
            
            # 仍缺失的参数
            all_params = {**extracted, **inferred}
            missing = [p for p in required if p not in all_params and required[p].required]
            if missing:
                print(f"仍需询问: {missing}")


if __name__ == "__main__":
    try:
        # 运行测试
        test_parameter_agent()
        test_enhanced_session()
        test_intelligent_completion()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()