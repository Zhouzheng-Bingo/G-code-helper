# -*- coding: utf-8 -*-
"""
意图识别模块测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from qa.intent_classifier import IntentClassifier, get_intent_classifier
from qa.question_parser import parse_process_type

def test_intent_classification():
    """测试意图识别功能"""
    print("=" * 60)
    print("意图识别模块测试")
    print("=" * 60)
    
    test_cases = [
        "我要加工外圆，长度是50mm，进给速度300",
        "请帮我车一个内孔，直径20mm",
        "外螺纹加工，M10螺纹",
        "切一个槽，深度5mm",
        "倒角处理，外倒角",
        "车端面加工",
        "内锥面加工，深度10",
        "这是什么意思？",  # 非工艺相关
        "你好",  # 问候语
        "加工一个外圆，L=100，F=200，转速1500"  # 多参数
    ]
    
    classifier = get_intent_classifier()
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] 输入: {test_text}")
        print("-" * 40)
        
        try:
            # 使用新的意图识别接口
            result = classifier.classify(test_text)
            
            print(f"主工艺: {result['main_process']}")
            print(f"子工艺: {result['sub_process']}")
            print(f"置信度: {result['confidence']:.2f}")
            print(f"识别方法: {result['method']}")
            print(f"推理过程: {result['reasoning']}")
            
            if result['entities']:
                print("提取的参数:")
                for entity in result['entities']:
                    print(f"  - {entity['type']}: {entity['value']}")
            else:
                print("提取的参数: 无")
                
        except Exception as e:
            print(f"测试失败: {e}")

def test_compatibility():
    """测试与原有系统的兼容性"""
    print("\n" + "=" * 60)
    print("兼容性测试 - 使用原有接口")
    print("=" * 60)
    
    test_cases = [
        "我要加工外圆",
        "车内孔",
        "螺纹加工"
    ]
    
    for test_text in test_cases:
        print(f"\n测试输入: {test_text}")
        try:
            result = parse_process_type(test_text)
            print(f"结果: {result}")
        except Exception as e:
            print(f"测试失败: {e}")

def test_performance():
    """测试性能对比"""
    print("\n" + "=" * 60)
    print("性能对比测试")
    print("=" * 60)
    
    import time
    
    test_text = "我要加工外圆，长度50mm，进给速度300"
    classifier = get_intent_classifier()
    
    # 测试新方法
    start_time = time.time()
    for _ in range(5):
        result = classifier.classify(test_text)
    new_method_time = (time.time() - start_time) / 5
    
    print(f"新方法平均耗时: {new_method_time:.3f}秒")
    print(f"识别方法: {result['method']}")
    print(f"识别结果: {result['main_process']} - {result['sub_process']}")

if __name__ == "__main__":
    # 设置环境变量
    os.environ['PY_ENVIRONMENT'] = 'local'
    
    try:
        test_intent_classification()
        test_compatibility()
        test_performance()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()