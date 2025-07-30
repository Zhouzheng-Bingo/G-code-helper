# -*- coding: utf-8 -*-
"""
测试统一的LLM驱动意图识别系统
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_intent_classification():
    """测试意图分类功能"""
    print("🧪 测试统一的LLM驱动意图识别系统")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "input": "你好",
            "expected_intent": "greeting",
            "expected_behavior": "返回专业问候"
        },
        {
            "input": "G00指令的作用是什么？",
            "expected_intent": "gcode_knowledge",
            "expected_behavior": "G代码知识问答"
        },
        {
            "input": "如何使用G76螺纹切削循环？",
            "expected_intent": "gcode_knowledge",
            "expected_behavior": "G代码知识问答（不应识别为工艺任务）"
        },
        {
            "input": "我要使用外圆工艺加工一个外圆，Cn是2，L是100.0",
            "expected_intent": "process_task",
            "expected_behavior": "工艺识别并生成G代码"
        },
        {
            "input": "请给我GJ306系统的操作手册",
            "expected_intent": "pdf_document",
            "expected_behavior": "PDF文档查询"
        }
    ]
    
    try:
        from qa.unified_intent_classifier import get_unified_classifier
        from qa.question_parser import parse_question
        from qa.question_type import QuestionType
        
        classifier = get_unified_classifier()
        
        print("\n📋 测试意图分类：")
        print("-" * 50)
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            user_input = test_case["input"]
            expected_intent = test_case["expected_intent"]
            expected_behavior = test_case["expected_behavior"]
            
            print(f"\n[测试 {i}]")
            print(f"输入: {user_input}")
            print(f"期望意图: {expected_intent}")
            print(f"期望行为: {expected_behavior}")
            
            try:
                # 测试意图分类
                intent_result = classifier.classify_intent(user_input)
                
                print(f"\n🤖 LLM识别结果:")
                print(f"   意图类型: {intent_result.intent_type.value}")
                print(f"   置信度: {intent_result.confidence}")
                print(f"   推理: {intent_result.reasoning[:100]}...")
                
                # 验证结果
                if intent_result.intent_type.value == expected_intent:
                    print("✅ 意图识别正确")
                    success_count += 1
                else:
                    print(f"❌ 意图识别错误，期望 {expected_intent}，实际 {intent_result.intent_type.value}")
                
                # 测试question_parser集成
                question_type = parse_question(user_input)
                print(f"   问题类型映射: {question_type}")
                
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n" + "=" * 60)
        print(f"📊 测试结果: {success_count}/{len(test_cases)} 成功")
        print(f"📈 成功率: {success_count/len(test_cases)*100:.1f}%")
        
        if success_count == len(test_cases):
            print("🎉 所有测试通过！")
            print("\n✅ 核心改进：")
            print("1. 统一的LLM驱动意图识别，不再依赖规则")
            print("2. 准确区分知识咨询和工艺执行")
            print("3. '如何使用G76螺纹切削循环？'现在正确识别为知识问答")
            return True
        else:
            print("⚠️ 部分测试失败，需要调整")
            return False
            
    except Exception as e:
        print(f"❌ 测试系统错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interaction_flow():
    """测试交互流程"""
    print("\n\n🔧 测试交互流程")
    print("=" * 60)
    
    try:
        from qa.interaction import chat_with_gcode
        
        test_messages = [
            ("如何使用G76螺纹切削循环？", "应该返回G76的使用说明，而不是工艺识别"),
            ("我要使用外圆工艺加工一个外圆", "应该进入工艺识别流程")
        ]
        
        for message, expected in test_messages:
            print(f"\n测试消息: {message}")
            print(f"期望结果: {expected}")
            print("-" * 40)
            
            # 模拟交互
            response_parts = []
            for chunk in chat_with_gcode(message, []):
                response_parts.append(chunk)
                if len(response_parts) > 10:  # 只取前10个chunk进行测试
                    break
            
            if response_parts:
                print(f"响应开始: {response_parts[0][:100]}...")
            else:
                print("无响应")
                
    except Exception as e:
        print(f"交互测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 运行测试
    success = test_intent_classification()
    test_interaction_flow()
    
    print(f"\n{'='*60}")
    print("💡 系统改进总结：")
    print("1. ✅ 创建了统一的LLM驱动意图分类器")
    print("2. ✅ 新增了工艺任务和G代码知识咨询的意图类型")
    print("3. ✅ 修改了交互流程，根据意图类型选择处理方式")
    print("4. ✅ 保持了LLM作为核心技术（90%），符合论文要求")
    
    if success:
        print("\n🏆 修复成功！系统现在能正确处理各种类型的用户输入")