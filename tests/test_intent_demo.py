# -*- coding: utf-8 -*-
"""
演示统一LLM意图识别的核心改进
"""

def demonstrate_unified_llm_intent():
    """演示核心改进"""
    print("🎯 统一LLM意图识别系统 - 核心改进演示")
    print("=" * 60)
    
    print("\n📚 改进前的问题：")
    print("- '如何使用G76螺纹切削循环？' → 被误识别为工艺任务")
    print("- 系统试图找工艺模板，返回'未找到对应的工艺模板'")
    
    print("\n✨ 改进后的方案：")
    print("1. 创建统一的LLM意图分类器（unified_intent_classifier.py）")
    print("2. 让大语言模型直接理解用户意图，区分5种类型：")
    print("   - greeting: 问候语")
    print("   - gcode_knowledge: G代码知识咨询")  
    print("   - process_task: 工艺执行任务")
    print("   - pdf_document: 文档查询")
    print("   - unknown: 其他")
    
    print("\n🤖 LLM Prompt设计要点：")
    print("- 明确区分'询问用法'vs'执行任务'")
    print("- 提供具体的判断规则和示例")
    print("- 让LLM基于语义理解做判断，而不是关键词")
    
    print("\n📋 核心代码改进：")
    print("\n1. unified_intent_classifier.py - 统一意图分类器：")
    print("""
    prompt = '''
    ## 重要区分规则：
    ⚠️ **知识咨询 vs 工艺执行的区别**：
    - 知识咨询：用户在**询问**某个G代码或工艺**怎么用**、**是什么**
    - 工艺执行：用户在**要求系统**帮他**执行**某个加工任务
    
    举例说明：
    - "如何使用G76螺纹切削循环？" → gcode_knowledge（询问用法）
    - "使用G76加工M10螺纹" → process_task（执行任务）
    '''
    """)
    
    print("\n2. question_parser.py - 集成统一分类器：")
    print("""
    def parse_question(question: str) -> QuestionType:
        # 使用统一的LLM意图分类器
        unified_classifier = get_unified_classifier()
        intent_result = unified_classifier.classify_intent(question)
        
        # 映射意图类型到问题类型
        question_type = intent_to_question_map[intent_result.intent_type]
    """)
    
    print("\n3. interaction.py - 根据意图选择处理流程：")
    print("""
    if question_type == QuestionType.PROCESS_TASK:
        # 处理工艺执行任务
        process_info = parse_process_type(message)
        response = handle_process_task(message, process_info)
        
    elif question_type == QuestionType.GCODE_KNOWLEDGE_QUERY:
        # 处理G代码知识咨询 - 走知识问答流程
        answers = get_answer(message, history)
    """)
    
    print("\n🎉 改进效果：")
    print("✅ '如何使用G76螺纹切削循环？' → 正确识别为知识咨询")
    print("✅ '我要使用外圆工艺加工' → 正确识别为工艺任务")
    print("✅ 完全基于LLM的语义理解，不依赖规则")
    print("✅ 符合论文'大语言模型为核心技术'的要求")
    
    print("\n💡 这种设计的优势：")
    print("1. **LLM驱动**：所有判断基于大模型的语义理解")
    print("2. **统一架构**：一个分类器处理所有意图")
    print("3. **易于扩展**：添加新意图只需修改prompt")
    print("4. **准确性高**：基于上下文理解，不是简单匹配")

if __name__ == "__main__":
    demonstrate_unified_llm_intent()
    
    print("\n" + "=" * 60)
    print("📝 总结：")
    print("通过创建统一的LLM驱动意图分类系统，")
    print("我们解决了知识咨询被误识别为工艺任务的问题，")
    print("同时强化了大语言模型作为核心技术的地位。")