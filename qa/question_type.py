from enum import Enum

class QuestionType(Enum):
    """
    问题类型
    """
    UNKNOWN = 0
    GCODE_KNOWLEDGE_GRAPH = 1
    PDF_DOCUMENT = 2
    HELLO = 3

QUESTION_MAP = {
    "G代码知识图谱查询": QuestionType.GCODE_KNOWLEDGE_GRAPH,
    "PDF文档查询": QuestionType.PDF_DOCUMENT,
    "问候语": QuestionType.HELLO,
    "其他": QuestionType.UNKNOWN,
}
