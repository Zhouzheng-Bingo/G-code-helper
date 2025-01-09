import time
from typing import List, Optional, Iterator

from qa.answer import get_answer
from qa.question_type import QuestionType
from qa.question_parser import parse_process_type
from qa.function_tool import get_process_template, parse_template_params, generate_gcode
from qa.session_state import current_session

# 定义为模块级常量
PROCESS_MAPPING = {
    "外圆工艺": ["外圆", "外锥面", "外圆弧"],
    "端面工艺": ["端面", "切槽", "内端面"],
    "里孔工艺": ["内圆", "内锥面", "内槽", "内弧", "中心孔"],
    "锥面工艺": ["外正锥面", "外反锥面", "内正锥面", "内反锥面"],
    "螺纹工艺": ["外直螺纹", "外锥（管）螺纹", "内直螺纹", "内锥（管）螺纹"],
    "倒角工艺": ["外圆角倒角", "外倒角", "内圆角倒角", "内倒角"]
}

def chat_with_gcode(message, history):
    """
    与G代码助手进行交互的聊天函数。
    """
    try:
        # 1. 检查是否在参数收集过程中
        if current_session.current_param is not None:  # 明确检查是否为None
            try:
                # 解析参数值
                param_value = message.strip()  # 先不做类型转换
                # 保存参数并获取下一步信息
                all_collected, next_prompt = current_session.add_param_value(param_value)
                
                if all_collected:
                    # 所有参数都已收集，生成G代码
                    try:
                        gcode = generate_gcode(
                            current_session.sub_process, 
                            current_session.param_values
                        )
                        response = f"已收集所有参数，生成的G代码：\n{gcode}"
                        current_session.clear()  # 清除会话状态
                    except Exception as e:
                        response = f"生成G代码时出错: {str(e)}"
                        current_session.clear()
                else:
                    response = next_prompt
                
                # 逐字符输出响应
                for i in range(len(response)):
                    time.sleep(0.05)
                    yield response[:i + 1]
                return  # 重要：确保在这里返回，不继续执行后面的代码

            except ValueError:
                yield "请输入有效的数值"
                return

        # 2. 尝试识别工艺类型
        process_info = parse_process_type(message)
        
        if process_info["main_process"] != "NO_PROCESS":
            response_parts = []
            response_parts.append(f"识别到工艺类型：{process_info['main_process']}")
            
            if process_info["sub_process"]:
                sub_process = process_info["sub_process"]
                response_parts.append(f"具体子工艺：{sub_process}")
                
                template = get_process_template(sub_process)
                if template:
                    param_list = parse_template_params(template)
                    # 初始化会话状态
                    current_session.init_session(
                        process_info["main_process"],
                        sub_process,
                        param_list
                    )
                    response_parts.append("\n请按顺序提供以下参数：")
                    for param in param_list:
                        param_type = current_session.param_types.get(param, float)
                        response_parts.append(f"- {param} ({param_type.__name__})")
                    response_parts.append(f"\n请输入第一个参数 {param_list[0]} ({current_session.param_types[param_list[0]].__name__}类型)")
                else:
                    response_parts.append("未找到对应的工艺模板")
            else:
                response_parts.append("请指定具体的子工艺类型。")
                if process_info["main_process"] in PROCESS_MAPPING:
                    response_parts.append("可选的子工艺类型有：")
                    for sub_type in PROCESS_MAPPING[process_info["main_process"]]:
                        response_parts.append(f"- {sub_type}")
            
            response = "\n".join(response_parts)
            for i in range(len(response)):
                time.sleep(0.05)
                yield response[:i + 1]
            return

        # 3. 如果不是工艺相关问题,继续原有的处理流程
        answers = get_answer(message, history)

        if answers[-1] == QuestionType.GCODE_KNOWLEDGE_GRAPH:
            # 处理G代码知识图谱查询
            response = answers[0]
            for i in range(len(response)):
                time.sleep(0.05)
                yield response[:i + 1]

        elif answers[-1] == QuestionType.HELLO or answers[-1] == QuestionType.UNKNOWN:
            # 处理问候语和未知问题
            partial_message = answers[0]  # 直接使用字符串
            yield partial_message

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

    except Exception as e:
        error_msg = f"处理过程中出现错误: {str(e)}"
        yield error_msg
