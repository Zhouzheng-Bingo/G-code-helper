#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试增强后的意图识别系统
"""

import os
import sys

# 设置环境变量
os.environ['PY_ENVIRONMENT'] = 'local'

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qa.llm_centric_classifier import get_llm_centric_classifier

def test_enhanced_intent_recognition():
    """测试增强的意图识别功能"""
    print("🚀 测试增强的意图识别系统")
    print("=" * 60)
    
    classifier = get_llm_centric_classifier()
    
    # 测试用例（包含一些可能触发自反思的模糊输入）
    test_cases = [
        # 清晰的输入（高置信度）
        "我要使用外圆工艺加工一个外圆，Cn是2，L是100",
        "车一个内孔，直径20mm",
        
        # 模糊的输入（可能触发自反思）
        "加工一个圆",  # 没有明确说是外圆还是内圆
        "车削加工",     # 没有具体工艺类型
        "做个螺纹",     # 没有说内螺纹还是外螺纹
        
        # 非工艺输入
        "你好",
        "G00指令的作用是什么？"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n📝 测试 {i}: {test_input}")
        print("-" * 40)
        
        try:
            result = classifier.classify(test_input)
            
            print(f"主工艺: {result['main_process']}")
            print(f"子工艺: {result.get('sub_process', 'None')}")
            print(f"置信度: {result['confidence']:.2f}")
            print(f"LLM置信度: {result.get('llm_confidence', 0):.2f}")
            print(f"方法: {result['method']}")
            
            if result.get('entities'):
                print("提取的参数:")
                for entity in result['entities']:
                    print(f"  - {entity['type']}: {entity['value']}")
            
            # 显示推理过程的前100个字符
            reasoning = result.get('reasoning', '')
            if reasoning:
                print(f"推理: {reasoning[:100]}...")
                
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    # 显示统计信息
    print("\n" + "=" * 60)
    print("📊 性能统计")
    print("=" * 60)
    
    stats = classifier.get_performance_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # 显示详细统计（如果有自反思案例）
    detailed_stats = classifier.get_detailed_performance_stats()
    reflection_summary = detailed_stats.get('reflection_summary', {})
    
    if reflection_summary.get('total_cases', 0) > 0:
        print(f"\n🔄 自反思统计:")
        print(f"触发次数: {reflection_summary['total_cases']}")
        print(f"改进次数: {reflection_summary['improved_cases']}")
        print(f"平均改进幅度: {reflection_summary['avg_improvement']:.2f}")
        
        # 显示自反思案例
        reflection_cases = detailed_stats['detailed_metrics']['reflection_cases']
        if reflection_cases:
            print(f"\n自反思案例详情:")
            for case in reflection_cases[:3]:  # 只显示前3个
                print(f"  输入: {case['input']}")
                print(f"  原置信度: {case['original_confidence']:.2f}")
                print(f"  新置信度: {case['new_confidence']:.2f}")
                print(f"  改进: {'是' if case['improved'] else '否'}")
                print()

if __name__ == "__main__":
    test_enhanced_intent_recognition()