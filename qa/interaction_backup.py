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

def extract_params_from_message(message: str, param_list: list, param_types: dict) -> dict:
    """
    从用户消息中提取参数值
    Args:
        message: 用户输入的消息
        param_list: 参数列表
        param_types: 参数类型字典
    Returns:
        dict: 提取的参数值字典
    """
    params = {}
    # 创建参数名的小写映射
    param_lower_map = {param.lower(): param for param in param_list}
    
    for param in param_list:
        # 构建可能的参数标识符（包含大小写变体）
        identifiers = []
        for base in [param, param.lower(), param.upper()]:
            identifiers.extend([
                f"{base}是", f"{base}=", f"{base}:", 
                f"{base}为", f"{base}：", f"{base} "
            ])
        
        for identifier in identifiers:
            if identifier in message:
                # 找到参数标识符后的值
                start_idx = message.find(identifier) + len(identifier)
                # 找下一个标识符或者引号或者逗号
                end_idx = len(message)
                
                # 检查所有参数的所有可能形式
                for next_param in param_list:
                    for next_base in [next_param, next_param.lower(), next_param.upper()]:
                        for next_id in [f"{next_base}是", f"{next_base}=", f"{next_base}:", 
                                      f"{next_base}为", f"{next_base}：", f"{next_base} "]:
                            next_pos = message.find(next_id, start_idx)
                            if next_pos != -1:
                                end_idx = min(end_idx, next_pos)
                
                # 也考虑逗号、空格等分隔符
                for separator in [",", "，", " ", ";", "；", '"', "'"]:
                    sep_pos = message.find(separator, start_idx)
                    if sep_pos != -1:
                        end_idx = min(end_idx, sep_pos)
                
                value = message[start_idx:end_idx].strip()
                if value:
                    try:
                        param_type = param_types.get(param, float)
                        if param_type == int:
                            params[param] = int(float(value))
                        elif param_type == float:
                            params[param] = float(value)
                        else:
                            params[param] = param_type(value)
                    except ValueError:
                        continue
                break
    
    return params

def chat_with_gcode(message, history):
    """
    与G代码助手进行交互的聊天函数。
    """
    try:
        # 1. 检查是否在参数收集过程中
        if current_session.current_param is not None:
            try:
                param_value = message.strip()
                all_collected, next_prompt = current_session.add_param_value(param_value)
                
                if all_collected:
                    try:
                        gcode = generate_gcode(
                            current_session.sub_process, 
                            current_session.param_values
                        )
                        response = f"已收集所有参数，生成的G代码：\n{gcode}"
                        current_session.clear()
                    except Exception as e:
                        response = f"生成G代码时出错: {str(e)}"
                        current_session.clear()
                else:
                    response = next_prompt
                
                for i in range(len(response)):
                    time.sleep(0.05)
                    yield response[:i + 1]
                return

            except ValueError:
                yield "请输入有效的数值"
                return

        # 2. 尝试识别工艺类型和意图
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
                    
                    # 尝试从消息中提取参数
                    params = extract_params_from_message(message, param_list, current_session.param_types)
                    
                    # 如果提取到了所有参数
                    if len(params) == len(param_list):
                        try:
                            gcode = generate_gcode(sub_process, params)
                            response = f"已从您的输入中提取所有参数，生成的G代码：\n{gcode}"
                            for i in range(len(response)):
                                time.sleep(0.05)
                                yield response[:i + 1]
                            return
                        except Exception as e:
                            response_parts.append(f"参数提取成功但生成G代码时出错: {str(e)}")
                    
                    # 如果只提取到部分参数，初始化会话并保存已有参数
                    current_session.init_session(
                        process_info["main_process"],
                        sub_process,
                        param_list
                    )
                    
                    # 保存已提取的参数
                    for param, value in params.items():
                        try:
                            current_session.param_values[param] = value
                            # 从待收集参数列表中移除已有参数
                            if param in current_session.param_list:
                                current_session.param_list.remove(param)
                        except ValueError as e:
                            print(f"参数 {param} 设置失败: {e}")
                    
                    # 更新当前需要收集的参数
                    if current_session.param_list:
                        current_session.current_param = current_session.param_list[0]
                        response_parts.append("\n需要提供以下参数：")
                        for param in current_session.param_list:
                            param_type = current_session.param_types.get(param, float)
                            response_parts.append(f"- {param} ({param_type.__name__})")
                        response_parts.append(f"\n请输入参数 {current_session.current_param} ({current_session.param_types[current_session.current_param].__name__}类型)")
                    else:
                        # 如果所有参数都已收集
                        try:
                            gcode = generate_gcode(sub_process, current_session.param_values)
                            response = f"已收集所有参数，生成的G代码：\n{gcode}"
                            current_session.clear()
                            for i in range(len(response)):
                                time.sleep(0.05)
                                yield response[:i + 1]
                            return
                        except Exception as e:
                            response_parts.append(f"生成G代码时出错: {str(e)}")
                            current_session.clear()
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

        elif answers[-1] == QuestionType.HELLO:
            # 处理问候语
            response = answers[0]  # 直接使用字符串
            for i in range(len(response)):
                time.sleep(0.05)
                yield response[:i + 1]

        elif answers[-1] == QuestionType.PDF_DOCUMENT:
            # 处理PDF文档查询
            partial_message = ""
            for chunk in answers[0][1]:
                partial_message += chunk.choices[0].delta.content
                yield partial_message
            partial_message += answers[0][0]
            yield partial_message

        elif answers[-1] == QuestionType.UNKNOWN:
            # 处理未知问题，包括G代码知识问答
            try:
                partial_message = ""
                for chunk in answers[0][1]:
                    if chunk.choices[0].delta.content:
                        partial_message += chunk.choices[0].delta.content
                        yield partial_message
            except Exception as e:
                print(f"处理未知问题时出错: {e}")
                yield "抱歉，处理您的问题时出现了错误。"

        else:
            raise Exception("Unknown question type")

    except Exception as e:
        error_msg = f"处理过程中出现错误: {str(e)}"
        yield error_msg


