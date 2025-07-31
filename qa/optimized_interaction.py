# -*- coding: utf-8 -*-
"""
优化的交互模块 - 减少LLM调用次数
"""

import time
from typing import List, Optional, Iterator
import json

from qa.answer import get_answer
from qa.question_type import QuestionType
from qa.question_parser import parse_question, parse_process_type
from qa.function_tool import get_process_template, parse_template_params, generate_gcode
from qa.session_state import current_session
from lang_chain.client.client_factory import ClientFactory

# 定义为模块级常量
PROCESS_MAPPING = {
    "外圆工艺": ["外圆", "外锥面", "外圆弧"],
    "端面工艺": ["端面", "切槽", "内端面"],
    "里孔工艺": ["内圆", "内锥面", "内槽", "内弧", "中心孔"],
    "锥面工艺": ["外正锥面", "外反锥面", "内正锥面", "内反锥面"],
    "螺纹工艺": ["外直螺纹", "外锥（管）螺纹", "内直螺纹", "内锥（管）螺纹"],
    "倒角工艺": ["外圆角倒角", "外倒角", "内圆角倒角", "内倒角"]
}

# 缓存简单问题的答案
SIMPLE_ANSWERS_CACHE = {
    "你好": "你好！我是G代码编程助手，可以帮助你解答G代码相关问题和生成加工程序。",
    "谢谢": "不客气！有其他问题随时问我。",
    "再见": "再见！祝你编程顺利！",
}

def is_simple_greeting(message: str) -> bool:
    """检查是否是简单问候语"""
    greetings = ["你好", "您好", "hi", "hello", "嗨", "早上好", "下午好", "晚上好"]
    return any(g in message.lower() for g in greetings)

def extract_params_from_message(message: str, param_list: list, param_types: dict) -> dict:
    """从用户消息中提取参数值（保持原有实现）"""
    params = {}
    param_lower_map = {param.lower(): param for param in param_list}
    
    for param in param_list:
        identifiers = []
        for base in [param, param.lower(), param.upper()]:
            identifiers.extend([
                f"{base}是", f"{base}=", f"{base}:", 
                f"{base}为", f"{base}：", f"{base} "
            ])
        
        for identifier in identifiers:
            if identifier in message:
                start_idx = message.find(identifier) + len(identifier)
                end_idx = len(message)
                
                for next_param in param_list:
                    for next_base in [next_param, next_param.lower(), next_param.upper()]:
                        for next_id in [f"{next_base}是", f"{next_base}=", f"{next_base}:", 
                                      f"{next_base}为", f"{next_base}：", f"{next_base} "]:
                            next_pos = message.find(next_id, start_idx)
                            if next_pos != -1:
                                end_idx = min(end_idx, next_pos)
                
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

def combined_llm_analysis(message: str) -> dict:
    """
    使用单次LLM调用完成意图识别和工艺分析
    """
    prompt = f"""请分析以下用户输入，返回JSON格式的分析结果：

用户输入：{message}

返回格式：
{{
    "intent": "greeting/gcode_knowledge/process_task/unknown",
    "process_type": "主工艺类型（如果是工艺任务）",
    "sub_process": "子工艺类型（如果是工艺任务）",
    "parameters": {{参数名: 参数值}}
}}

注意：
1. intent必须是四个选项之一
2. 如果不是process_task，process_type和sub_process为null
3. 只返回JSON，不要有其他内容
"""
    
    try:
        client = ClientFactory().get_client()
        response = client.chat_with_ai(prompt)
        
        # 提取JSON
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            return result
        else:
            return {"intent": "unknown"}
    except Exception as e:
        print(f"LLM分析失败: {e}")
        return {"intent": "unknown"}

