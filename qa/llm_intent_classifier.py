# -*- coding: utf-8 -*-
"""
基于大语言模型的增强意图识别模块
作者: Claude Code
功能: 以大语言模型为核心，结合BERT和知识图谱的智能意图识别
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers未安装，将使用纯LLM方法")

from lang_chain.client.client_factory import ClientFactory


@dataclass
class IntentResult:
    """意图识别结果"""
    main_process: str
    sub_process: Optional[str]
    confidence: float
    entities: List[Dict[str, any]]
    reasoning: str
    method: str


class WorkflowKnowledgeBase:
    """工艺知识库 - 为LLM提供上下文信息"""
    
    def __init__(self):
        self.PROCESS_HIERARCHY = {
            "外圆工艺": {
                "description": "车削工件外表面的加工工艺",
                "sub_processes": {
                    "外圆": "车削圆柱形外表面",
                    "外锥面": "车削锥形外表面", 
                    "外圆弧": "车削圆弧形外表面"
                },
                "common_params": ["直径", "长度", "进给速度", "转速", "切削深度"],
                "keywords": ["外圆", "外径", "车外圆", "外表面"]
            },
            "端面工艺": {
                "description": "加工工件端面的工艺",
                "sub_processes": {
                    "端面": "车削平整端面",
                    "切槽": "在端面切削槽形",
                    "内端面": "加工内侧端面"
                },
                "common_params": ["深度", "宽度", "进给速度", "转速"],
                "keywords": ["端面", "车端面", "切槽", "开槽"]
            },
            "里孔工艺": {
                "description": "加工工件内孔的工艺",
                "sub_processes": {
                    "内圆": "镗削圆形内孔",
                    "内锥面": "镗削锥形内孔",
                    "内槽": "在内孔切削槽形",
                    "内弧": "镗削圆弧形内孔",
                    "中心孔": "加工中心定位孔"
                },
                "common_params": ["内径", "深度", "进给速度", "转速"],
                "keywords": ["内孔", "内径", "镗孔", "内圆"]
            },
            "锥面工艺": {
                "description": "加工锥形表面的工艺",
                "sub_processes": {
                    "外正锥面": "车削外正锥面",
                    "外反锥面": "车削外反锥面", 
                    "内正锥面": "镗削内正锥面",
                    "内反锥面": "镗削内反锥面"
                },
                "common_params": ["锥度", "长度", "大径", "小径"],
                "keywords": ["锥面", "锥度", "正锥", "反锥"]
            },
            "螺纹工艺": {
                "description": "加工螺纹的工艺",
                "sub_processes": {
                    "外直螺纹": "车削外直螺纹",
                    "外锥（管）螺纹": "车削外锥螺纹",
                    "内直螺纹": "攻制内直螺纹", 
                    "内锥（管）螺纹": "攻制内锥螺纹"
                },
                "common_params": ["螺距", "直径", "长度", "螺纹类型"],
                "keywords": ["螺纹", "螺牙", "丝扣", "攻螺纹"]
            },
            "倒角工艺": {
                "description": "去除工件锐边的工艺",
                "sub_processes": {
                    "外圆角倒角": "外圆角倒角处理",
                    "外倒角": "外侧倒角处理",
                    "内圆角倒角": "内圆角倒角处理",
                    "内倒角": "内侧倒角处理"
                },
                "common_params": ["倒角尺寸", "倒角角度"],
                "keywords": ["倒角", "去毛刺", "圆角", "倒边"]
            }
        }
    
    def get_context_for_llm(self) -> str:
        """为LLM生成工艺知识上下文"""
        context_parts = ["数控加工工艺知识库：\n"]
        
        for main_process, info in self.PROCESS_HIERARCHY.items():
            context_parts.append(f"## {main_process}")
            context_parts.append(f"- 描述：{info['description']}")
            context_parts.append("- 子工艺：")
            for sub_name, sub_desc in info['sub_processes'].items():
                context_parts.append(f"  * {sub_name}：{sub_desc}")
            context_parts.append(f"- 常见参数：{', '.join(info['common_params'])}")
            context_parts.append(f"- 关键词：{', '.join(info['keywords'])}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_similar_processes(self, query: str, top_k: int = 3) -> List[str]:
        """获取与查询最相似的工艺"""
        # 简单的关键词匹配，可以用BERT增强
        similarities = []
        query_lower = query.lower()
        
        for main_process, info in self.PROCESS_HIERARCHY.items():
            score = 0
            # 检查关键词匹配
            for keyword in info['keywords']:
                if keyword.lower() in query_lower:
                    score += len(keyword) / len(query)
            
            # 检查子工艺匹配
            for sub_name in info['sub_processes'].keys():
                if sub_name.lower() in query_lower:
                    score += len(sub_name) / len(query) * 1.5  # 子工艺权重更高
            
            if score > 0:
                similarities.append((main_process, score))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [proc for proc, _ in similarities[:top_k]]


class ContextAwareLLMPromptBuilder:
    """上下文感知的LLM提示构建器"""
    
    def __init__(self, knowledge_base: WorkflowKnowledgeBase):
        self.kb = knowledge_base
        
        # 使用BERT增强上下文理解（如果可用）
        if HAS_TRANSFORMERS:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-bert-wwm-ext")
                self.model = AutoModel.from_pretrained("hfl/chinese-bert-wwm-ext")
                self.model.eval()
                self.has_bert = True
                print("BERT模型加载成功，将用于增强上下文理解")
            except Exception as e:
                print(f"BERT模型加载失败: {e}")
                self.has_bert = False
        else:
            self.has_bert = False
    
    def build_enhanced_prompt(self, user_input: str, conversation_history: List[str] = None) -> str:
        """构建增强的LLM提示"""
        
        # 1. 获取相关工艺上下文
        relevant_processes = self.kb.get_similar_processes(user_input)
        
        # 2. 构建上下文信息
        context_info = ""
        if relevant_processes:
            context_info = "相关工艺参考：\n"
            for proc in relevant_processes:
                proc_info = self.kb.PROCESS_HIERARCHY[proc]
                context_info += f"- {proc}：{proc_info['description']}\n"
                for sub_name, sub_desc in proc_info['sub_processes'].items():
                    context_info += f"  * {sub_name}：{sub_desc}\n"
        
        # 3. 使用BERT增强语义理解（如果可用）
        semantic_enhancement = ""
        if self.has_bert:
            semantic_enhancement = self._get_semantic_context(user_input)
        
        # 4. 构建完整提示
        prompt = f"""你是一个专业的数控加工工艺识别专家。请根据用户的描述，准确识别出所需的加工工艺类型。

