# -*- coding: utf-8 -*-
"""
LLM驱动的智能参数补全代理
"""

import re
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from lang_chain.client.client_factory import ClientFactory
from qa.session_state import ProcessSession


@dataclass
class ParameterInfo:
    """参数信息"""
    name: str
    type: type
    description: str
    required: bool = True
    default_value: Optional[any] = None
    dependencies: List[str] = None  # 依赖的其他参数


class LLMParameterAgent:
    """LLM驱动的参数补全代理"""
    
    def __init__(self):
        self.llm_client = ClientFactory().get_client()
        
        # 参数知识库
        self.param_knowledge = {
            "Cn": ParameterInfo("Cn", int, "圈数/循环次数", required=True),
            "L": ParameterInfo("L", float, "加工长度(mm)", required=True),
            "Tr": ParameterInfo("Tr", float, "过渡半径/退刀量(mm)", required=True),
            "Cr": ParameterInfo("Cr", float, "退回半径(mm)", required=True),
            "F": ParameterInfo("F", float, "进给速度(mm/min)", required=True),
            "D": ParameterInfo("D", float, "直径(mm)", required=False),
            "S": ParameterInfo("S", int, "主轴转速(rpm)", required=False),
            "depth": ParameterInfo("depth", float, "深度(mm)", required=False),
        }
        
        # 参数依赖关系
        self.param_dependencies = {
            "F": ["material", "tool_type"],  # 进给速度依赖材料和刀具
            "S": ["D", "material"],          # 转速依赖直径和材料
        }
    
    def analyze_required_params(self, process_type: str, sub_process: str) -> Dict[str, ParameterInfo]:
        """使用LLM分析工艺所需参数"""
        prompt = f"""你是数控加工专家。请分析以下工艺所需的参数。

工艺类型：{process_type}
子工艺：{sub_process}

请基于你的专业知识，列出该工艺必需的参数和可选参数。

注意：
1. 必需参数是完成该工艺必不可少的
2. 可选参数可以提升加工质量但不是必需的
3. 考虑参数之间的依赖关系

输出JSON格式：
{{
    "required_params": ["参数1", "参数2", ...],
    "optional_params": ["参数3", "参数4", ...],
    "param_descriptions": {{
        "参数1": "描述",
        "参数2": "描述"
    }},
    "dependencies": {{
        "参数1": ["依赖的参数"],
        ...
    }}
}}"""

        try:
            response = self.llm_client.chat_with_ai(prompt)
            # 解析LLM响应
            import json
            
            # 提取JSON
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            # 清理JSON字符串
            json_str = json_str.replace('\n', '').replace('\r', '')
            if not json_str.startswith('{'):
                start_idx = json_str.find('{')
                if start_idx != -1:
                    json_str = json_str[start_idx:]
            if not json_str.endswith('}'):
                end_idx = json_str.rfind('}')
                if end_idx != -1:
                    json_str = json_str[:end_idx+1]
            
            print(f"解析参数分析JSON: {json_str}")  # 调试信息
            result = json.loads(json_str)
            
            # 构建参数信息
            params = {}
            for param in result.get('required_params', []):
                if param in self.param_knowledge:
                    params[param] = self.param_knowledge[param]
                else:
                    params[param] = ParameterInfo(
                        param, float, 
                        result.get('param_descriptions', {}).get(param, ""),
                        required=True
                    )
            
            for param in result.get('optional_params', []):
                if param in self.param_knowledge:
                    info = self.param_knowledge[param]
                    info.required = False
                    params[param] = info
                else:
                    params[param] = ParameterInfo(
                        param, float,
                        result.get('param_descriptions', {}).get(param, ""),
                        required=False
                    )
            
            return params
            
        except Exception as e:
            print(f"LLM分析参数失败，使用默认参数集: {e}")
            # 降级到默认参数集
            return self._get_default_params(process_type, sub_process)
    
    def _get_default_params(self, process_type: str, sub_process: str) -> Dict[str, ParameterInfo]:
        """获取默认参数集（降级方案）"""
        # 基于现有模板的默认参数
        default_sets = {
            "外圆": ["Cn", "L", "Tr", "Cr", "F"],
            "内圆": ["D", "L", "F"],
            "端面": ["L", "F"],
            "切槽": ["depth", "L", "F"],
            "螺纹": ["D", "L", "F", "S"],
        }
        
        param_names = default_sets.get(sub_process, ["L", "F"])
        return {name: self.param_knowledge[name] for name in param_names if name in self.param_knowledge}
    
    def generate_natural_question(self, param: str, context: Dict[str, any]) -> str:
        """生成自然的参数询问"""
        # 构建上下文提示
        context_info = ""
        if context:
            context_info = "已知参数：\n"
            for p, v in context.items():
                context_info += f"- {p} = {v}\n"
        
        prompt = f"""你是友好的数控编程助手。请为参数'{param}'生成一个自然、友好的询问语句。

{context_info}

参数信息：
- 参数名：{param}
- 描述：{self.param_knowledge.get(param, ParameterInfo(param, float, "")).description}

要求：
1. 使用自然的中文表达
2. 如果有已知参数，可以参考它们给出建议范围
3. 语气友好、专业
4. 可以提供常用值作为参考

请直接输出询问语句，不要有其他内容。"""

        try:
            question = self.llm_client.chat_with_ai(prompt)
            return question.strip()
        except Exception as e:
            print(f"生成自然问题失败: {e}")
            # 降级到简单询问
            param_info = self.param_knowledge.get(param, ParameterInfo(param, float, ""))
            return f"请输入{param_info.description or param}："
    
    def parse_user_answer(self, answer: str, param: str, param_type: type) -> Optional[any]:
        """从用户回答中提取参数值"""
        # 先尝试直接解析
        try:
            if param_type == int:
                # 处理可能的小数输入
                val = float(answer.strip())
                if val.is_integer():
                    return int(val)
                else:
                    raise ValueError("需要整数")
            elif param_type == float:
                return float(answer.strip())
            else:
                return param_type(answer.strip())
        except:
            # 如果直接解析失败，使用LLM理解
            pass
        
        # 使用LLM理解用户意图
        prompt = f"""用户在回答参数'{param}'的值时说："{answer}"

请从中提取数值。注意：
1. 用户可能用自然语言表达，如"大概50左右"、"差不多100"
2. 可能包含单位，如"20毫米"、"300mm/min"
3. 可能有范围表达，取中间值

如果能提取到明确数值，直接返回数字。
如果无法提取，返回"UNABLE_TO_PARSE"。

只返回数字或"UNABLE_TO_PARSE"，不要有其他内容。"""

        try:
            result = self.llm_client.chat_with_ai(prompt).strip()
            
            if result == "UNABLE_TO_PARSE":
                return None
            
            # 尝试转换结果
            if param_type == int:
                return int(float(result))
            elif param_type == float:
                return float(result)
            else:
                return param_type(result)
                
        except Exception as e:
            print(f"LLM解析用户回答失败: {e}")
            return None
    
    def infer_related_params(self, known_params: Dict[str, any], 
                           all_params: Dict[str, ParameterInfo]) -> Dict[str, any]:
        """基于已知参数推理其他参数"""
        inferred = {}
        
        # 构建推理提示
        known_str = "\n".join([f"- {k} = {v}" for k, v in known_params.items()])
        missing = [p for p in all_params if p not in known_params and not all_params[p].required]
        
        if not missing:
            return inferred
        
        prompt = f"""基于以下已知参数，推理其他参数的合理值。

已知参数：
{known_str}

需要推理的参数：{', '.join(missing)}

请基于数控加工经验给出合理的推荐值。考虑：
1. 材料特性（如果能推断）
2. 加工精度要求
3. 安全性
4. 效率

输出JSON格式：
{{
    "参数名": 推荐值,
    "reasoning": "推理依据"
}}"""

        try:
            response = self.llm_client.chat_with_ai(prompt)
            
            # 解析响应
            import json
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            # 清理可能的问题字符
            json_str = json_str.replace('\n', '').replace('\r', '')
            
            # 尝试修复常见的JSON格式问题
            if not json_str.startswith('{'):
                # 寻找第一个{
                start_idx = json_str.find('{')
                if start_idx != -1:
                    json_str = json_str[start_idx:]
            
            if not json_str.endswith('}'):
                # 寻找最后一个}
                end_idx = json_str.rfind('}')
                if end_idx != -1:
                    json_str = json_str[:end_idx+1]
            
            print(f"尝试解析JSON: {json_str}")  # 调试信息
            result = json.loads(json_str)
            
            # 提取推理的参数值
            for param, value in result.items():
                if param != "reasoning" and param in missing:
                    param_info = all_params[param]
                    try:
                        if param_info.type == int:
                            inferred[param] = int(value)
                        elif param_info.type == float:
                            inferred[param] = float(value)
                        else:
                            inferred[param] = value
                    except:
                        pass
            
            if result.get("reasoning"):
                print(f"参数推理依据：{result['reasoning']}")
                
        except Exception as e:
            print(f"参数推理失败: {e}")
        
        return inferred
    
    def validate_params(self, params: Dict[str, any], process_type: str, sub_process: str) -> Tuple[bool, str]:
        """验证参数完整性和合理性"""
        prompt = f"""验证以下参数对于{process_type}-{sub_process}工艺是否完整且合理。

参数：
{chr(10).join([f'- {k} = {v}' for k, v in params.items()])}

请检查：
1. 是否所有必需参数都已提供
2. 参数值是否在合理范围内
3. 参数之间是否存在冲突
4. 是否需要警告或建议

输出JSON格式：
{{
    "is_valid": true/false,
    "missing_params": ["参数1", ...],
    "warnings": ["警告1", ...],
    "suggestions": ["建议1", ...]
}}"""

        try:
            response = self.llm_client.chat_with_ai(prompt)
            
            import json
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
                
            # 清理JSON字符串
            json_str = json_str.replace('\n', '').replace('\r', '')
            if not json_str.startswith('{'):
                start_idx = json_str.find('{')
                if start_idx != -1:
                    json_str = json_str[start_idx:]
            if not json_str.endswith('}'):
                end_idx = json_str.rfind('}')
                if end_idx != -1:
                    json_str = json_str[:end_idx+1]
            
            print(f"解析参数验证JSON: {json_str}")  # 调试信息
            result = json.loads(json_str)
            
            is_valid = result.get('is_valid', True)
            messages = []
            
            if result.get('missing_params'):
                messages.append(f"缺少参数：{', '.join(result['missing_params'])}")
            
            if result.get('warnings'):
                messages.extend(result['warnings'])
                
            if result.get('suggestions'):
                messages.extend(result['suggestions'])
            
            return is_valid, '\n'.join(messages) if messages else "参数验证通过"
            
        except Exception as e:
            print(f"参数验证失败: {e}")
            # 降级到基础验证
            return True, "参数已收集完成"


# 全局实例
_parameter_agent = None

def get_parameter_agent() -> LLMParameterAgent:
    """获取参数补全代理的单例"""
    global _parameter_agent
    if _parameter_agent is None:
        _parameter_agent = LLMParameterAgent()
    return _parameter_agent