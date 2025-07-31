# -*- coding: utf-8 -*-
"""
增强的G代码生成器 - 集成LLM模板选择
"""

from typing import Dict, Optional, Tuple
from qa.function_tool import generate_gcode as original_generate_gcode
from qa.llm_template_selector import get_template_selector
from qa.llm_gcode_verifier import get_gcode_verifier, VerificationLevel
from lang_chain.client.client_factory import ClientFactory


class EnhancedGCodeGenerator:
    """增强的G代码生成器"""
    
    def __init__(self):
        self.template_selector = get_template_selector()
        self.verifier = get_gcode_verifier()
        self.llm_client = ClientFactory().get_client()
    
    def generate_with_intelligence(self, process_type: str, sub_process: str, 
                                 params: Dict[str, any], user_description: str = "") -> Tuple[str, str]:
        """
        智能生成G代码
        Args:
            process_type: 主工艺类型
            sub_process: 子工艺类型
            params: 参数字典
            user_description: 用户的原始描述
        Returns:
            (G代码, 生成说明)
        """
        # 1. 使用LLM选择最佳模板
        template_code, explanation, suggestions = self.template_selector.select_best_template(
            process_type, sub_process, params, user_description
        )
        
        if not template_code:
            return "", "未找到合适的加工模板"
        
        # 2. 生成G代码
        try:
            # 使用原有的生成函数，但传入选定的模板
            gcode = original_generate_gcode(sub_process, params)
            
            # 3. LLM优化G代码
            optimized_gcode = self._optimize_gcode(gcode, process_type, sub_process, params)
            
            # 4. 验证G代码
            verification_result = self.verifier.verify_gcode(
                optimized_gcode, process_type, sub_process, {"params": params}
            )
            
            # 5. 如果验证失败，尝试修复
            if not verification_result.is_valid:
                fixed_gcode, fixed_result = self.verifier.verify_and_fix(
                    optimized_gcode, process_type, sub_process
                )
                if fixed_result.is_valid:
                    optimized_gcode = fixed_gcode
                    verification_result = fixed_result
            
            # 6. 生成完整说明
            full_explanation = self._generate_full_explanation(
                explanation, suggestions, gcode != optimized_gcode,
                verification_result
            )
            
            return optimized_gcode, full_explanation
            
        except Exception as e:
            return "", f"G代码生成失败: {str(e)}"
    
    def _optimize_gcode(self, gcode: str, process_type: str, 
                       sub_process: str, params: Dict[str, any]) -> str:
        """使用LLM优化G代码"""
        prompt = f"""作为数控专家，请检查并优化以下G代码。

工艺信息：
- 类型：{process_type} - {sub_process}
- 参数：{params}

生成的G代码：
{gcode}

请检查：
1. 安全性（进给速度、切削深度是否合理）
2. 效率（是否可以优化路径）
3. 规范性（指令格式是否标准）

如果需要优化，请返回优化后的G代码。
如果不需要优化，请返回"NO_OPTIMIZATION_NEEDED"。"""

        try:
            response = self.llm_client.chat_with_ai(prompt)
            
            if "NO_OPTIMIZATION_NEEDED" in response:
                return gcode
            
            # 提取优化后的代码
            if "```" in response:
                # 提取代码块
                start = response.find("```") + 3
                if response[start:start+5].lower() == "gcode":
                    start += 5
                end = response.find("```", start)
                if end > start:
                    optimized = response[start:end].strip()
                    return optimized
            
            # 如果格式不标准，检查是否包含G代码指令
            lines = response.strip().split('\n')
            gcode_lines = [line for line in lines if any(
                line.strip().startswith(cmd) for cmd in ['G', 'M', 'T', 'S', 'F']
            )]
            
            if gcode_lines:
                return '\n'.join(gcode_lines)
                
        except Exception as e:
            print(f"G代码优化失败: {e}")
        
        return gcode  # 优化失败则返回原代码
    
    def _generate_full_explanation(self, template_explanation: str, 
                                  suggestions: str, was_optimized: bool,
                                  verification_result=None) -> str:
        """生成完整的说明"""
        parts = []
        
        # 模板选择说明
        if template_explanation:
            parts.append(f"📋 模板选择：{template_explanation}")
        
        # 参数建议
        if suggestions:
            parts.append(f"💡 参数建议：{suggestions}")
        
        # 优化说明
        if was_optimized:
            parts.append("✨ G代码已优化：提升了安全性和效率")
        
        # 验证结果
        if verification_result:
            parts.append(f"🔍 验证结果：{verification_result.summary}")
            
            # 如果有警告，显示关键警告
            warnings = [issue for issue in verification_result.issues 
                       if issue.level == VerificationLevel.WARNING]
            if warnings and len(warnings) <= 3:
                parts.append("⚠️ 注意事项：")
                for warning in warnings[:3]:
                    parts.append(f"  - {warning.description}")
        
        return '\n'.join(parts) if parts else "G代码生成成功"
    
    def analyze_gcode_quality(self, gcode: str) -> Dict[str, any]:
        """分析G代码质量"""
        prompt = f"""分析以下G代码的质量。

G代码：
{gcode}

请评估并返回JSON格式：
{{
    "safety_score": 0-10的安全性评分,
    "efficiency_score": 0-10的效率评分,
    "standard_score": 0-10的规范性评分,
    "issues": ["问题1", "问题2"],
    "improvements": ["改进建议1", "改进建议2"]
}}"""

        try:
            response = self.llm_client.chat_with_ai(prompt)
            
            import json
            # 提取JSON
            if '```json' in response:
                start = response.find('```json') + 7
                end = response.find('```', start)
                json_str = response[start:end].strip()
            else:
                # 尝试直接解析
                json_str = response
            
            return json.loads(json_str)
            
        except Exception as e:
            print(f"质量分析失败: {e}")
            return {
                "safety_score": 5,
                "efficiency_score": 5,
                "standard_score": 5,
                "issues": [],
                "improvements": []
            }


# 便捷函数
def generate_gcode_intelligently(process_type: str, sub_process: str, 
                               params: Dict[str, any], description: str = "") -> Tuple[str, str]:
    """智能生成G代码的便捷接口"""
    generator = EnhancedGCodeGenerator()
    return generator.generate_with_intelligence(process_type, sub_process, params, description)