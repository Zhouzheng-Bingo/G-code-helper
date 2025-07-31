# -*- coding: utf-8 -*-
"""
LLM驱动的G代码验证器 - 轻量级验证机制
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re

from lang_chain.client.client_factory import ClientFactory


class VerificationLevel(Enum):
    """验证级别"""
    PASS = "通过"
    WARNING = "警告"
    ERROR = "错误"


@dataclass
class VerificationIssue:
    """验证问题"""
    level: VerificationLevel
    category: str  # 安全性/效率/规范性
    description: str
    line_number: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class VerificationResult:
    """验证结果"""
    is_valid: bool
    safety_score: float  # 0-10
    efficiency_score: float  # 0-10
    standard_score: float  # 0-10
    overall_score: float  # 0-10
    issues: List[VerificationIssue]
    summary: str
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "is_valid": self.is_valid,
            "scores": {
                "safety": self.safety_score,
                "efficiency": self.efficiency_score,
                "standard": self.standard_score,
                "overall": self.overall_score
            },
            "issues": [
                {
                    "level": issue.level.value,
                    "category": issue.category,
                    "description": issue.description,
                    "line": issue.line_number,
                    "suggestion": issue.suggestion
                }
                for issue in self.issues
            ],
            "summary": self.summary
        }


class LLMGCodeVerifier:
    """LLM驱动的G代码验证器"""
    
    def __init__(self):
        self.llm_client = ClientFactory().get_client()
        
        # 参数安全范围（简化的规则库）
        self.safety_ranges = {
            'F': (10, 3000),     # 进给速度 mm/min
            'S': (100, 5000),    # 主轴转速 rpm
            'depth': (0.1, 50),  # 切削深度 mm
            'D': (1, 500),       # 直径 mm
            'L': (1, 1000),      # 长度 mm
        }
        
        # 关键安全指令
        self.critical_commands = ['G00', 'G01', 'G02', 'G03', 'M03', 'M04', 'M05']
    
    def verify_gcode(self, gcode: str, process_type: str = "", 
                     sub_process: str = "", context: Dict = None) -> VerificationResult:
        """
        验证G代码
        Args:
            gcode: G代码字符串
            process_type: 主工艺类型
            sub_process: 子工艺类型
            context: 上下文信息（如材料、机床等）
        Returns:
            VerificationResult: 验证结果
        """
        if not gcode or not gcode.strip():
            return VerificationResult(
                is_valid=False,
                safety_score=0,
                efficiency_score=0,
                standard_score=0,
                overall_score=0,
                issues=[VerificationIssue(
                    level=VerificationLevel.ERROR,
                    category="基础检查",
                    description="G代码为空"
                )],
                summary="G代码内容为空，无法验证"
            )
        
        # 1. 基础语法检查
        basic_issues = self._basic_syntax_check(gcode)
        
        # 2. 参数范围检查
        param_issues = self._parameter_range_check(gcode)
        
        # 3. LLM深度验证
        llm_result = self._llm_deep_verification(gcode, process_type, sub_process, context)
        
        # 4. 综合评估
        all_issues = basic_issues + param_issues + llm_result.get('issues', [])
        
        # 计算最终分数
        safety_score = llm_result.get('safety_score', 7.0)
        efficiency_score = llm_result.get('efficiency_score', 7.0)
        standard_score = llm_result.get('standard_score', 7.0)
        
        # 根据问题调整分数
        for issue in all_issues:
            if issue.level == VerificationLevel.ERROR:
                if issue.category == "安全性":
                    safety_score -= 2
                elif issue.category == "效率":
                    efficiency_score -= 1.5
                elif issue.category == "规范性":
                    standard_score -= 1.5
            elif issue.level == VerificationLevel.WARNING:
                if issue.category == "安全性":
                    safety_score -= 1
                elif issue.category == "效率":
                    efficiency_score -= 0.5
                elif issue.category == "规范性":
                    standard_score -= 0.5
        
        # 确保分数在合理范围内
        safety_score = max(0, min(10, safety_score))
        efficiency_score = max(0, min(10, efficiency_score))
        standard_score = max(0, min(10, standard_score))
        
        # 计算总分（安全性权重最高）
        overall_score = (safety_score * 0.5 + efficiency_score * 0.25 + standard_score * 0.25)
        
        # 判断是否通过
        has_errors = any(issue.level == VerificationLevel.ERROR for issue in all_issues)
        is_valid = not has_errors and safety_score >= 6
        
        # 生成摘要
        summary = self._generate_summary(is_valid, overall_score, all_issues)
        
        return VerificationResult(
            is_valid=is_valid,
            safety_score=safety_score,
            efficiency_score=efficiency_score,
            standard_score=standard_score,
            overall_score=overall_score,
            issues=all_issues,
            summary=summary
        )
    
    def _basic_syntax_check(self, gcode: str) -> List[VerificationIssue]:
        """基础语法检查"""
        issues = []
        lines = gcode.strip().split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('('):  # 跳过空行和注释
                continue
            
            # 检查是否以有效的G/M/T/S/F指令开头
            if not re.match(r'^[GMTSF]\d+', line, re.IGNORECASE):
                # 检查是否是坐标行（X/Y/Z/I/J/K）
                if not re.match(r'^[XYZIJK][-\d.]+', line, re.IGNORECASE):
                    issues.append(VerificationIssue(
                        level=VerificationLevel.WARNING,
                        category="规范性",
                        description=f"第{i}行可能存在语法错误",
                        line_number=i,
                        suggestion="确保每行以有效的G/M/T/S/F指令或坐标值开头"
                    ))
            
            # 检查危险的快速定位
            if 'G00' in line.upper() and any(coord in line.upper() for coord in ['X', 'Y', 'Z']):
                # 检查是否有过大的移动
                coords = re.findall(r'[XYZ]([-\d.]+)', line, re.IGNORECASE)
                for coord in coords:
                    try:
                        value = abs(float(coord[1]))
                        if value > 500:  # 超过500mm的快速移动
                            issues.append(VerificationIssue(
                                level=VerificationLevel.WARNING,
                                category="安全性",
                                description=f"第{i}行快速定位距离较大({value}mm)",
                                line_number=i,
                                suggestion="检查是否确实需要如此大的快速移动"
                            ))
                    except ValueError:
                        pass
        
        return issues
    
    def _parameter_range_check(self, gcode: str) -> List[VerificationIssue]:
        """参数范围检查"""
        issues = []
        
        # 检查进给速度
        f_values = re.findall(r'F(\d+\.?\d*)', gcode, re.IGNORECASE)
        for f_val in f_values:
            try:
                f = float(f_val)
                min_f, max_f = self.safety_ranges['F']
                if f < min_f or f > max_f:
                    issues.append(VerificationIssue(
                        level=VerificationLevel.WARNING,
                        category="安全性",
                        description=f"进给速度F{f}超出推荐范围({min_f}-{max_f})",
                        suggestion=f"建议将进给速度调整到{min_f}-{max_f}mm/min范围内"
                    ))
            except ValueError:
                pass
        
        # 检查主轴转速
        s_values = re.findall(r'S(\d+\.?\d*)', gcode, re.IGNORECASE)
        for s_val in s_values:
            try:
                s = float(s_val)
                min_s, max_s = self.safety_ranges['S']
                if s < min_s or s > max_s:
                    issues.append(VerificationIssue(
                        level=VerificationLevel.WARNING,
                        category="安全性",
                        description=f"主轴转速S{s}超出推荐范围({min_s}-{max_s})",
                        suggestion=f"建议将主轴转速调整到{min_s}-{max_s}rpm范围内"
                    ))
            except ValueError:
                pass
        
        return issues
    
    def _llm_deep_verification(self, gcode: str, process_type: str, 
                               sub_process: str, context: Dict) -> Dict:
        """使用LLM进行深度验证"""
        context_str = ""
        if context:
            context_str = f"\n上下文信息：{context}"
        
        prompt = f"""作为数控专家，请对以下G代码进行全面的安全性、效率和规范性验证。

