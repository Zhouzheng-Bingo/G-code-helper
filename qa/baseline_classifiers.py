# -*- coding: utf-8 -*-
"""
基线意图识别方法，用于对比实验
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class BaselineResult:
    """基线方法的结果格式"""
    main_process: str
    sub_process: Optional[str]
    confidence: float
    method: str
    parameters: Dict[str, any] = None


class KeywordBasedClassifier:
    """基线方法1：基于关键词匹配的分类器"""
    
    def __init__(self):
        # 定义关键词映射
        self.process_keywords = {
            "外圆工艺": ["外圆", "外径", "外表面", "外圆柱"],
            "端面工艺": ["端面", "切槽", "槽"],
            "里孔工艺": ["内孔", "内圆", "内径", "孔", "镗孔", "镗"],
            "锥面工艺": ["锥面", "锥度", "斜面"],
            "螺纹工艺": ["螺纹", "螺牙", "攻丝"],
            "倒角工艺": ["倒角", "圆角", "去毛刺"]
        }
        
        self.sub_process_keywords = {
            "外圆": ["外圆", "圆柱"],
            "外锥面": ["外锥", "外斜面"],
            "端面": ["端面", "平面"],
            "切槽": ["切槽", "开槽", "槽"],
            "内圆": ["内圆", "内孔", "孔"],
            "内锥面": ["内锥", "内斜面"],
            "外直螺纹": ["外螺纹", "外牙"],
            "内直螺纹": ["内螺纹", "内牙", "攻丝"],
            "外倒角": ["外倒角", "外圆角"],
            "内倒角": ["内倒角", "内圆角"]
        }
    
    def classify(self, text: str) -> BaselineResult:
        """基于关键词的分类"""
        text_lower = text.lower()
        
        # 查找主工艺
        main_process = "NO_PROCESS"
        max_score = 0
        
        for process, keywords in self.process_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > max_score:
                max_score = score
                main_process = process
        
        # 查找子工艺
        sub_process = None
        if main_process != "NO_PROCESS":
            for sub, keywords in self.sub_process_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    sub_process = sub
                    break
        
        # 简单的置信度计算
        confidence = min(max_score * 0.3, 0.9) if max_score > 0 else 0.1
        
        # 提取参数（简单正则）
        parameters = {}
        # 匹配 Cn=2 这样的模式
        param_pattern = r'([A-Za-z]+)\s*[=是]\s*(\d+(?:\.\d+)?)'
        matches = re.findall(param_pattern, text)
        for param, value in matches:
            parameters[param] = float(value) if '.' in value else int(value)
        
        # 匹配 "长度100mm" 这样的模式
        if "长度" in text_lower:
            length_match = re.search(r'长度\s*(\d+(?:\.\d+)?)', text_lower)
            if length_match:
                parameters["L"] = float(length_match.group(1))
        
        return BaselineResult(
            main_process=main_process,
            sub_process=sub_process,
            confidence=confidence,
            method="Keyword_Matching",
            parameters=parameters
        )


class RuleBasedClassifier:
    """基线方法2：基于规则的分类器"""
    
    def __init__(self):
        # 定义规则模板
        self.rules = [
            # (pattern, main_process, sub_process, confidence)
            (r'(使用|用)?外圆工艺.*(加工|车削?)?.*外圆', "外圆工艺", "外圆", 0.9),
            (r'车.*(外圆|外径)', "外圆工艺", "外圆", 0.85),
            (r'(使用|用)?里孔工艺.*(加工|镗)?.*内圆', "里孔工艺", "内圆", 0.9),
            (r'(镗|车).*(内孔|孔)', "里孔工艺", "内圆", 0.85),
            (r'(车|加工).*端面', "端面工艺", "端面", 0.85),
            (r'切槽|开槽', "端面工艺", "切槽", 0.9),
            (r'(车|加工).*螺纹', "螺纹工艺", None, 0.8),
            (r'外螺纹', "螺纹工艺", "外直螺纹", 0.9),
            (r'内螺纹|攻丝', "螺纹工艺", "内直螺纹", 0.9),
            (r'倒角|去毛刺', "倒角工艺", None, 0.8),
        ]
    
    def classify(self, text: str) -> BaselineResult:
        """基于规则的分类"""
        text_lower = text.lower()
        
        # 应用规则
        for pattern, main_process, sub_process, base_confidence in self.rules:
            if re.search(pattern, text_lower):
                # 提取参数
                parameters = self._extract_parameters(text)
                
                # 调整置信度
                confidence = base_confidence
                if parameters:
                    confidence = min(confidence + 0.05, 0.95)
                
                return BaselineResult(
                    main_process=main_process,
                    sub_process=sub_process,
                    confidence=confidence,
                    method="Rule_Based",
                    parameters=parameters
                )
        
        # 没有匹配任何规则
        return BaselineResult(
            main_process="NO_PROCESS",
            sub_process=None,
            confidence=0.1,
            method="Rule_Based",
            parameters={}
        )
    
    def _extract_parameters(self, text: str) -> Dict[str, any]:
        """提取参数"""
        parameters = {}
        
        # 参数提取规则
        param_rules = [
            (r'Cn\s*[=是:]\s*(\d+)', 'Cn', int),
            (r'L\s*[=是:]\s*(\d+(?:\.\d+)?)', 'L', float),
            (r'长度\s*[=是:：]?\s*(\d+(?:\.\d+)?)', 'L', float),
            (r'直径\s*[=是:：]?\s*(\d+(?:\.\d+)?)', 'D', float),
            (r'深度\s*[=是:：]?\s*(\d+(?:\.\d+)?)', 'depth', float),
            (r'进给\s*[=是:：]?\s*(\d+(?:\.\d+)?)', 'F', float),
        ]
        
        for pattern, param_name, param_type in param_rules:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    parameters[param_name] = param_type(match.group(1))
                except ValueError:
                    pass
        
        return parameters


# 如果安装了transformers，可以实现BERT分类器
try:
    from transformers import AutoTokenizer, AutoModel
    import torch
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity
    
    class BERTOnlyClassifier:
        """基线方法3：仅使用BERT的分类器（不用LLM）"""
        
        def __init__(self):
            try:
                self.tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-bert-wwm-ext")
                self.model = AutoModel.from_pretrained("hfl/chinese-bert-wwm-ext")
                self.model.eval()
                
                # 预定义每个工艺的描述
                self.process_descriptions = {
                    "外圆工艺": "车削加工工件的外圆表面，获得所需的直径和表面质量",
                    "端面工艺": "车削加工工件的端面，获得平整的端面表面",
                    "里孔工艺": "镗削加工工件的内孔，获得所需的内径和孔表面质量",
                    "锥面工艺": "车削或镗削锥形表面，获得特定的锥度",
                    "螺纹工艺": "车削或攻制螺纹，获得标准的螺纹牙形",
                    "倒角工艺": "去除工件的锐边毛刺，获得倒角或圆角"
                }
                
                # 预计算工艺描述的向量
                self.process_embeddings = {}
                for process, desc in self.process_descriptions.items():
                    self.process_embeddings[process] = self._get_embedding(desc)
                    
            except Exception as e:
                print(f"BERT模型加载失败: {e}")
                raise
        
        def _get_embedding(self, text: str) -> np.ndarray:
            """获取文本的BERT嵌入向量"""
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, 
                                   truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                # 使用[CLS]向量作为句子表示
                embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
            return embedding
        
        def classify(self, text: str) -> BaselineResult:
            """基于BERT相似度的分类"""
            # 获取输入文本的嵌入
            text_embedding = self._get_embedding(text)
            
            # 计算与各工艺的相似度
            similarities = {}
            for process, process_embedding in self.process_embeddings.items():
                sim = cosine_similarity(
                    text_embedding.reshape(1, -1),
                    process_embedding.reshape(1, -1)
                )[0][0]
                similarities[process] = sim
            
            # 选择相似度最高的工艺
            main_process = max(similarities, key=similarities.get)
            confidence = similarities[main_process]
            
            # 如果相似度太低，认为不是工艺相关
            if confidence < 0.3:
                main_process = "NO_PROCESS"
                confidence = 0.1
            
            # BERT方法不擅长提取子工艺和参数
            sub_process = None
            parameters = {}
            
            return BaselineResult(
                main_process=main_process,
                sub_process=sub_process,
                confidence=float(confidence),
                method="BERT_Only",
                parameters=parameters
            )
    
    HAS_BERT = True
except ImportError:
    HAS_BERT = False
    
    class BERTOnlyClassifier:
        """BERT不可用时的占位类"""
        def __init__(self):
            raise NotImplementedError("BERT模型未安装，无法使用BERTOnlyClassifier")
        
        def classify(self, text: str) -> BaselineResult:
            raise NotImplementedError("BERT模型未安装")