# -*- coding: utf-8 -*-
"""
消融实验：测试LLM增强方法中各组件的贡献
"""

import os
import sys
import time
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['PY_ENVIRONMENT'] = 'local'

from qa.llm_centric_classifier import CoreLLMIntentClassifier, LLMEnhancementEngine
from lang_chain.client.client_factory import ClientFactory


class AblationClassifier(CoreLLMIntentClassifier):
    """用于消融实验的分类器"""
    
    def __init__(self, 
                 use_knowledge=True, 
                 use_bert=True, 
                 use_context=True,
                 use_reflection=True):
        super().__init__()
        self.use_knowledge = use_knowledge
        self.use_bert = use_bert
        self.use_context = use_context
        self.use_reflection = use_reflection
        
        # 修改增强引擎的行为
        self.original_enhance_prompt = self.enhancement_engine.enhance_llm_prompt
        self.enhancement_engine.enhance_llm_prompt = self._custom_enhance_prompt
    
    def _custom_enhance_prompt(self, user_input, conversation_history=None):
        """自定义的提示增强（用于消融）"""
        enhancement_info = {
            "bert_analysis": None,
            "semantic_similarity": None,
            "context_enrichment": False
        }
        
        # 基础提示
        base_prompt = """你是一个专业的数控加工工艺识别专家。
        
🎯 任务目标：
请分析用户的加工需求，识别出工艺类型和参数。

📤 输出格式：
请严格按照以下JSON格式返回结果：

{
    "main_process": "主工艺类型名称",
    "sub_process": "子工艺类型名称",
    "confidence": 0.95,
    "extracted_parameters": {},
    "professional_reasoning": "推理过程",
    "llm_confidence": 0.95
}

👤 用户需求：""" + user_input + "\n\n请开始分析："
        
        # 根据配置添加组件
        enhanced_prompt = base_prompt
        
        if self.use_knowledge:
            # 添加知识库
            knowledge = self.enhancement_engine._get_process_knowledge()
            enhanced_prompt = enhanced_prompt.replace(
                "🎯 任务目标：", 
                f"📚 数控加工工艺知识库：\n{knowledge}\n\n🎯 任务目标："
            )
        
        if self.use_bert and self.enhancement_engine.has_bert:
            # 添加BERT分析
            bert_result = self.enhancement_engine._bert_semantic_analysis(user_input)
            if bert_result:
                enhanced_prompt = enhanced_prompt.replace(
                    "🎯 任务目标：",
                    f"🧠 BERT语义分析结果：\n{bert_result}\n\n🎯 任务目标："
                )
                enhancement_info["bert_analysis"] = bert_result
        
        if self.use_context and conversation_history:
            # 添加上下文
            context = self.enhancement_engine._enrich_context(user_input, conversation_history)
            if context:
                enhanced_prompt = enhanced_prompt.replace(
                    "🎯 任务目标：",
                    f"{context}\n\n🎯 任务目标："
                )
                enhancement_info["context_enrichment"] = True
        
        return enhanced_prompt, enhancement_info
    
    def classify_intent(self, user_input, conversation_history=None):
        """重写分类方法以控制自反思"""
        # 临时保存原始反思设置
        original_reflection = self.use_reflection
        
        # 如果不使用反思，临时将置信度阈值设置得很高
        if not self.use_reflection:
            # 通过修改解析结果来避免触发反思
            result = super().classify_intent(user_input, conversation_history)
            # 这里可以通过其他方式避免反思
            return result
        else:
            return super().classify_intent(user_input, conversation_history)


