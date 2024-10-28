
# 定义可能的问答类型
from qa.question_type import QUESTION_MAP


QUESTION_PARSE_TEMPLATE = (
    f"你是一位文本分类助手，需要将用户的输入分类为以下{len(QUESTION_MAP)}种类别：\n"
    f"1. G代码知识图谱查询\n"
    f"2. PDF文档查询\n"
    f"3. 问候语\n"
    f"4. 其他\n"
    f"以下是一些示例：\n"
    f"'G00代码的作用是什么？'，文本分类结果是G代码知识图谱查询；\n"
    f"'如何设置GJ306系统的进给速度？'，文本分类结果是G代码知识图谱查询；\n"
    f"'请给我GJ306系统的操作手册'，文本分类结果是PDF文档查询；\n"
    f"'你好，你是谁？'，文本分类结果是问候语；\n"
    f"'今天天气怎么样？'，文本分类结果是其他。\n"
    f"请参考上述示例，直接给出一种分类结果，不要解释，不要包含多余的内容或符号。\n"
    f"请对以下内容进行文本分类：\n"
)

HELLO_ANSWER_TEMPLATE = f"""你是一位高级文案创作者，可以适当增加严谨助理的风格，请你帮我润色以下内容：\n我是[GJ306辅助ai助手]，一个基于超级知识图谱的智能聊天机器人，旨在回答与GJ306相关的问题。\n"""

LLM_HINT = "你是一位高级文案创作者，要求正式，请你帮我润色以下内容:\n <u>本地知识图谱信息有限，下面结合大模型给出答案：</u>\n"

def get_question_parser_prompt(text: str) -> str:
    """
    根据输入的文本生成用于意图识别的提示词
    :param text: 用户输入的文本
    :return: 用于意图识别的prompt
    """
    return f"{QUESTION_PARSE_TEMPLATE}{text}"
