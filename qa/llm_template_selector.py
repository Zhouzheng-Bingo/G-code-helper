# -*- coding: utf-8 -*-
"""
LLM驱动的智能模板选择器
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import re

from dao.graph.graph_dao import GraphDao
from lang_chain.client.client_factory import ClientFactory
from qa.function_tool import get_process_template, parse_template_params, generate_gcode


@dataclass
class TemplateInfo:
    """模板信息"""
    name: str
    code: str
    params: List[str]
    description: str = ""
    usage_count: int = 0


@dataclass
class TemplateScore:
    """模板评分"""
    template: TemplateInfo
    llm_score: float = 0.0
    param_match_score: float = 0.0
    usage_score: float = 0.0
    semantic_score: float = 0.0
    total_score: float = 0.0
    explanation: str = ""


class LLMTemplateSelector:
    """LLM驱动的模板选择器"""
    
    def __init__(self):
        self.llm_client = ClientFactory().get_client()
        self.graph_dao = GraphDao()
        
        # 权重配置
        self.weights = {
            'llm': 0.5,      # LLM评分权重最高
            'param': 0.2,    # 参数匹配度
            'usage': 0.1,    # 历史使用
            'semantic': 0.2  # 语义相似度
        }
    
    def select_best_template(self, process_type: str, sub_process: str, 
                           user_params: Dict[str, any], user_description: str = "") -> Tuple[Optional[str], str, str]:
        """
        选择最佳模板
        Args:
            process_type: 主工艺类型
            sub_process: 子工艺类型
            user_params: 用户提供的参数
            user_description: 用户的自然语言描述
        Returns:
            (模板代码, 选择理由, 优化建议)
        """
        # 1. 获取候选模板
        candidates = self._get_candidate_templates(process_type, sub_process)
        
        if not candidates:
            return None, "未找到匹配的模板", ""
        
        # 如果只有一个候选，直接返回
        if len(candidates) == 1:
            return candidates[0].code, f"找到唯一匹配的{sub_process}模板", ""
        
        # 2. 评估每个模板
        scores = []
        for template in candidates:
            score = self._evaluate_template(template, user_params, user_description)
            scores.append(score)
        
        # 3. 选择最优模板
        best_score = max(scores, key=lambda s: s.total_score)
        
        # 4. 生成详细解释
        explanation = self._generate_explanation(best_score, scores)
        
        # 5. 生成优化建议
        suggestions = self._generate_suggestions(best_score.template, user_params)
        
        return best_score.template.code, explanation, suggestions
    
    def _get_candidate_templates(self, process_type: str, sub_process: str) -> List[TemplateInfo]:
        """从知识图谱获取候选模板"""
        templates = []
        
        # 精确匹配
        template_code = get_process_template(sub_process)
        if template_code:
            params = parse_template_params(template_code)
            templates.append(TemplateInfo(
                name=sub_process,
                code=template_code,
                params=params,
                description=f"{process_type}-{sub_process}",
                usage_count=self._get_usage_count(sub_process)
            ))
        
        # 如果没有精确匹配，尝试模糊搜索
        if not templates:
            # 查询同一主工艺下的其他子工艺
            query = f"""
            MATCH (p:Process {{name: '{process_type}'}})-[:INCLUDES]->(s:SubProcess)
            WHERE s.code IS NOT NULL
            RETURN s.name as name, s.code as code
            """
            
            try:
                results = self.graph_dao.run_cypher(query).data()
                for result in results:
                    if result['code']:
                        params = parse_template_params(result['code'])
                        templates.append(TemplateInfo(
                            name=result['name'],
                            code=result['code'],
                            params=params,
                            description=f"{process_type}-{result['name']}",
                            usage_count=self._get_usage_count(result['name'])
                        ))
            except Exception as e:
                print(f"模糊搜索失败: {e}")
        
        return templates
    
    def _get_usage_count(self, template_name: str) -> int:
        """获取模板使用次数（从图谱或缓存中）"""
        # 这里简化处理，实际可以从图谱中查询
        # 或维护一个使用计数器
        default_counts = {
            "外圆": 100,
            "内圆": 80,
            "端面": 60,
            "切槽": 40,
            "螺纹": 50,
        }
        return default_counts.get(template_name, 10)
    
    def _evaluate_template(self, template: TemplateInfo, user_params: Dict[str, any], 
                          user_description: str) -> TemplateScore:
        """评估单个模板"""
        score = TemplateScore(template=template)
        
        # 1. LLM评估
        score.llm_score = self._llm_evaluate(template, user_params, user_description)
        
        # 2. 参数匹配度
        score.param_match_score = self._calculate_param_match(template.params, user_params)
        
        # 3. 使用频率得分
        total_usage = sum(self._get_usage_count(t) for t in ["外圆", "内圆", "端面", "切槽", "螺纹"])
        score.usage_score = template.usage_count / max(total_usage, 1)
        
        # 4. 语义相似度（简化处理）
        score.semantic_score = self._calculate_semantic_similarity(template.description, user_description)
        
        # 5. 计算总分
        score.total_score = (
            self.weights['llm'] * score.llm_score +
            self.weights['param'] * score.param_match_score +
            self.weights['usage'] * score.usage_score +
            self.weights['semantic'] * score.semantic_score
        )
        
        return score
    
    def _llm_evaluate(self, template: TemplateInfo, user_params: Dict[str, any], 
                     user_description: str) -> float:
        """使用LLM评估模板适配度"""
        prompt = f"""作为数控专家，请评估以下模板对用户需求的适配度。