工艺信息：
- 主工艺：{process_type or '未指定'}
- 子工艺：{sub_process or '未指定'}{context_str}

G代码：
```
{gcode}
```

请从以下三个方面进行评估：

1. 安全性（最重要）：
   - 进给速度和主轴转速是否合理
   - 切削深度是否过大
   - 是否有碰撞风险
   - 刀具路径是否安全

2. 效率：
   - 加工路径是否优化
   - 是否有不必要的空行程
   - 切削参数是否可以优化

3. 规范性：
   - G/M代码使用是否规范
   - 程序结构是否清晰
   - 是否缺少必要的指令

请返回JSON格式的验证结果：
{{
    "safety_score": 0-10的安全性评分,
    "efficiency_score": 0-10的效率评分,
    "standard_score": 0-10的规范性评分,
    "issues": [
        {{
            "level": "ERROR/WARNING/PASS",
            "category": "安全性/效率/规范性",
            "description": "问题描述",
            "line_number": 行号(如果适用),
            "suggestion": "改进建议"
        }}
    ],
    "critical_safety_concern": true/false,
    "optimization_suggestions": ["建议1", "建议2"]
}}"""

        try:
            response = self.llm_client.chat_with_ai(prompt)
            
            # 解析JSON响应
            import json
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            else:
                json_str = response
            
            result = json.loads(json_str)
            
            # 转换issues格式
            converted_issues = []
            for issue in result.get('issues', []):
                level_map = {
                    'ERROR': VerificationLevel.ERROR,
                    'WARNING': VerificationLevel.WARNING,
                    'PASS': VerificationLevel.PASS
                }
                converted_issues.append(VerificationIssue(
                    level=level_map.get(issue['level'], VerificationLevel.WARNING),
                    category=issue['category'],
                    description=issue['description'],
                    line_number=issue.get('line_number'),
                    suggestion=issue.get('suggestion')
                ))
            
            return {
                'safety_score': result.get('safety_score', 7),
                'efficiency_score': result.get('efficiency_score', 7),
                'standard_score': result.get('standard_score', 7),
                'issues': converted_issues,
                'critical_safety_concern': result.get('critical_safety_concern', False),
                'optimization_suggestions': result.get('optimization_suggestions', [])
            }
            
        except Exception as e:
            print(f"LLM验证失败: {e}")
            # 返回默认值
            return {
                'safety_score': 7,
                'efficiency_score': 7,
                'standard_score': 7,
                'issues': [],
                'critical_safety_concern': False,
                'optimization_suggestions': []
            }
    
    def _generate_summary(self, is_valid: bool, overall_score: float, 
                         issues: List[VerificationIssue]) -> str:
        """生成验证摘要"""
        error_count = sum(1 for issue in issues if issue.level == VerificationLevel.ERROR)
        warning_count = sum(1 for issue in issues if issue.level == VerificationLevel.WARNING)
        
        if is_valid:
            if overall_score >= 8:
                status = "优秀"
            elif overall_score >= 7:
                status = "良好"
            else:
                status = "合格"
            
            summary = f"✅ G代码验证通过（{status}，总分{overall_score:.1f}/10）"
            
            if warning_count > 0:
                summary += f"，存在{warning_count}个警告建议改进"
        else:
            summary = f"❌ G代码验证失败（总分{overall_score:.1f}/10）"
            
            if error_count > 0:
                summary += f"，发现{error_count}个错误"
            if warning_count > 0:
                summary += f"和{warning_count}个警告"
            
            summary += "，需要修正后才能使用"
        
        return summary
    
    def verify_and_fix(self, gcode: str, process_type: str = "", 
                      sub_process: str = "") -> Tuple[str, VerificationResult]:
        """
        验证并尝试修复G代码
        Args:
            gcode: 原始G代码
            process_type: 主工艺类型
            sub_process: 子工艺类型
        Returns:
            (修复后的G代码, 验证结果)
        """
        # 先验证原始代码
        result = self.verify_gcode(gcode, process_type, sub_process)
        
        if result.is_valid:
            return gcode, result
        
        # 如果有错误，尝试修复
        errors = [issue for issue in result.issues if issue.level == VerificationLevel.ERROR]
        
        if not errors:
            return gcode, result
        
        # 使用LLM修复
        prompt = f"""作为数控专家，请修复以下G代码中的错误。

