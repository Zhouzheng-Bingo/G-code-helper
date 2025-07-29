# -*- coding: utf-8 -*-
"""
基于BERT的意图识别模块
作者: Claude Code
功能: 使用BERT模型进行工艺类型识别和实体抽取
"""

import json
import os
import re
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("Warning: transformers/torch not installed. Using fallback to LLM method.")

from lang_chain.client.client_factory import ClientFactory


@dataclass
class IntentResult:
    """意图识别结果"""
    main_process: str
    sub_process: Optional[str]
    confidence: float
    entities: List[Dict[str, any]]
    reasoning: str


class ProcessMatcher:
    """工艺匹配器 - 基于语义相似度的工艺识别"""
    
    def __init__(self):
        # 工艺映射表
        self.PROCESS_MAPPING = {
            "外圆工艺": ["外圆", "外锥面", "外圆弧"],
            "端面工艺": ["端面", "切槽", "内端面"],
            "里孔工艺": ["内圆", "内锥面", "内槽", "内弧", "中心孔"],
            "锥面工艺": ["外正锥面", "外反锥面", "内正锥面", "内反锥面"],
            "螺纹工艺": ["外直螺纹", "外锥（管）螺纹", "内直螺纹", "内锥（管）螺纹"],
            "倒角工艺": ["外圆角倒角", "外倒角", "内圆角倒角", "内倒角"]
        }
        
        # 扩展关键词映射
        self.KEYWORD_MAPPING = {
            # 外圆工艺相关
            "外圆": ["外圆", "外径", "外表面", "车外圆", "外圆加工"],
            "外锥面": ["外锥", "外锥面", "外锥度", "锥度外圆"],
            "外圆弧": ["外圆弧", "外弧", "圆弧外表面"],
            
            # 端面工艺相关
            "端面": ["端面", "端面加工", "车端面", "平端面"],
            "切槽": ["切槽", "槽加工", "开槽", "切割槽"],
            "内端面": ["内端面", "内侧端面"],
            
            # 里孔工艺相关
            "内圆": ["内圆", "内径", "内孔", "镗孔", "内圆加工"],
            "内锥面": ["内锥", "内锥面", "内锥孔", "锥孔"],
            "内槽": ["内槽", "内切槽", "孔内槽"],
            "内弧": ["内弧", "内圆弧", "孔内弧"],
            "中心孔": ["中心孔", "顶尖孔", "中心定位孔"],
            
            # 锥面工艺相关
            "外正锥面": ["外正锥", "外正锥面"],
            "外反锥面": ["外反锥", "外反锥面"],
            "内正锥面": ["内正锥", "内正锥面"],
            "内反锥面": ["内反锥", "内反锥面"],
            
            # 螺纹工艺相关
            "外直螺纹": ["外螺纹", "外直螺纹", "车外螺纹"],
            "外锥（管）螺纹": ["外锥螺纹", "外管螺纹", "锥管螺纹"],
            "内直螺纹": ["内螺纹", "内直螺纹", "攻螺纹"],
            "内锥（管）螺纹": ["内锥螺纹", "内管螺纹"],
            
            # 倒角工艺相关
            "外圆角倒角": ["外圆角", "外倒圆角"],
            "外倒角": ["外倒角", "外侧倒角"],
            "内圆角倒角": ["内圆角", "内倒圆角"],
            "内倒角": ["内倒角", "内侧倒角"]
        }
    
    def match_by_keywords(self, text: str) -> Tuple[str, Optional[str], float]:
        """基于关键词匹配工艺类型"""
        text_lower = text.lower()
        best_match = ("NO_PROCESS", None, 0.0)
        
        # 遍历所有子工艺
        for main_process, sub_processes in self.PROCESS_MAPPING.items():
            for sub_process in sub_processes:
                if sub_process in self.KEYWORD_MAPPING:
                    keywords = self.KEYWORD_MAPPING[sub_process]
                    for keyword in keywords:
                        if keyword.lower() in text_lower:
                            # 计算匹配度：关键词长度越长，匹配度越高
                            confidence = len(keyword) / len(text) + 0.1
                            if confidence > best_match[2]:
                                best_match = (main_process, sub_process, min(confidence, 1.0))
        
        return best_match


