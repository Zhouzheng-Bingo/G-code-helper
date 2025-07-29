from typing import List

from icecream import ic

from lang_chain.client.client_factory import ClientFactory
from model.graph_entity.search_model import _Value
from model.graph_entity.search_service import search
from qa.prompt_templates import get_question_parser_prompt
from qa.question_type import QuestionType, QUESTION_MAP
from qa.function_tool import identify_process_type
from qa.llm_centric_classifier import llm_centric_parse_process_type, get_llm_centric_classifier


def parse_question(question: str) -> QuestionType:

    prompt = get_question_parser_prompt(question)
    parse_result = ClientFactory().get_client().chat_with_ai(prompt)
    question_type = QUESTION_MAP[parse_result]
    ic(question_type)

    return question_type


def check_entity(question: str) -> List[_Value] | None:
    """
    检查问题中的实体，添加异常处理
    """
    try:
        code, msg, results = search(question)
        if code == 0 and results is not None:
            # 验证结果格式
            if isinstance(results, list):
                return results
            else:
                print(f"警告：实体搜索返回格式异常: {type(results)}")
                return None
        else:
            print(f"实体搜索失败: code={code}, msg={msg}")
            return None
    except Exception as e:
        print(f"check_entity异常: {e}")
        return None


def parse_process_type(question: str) -> dict:
    """
    解析工艺类型和参数 - 核心使用大语言模型，BERT等技术作为增强
    Args:
        question: 用户输入的问题
    Returns:
        dict: 解析结果，包含主工艺类型、子工艺类型和参数
    """
    print(f"🤖 启动大语言模型驱动的意图识别系统")
    
    # 主要方法：大语言模型驱动（这是我们论文的核心技术）
    try:
        result = llm_centric_parse_process_type(question)
        print(f"✅ 大语言模型意图识别成功: {result['method']}")
        print(f"📊 LLM置信度: {result.get('llm_confidence', 'N/A')}")
        print(f"🧠 BERT增强: {'是' if result.get('enhancement_used') else '否'}")
        return result
    except Exception as e:
        print(f"❌ 大语言模型意图识别失败: {e}")
        
        # 备用方案：基础LLM方法（仍然是LLM，不是关键词）
        print("🔄 尝试基础大语言模型方法...")
        try:
            process_info = identify_process_type(question)
            return {
                "main_process": process_info["main_process"],
                "sub_process": process_info["sub_process"],
                "parameters": {},
                "confidence": 0.6,
                "reasoning": "使用基础大语言模型方法",
                "method": "Basic_LLM",
                "llm_confidence": 0.6,
                "enhancement_used": False
            }
        except Exception as e2:
            print(f"❌ 基础LLM方法也失败: {e2}")
            
            # 最终错误处理（不使用非LLM方法）
            return {
                "main_process": "NO_PROCESS",
                "sub_process": None,
                "parameters": {},
                "confidence": 0.0,
                "reasoning": f"大语言模型系统故障: {str(e2)}。请检查模型服务连接。",
                "method": "LLM_System_Error",
                "llm_confidence": 0.0,
                "enhancement_used": False
            }