{context_info}

{semantic_enhancement}

任务要求：
1. 从用户输入中识别主工艺类型和子工艺类型
2. 提取所有相关的加工参数
3. 评估识别结果的置信度（0-1之间）
4. 提供详细的推理过程

严格按照以下JSON格式返回结果，不要包含任何其他文字：
{{
    "main_process": "主工艺名称或NO_PROCESS",
    "sub_process": "子工艺名称或null", 
    "confidence": 0.85,
    "extracted_params": {{
        "参数名": "参数值",
        "进给速度": "300",
        "长度": "50"
    }},
    "reasoning": "详细的推理过程说明"
}}

用户输入：{user_input}

请分析并返回结果："""

        return prompt
    
    def _get_semantic_context(self, text: str) -> str:
        """使用BERT获取语义上下文信息"""
        if not self.has_bert:
            return ""
        
        try:
            # 获取文本的BERT向量
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
                text_embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
            
            # 与工艺描述计算语义相似度
            most_similar = []
            for main_proc, info in self.kb.PROCESS_HIERARCHY.items():
                proc_desc = info['description']
                desc_inputs = self.tokenizer(proc_desc, return_tensors="pt", padding=True, truncation=True)
                with torch.no_grad():
                    desc_outputs = self.model(**desc_inputs)
                    desc_embedding = desc_outputs.last_hidden_state[:, 0, :].numpy()[0]
                
                similarity = cosine_similarity(
                    text_embedding.reshape(1, -1),
                    desc_embedding.reshape(1, -1)
                )[0][0]
                
                most_similar.append((main_proc, similarity))
            
            most_similar.sort(key=lambda x: x[1], reverse=True)
            
            if most_similar[0][1] > 0.3:
                return f"语义分析：输入文本与'{most_similar[0][0]}'最相似（相似度：{most_similar[0][1]:.2f}）\n"
            
        except Exception as e:
            print(f"BERT语义分析失败: {e}")
        
        return ""


class LLMIntentClassifier:
    """基于大语言模型的核心意图分类器"""
    
    def __init__(self):
        self.knowledge_base = WorkflowKnowledgeBase()
        self.prompt_builder = ContextAwareLLMPromptBuilder(self.knowledge_base)
        self.client = ClientFactory().get_client()
    
    def classify_intent(self, user_input: str, conversation_history: List[str] = None) -> IntentResult:
        """
        使用大语言模型进行意图分类
        
        Args:
            user_input: 用户输入文本
            conversation_history: 对话历史（可选）
            
        Returns:
            IntentResult: 分类结果
        """
        try:
            # 1. 构建增强提示
            enhanced_prompt = self.prompt_builder.build_enhanced_prompt(user_input, conversation_history)
            
            # 2. 调用大语言模型
            llm_response = self.client.chat_with_ai(enhanced_prompt)
            
            # 3. 解析LLM响应
            parsed_result = self._parse_llm_response(llm_response, user_input)
            
            return IntentResult(
                main_process=parsed_result.get("main_process", "NO_PROCESS"),
                sub_process=parsed_result.get("sub_process"),
                confidence=parsed_result.get("confidence", 0.8),
                entities=self._format_entities(parsed_result.get("extracted_params", {})),
                reasoning=parsed_result.get("reasoning", "基于大语言模型分析"),
                method="Enhanced_LLM_with_BERT" if self.prompt_builder.has_bert else "Enhanced_LLM"
            )
            
        except Exception as e:
            print(f"LLM意图识别失败: {e}")
            # 返回错误结果，不使用后备方案（保持LLM为核心）
            return IntentResult(
                main_process="NO_PROCESS",
                sub_process=None,
                confidence=0.0,
                entities=[],
                reasoning=f"LLM处理失败: {str(e)}",
                method="LLM_Error"
            )
    
    def _parse_llm_response(self, response: str, original_input: str) -> Dict:
        """解析LLM的JSON响应"""
        try:
            # 清理响应文本
            response = response.strip()
            
            # 提取JSON部分
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
            elif '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                response = response[start:end]
            
            result = json.loads(response)
            
            # 验证结果格式
            required_fields = ["main_process", "sub_process", "confidence", "reasoning"]
            for field in required_fields:
                if field not in result:
                    result[field] = None if field != "confidence" else 0.5
            
            return result
            
        except Exception as e:
            print(f"解析LLM响应失败: {e}")
            print(f"原始响应: {response}")
            
            # 使用正则表达式作为后备解析方法
            return self._fallback_parse(response, original_input)
    
    def _fallback_parse(self, response: str, original_input: str) -> Dict:
        """后备解析方法"""
        result = {
            "main_process": "NO_PROCESS",
            "sub_process": None,
            "confidence": 0.3,
            "extracted_params": {},
            "reasoning": "使用后备解析方法"
        }
        
        # 尝试从响应中提取工艺信息
        for main_proc in self.knowledge_base.PROCESS_HIERARCHY.keys():
            if main_proc in response:
                result["main_process"] = main_proc
                result["confidence"] = 0.6
                break
        
        return result
    
    def _format_entities(self, params: Dict[str, str]) -> List[Dict]:
        """格式化参数实体"""
        entities = []
        for param_name, param_value in params.items():
            try:
                # 尝试转换为数值
                if isinstance(param_value, str) and param_value.replace('.', '').isdigit():
                    value = float(param_value)
                else:
                    value = param_value
                
                entities.append({
                    'type': param_name,
                    'value': value,
                    'text': f"{param_name}={param_value}",
                    'source': 'LLM_extraction'
                })
            except:
                continue
        
        return entities


class EnhancedIntentClassifier:
    """增强的意图识别主类 - 以大语言模型为核心"""
    
    def __init__(self):
        self.llm_classifier = LLMIntentClassifier()
    
    def classify(self, text: str, conversation_history: List[str] = None) -> Dict[str, any]:
        """
        使用增强的大语言模型进行意图分类
        
        Args:
            text: 用户输入文本
            conversation_history: 对话历史
            
        Returns:
            Dict: 分类结果
        """
        result = self.llm_classifier.classify_intent(text, conversation_history)
        
        return {
            "main_process": result.main_process,
            "sub_process": result.sub_process,
            "confidence": result.confidence,
            "entities": result.entities,
            "reasoning": result.reasoning,
            "method": result.method
        }


# 全局实例
_enhanced_classifier = None

def get_enhanced_intent_classifier() -> EnhancedIntentClassifier:
    """获取增强意图分类器单例"""
    global _enhanced_classifier
    if _enhanced_classifier is None:
        _enhanced_classifier = EnhancedIntentClassifier()
    return _enhanced_classifier


# 兼容性接口
def enhanced_llm_parse_process_type(question: str) -> dict:
    """
    基于增强大语言模型的工艺类型解析
    
    Args:
        question: 用户输入的问题
        
    Returns:
        dict: 解析结果
    """
    classifier = get_enhanced_intent_classifier()
    result = classifier.classify(question)
    
    return {
        "main_process": result["main_process"],
        "sub_process": result["sub_process"],
        "parameters": {entity['type']: entity['value'] for entity in result.get("entities", [])},
        "confidence": result.get("confidence", 0.0),
        "reasoning": result.get("reasoning", ""),
        "method": result.get("method", "Enhanced_LLM")
    }


if __name__ == "__main__":
    # 测试代码
    import os
    os.environ['PY_ENVIRONMENT'] = 'local'
    
    classifier = EnhancedIntentClassifier()
    
    test_cases = [
        "我要加工外圆，长度是50mm，进给速度300",
        "请帮我车一个内孔，直径20",
        "外螺纹加工，M10螺纹",
        "切一个槽，深度5mm"
    ]
    
    for test_text in test_cases:
        print(f"\n测试文本: {test_text}")
        result = classifier.classify(test_text)
        print(f"结果: {result}")