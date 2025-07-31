# -*- coding: utf-8 -*-
"""
简化的意图识别模块测试脚本 - 不依赖完整环境
"""

import sys
import os
import re
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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

class SimpleIntentClassifier:
    """简化的意图分类器 - 用于测试"""
    
    def __init__(self):
        self.process_matcher = ProcessMatcher()
        self.entity_extractor = EntityExtractor()
    
    def classify(self, text: str) -> Dict[str, any]:
        """对输入文本进行意图分类"""
        # 1. 实体抽取
        entities = self.entity_extractor.extract_entities(text)
        
        # 2. 工艺匹配
        main_process, sub_process, confidence = self.process_matcher.match_by_keywords(text)
        
        # 3. 生成推理说明
        reasoning = self._generate_reasoning(text, main_process, sub_process, entities)
        
        return {
            "main_process": main_process,
            "sub_process": sub_process,
            "confidence": confidence,
            "entities": entities,
            "reasoning": reasoning,
            "method": "Keywords"
        }
    
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

def test_simple_intent_classification():
    """测试简化版意图识别功能"""
    print("=" * 60)
    print("简化版意图识别模块测试")
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
    
    classifier = SimpleIntentClassifier()
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\n[测试 {i}] 输入: {test_text}")
        print("-" * 40)
        
        try:
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
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    try:
        test_simple_intent_classification()
        
        print("\n" + "=" * 60)
        print("简化版测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()