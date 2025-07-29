# -*- coding: utf-8 -*-
"""
大语言模型中心意图识别系统测试
"""

import sys
import os
import time
from typing import Dict, List

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ['PY_ENVIRONMENT'] = 'local'

def test_llm_centric_intent():
    """测试大语言模型中心的意图识别"""
    print("🚀 启动大语言模型中心意图识别系统测试")
    print("=" * 80)
    
    try:
        # 尝试导入和初始化
        from qa.llm_centric_classifier import LLMCentricIntentClassifier, get_llm_centric_classifier
        from qa.question_parser import parse_process_type
        
        print("✅ 模块导入成功")
        
        # 初始化分类器
        classifier = get_llm_centric_classifier()
        print("✅ 分类器初始化成功")
        
        # 测试用例
        test_cases = [
            {
                "input": "我要加工外圆，长度是50mm，进给速度300",
                "expected_main": "外圆工艺",
                "expected_sub": "外圆"
            },
            {
                "input": "请帮我车一个内孔，直径20mm",
                "expected_main": "里孔工艺", 
                "expected_sub": "内圆"
            },
            {
                "input": "外螺纹加工，M10螺纹",
                "expected_main": "螺纹工艺",
                "expected_sub": "外直螺纹"
            },
            {
                "input": "车端面，表面要平整",
                "expected_main": "端面工艺",
                "expected_sub": "端面"
            },
            {
                "input": "切一个槽，深度5mm，宽度3mm",
                "expected_main": "端面工艺",
                "expected_sub": "切槽"
            },
            {
                "input": "外倒角处理，45度倒角",
                "expected_main": "倒角工艺",
                "expected_sub": "外倒角"
            }
        ]
        
        successful_tests = 0
        total_tests = len(test_cases)
        detailed_results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 [测试 {i}/{total_tests}] {test_case['input']}")
            print("-" * 60)
            
            start_time = time.time()
            
            try:
                # 使用更新后的接口进行测试
                result = parse_process_type(test_case['input'])
                
                end_time = time.time()
                response_time = end_time - start_time
                
                # 分析结果
                main_correct = result['main_process'] == test_case['expected_main']
                sub_correct = result['sub_process'] == test_case['expected_sub']
                
                print(f"🔍 识别结果：")
                print(f"   主工艺: {result['main_process']} {'✅' if main_correct else '❌'}")
                print(f"   子工艺: {result['sub_process']} {'✅' if sub_correct else '❌'}")
                print(f"   置信度: {result.get('confidence', 'N/A')}")
                print(f"   LLM置信度: {result.get('llm_confidence', 'N/A')}")
                print(f"   识别方法: {result.get('method', 'Unknown')}")
                print(f"   BERT增强: {'是' if result.get('enhancement_used') else '否'}")
                print(f"   响应时间: {response_time:.2f}秒")
                
                if result.get('entities'):
                    print(f"   提取参数:")
                    for entity in result['entities']:
                        print(f"     - {entity['type']}: {entity['value']}")
                
                print(f"   推理过程: {result.get('reasoning', 'N/A')[:100]}...")
                
                # 评估成功率
                if main_correct and (sub_correct or result['sub_process'] is None):
                    successful_tests += 1
                    status = "✅ 成功"
                else:
                    status = "❌ 失败"
                
                detailed_results.append({
                    'test_input': test_case['input'],
                    'expected': f"{test_case['expected_main']}/{test_case['expected_sub']}",
                    'actual': f"{result['main_process']}/{result['sub_process']}",
                    'method': result.get('method', 'Unknown'),
                    'confidence': result.get('confidence', 0),
                    'llm_confidence': result.get('llm_confidence', 0),
                    'bert_enhanced': result.get('enhancement_used', False),
                    'response_time': response_time,
                    'success': main_correct and (sub_correct or result['sub_process'] is None)
                })
                
                print(f"📊 测试状态: {status}")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                print(f"错误类型: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                
                detailed_results.append({
                    'test_input': test_case['input'],
                    'expected': f"{test_case['expected_main']}/{test_case['expected_sub']}",
                    'actual': f"ERROR: {str(e)}",
                    'method': 'Error',
                    'confidence': 0,
                    'llm_confidence': 0,
                    'bert_enhanced': False,
                    'response_time': 0,
                    'success': False
                })
        
        # 统计结果
        print("\n" + "=" * 80)
        print("📊 测试结果统计")
        print("=" * 80)
        
        success_rate = (successful_tests / total_tests) * 100
        print(f"总测试数: {total_tests}")
        print(f"成功数: {successful_tests}")
        print(f"成功率: {success_rate:.1f}%")
        
        # 方法统计
        method_stats = {}
        enhancement_count = 0
        total_response_time = 0
        valid_responses = 0
        
        for result in detailed_results:
            method = result['method']
            method_stats[method] = method_stats.get(method, 0) + 1
            
            if result['bert_enhanced']:
                enhancement_count += 1
            
            if result['response_time'] > 0:
                total_response_time += result['response_time']
                valid_responses += 1
        
        print(f"\n🔧 方法分布:")
        for method, count in method_stats.items():
            print(f"   {method}: {count}次 ({count/total_tests*100:.1f}%)")
        
        print(f"\n🧠 BERT增强使用: {enhancement_count}/{total_tests} ({enhancement_count/total_tests*100:.1f}%)")
        
        if valid_responses > 0:
            avg_response_time = total_response_time / valid_responses
            print(f"⏱️ 平均响应时间: {avg_response_time:.2f}秒")
        
        # 详细结果表格
        print(f"\n📋 详细测试结果:")
        print("-" * 120)
        print(f"{'输入':<30} {'期望':<20} {'实际':<20} {'方法':<15} {'置信度':<8} {'耗时':<8} {'状态':<6}")
        print("-" * 120)
        
        for result in detailed_results:
            input_short = result['test_input'][:28] + ".." if len(result['test_input']) > 30 else result['test_input']
            expected_short = result['expected'][:18] + ".." if len(result['expected']) > 20 else result['expected']
            actual_short = result['actual'][:18] + ".." if len(result['actual']) > 20 else result['actual']
            method_short = result['method'][:13] + ".." if len(result['method']) > 15 else result['method']
            
            print(f"{input_short:<30} {expected_short:<20} {actual_short:<20} {method_short:<15} "
                  f"{result['confidence']:<8.2f} {result['response_time']:<8.2f} {'✅' if result['success'] else '❌':<6}")
        
        # 性能评估
        if hasattr(classifier, 'get_performance_stats'):
            stats = classifier.get_performance_stats()
            print(f"\n📈 系统性能统计:")
            print(f"   总调用次数: {stats.get('total_calls', 0)}")
            print(f"   成功调用次数: {stats.get('successful_calls', 0)}")
            print(f"   增强调用次数: {stats.get('enhanced_calls', 0)}")
            print(f"   成功率: {stats.get('success_rate', 0)*100:.1f}%")
            print(f"   增强使用率: {stats.get('enhancement_rate', 0)*100:.1f}%")
        
        print("\n" + "=" * 80)
        print("🎉 测试完成!")
        
        if success_rate >= 80:
            print("✅ 系统表现优秀!")
        elif success_rate >= 60:
            print("⚠️ 系统表现良好，但有改进空间")
        else:
            print("❌ 系统需要进一步优化")
            
        return success_rate, detailed_results
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保所有依赖已正确安装")
        return 0, []
    except Exception as e:
        print(f"❌ 测试过程中出现未预期错误: {e}")
        import traceback
        traceback.print_exc() 
        return 0, []

def test_fallback_behavior():
    """测试后备机制"""
    print("\n" + "=" * 80)
    print("🔄 测试后备机制")
    print("=" * 80)
    
    # 这里可以测试在模型不可用情况下的表现
    print("注意: 后备机制测试需要在LLM服务不可用时进行")

if __name__ == "__main__":
    try:
        # 主要测试
        success_rate, results = test_llm_centric_intent()
        
        # 后备机制测试
        test_fallback_behavior()
        
        print(f"\n🏁 最终成功率: {success_rate:.1f}%")
        
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试程序异常: {e}")
        import traceback
        traceback.print_exc()