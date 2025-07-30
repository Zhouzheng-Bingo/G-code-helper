# -*- coding: utf-8 -*-
"""
统一的LLM驱动意图分类器
核心理念：让大语言模型直接理解用户意图，准确区分知识咨询和工艺执行
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

from lang_chain.client.client_factory import ClientFactory


class IntentType(Enum):
    """统一的意图类型定义"""
    GREETING = "greeting"  # 问候语
    GCODE_KNOWLEDGE = "gcode_knowledge"  # G代码知识咨询
    PROCESS_TASK = "process_task"  # 工艺执行任务
    PDF_DOCUMENT = "pdf_document"  # PDF文档查询
    UNKNOWN = "unknown"  # 其他


@dataclass
class IntentResult:
    """意图识别结果"""
    intent_type: IntentType
    confidence: float
    reasoning: str
    # 工艺任务特有的额外信息
    process_info: Optional[Dict] = None


class UnifiedIntentClassifier:
    """统一的LLM驱动意图分类器"""
    
    def __init__(self):
        self.llm_client = ClientFactory().get_client()
    
    def classify_intent(self, user_input: str, conversation_history: List[str] = None) -> IntentResult:
        """
        使用大语言模型进行统一的意图分类
        
        Args:
            user_input: 用户输入
            conversation_history: 对话历史
            
        Returns:
            IntentResult: 意图识别结果
        """
        # 构建精心设计的prompt
        prompt = self._build_intent_classification_prompt(user_input, conversation_history)
        
        try:
            # 调用LLM进行意图识别
            llm_response = self.llm_client.chat_with_ai(prompt)
            
            # 解析LLM响应
            result = self._parse_llm_response(llm_response, user_input)
            
            return result
            
        except Exception as e:
            print(f"❌ LLM意图识别失败: {e}")
            return IntentResult(
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                reasoning=f"LLM识别失败: {str(e)}"
            )
    
    def _build_intent_classification_prompt(self, user_input: str, conversation_history: List[str] = None) -> str:
        """构建意图分类的prompt"""
        
        prompt = """你是一个专业的数控系统意图识别专家。请仔细分析用户输入，准确识别用户的真实意图。

## 意图类型定义：

1. **greeting（问候语）**
   - 用户打招呼、问候
   - 例如："你好"、"您好"、"Hi"、"早上好"

2. **gcode_knowledge（G代码知识咨询）**
   - 用户询问G代码的功能、用法、含义
   - 关键特征：包含"如何使用"、"怎么用"、"作用是什么"、"什么意思"等询问词汇
   - 例如：
     * "G00指令的作用是什么？"
     * "如何使用G76螺纹切削循环？"
     * "G01直线插补怎么用？"
     * "M03是什么意思？"

3. **process_task（工艺执行任务）**
   - 用户明确要求执行加工任务、生成G代码
   - 关键特征：包含"我要加工"、"使用XX工艺"、"车一个"、"加工一个"等执行动词
   - 例如：
     * "我要使用外圆工艺加工一个外圆"
     * "车一个内孔，直径20mm"
     * "使用螺纹工艺加工M10螺纹"
     * "外圆工艺，参数Cn=2，L=100"

4. **pdf_document（PDF文档查询）**
   - 用户请求查看文档、手册
   - 例如："请给我GJ306系统的操作手册"、"查看使用说明书"

5. **unknown（其他）**
   - 不属于以上任何类别的输入

## 重要区分规则：

⚠️ **知识咨询 vs 工艺执行的区别**：
- 知识咨询：用户在**询问**某个G代码或工艺**怎么用**、**是什么**
- 工艺执行：用户在**要求系统**帮他**执行**某个加工任务

举例说明：
- "如何使用G76螺纹切削循环？" → gcode_knowledge（询问用法）
- "使用G76加工M10螺纹" → process_task（执行任务）
- "外圆工艺怎么用？" → gcode_knowledge（询问用法）
- "使用外圆工艺加工" → process_task（执行任务）

## 输出格式：

请严格按照以下JSON格式返回结果：
{
    "intent_type": "意图类型（greeting/gcode_knowledge/process_task/pdf_document/unknown）",
    "confidence": 0.95,
    "reasoning": "判断理由说明",
    "process_info": {
        "main_process": "主工艺类型（仅当intent_type为process_task时提供）",
        "sub_process": "子工艺类型（如果能识别）",
        "has_parameters": true/false
    }
}

## 用户输入：
""" + user_input + """

请开始分析："""

        return prompt
    
    def _parse_llm_response(self, response: str, original_input: str) -> IntentResult:
        """解析LLM响应"""
        import json
        
        try:
            # 提取JSON内容
            json_text = response
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                if end != -1:
                    json_text = response[start:end].strip()
            elif '{' in response and '}' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_text = response[start:end]
            
            # 解析JSON
            data = json.loads(json_text)
            
            # 映射意图类型
            intent_map = {
                "greeting": IntentType.GREETING,
                "gcode_knowledge": IntentType.GCODE_KNOWLEDGE,
                "process_task": IntentType.PROCESS_TASK,
                "pdf_document": IntentType.PDF_DOCUMENT,
                "unknown": IntentType.UNKNOWN
            }
            
            intent_type = intent_map.get(data.get("intent_type", "unknown"), IntentType.UNKNOWN)
            
            return IntentResult(
                intent_type=intent_type,
                confidence=data.get("confidence", 0.8),
                reasoning=data.get("reasoning", ""),
                process_info=data.get("process_info") if intent_type == IntentType.PROCESS_TASK else None
            )
            
        except Exception as e:
            print(f"解析LLM响应失败: {e}")
            print(f"原始响应: {response[:200]}...")
            
            # 降级处理：基于关键词的简单判断
            text_lower = original_input.lower()
            if any(word in text_lower for word in ["你好", "您好", "hello", "hi"]):
                return IntentResult(IntentType.GREETING, 0.7, "降级识别：问候语")
            elif any(word in text_lower for word in ["如何使用", "怎么用", "作用是什么", "什么意思"]):
                return IntentResult(IntentType.GCODE_KNOWLEDGE, 0.7, "降级识别：知识咨询")
            elif any(word in text_lower for word in ["我要加工", "使用", "车一个", "加工一个"]):
                return IntentResult(IntentType.PROCESS_TASK, 0.7, "降级识别：工艺任务")
            else:
                return IntentResult(IntentType.UNKNOWN, 0.5, "降级识别：未知类型")


# 全局单例
_unified_classifier = None

def get_unified_classifier() -> UnifiedIntentClassifier:
    """获取统一意图分类器的单例"""
    global _unified_classifier
    if _unified_classifier is None:
        _unified_classifier = UnifiedIntentClassifier()
    return _unified_classifier


# 测试代码
if __name__ == "__main__":
    classifier = UnifiedIntentClassifier()
    
    test_cases = [
        "你好",
        "G00指令的作用是什么？",
        "如何使用G76螺纹切削循环？",
        "我要使用外圆工艺加工一个外圆，Cn是2，L是100.0",
        "请给我GJ306系统的操作手册"
    ]
    
    print("🧪 测试统一意图分类器")
    print("=" * 60)
    
    for test_input in test_cases:
        print(f"\n输入: {test_input}")
        result = classifier.classify_intent(test_input)
        print(f"意图类型: {result.intent_type.value}")
        print(f"置信度: {result.confidence}")
        print(f"推理: {result.reasoning}")
        if result.process_info:
            print(f"工艺信息: {result.process_info}")