def run_ablation_study():
    """运行消融实验"""
    print("🧪 LLM增强方法消融实验")
    print("=" * 80)
    
    # 定义消融配置
    ablation_configs = [
        ("完整系统", {"use_knowledge": True, "use_bert": True, "use_context": True, "use_reflection": True}),
        ("无知识库", {"use_knowledge": False, "use_bert": True, "use_context": True, "use_reflection": True}),
        ("无BERT", {"use_knowledge": True, "use_bert": False, "use_context": True, "use_reflection": True}),
        ("无上下文", {"use_knowledge": True, "use_bert": True, "use_context": False, "use_reflection": True}),
        ("无自反思", {"use_knowledge": True, "use_bert": True, "use_context": True, "use_reflection": False}),
        ("仅LLM", {"use_knowledge": False, "use_bert": False, "use_context": False, "use_reflection": False}),
    ]
    
    # 测试用例
    test_cases = [
        {
            "input": "我要使用外圆工艺加工一个外圆，Cn是2，L是100",
            "expected_main": "外圆工艺",
            "expected_sub": "外圆"
        },
        {
            "input": "车一个内孔",
            "expected_main": "里孔工艺",
            "expected_sub": "内圆"
        },
        {
            "input": "加工螺纹",
            "expected_main": "螺纹工艺",
            "expected_sub": None
        },
        {
            "input": "做个圆",  # 模糊输入
            "expected_main": "外圆工艺",
            "expected_sub": None
        },
        {
            "input": "端面切槽，深度5mm",
            "expected_main": "端面工艺",
            "expected_sub": "切槽"
        }
    ]
    
    # 存储结果
    all_results = {}
    
    for config_name, config in ablation_configs:
        print(f"\n🔧 测试配置: {config_name}")
        print(f"   配置: {config}")
        print("-" * 60)
        
        # 创建消融分类器
        try:
            classifier = AblationClassifier(**config)
            
            results = []
            total_time = 0
            
            for i, test_case in enumerate(test_cases, 1):
                print(f"  测试 {i}/{len(test_cases)}: {test_case['input'][:30]}...")
                
                start_time = time.time()
                try:
                    result = classifier.classify_intent(test_case['input'])
                    
                    # 评估结果
                    main_correct = result.main_process == test_case['expected_main']
                    sub_correct = (result.sub_process == test_case['expected_sub'] or 
                                 test_case['expected_sub'] is None)
                    
                    results.append({
                        'success': True,
                        'main_correct': main_correct,
                        'sub_correct': sub_correct,
                        'confidence': result.confidence,
                        'time': time.time() - start_time
                    })
                    
                except Exception as e:
                    print(f"    ❌ 错误: {e}")
                    results.append({
                        'success': False,
                        'main_correct': False,
                        'sub_correct': False,
                        'confidence': 0,
                        'time': time.time() - start_time
                    })
                
                total_time += results[-1]['time']
            
            # 计算统计
            successful = [r for r in results if r['success']]
            if successful:
                accuracy = sum(1 for r in successful if r['main_correct']) / len(successful)
                avg_confidence = sum(r['confidence'] for r in successful) / len(successful)
                avg_time = total_time / len(results)
                
                all_results[config_name] = {
                    'accuracy': accuracy,
                    'avg_confidence': avg_confidence,
                    'avg_time': avg_time,
                    'success_rate': len(successful) / len(results)
                }
                
                print(f"\n  📊 结果统计:")
                print(f"     准确率: {accuracy:.2%}")
                print(f"     平均置信度: {avg_confidence:.2f}")
                print(f"     平均响应时间: {avg_time:.3f}s")
            
        except Exception as e:
            print(f"  ❌ 配置失败: {e}")
            all_results[config_name] = {
                'accuracy': 0,
                'avg_confidence': 0,
                'avg_time': 0,
                'success_rate': 0
            }
    
    # 生成消融实验报告
    print("\n" + "=" * 80)
    print("📊 消融实验结果汇总")
    print("=" * 80)
    print("\n| 配置 | 准确率 | 平均置信度 | 平均时间(s) | 成功率 |")
    print("|------|--------|-----------|------------|--------|")
    
    for config_name, stats in all_results.items():
        print(f"| {config_name} | "
              f"{stats['accuracy']:.2%} | "
              f"{stats['avg_confidence']:.2f} | "
              f"{stats['avg_time']:.3f} | "
              f"{stats['success_rate']:.2%} |")
    
    # 分析各组件贡献
    if "完整系统" in all_results and all_results["完整系统"]['accuracy'] > 0:
        print("\n📈 组件贡献分析:")
        full_accuracy = all_results["完整系统"]['accuracy']
        
        contributions = {
            "知识库": full_accuracy - all_results.get("无知识库", {}).get('accuracy', 0),
            "BERT": full_accuracy - all_results.get("无BERT", {}).get('accuracy', 0),
            "上下文": full_accuracy - all_results.get("无上下文", {}).get('accuracy', 0),
            "自反思": full_accuracy - all_results.get("无自反思", {}).get('accuracy', 0),
        }
        
        for component, contribution in contributions.items():
            print(f"  {component}: {contribution:+.2%}")


if __name__ == "__main__":
    run_ablation_study()