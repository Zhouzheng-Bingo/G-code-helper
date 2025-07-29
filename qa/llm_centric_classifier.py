# -*- coding: utf-8 -*-
"""
大语言模型驱动的意图识别系统
核心理念：大语言模型是主要技术，BERT和其他技术只是辅助增强
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

from lang_chain.client.client_factory import ClientFactory


@dataclass
class EnhancedIntentResult:
    """增强的意图识别结果"""
    main_process: str
    sub_process: Optional[str]
    confidence: float
    entities: List[Dict[str, any]]
    reasoning: str
    method: str
    llm_confidence: float  # LLM自身的置信度
    enhancement_info: Dict[str, any]  # 增强技术的贡献信息


class LLMEnhancementEngine:
    """大语言模型增强引擎 - 使用BERT等技术提升LLM效果"""
    
    def __init__(self):
        self.has_bert = False
        if HAS_TRANSFORMERS:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained("hfl/chinese-bert-wwm-ext")
                self.model = AutoModel.from_pretrained("hfl/chinese-bert-wwm-ext")
                self.model.eval()
                self.has_bert = True
                print("✅ BERT模型加载成功 - 将用于增强大语言模型的理解能力")
            except Exception as e:
                print(f"⚠️ BERT模型加载失败: {e} - 将使用纯大语言模型方法")
    
    def enhance_llm_prompt(self, user_input: str, conversation_history: List[str] = None) -> Tuple[str, Dict]:
        """
        使用BERT等技术增强大语言模型的提示
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史
            
        Returns:
            Tuple[增强后的提示, 增强信息]
        """
        enhancement_info = {
            "bert_analysis": None,
            "semantic_similarity": None,
            "context_enrichment": False
        }
        
        # 1. 基础工艺知识库
        process_knowledge = self._get_process_knowledge()
        
        # 2. BERT语义分析（如果可用）
        bert_analysis = ""
        if self.has_bert:
            bert_result = self._bert_semantic_analysis(user_input)
            if bert_result:
                bert_analysis = f"\n🧠 BERT语义分析结果：\n{bert_result}\n"
                enhancement_info["bert_analysis"] = bert_result
                enhancement_info["semantic_similarity"] = True
        
        # 3. 上下文丰富化
        context_enhancement = self._enrich_context(user_input, conversation_history)
        if context_enhancement:
            enhancement_info["context_enrichment"] = True
        
        # 4. 构建增强提示
        enhanced_prompt = f"""你是一个专业的数控加工工艺识别专家，具备深厚的机械加工理论知识和丰富的实践经验。

📚 数控加工工艺知识库：
{process_knowledge}

{bert_analysis}

{context_enhancement}

🎯 任务目标：
请基于你的专业知识，对用户的加工需求进行深入分析，识别出准确的工艺类型和参数。

📋 分析要求：
1. 仔细分析用户的表达方式和专业术语
2. 识别主工艺类型和具体的子工艺类型  
3. 提取所有相关的加工参数和数值（包括Cn、L、Tr、Cr、F等参数）
4. 评估你的识别结果的置信度（0.0-1.0）
5. 提供详细的专业推理过程

🔧 子工艺识别规则：
- 外圆工艺：
  * "外圆工艺加工一个外圆" → 子工艺是"外圆"
  * "外圆工艺加工外锥面" → 子工艺是"外锥面"  
  * "外圆工艺加工外圆弧" → 子工艺是"外圆弧"
- 端面工艺：
  * "端面工艺加工端面" → 子工艺是"端面"
  * "端面工艺切槽" → 子工艺是"切槽"
- 里孔工艺：
  * "里孔工艺加工内圆" → 子工艺是"内圆"
  * "里孔工艺加工内锥面" → 子工艺是"内锥面"

🔍 参数识别规则：
- Cn = 圈数/循环数
- L = 长度 (mm)
- Tr = 过渡半径/退刀量 (mm)  
- Cr = 退回半径 (mm)
- F = 进给速度 (mm/min)
- D = 直径 (mm)
- 其他数值参数也要提取