模板信息：
- 名称：{template.name}
- 所需参数：{', '.join(template.params)}
- 描述：{template.description}

用户需求：
- 描述：{user_description or '无具体描述'}
- 提供的参数：{user_params}

请评估该模板的适配度，输出一个0到1之间的分数。
只输出数字，不要其他内容。

评估标准：
1. 参数是否匹配（0.4权重）
2. 工艺是否适用（0.4权重）
3. 精度要求是否满足（0.2权重）"""

        try:
            response = self.llm_client.chat_with_ai(prompt)
            # 提取数字
            score_match = re.search(r'(\d*\.?\d+)', response.strip())
            if score_match:
                score = float(score_match.group(1))
                return min(max(score, 0.0), 1.0)  # 确保在0-1范围内
        except Exception as e:
            print(f"LLM评估失败: {e}")
        
        return 0.5  # 默认中等分数
    
    def _calculate_param_match(self, template_params: List[str], user_params: Dict[str, any]) -> float:
        """计算参数匹配度"""
        if not template_params:
            return 1.0
        
        matched = sum(1 for param in template_params if param in user_params)
        return matched / len(template_params)
    
    def _calculate_semantic_similarity(self, template_desc: str, user_desc: str) -> float:
        """计算语义相似度（简化版本）"""
        if not user_desc:
            return 0.5
        
        # 简单的关键词匹配
        template_words = set(template_desc.lower().split('-'))
        user_words = set(user_desc.lower().split())
        
        common_words = template_words & user_words
        if not template_words:
            return 0.5
        
        return len(common_words) / len(template_words)
    
    def _generate_explanation(self, best_score: TemplateScore, all_scores: List[TemplateScore]) -> str:
        """生成选择解释"""
        prompt = f"""基于以下评分结果，解释为什么选择了{best_score.template.name}模板。

选中的模板：
- 名称：{best_score.template.name}
- 总分：{best_score.total_score:.2f}
- LLM评分：{best_score.llm_score:.2f}
- 参数匹配度：{best_score.param_match_score:.2f}

其他候选模板：
{self._format_other_scores(best_score, all_scores)}

请用简洁的中文解释选择理由，重点说明：
1. 该模板的主要优势
2. 为什么它比其他模板更合适

保持在2-3句话以内。"""

        try:
            explanation = self.llm_client.chat_with_ai(prompt)
            return explanation.strip()
        except Exception as e:
            print(f"生成解释失败: {e}")
            return f"选择了{best_score.template.name}模板，因为它的综合评分最高（{best_score.total_score:.2f}）"
    
    def _format_other_scores(self, best_score: TemplateScore, all_scores: List[TemplateScore]) -> str:
        """格式化其他模板的分数"""
        other_scores = [s for s in all_scores if s.template.name != best_score.template.name]
        if not other_scores:
            return "无其他候选模板"
        
        lines = []
        for score in other_scores[:3]:  # 最多显示3个
            lines.append(f"- {score.template.name}: 总分{score.total_score:.2f}")
        
        return '\n'.join(lines)
    
    def _generate_suggestions(self, template: TemplateInfo, user_params: Dict[str, any]) -> str:
        """生成优化建议"""
        missing_params = [p for p in template.params if p not in user_params]
        
        if not missing_params:
            return ""
        
        prompt = f"""用户选择了{template.name}加工，但缺少以下参数：{', '.join(missing_params)}

请给出简短的参数建议，包括：
1. 这些参数的推荐值
2. 选择依据

保持简洁，2-3句话。"""

        try:
            suggestions = self.llm_client.chat_with_ai(prompt)
            return suggestions.strip()
        except Exception as e:
            print(f"生成建议失败: {e}")
            return f"建议补充参数：{', '.join(missing_params)}"


# 全局实例
_template_selector = None

def get_template_selector() -> LLMTemplateSelector:
    """获取模板选择器的单例"""
    global _template_selector
    if _template_selector is None:
        _template_selector = LLMTemplateSelector()
    return _template_selector