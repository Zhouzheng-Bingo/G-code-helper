from qa.function_tool import P

class OuterCircle1Process(P):
    def __init__(self, sub_process_type: str, Cn: int, L: float, Tr: float, Cr: float, F: float, **kwargs):
        """
        初始化外圆工艺加工过程的参数。

        参数:
            sub_process_type (str): 子工艺类型。
            Cn (int): 圆圈数量。
            L (float): 长度。
            Tr (float): 过渡半径。
            Cr (float): 退回半径。
            F (float): 进给速度。
        """
        super().__init__(sub_process_type, **kwargs)
        self.Cn = int(Cn)  # 圆圈数量
        self.L = float(L)  # 长度
        self.Tr = float(Tr)  # 过渡半径
        self.Cr = float(Cr)  # 退回半径
        self.F = float(F)  # 进给速度

    def generate_gcode(self) -> str:
        """
        根据外圆工艺参数生成 G 代码。
        返回:
            str: 生成的 G 代码。
        """
        gcode_lines = []
        
        try:
            self.Cn = int(self.Cn)
        except ValueError:
            raise ValueError(f"Cn 的值 {self.Cn} 不是有效的整数")

        for a in range(self.Cn):
            if a == 0:
                # 第一圈的 G 代码生成逻辑
                gcode_lines.extend([
                    f"G01 U[{self.Tr} * #521] F{self.F};",
                    f"G01 W[{self.L} * #520] F{self.F};",
                    f"G00 U[{self.Tr} * #521 * -1] F{self.F};",
                    f"G00 W[{self.L} * #520 * -1] F{self.F};"
                ])

                if self.Cn == 1:
                    gcode_lines.extend([
                        "G00 Z0;",  # 返回起始点
                        "M30;"      # 程序结束
                    ])
            elif a < self.Cn - 1:
                # 中间圈的 G 代码生成逻辑
                gcode_lines.extend([
                    f"G01 U[{self.Tr * 2} * #521] F{self.F};",
                    f"G01 W[{self.L} * #520] F{self.F};",
                    f"G00 U[{self.Tr} * #521 * -1] F{self.F};",
                    f"G00 W[{self.L} * #520 * -1] F{self.F};"
                ])
            else:
                # 最后一圈的 G 代码生成逻辑
                gcode_lines.extend([
                    f"G01 U[{self.Tr * 2} * #521] F{self.F};",
                    f"G01 W[{self.L} * #520] F{self.F};",
                    f"G00 U[{self.Cr} * #521 * -1] F{self.F};",
                    f"G00 W[{self.L} * #520 * -1] F{self.F};",
                    "G00 Z0;",  # 返回起始点
                    "M30;"      # 程序结束
                ])

        return '\n'.join(gcode_lines) 