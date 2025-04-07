class ProcessSession:
    def __init__(self):
        self.main_process = None
        self.sub_process = None
        self.param_list = []      # 参数名列表
        self.param_values = {}    # 参数值字典
        self.current_param = None # 当前参数名
        self.param_types = {      # 参数类型映射
            'Cn': int,
            'L': float,
            'Tr': float,
            'Cr': float,
            'F': float
        }

    def init_session(self, main_process: str, sub_process: str, param_list: list):
        """初始化会话"""
        self.main_process = main_process
        self.sub_process = sub_process
        self.param_list = param_list
        self.param_values = {}
        self.current_param = param_list[0] if param_list else None

    def add_param_value(self, value: str) -> tuple[bool, str]:
        """
        添加参数值
        Args:
            value: 参数值字符串
        Returns:
            (是否所有参数都已收集, 下一步提示信息)
        """
        if not self.current_param:
            return True, "所有参数已收集完成"

        try:
            param_type = self.param_types.get(self.current_param, float)
            value = value.strip()

            # 对于int类型，先检查是否是有效的整数
            if param_type == int:
                try:
                    float_val = float(value)
                    if not float_val.is_integer():
                        raise ValueError(f"参数 {self.current_param} 必须是整数，不能是小数")
                    converted_value = int(float_val)
                except ValueError as e:
                    if "could not convert string to float" in str(e):
                        raise ValueError(f"参数 {self.current_param} 必须是数字")
                    raise
            # 对于float类型，直接转换
            elif param_type == float:
                try:
                    converted_value = float(value)
                except ValueError:
                    raise ValueError(f"参数 {self.current_param} 必须是有效的数字")
            else:
                converted_value = param_type(value)

            self.param_values[self.current_param] = converted_value

            current_index = self.param_list.index(self.current_param)
            if current_index < len(self.param_list) - 1:
                self.current_param = self.param_list[current_index + 1]
                next_type = self.param_types.get(self.current_param, float)
                return False, f"请输入参数 {self.current_param} ({next_type.__name__}类型)"
            else:
                self.current_param = None
                return True, "所有参数已收集完成"
        except ValueError as e:
            return False, str(e)

    def clear(self):
        """清除会话状态"""
        self.__init__()

# 全局会话状态
current_session = ProcessSession()