⚠️ 重要说明：
- 当用户说"外圆工艺加工一个外圆"时，主工艺是"外圆工艺"，子工艺是"外圆"
- 当用户提供参数如"Cn=2, L=100.0"时，务必提取所有参数
- 如果用户明确提到工艺和子工艺，不要遗漏任何信息
- 置信度要反映你对结果的确信程度

📤 输出格式：
请严格按照以下JSON格式返回结果，不要包含其他任何文字：

{{
    "main_process": "主工艺类型名称",
    "sub_process": "子工艺类型名称",
    "confidence": 0.95,
    "extracted_parameters": {{
        "Cn": "2",
        "L": "100.0",
        "Tr": "0.5",
        "Cr": "1.0", 
        "F": "300.0"
    }},
    "professional_reasoning": "用户明确提到了外圆工艺和外圆子工艺，并提供了完整的加工参数...",
    "llm_confidence": 0.95
}}

👤 用户需求：{user_input}

请开始专业分析："""

        return enhanced_prompt, enhancement_info
    
    def _get_process_knowledge(self) -> str:
        """获取工艺知识库"""
        return """
🔧 主要加工工艺类型：

1. 外圆工艺 - 车削工件外表面
   • 外圆：标准圆柱外表面车削
   • 外锥面：锥形外表面车削
   • 外圆弧：圆弧形外表面车削
   
2. 端面工艺 - 加工工件端面
   • 端面：平整端面车削
   • 切槽：端面槽形切削
   • 内端面：内侧端面加工
   
3. 里孔工艺 - 内孔加工
   • 内圆：圆形内孔镗削
   • 内锥面：锥形内孔镗削
   • 内槽：内孔槽形切削
   • 内弧：圆弧形内孔镗削
   • 中心孔：中心定位孔加工
   
4. 锥面工艺 - 锥形表面加工
   • 外正锥面、外反锥面
   • 内正锥面、内反锥面
   
5. 螺纹工艺 - 螺纹加工
   • 外直螺纹、外锥螺纹
   • 内直螺纹、内锥螺纹
   
6. 倒角工艺 - 边缘处理
   • 外圆角倒角、外倒角
   • 内圆角倒角、内倒角