def handle_process_task(message: str, process_info: dict):
    """处理工艺执行任务（保持原有实现）"""
    response_parts = []
    response_parts.append(f"识别到工艺类型：{process_info['main_process']}")
    
    if process_info["sub_process"]:
        sub_process = process_info["sub_process"]
        response_parts.append(f"具体子工艺：{sub_process}")
        
        template = get_process_template(sub_process)
        if template:
            param_list = parse_template_params(template)
            
            params = extract_params_from_message(message, param_list, current_session.param_types)
            
            if len(params) == len(param_list):
                try:
                    gcode = generate_gcode(sub_process, params)
                    response_parts.append(f"生成的G代码：\n{gcode}")
                    return "\n".join(response_parts)
                except Exception as e:
                    response_parts.append(f"生成G代码时出错: {str(e)}")
            else:
                current_session.sub_process = sub_process
                current_session.template = template
                current_session.param_list = param_list
                
                for param in param_list:
                    if param in params:
                        try:
                            current_session.set_param_value(param, params[param])
                        except ValueError as e:
                            print(f"参数 {param} 设置失败: {e}")
                
                if current_session.param_list:
                    current_session.current_param = current_session.param_list[0]
                    response_parts.append("\n需要提供以下参数：")
                    for param in current_session.param_list:
                        param_type = current_session.param_types.get(param, float)
                        response_parts.append(f"- {param} ({param_type.__name__})")
                    response_parts.append(f"\n请输入参数 {current_session.current_param} ({current_session.param_types[current_session.current_param].__name__}类型)")
                else:
                    try:
                        gcode = generate_gcode(sub_process, current_session.param_values)
                        current_session.clear()
                        return f"已收集所有参数，生成的G代码：\n{gcode}"
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
    
    return "\n".join(response_parts)

def chat_with_gcode_optimized(message, history):
    """
    优化后的聊天函数 - 减少LLM调用
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
                
                # 移除sleep延迟，直接返回
                yield response
                return

            except ValueError:
                yield "请输入有效的数值"
                return

        # 2. 检查简单问候语缓存
        for key, cached_response in SIMPLE_ANSWERS_CACHE.items():
            if key in message:
                yield cached_response
                return
        
        # 3. 对于简单问候，快速处理
        if is_simple_greeting(message):
            yield "你好！我是G代码编程助手，可以帮助你解答G代码相关问题和生成加工程序。"
            return

        # 4. 使用组合LLM分析（单次调用）
        analysis = combined_llm_analysis(message)
        
        intent = analysis.get("intent", "unknown")
        
        if intent == "greeting":
            yield "你好！有什么G代码编程问题可以问我。"
            return
            
        elif intent == "process_task":
            # 处理工艺任务
            process_info = {
                "main_process": analysis.get("process_type"),
                "sub_process": analysis.get("sub_process"),
                "parameters": analysis.get("parameters", {})
            }
            response = handle_process_task(message, process_info)
            yield response
            return
            
        elif intent == "gcode_knowledge":
            # G代码知识查询
            answers = get_answer(message, history)
            
            if not answers[0] or answers[-1] == QuestionType.UNKNOWN:
                answers = get_answer(message, history)
                answers = (answers[0], QuestionType.UNKNOWN)
            
            if answers[-1] == QuestionType.UNKNOWN:
                try:
                    partial_message = ""
                    for chunk in answers[0][1]:
                        if chunk.choices[0].delta.content:
                            partial_message += chunk.choices[0].delta.content
                            yield partial_message
                except Exception as e:
                    print(f"处理知识问答时出错: {e}")
                    yield "抱歉，处理您的问题时出现了错误。"
            else:
                response = answers[0]
                if isinstance(response, tuple):
                    response = response[0]
                if isinstance(response, str):
                    yield response
                else:
                    yield str(response)
            return
            
        else:
            # 未知类型，使用通用LLM回答
            try:
                client = ClientFactory().get_client()
                response = client.chat_completion_stream(
                    [{"role": "user", "content": message}]
                )
                
                partial_message = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        partial_message += chunk.choices[0].delta.content
                        yield partial_message
            except Exception as e:
                yield f"抱歉，我无法理解您的问题。错误：{str(e)}"
                
    except Exception as e:
        print(f"聊天处理出错: {e}")
        import traceback
        traceback.print_exc()
        yield "抱歉，处理您的消息时出现了错误。"