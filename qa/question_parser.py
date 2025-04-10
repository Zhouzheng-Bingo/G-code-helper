from typing import List

from icecream import ic

from lang_chain.client.client_factory import ClientFactory
from model.graph_entity.search_model import _Value
from model.graph_entity.search_service import search
from qa.prompt_templates import get_question_parser_prompt
from qa.question_type import QuestionType, QUESTION_MAP
from qa.function_tool import identify_process_type


def parse_question(question: str) -> QuestionType:

    prompt = get_question_parser_prompt(question)
    parse_result = ClientFactory().get_client().chat_with_ai(prompt)
    question_type = QUESTION_MAP[parse_result]
    ic(question_type)

    return question_type


def check_entity(question: str) -> List[_Value] | None:

    code, msg, results = search(question)
    if code == 0:
        return results

    else:
        return None


def parse_process_type(question: str) -> dict:
    """
    解析工艺类型和参数
    Args:
        question: 用户输入的问题
    Returns:
        dict: 解析结果，包含主工艺类型、子工艺类型和参数
    """
    process_info = identify_process_type(question)
    
    return {
        "main_process": process_info["main_process"],
        "sub_process": process_info["sub_process"],
        "parameters": {}  # 后续实现参数解析
    }