class EntityExtractor:
    """实体抽取器 - 从文本中提取加工参数"""
    
    def __init__(self):
        # 参数模式匹配
        self.PARAM_PATTERNS = {
            # 数值参数
            'length': [r'长度?[:：=是为]\s*(\d+(?:\.\d+)?)', r'L[:：=]\s*(\d+(?:\.\d+)?)', r'(\d+(?:\.\d+)?)\s*mm'],
            'diameter': [r'直径[:：=是为]\s*(\d+(?:\.\d+)?)', r'φ\s*(\d+(?:\.\d+)?)', r'直径\s*(\d+(?:\.\d+)?)'],
            'depth': [r'深度[:：=是为]\s*(\d+(?:\.\d+)?)', r'深\s*(\d+(?:\.\d+)?)', r'Z\s*(\d+(?:\.\d+)?)'],
            'feed_rate': [r'进给[:：=是为]\s*(\d+(?:\.\d+)?)', r'F[:：=]\s*(\d+(?:\.\d+)?)', r'进给速度\s*(\d+(?:\.\d+)?)'],
            'speed': [r'转速[:：=是为]\s*(\d+(?:\.\d+)?)', r'S[:：=]\s*(\d+(?:\.\d+)?)', r'主轴转速\s*(\d+(?:\.\d+)?)'],
            'count': [r'圈数[:：=是为]\s*(\d+)', r'循环\s*(\d+)', r'次数\s*(\d+)'],
            
            # 坐标参数
            'x_coord': [r'X[:：=]\s*(\d+(?:\.\d+)?)', r'X坐标\s*(\d+(?:\.\d+)?)'],
            'y_coord': [r'Y[:：=]\s*(\d+(?:\.\d+)?)', r'Y坐标\s*(\d+(?:\.\d+)?)'],
            'z_coord': [r'Z[:：=]\s*(\d+(?:\.\d+)?)', r'Z坐标\s*(\d+(?:\.\d+)?)'],
        }
    
    def extract_entities(self, text: str) -> List[Dict[str, any]]:
        """从文本中提取实体参数"""
        entities = []
        
        for param_type, patterns in self.PARAM_PATTERNS.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        value = float(match.group(1))
                        entities.append({
                            'type': param_type,
                            'value': value,
                            'text': match.group(0),
                            'start': match.start(),
                            'end': match.end()
                        })
                    except (ValueError, IndexError):
                        continue
        
        return entities