📊 常见加工参数：
- 几何参数：长度(L)、直径(D)、深度、角度
- 工艺参数：进给速度(F)、主轴转速(S)、切削深度
- 坐标参数：X、Y、Z坐标位置
"""
    
    def _bert_semantic_analysis(self, text: str) -> Optional[str]:
        """使用BERT进行语义分析，为LLM提供额外信息"""
        if not self.has_bert:
            return None
        
        try:
            # 定义工艺描述库
            process_descriptions = {
                "外圆工艺": "车削加工工件的外圆表面，获得所需的直径和表面质量",
                "端面工艺": "车削加工工件的端面，获得平整的端面表面",  
                "里孔工艺": "镗削加工工件的内孔，获得所需的内径和孔表面质量",
                "锥面工艺": "车削或镗削锥形表面，获得特定的锥度",
                "螺纹工艺": "车削或攻制螺纹，获得标准的螺纹牙形",
                "倒角工艺": "去除工件的锐边毛刺，获得倒角或圆角"
            }
            
            # 获取用户输入的BERT向量
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(**inputs)
                text_embedding = outputs.last_hidden_state[:, 0, :].numpy()[0]
            
            # 计算与各工艺描述的相似度
            similarities = []
            for process_name, description in process_descriptions.items():
                desc_inputs = self.tokenizer(description, return_tensors="pt", padding=True, truncation=True, max_length=512)
                with torch.no_grad():
                    desc_outputs = self.model(**desc_inputs)
                    desc_embedding = desc_outputs.last_hidden_state[:, 0, :].numpy()[0]
                
                similarity = cosine_similarity(
                    text_embedding.reshape(1, -1),
                    desc_embedding.reshape(1, -1)
                )[0][0]
                
                similarities.append((process_name, similarity))
            
            # 排序并返回最相关的工艺
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            if similarities[0][1] > 0.3:  # 相似度阈值
                result = f"• 最相关工艺：{similarities[0][0]} (相似度: {similarities[0][1]:.3f})\n"
                if similarities[1][1] > 0.25:
                    result += f"• 次相关工艺：{similarities[1][0]} (相似度: {similarities[1][1]:.3f})\n"
                result += "• 建议：重点考虑上述工艺类型进行分析"
                return result
            
        except Exception as e:
            print(f"BERT语义分析失败: {e}")
        
        return None
    
    def _enrich_context(self, user_input: str, conversation_history: List[str] = None) -> str:
        """丰富上下文信息"""
        context_parts = []
        
        # 添加对话历史分析
        if conversation_history and len(conversation_history) > 0:
            context_parts.append("💬 对话上下文：")
            context_parts.append("根据之前的对话，请考虑上下文的连续性和一致性。")
        
        # 添加常见表达模式提示
        if any(keyword in user_input.lower() for keyword in ['车', '铣', '镗', '钻', '攻']):
            context_parts.append("🔍 检测到加工动词，这通常表示明确的加工意图。")
        
        if re.search(r'\d+(?:\.\d+)?', user_input):
            context_parts.append("📏 检测到数值参数，请注意提取和解析。")
        
        return "\n".join(context_parts) if context_parts else ""


class CoreLLMIntentClassifier:
    """核心大语言模型意图分类器"""
    
    def __init__(self):
        self.llm_client = ClientFactory().get_client()
        self.enhancement_engine = LLMEnhancementEngine()
        
        # 统计信息
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "enhanced_calls": 0
        }
    
    def classify_intent(self, user_input: str, conversation_history: List[str] = None) -> EnhancedIntentResult:
        """
        使用增强的大语言模型进行意图分类
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史
            
        Returns:
            EnhancedIntentResult: 增强的分类结果
        """
        self.stats["total_calls"] += 1
        
        try:
            # 🔍 首先进行意图预分类，判断是否为工艺相关问题
            if not self._is_process_related_query(user_input):
                print(f"📋 检测到非工艺相关输入: {user_input}")
                return EnhancedIntentResult(
                    main_process="NO_PROCESS",
                    sub_process=None,
                    confidence=0.95,  # 对非工艺识别很有信心
                    entities=[],
                    reasoning=f"输入内容为非工艺相关（问候语、一般性问题等），不需要工艺识别",
                    method="Non_Process_Detection",
                    llm_confidence=0.95,
                    enhancement_info={"is_process_related": False}
                )
            
            print(f"🔧 检测到工艺相关输入，启动专业分析...")
            
            # 1. 使用增强引擎构建提示
            enhanced_prompt, enhancement_info = self.enhancement_engine.enhance_llm_prompt(
                user_input, conversation_history
            )
            
            if enhancement_info.get("bert_analysis"):
                self.stats["enhanced_calls"] += 1
            
            # 2. 调用大语言模型（核心步骤）
            print("🤖 正在调用大语言模型进行意图识别...")
            llm_response = self.llm_client.chat_with_ai(enhanced_prompt)
            
            # 3. 解析LLM响应
            parsed_result = self._parse_llm_response(llm_response, user_input)
            
            self.stats["successful_calls"] += 1
            
            # 4. 构建增强结果
            return EnhancedIntentResult(
                main_process=parsed_result.get("main_process", "NO_PROCESS"),
                sub_process=parsed_result.get("sub_process"),
                confidence=parsed_result.get("confidence", 0.8),
                entities=self._extract_entities_from_params(parsed_result.get("extracted_parameters", {})),
                reasoning=parsed_result.get("professional_reasoning", "基于大语言模型专业分析"),
                method=f"Enhanced_LLM{'_with_BERT' if enhancement_info.get('bert_analysis') else ''}",
                llm_confidence=parsed_result.get("llm_confidence", parsed_result.get("confidence", 0.8)),
                enhancement_info=enhancement_info
            )
            
        except Exception as e:
            print(f"❌ 大语言模型意图识别失败: {e}")
            
            # 这里不使用任何非LLM的后备方案，保持LLM为核心
            return EnhancedIntentResult(
                main_process="NO_PROCESS",
                sub_process=None,
                confidence=0.0,
                entities=[],
                reasoning=f"大语言模型处理失败: {str(e)}。请检查模型连接或输入格式。",
                method="LLM_Error",
                llm_confidence=0.0,
                enhancement_info={"error": str(e)}
            )
    
    def _is_process_related_query(self, user_input: str) -> bool:
        """
        快速判断输入是否为工艺相关问题
        使用简单规则进行预筛选，避免将问候语等误识别为工艺
        """
        text_lower = user_input.lower()
        
        # 明确的非工艺输入
        non_process_patterns = [
            # 问候语
            "你好", "您好", "hello", "hi", "早上好", "下午好", "晚上好",
            # 感谢语
            "谢谢", "谢谢你", "感谢", "多谢",
            # 一般性问题
            "是什么", "什么意思", "怎么样", "可以吗", "好吗",
            # 系统询问
            "帮助", "help", "功能", "使用方法",
        ]
        
        for pattern in non_process_patterns:
            if pattern in text_lower:
                return False
        
        # 明确的工艺相关关键词
        process_keywords = [
            # 加工动作
            "加工", "车", "铣", "镗", "钻", "攻", "切", "削", "磨",
            # 工艺类型
            "外圆", "内圆", "端面", "螺纹", "倒角", "锥面", "切槽",
            # 参数相关
            "直径", "长度", "深度", "进给", "转速", "切削", "刀具",
            # 坐标相关
            "坐标", "位置", "x", "y", "z",
            # 代码相关
            "g代码", "gcode", "程序", "编程"
        ]
        
        for keyword in process_keywords:
            if keyword in text_lower:
                return True
        
        # 如果包含数字+单位，可能是工艺参数
        import re
        if re.search(r'\d+(?:\.\d+)?\s*(?:mm|cm|度|°|rpm)', text_lower):
            return True
        
        # 默认情况：如果长度很短且没有明确工艺词汇，可能不是工艺相关
        if len(user_input.strip()) < 5:
            return False
        
        # 其他情况保守地认为可能是工艺相关（让LLM进一步判断）
        return True
    
    def _parse_llm_response(self, response: str, original_input: str) -> Dict:
        """解析LLM的JSON响应"""
        try:
            # 清理响应文本
            response = response.strip()
            
            # 多种方式提取JSON
            json_text = None
            
            # 方式1：查找```json代码块
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                if end != -1:
                    json_text = response[start:end].strip()
            
            # 方式2：查找{}包围的内容
            if not json_text and '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_text = response[start:end]
            
            # 方式3：整个响应就是JSON
            if not json_text:
                json_text = response
            
            # 解析JSON
            result = json.loads(json_text)
            
            # 验证必要字段
            if not isinstance(result, dict):
                raise ValueError("响应不是有效的字典格式")
            
            # 确保必要字段存在
            default_result = {
                "main_process": "NO_PROCESS",
                "sub_process": None,
                "confidence": 0.5,
                "extracted_parameters": {},
                "professional_reasoning": "解析结果",
                "llm_confidence": 0.5
            }
            
            for key, default_value in default_result.items():
                if key not in result:
                    result[key] = default_value
            
            return result
            
        except Exception as e:
            print(f"⚠️ JSON解析失败: {e}")
            print(f"原始LLM响应: {response[:500]}...")
            
            # 即使解析失败，也尝试从文本中提取信息
            return self._emergency_text_parse(response, original_input)
    
    def _emergency_text_parse(self, response: str, original_input: str) -> Dict:
        """应急文本解析 - 当JSON解析失败时"""
        print("🚨 启用应急文本解析模式")
        
        result = {
            "main_process": "NO_PROCESS",
            "sub_process": None,
            "confidence": 0.3,
            "extracted_parameters": {},
            "professional_reasoning": "应急解析：JSON格式解析失败，使用文本分析",
            "llm_confidence": 0.3
        }
        
        # 尝试从响应中提取工艺信息
        process_types = ["外圆工艺", "端面工艺", "里孔工艺", "锥面工艺", "螺纹工艺", "倒角工艺"]
        for process_type in process_types:
            if process_type in response:
                result["main_process"] = process_type
                result["confidence"] = 0.5
                break
        
        # 尝试提取数值参数
        numbers = re.findall(r'\d+(?:\.\d+)?', original_input)
        if numbers:
            if "长度" in original_input or "L" in original_input:
                result["extracted_parameters"]["长度"] = numbers[0]
            if "进给" in original_input or "F" in original_input:
                result["extracted_parameters"]["进给速度"] = numbers[-1] if len(numbers) > 1 else numbers[0]
        
        return result
    
    def _extract_entities_from_params(self, parameters: Dict[str, str]) -> List[Dict]:
        """从参数字典中提取实体"""
        entities = []
        for param_name, param_value in parameters.items():
            try:
                # 尝试转换为数值
                if isinstance(param_value, str):
                    # 移除单位符号
                    clean_value = re.sub(r'[^\d\.]', '', param_value)
                    if clean_value and clean_value.replace('.', '').isdigit():
                        numeric_value = float(clean_value)
                    else:
                        numeric_value = param_value
                else:
                    numeric_value = param_value
                
                entities.append({
                    'type': param_name,
                    'value': numeric_value,
                    'text': f"{param_name}={param_value}",
                    'source': 'LLM_extraction',
                    'confidence': 0.8
                })
            except Exception as e:
                print(f"参数转换失败 {param_name}={param_value}: {e}")
                continue
        
        return entities
    
    def get_stats(self) -> Dict:
        """获取分类器使用统计"""
        return {
            **self.stats,
            "success_rate": self.stats["successful_calls"] / max(self.stats["total_calls"], 1),
            "enhancement_rate": self.stats["enhanced_calls"] / max(self.stats["total_calls"], 1)
        }


# 主要对外接口
class LLMCentricIntentClassifier:
    """以大语言模型为中心的意图分类器"""
    
    def __init__(self):
        self.core_classifier = CoreLLMIntentClassifier()
    
    def classify(self, text: str, conversation_history: List[str] = None) -> Dict[str, any]:
        """
        使用大语言模型进行意图分类
        
        Args:
            text: 用户输入文本
            conversation_history: 对话历史
            
        Returns:
            Dict: 分类结果
        """
        result = self.core_classifier.classify_intent(text, conversation_history)
        
        return {
            "main_process": result.main_process,
            "sub_process": result.sub_process,
            "confidence": result.confidence,
            "entities": result.entities,
            "reasoning": result.reasoning,
            "method": result.method,
            "llm_confidence": result.llm_confidence,
            "enhancement_info": result.enhancement_info
        }
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        return self.core_classifier.get_stats()


# 全局单例
_llm_centric_classifier = None

def get_llm_centric_classifier() -> LLMCentricIntentClassifier:
    """获取以LLM为中心的意图分类器"""
    global _llm_centric_classifier
    if _llm_centric_classifier is None:
        _llm_centric_classifier = LLMCentricIntentClassifier()
    return _llm_centric_classifier


# 兼容接口
def llm_centric_parse_process_type(question: str) -> dict:
    """
    以大语言模型为中心的工艺类型解析
    
    Args:
        question: 用户输入的问题
        
    Returns:
        dict: 解析结果
    """
    classifier = get_llm_centric_classifier()
    result = classifier.classify(question)
    
    return {
        "main_process": result["main_process"],
        "sub_process": result["sub_process"],
        "parameters": {entity['type']: entity['value'] for entity in result.get("entities", [])},
        "confidence": result.get("confidence", 0.0),
        "reasoning": result.get("reasoning", ""),
        "method": result.get("method", "LLM_Centric"),
        "llm_confidence": result.get("llm_confidence", 0.0),
        "enhancement_used": bool(result.get("enhancement_info", {}).get("bert_analysis"))
    }


if __name__ == "__main__":
    # 测试
    print("🚀 启动大语言模型中心的意图识别测试")
    classifier = LLMCentricIntentClassifier()
    
    test_cases = [
        "我要加工外圆，长度是50mm",
        "车一个内孔，直径20",
        "外螺纹加工"
    ]
    
    for test_text in test_cases:
        print(f"\n📝 测试: {test_text}")
        result = classifier.classify(test_text)
        print(f"📊 结果: {result['method']} - {result['main_process']}")