原始G代码：
```
{gcode}
```

发现的错误：
{self._format_issues_for_fix(errors)}

请返回修复后的G代码，只返回代码，不要其他说明。
保持原有的功能不变，只修复安全性和语法错误。"""

        try:
            fixed_gcode = self.llm_client.chat_with_ai(prompt)
            
            # 提取代码
            if '```' in fixed_gcode:
                start = fixed_gcode.find('```') + 3
                if fixed_gcode[start:start+5].lower() == 'gcode':
                    start += 5
                end = fixed_gcode.find('```', start)
                if end > start:
                    fixed_gcode = fixed_gcode[start:end].strip()
            
            # 验证修复后的代码
            fixed_result = self.verify_gcode(fixed_gcode, process_type, sub_process)
            
            return fixed_gcode, fixed_result
            
        except Exception as e:
            print(f"自动修复失败: {e}")
            return gcode, result
    
    def _format_issues_for_fix(self, issues: List[VerificationIssue]) -> str:
        """格式化问题列表用于修复"""
        lines = []
        for issue in issues:
            line_info = f"第{issue.line_number}行" if issue.line_number else ""
            lines.append(f"- {line_info} {issue.description}")
            if issue.suggestion:
                lines.append(f"  建议：{issue.suggestion}")
        return '\n'.join(lines)


# 便捷函数
def verify_gcode(gcode: str, process_type: str = "", sub_process: str = "") -> VerificationResult:
    """验证G代码的便捷接口"""
    verifier = LLMGCodeVerifier()
    return verifier.verify_gcode(gcode, process_type, sub_process)


def verify_and_fix_gcode(gcode: str, process_type: str = "", sub_process: str = "") -> Tuple[str, VerificationResult]:
    """验证并修复G代码的便捷接口"""
    verifier = LLMGCodeVerifier()
    return verifier.verify_and_fix(gcode, process_type, sub_process)


# 全局实例
_verifier = None

def get_gcode_verifier() -> LLMGCodeVerifier:
    """获取验证器的单例"""
    global _verifier
    if _verifier is None:
        _verifier = LLMGCodeVerifier()
    return _verifier