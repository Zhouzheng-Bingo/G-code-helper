from enum import Enum

class QuestionType(Enum):
    """
    问题类型 - 支持统一的LLM驱动意图识别
    """
    UNKNOWN = 0
    GCODE_KNOWLEDGE_GRAPH = 1
    PDF_DOCUMENT = 2
    HELLO = 3
    PROCESS_TASK = 4  # 新增：工艺执行任务
    GCODE_KNOWLEDGE_QUERY = 5  # 新增：G代码知识咨询

QUESTION_MAP = {
    "G代码知识图谱查询": QuestionType.GCODE_KNOWLEDGE_GRAPH,
    "PDF文档查询": QuestionType.PDF_DOCUMENT,
    "问候语": QuestionType.HELLO,
    "工艺执行任务": QuestionType.PROCESS_TASK,  # 新增
    "G代码知识咨询": QuestionType.GCODE_KNOWLEDGE_QUERY,  # 新增
    "其他": QuestionType.UNKNOWN,
}
