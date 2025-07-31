# -*- coding: utf-8 -*-
"""
增强的会话管理 - 支持LLM智能交互
"""

from qa.session_state import ProcessSession
from qa.llm_parameter_agent import get_parameter_agent


class EnhancedProcessSession(ProcessSession):
    """增强的会话管理，支持LLM智能参数收集"""
    
    def __init__(self):
        super().__init__()
        self.param_agent = get_parameter_agent()
        self.collected_context = {}  # 存储收集过程的上下文
        self.param_info = {}  # 存储参数的详细信息
    
    def init_session(self, main_process: str, sub_process: str, param_list: list):
        """初始化会话 - 增强版"""
        super().init_session(main_process, sub_process, param_list)
        
        # 获取参数的详细信息
        self.param_info = self.param_agent.analyze_required_params(main_process, sub_process)
        
        # 重新排序参数列表（关键参数优先）
        self._reorder_params()
    
    def _reorder_params(self):
        """根据参数重要性重新排序"""
        # 将必需参数排在前面
        required = []
        optional = []
        
        for param in self.param_list:
            if param in self.param_info and self.param_info[param].required:
                required.append(param)
            else:
                optional.append(param)
        
        self.param_list = required + optional
        if self.param_list:
            self.current_param = self.param_list[0]
    
    def get_next_question(self) -> str:
        """获取下一个参数的自然询问"""
        if not self.current_param:
            return "所有参数已收集完成"
        
        # 使用LLM生成自然的询问
        question = self.param_agent.generate_natural_question(
            self.current_param,
            self.param_values  # 传入已收集的参数作为上下文
        )
        
        return question
    
    def add_param_value_smart(self, user_input: str) -> tuple[bool, str]:
        """
        智能添加参数值 - 能理解自然语言回答
        Args:
            user_input: 用户的回答（可能是自然语言）
        Returns:
            (是否所有参数都已收集, 下一步提示信息)
        """
        if not self.current_param:
            return True, "所有参数已收集完成"
        
        # 获取参数类型
        param_type = self.param_types.get(self.current_param, float)
        
        # 使用LLM解析用户回答
        value = self.param_agent.parse_user_answer(user_input, self.current_param, param_type)
        
        if value is None:
            # 如果解析失败，给出更友好的提示
            return False, f"抱歉，我没能理解您的回答。请提供{self.current_param}的数值，例如：{self._get_example_value()}"
        
        # 存储参数值
        self.param_values[self.current_param] = value
        
        # 尝试推理相关参数
        inferred = self.param_agent.infer_related_params(
            self.param_values,
            self.param_info
        )
        
        # 应用推理的参数
        for param, inferred_value in inferred.items():
            if param in self.param_list and param not in self.param_values:
                self.param_values[param] = inferred_value
                # 从待收集列表中移除
                if param in self.param_list:
                    self.param_list.remove(param)
        
        # 移动到下一个参数
        current_index = self.param_list.index(self.current_param) if self.current_param in self.param_list else -1
        
        if current_index >= 0 and current_index < len(self.param_list) - 1:
            # 找到下一个未收集的参数
            remaining_params = [p for p in self.param_list if p not in self.param_values]
            if remaining_params:
                self.current_param = remaining_params[0]
                next_question = self.get_next_question()
                
                if inferred:
                    next_question = f"已智能推理出：{', '.join([f'{k}={v}' for k, v in inferred.items()])}\n\n{next_question}"
                
                return False, next_question
        
        # 所有参数已收集
        self.current_param = None
        
        # 验证参数完整性
        is_valid, validation_msg = self.param_agent.validate_params(
            self.param_values,
            self.main_process,
            self.sub_process
        )
        
        if not is_valid:
            # 如果验证失败，可能需要补充参数
            return False, validation_msg
        
        return True, "所有参数已收集完成，可以生成G代码了！"
    
    def _get_example_value(self) -> str:
        """获取参数的示例值"""
        examples = {
            "Cn": "2",
            "L": "100.0",
            "Tr": "0.5",
            "Cr": "1.0",
            "F": "300.0",
            "D": "20.0",
            "S": "1500",
            "depth": "5.0"
        }
        return examples.get(self.current_param, "一个数值")


# 创建增强版会话的全局实例
enhanced_session = EnhancedProcessSession()