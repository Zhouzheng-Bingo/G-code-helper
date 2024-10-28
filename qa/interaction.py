import time
from typing import List, Optional, Iterator

from qa.answer import get_answer
from qa.question_type import QuestionType

def chat_with_gcode(message, history):
    """
    与G代码助手进行交互的聊天函数。

    参数：
        message (str): 用户的输入消息。
        history (Optional[List[List]]): 会话历史记录。

    生成器：
        str: 逐步生成的回复内容。
    """
    answers = get_answer(message, history)

    if answers[-1] == QuestionType.GCODE_KNOWLEDGE_GRAPH:
        # 处理G代码知识图谱查询
        response = answers[0]
        for i in range(len(response)):
            time.sleep(0.05)
            yield response[:i + 1]

    # elif answers[-1] == QuestionType.HELLO or answers[-1] == QuestionType.UNKNOWN:
    #     # 处理问候语和未知问题
    #     partial_message = answers[0][0]
    #
    #     for chunk in answers[0][1]:
    #         partial_message = partial_message + (chunk.choices[0].delta.content or "")
    #         yield partial_message

    elif answers[-1] == QuestionType.HELLO or answers[-1] == QuestionType.UNKNOWN:
        # 处理问候语和未知问题
        partial_message = answers[0]  # 直接使用字符串

        # 如果需要，可以添加更多的内容，比如继续拼接其他信息
        # partial_message += " 更多信息..."

        yield partial_message


    # 调试过程
    # elif answers[-1] == QuestionType.HELLO or answers[-1] == QuestionType.UNKNOWN:
    #     # 处理问候语和未知问题
    #     partial_message = answers[0][0]
    #
    #     print("Answers:", answers)  # 打印整个 answers 内容
    #     print("Type of chunk:", type(answers[0][1]))  # 打印 chunk 的类型
    #
    #     for chunk in answers[0][1]:
    #         print("Chunk:", chunk)  # 打印每个 chunk 的内容
    #         if isinstance(chunk, str):
    #             partial_message += chunk  # 如果 chunk 是字符串，直接拼接
    #         else:
    #             # 假设 chunk 是对象，检查它是否有 choices 属性
    #             if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
    #                 partial_message += (chunk.choices[0].delta.content or "")
    #             else:
    #                 print("Unexpected chunk structure:", chunk)  # 打印未预期的 chunk 结构
    #
    #     yield partial_message



    elif answers[-1] == QuestionType.PDF_DOCUMENT:
        # 处理PDF文档查询
        partial_message = ""
        for chunk in answers[0][1]:
            partial_message += chunk.choices[0].delta.content
            yield partial_message
        partial_message += answers[0][0]
        yield partial_message

    else:
        raise Exception("Unknown question type")
