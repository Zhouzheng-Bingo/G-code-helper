from typing import Tuple, List, Any

from dao.graph.graph_dao import GraphDao
from model.graph_entity.file_utils import FIELD_NAMES
from qa.function_tool import map_question_to_function, map_question_to_function_args, relation_tool, hello_tool
from collections import namedtuple
from qa.question_parser import parse_question, check_entity, QuestionType


def get_answer(question: str,
               history: List[List | None] = None) -> (
        Tuple[Any, QuestionType]):
    question_type = parse_question(question)
    entities = check_entity(question)

    function = map_question_to_function(question_type)
    args_getter = map_question_to_function_args(question_type)
    args = args_getter([question_type, question, history, entities])
    print("=============")
    print(function)
    # result = function(*args)
    result = function(*args)
    if not result:
        function = map_question_to_function(QuestionType.UNKNOWN)
        args_getter = map_question_to_function_args(QuestionType.UNKNOWN)
        args = args_getter([question_type, question, history, entities])
        result = function(*args)

    return result

#
# _dao = GraphDao()
# _Value = namedtuple("_Value", (fn for fn in FIELD_NAMES))
#
#
# def relation_tool1(*entities: _Value) -> Tuple[str, QuestionType] | None:
#     """G指令关系"""
#     if not entities or len(entities) < 2:
#         return None
#     relationship_match = _dao.query_relationship_by_2points(entities[0].name, entities[1].name)
#     if relationship_match:
#
#         rel = relationship_match[0]['type(r)']
#         if entities[0].name not in rel:
#             start_name = entities[0].name
#         else:
#             start_name = entities[1].name
#         return f"关系如下：{start_name}{rel}，详见:{relationship_match[0]['r']['Notes']}", QuestionType.GCODE_KNOWLEDGE_GRAPH