class BERTIntentClassifier:
    """基于BERT的意图分类器"""
    
    def __init__(self, model_name: str = "hfl/chinese-bert-wwm-ext"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.process_matcher = ProcessMatcher()
        self.entity_extractor = EntityExtractor()
        
        if HAS_TRANSFORMERS:
            self._initialize_bert_model()
    
    def _initialize_bert_model(self):
        """初始化BERT模型"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.eval()
            print(f"BERT模型 {self.model_name} 初始化成功")
        except Exception as e:
            print(f"BERT模型初始化失败: {e}")
            print("将使用关键词匹配作为后备方案")
            self.tokenizer = None
            self.model = None
    
    def _get_bert_embedding(self, text: str) -> np.ndarray:
        """获取文本的BERT嵌入向量"""
        if not self.tokenizer or not self.model:
            return None
        
        try:
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                # 使用[CLS]标记的向量作为句子表示
                embeddings = outputs.last_hidden_state[:, 0, :].numpy()
            return embeddings[0]
        except Exception as e:
            print(f"获取BERT嵌入向量失败: {e}")
            return None
    
    def _compute_semantic_similarity(self, text: str, reference_texts: List[str]) -> List[float]:
        """计算语义相似度"""
        text_embedding = self._get_bert_embedding(text)
        if text_embedding is None:
            return [0.0] * len(reference_texts)
        
        similarities = []
        for ref_text in reference_texts:
            ref_embedding = self._get_bert_embedding(ref_text)
            if ref_embedding is not None:
                similarity = cosine_similarity(
                    text_embedding.reshape(1, -1),
                    ref_embedding.reshape(1, -1)
                )[0][0]
                similarities.append(float(similarity))
            else:
                similarities.append(0.0)
        
        return similarities
    
    def classify_intent(self, text: str) -> IntentResult:
        """
        对输入文本进行意图分类
        
        Args:
            text: 用户输入的文本
            
        Returns:
            IntentResult: 意图识别结果
        """
        # 1. 实体抽取
        entities = self.entity_extractor.extract_entities(text)
        
        # 2. 工艺匹配 - 优先使用BERT语义匹配
        if self.tokenizer and self.model:
            main_process, sub_process, confidence = self._semantic_match(text)
        else:
            # 后备方案：关键词匹配
            main_process, sub_process, confidence = self.process_matcher.match_by_keywords(text)
        
        # 3. 生成推理说明
        reasoning = self._generate_reasoning(text, main_process, sub_process, entities)
        
        return IntentResult(
            main_process=main_process,
            sub_process=sub_process,
            confidence=confidence,
            entities=entities,
            reasoning=reasoning
        )
    
    def _semantic_match(self, text: str) -> Tuple[str, Optional[str], float]:
        """基于BERT语义匹配工艺类型"""
        best_match = ("NO_PROCESS", None, 0.0)
        
        # 构建参考文本列表
        reference_texts = []
        process_mapping = []
        
        for main_process, sub_processes in self.process_matcher.PROCESS_MAPPING.items():
            for sub_process in sub_processes:
                # 为每个子工艺构建描述性文本
                description = f"进行{sub_process}加工操作"
                reference_texts.append(description)
                process_mapping.append((main_process, sub_process))
        
        # 计算语义相似度
        similarities = self._compute_semantic_similarity(text, reference_texts)
        
        if similarities:
            max_idx = np.argmax(similarities)
            max_similarity = similarities[max_idx]
            
            if max_similarity > 0.3:  # 设置相似度阈值
                main_process, sub_process = process_mapping[max_idx]
                best_match = (main_process, sub_process, max_similarity)
        
        # 如果BERT匹配效果不好，使用关键词匹配作为后备
        if best_match[2] < 0.5:
            keyword_match = self.process_matcher.match_by_keywords(text)
            if keyword_match[2] > best_match[2]:
                best_match = keyword_match
        
        return best_match
    
    def _generate_reasoning(self, text: str, main_process: str, sub_process: Optional[str], entities: List[Dict]) -> str:
        """生成推理说明"""
        reasoning_parts = []
        
        if main_process != "NO_PROCESS":
            reasoning_parts.append(f"识别到主工艺: {main_process}")
            if sub_process:
                reasoning_parts.append(f"识别到子工艺: {sub_process}")
        else:
            reasoning_parts.append("未识别到明确的加工工艺")
        
        if entities:
            entity_info = []
            for entity in entities:
                entity_info.append(f"{entity['type']}={entity['value']}")
            reasoning_parts.append(f"提取到参数: {', '.join(entity_info)}")
        
        return "; ".join(reasoning_parts)


class IntentClassifier:
    """意图识别主类 - 对外统一接口"""
    
    def __init__(self):
        self.bert_classifier = BERTIntentClassifier()
        self.fallback_enabled = True
    
    def classify(self, text: str) -> Dict[str, any]:
        """
        对输入文本进行意图分类
        
        Args:
            text: 用户输入的文本
            
        Returns:
            Dict: 兼容原有接口的结果格式
        """
        try:
            # 使用BERT分类器
            result = self.bert_classifier.classify_intent(text)
            
            return {
                "main_process": result.main_process,
                "sub_process": result.sub_process,
                "confidence": result.confidence,
                "entities": result.entities,
                "reasoning": result.reasoning,
                "method": "BERT" if HAS_TRANSFORMERS else "Keywords"
            }
            
        except Exception as e:
            print(f"BERT意图识别失败: {e}")
            
            # 后备方案：使用原有的LLM方法
            if self.fallback_enabled:
                return self._fallback_to_llm(text)
            else:
                return {
                    "main_process": "NO_PROCESS",
                    "sub_process": None,
                    "confidence": 0.0,
                    "entities": [],
                    "reasoning": f"分类失败: {str(e)}",
                    "method": "Error"
                }
    
    def _fallback_to_llm(self, text: str) -> Dict[str, any]:
        """后备方案：使用原有的LLM方法"""
        try:
            # 导入原有函数
            from qa.function_tool import identify_process_type
            result = identify_process_type(text)
            
            return {
                "main_process": result.get("main_process", "NO_PROCESS"),
                "sub_process": result.get("sub_process"),
                "confidence": 0.8,  # LLM方法假设有较高置信度
                "entities": [],
                "reasoning": "使用大语言模型进行工艺识别",
                "method": "LLM_Fallback"
            }
        except Exception as e:
            print(f"LLM后备方案也失败: {e}")
            return {
                "main_process": "NO_PROCESS",
                "sub_process": None,
                "confidence": 0.0,
                "entities": [],
                "reasoning": f"所有方法都失败: {str(e)}",
                "method": "Error"
            }


# 全局实例
_intent_classifier = None

def get_intent_classifier() -> IntentClassifier:
    """获取意图分类器单例"""
    global _intent_classifier
    if _intent_classifier is None:
        _intent_classifier = IntentClassifier()
    return _intent_classifier


# 兼容性函数 - 保持与原有代码的接口一致
def enhanced_parse_process_type(question: str) -> dict:
    """
    增强版工艺类型解析 - 兼容原有接口
    
    Args:
        question: 用户输入的问题
        
    Returns:
        dict: 解析结果，包含主工艺类型、子工艺类型和参数
    """
    classifier = get_intent_classifier()
    result = classifier.classify(question)
    
    return {
        "main_process": result["main_process"],
        "sub_process": result["sub_process"],
        "parameters": {entity['type']: entity['value'] for entity in result.get("entities", [])},
        "confidence": result.get("confidence", 0.0),
        "reasoning": result.get("reasoning", ""),
        "method": result.get("method", "Unknown")
    }


if __name__ == "__main__":
    # 测试代码
    classifier = IntentClassifier()
    
    test_cases = [
        "我要加工外圆，长度是50mm，进给速度300",
        "请帮我车一个内孔，直径20",
        "外螺纹加工，M10螺纹",
        "切一个槽，深度5mm",
        "倒角处理",
        "这是什么意思？"
    ]
    
    for test_text in test_cases:
        print(f"\n测试文本: {test_text}")
        result = classifier.classify(test_text)
        print(f"结果: {result}")