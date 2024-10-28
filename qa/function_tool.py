import json
from typing import List, Tuple, Callable, Optional

from openai import Stream
from openai.types.chat import ChatCompletionChunk

from dao.graph.graph_dao import GraphDao
from lang_chain import rag_chain
from lang_chain.client.client_factory import ClientFactory
from qa.question_type import QuestionType
from model.graph_entity.search_model import _Value
from qa.prompt_templates import HELLO_ANSWER_TEMPLATE, LLM_HINT

_dao = GraphDao()


def relation_tool(entities: List[_Value] | None) -> Tuple[str, QuestionType] | None:
    """G指令关系"""
    if not entities or len(entities) < 2:
        return None
    relationship_match = _dao.query_relationship_by_2points(entities[0].name, entities[1].name)
    if relationship_match:

        rel = relationship_match[0]['type(r)']
        if entities[0].name not in rel:
            start_name = entities[0].name
        else:
            start_name = entities[1].name
        return f"关系如下：{start_name}{rel}，详见:{relationship_match[0]['r']['Notes']}", QuestionType.GCODE_KNOWLEDGE_GRAPH


def document_search_tool(
        question: str,
        history: List[List[str] | None] = None
) -> Tuple[Tuple[str, Stream[ChatCompletionChunk]], QuestionType]:
    reference, response = rag_chain.invoke(question, history)
    return (reference, response), QuestionType.PDF_DOCUMENT

def hello_tool() -> Tuple[str, QuestionType]:
    """问候语"""
    response = ClientFactory().get_client().chat_with_ai(HELLO_ANSWER_TEMPLATE)
    return response, QuestionType.HELLO

def process_unknown_question_tool(
        question: str,
        history: List[List[str] | None] = None,
) -> Tuple[Tuple[str, Stream[ChatCompletionChunk]], QuestionType]:
    head_: str = ClientFactory().get_client().chat_with_ai(LLM_HINT)
    response = ClientFactory().get_client().chat_with_ai_stream(question, history[-5:])
    return (head_, response), QuestionType.UNKNOWN

TOOLS_MAPPING = {
    QuestionType.GCODE_KNOWLEDGE_GRAPH: relation_tool,
    QuestionType.PDF_DOCUMENT: document_search_tool,
    QuestionType.HELLO: hello_tool,
    QuestionType.UNKNOWN: process_unknown_question_tool,
}

def map_question_to_function(
    question_type: QuestionType,
) -> Callable:
    if question_type in TOOLS_MAPPING:
        return TOOLS_MAPPING[question_type]
    else:
        raise ValueError(f"No tool found for question type: {question_type}")

FUNCTION_ARGS_MAPPING = {
    QuestionType.GCODE_KNOWLEDGE_GRAPH: lambda args: args[1:3],
    QuestionType.PDF_DOCUMENT: lambda args: args[1:3],
    QuestionType.HELLO: lambda args: [],
    QuestionType.UNKNOWN: lambda args: args[1:3],
}

def map_question_to_function_args(
    question_type: QuestionType,
) -> Callable[[List], List]:
    if question_type in FUNCTION_ARGS_MAPPING:
        return FUNCTION_ARGS_MAPPING[question_type]
    else:
        raise ValueError(f"No argument mapping found for question type: {question_type}")
