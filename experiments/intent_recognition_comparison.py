# -*- coding: utf-8 -*-
"""
意图识别对比实验
比较不同方法的性能
"""

import os
import sys
import time
import json
from typing import Dict, List, Tuple
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ['PY_ENVIRONMENT'] = 'local'

from qa.baseline_classifiers import KeywordBasedClassifier, RuleBasedClassifier, BERTOnlyClassifier, HAS_BERT
from qa.llm_centric_classifier import get_llm_centric_classifier


class IntentRecognitionExperiment:
    """意图识别对比实验"""
    
    def __init__(self):
        # 初始化所有分类器
        self.classifiers = {
            "Keyword": KeywordBasedClassifier(),
            "Rule": RuleBasedClassifier(),
        }
        
        # BERT分类器（如果可用）
        if HAS_BERT:
            try:
                self.classifiers["BERT_Only"] = BERTOnlyClassifier()
                print("✅ BERT分类器加载成功")
            except Exception as e:
                print(f"⚠️ BERT分类器加载失败: {e}")
        
        # LLM分类器（我们的方法）
        try:
            self.classifiers["LLM_Enhanced"] = get_llm_centric_classifier()
            print("✅ LLM增强分类器加载成功")
        except Exception as e:
            print(f"❌ LLM分类器加载失败: {e}")
    
    def create_test_dataset(self) -> List[Dict]:
        """创建测试数据集"""
        return [
            # 简单清晰的案例
            {
                "id": 1,
                "input": "我要使用外圆工艺加工一个外圆，Cn是2，L是100",
                "expected_main": "外圆工艺",
                "expected_sub": "外圆",
                "difficulty": "easy",
                "has_params": True
            },
            {
                "id": 2,
                "input": "车一个内孔，直径20mm",
                "expected_main": "里孔工艺",
                "expected_sub": "内圆",
                "difficulty": "easy",
                "has_params": True
            },
            
            # 中等难度案例
            {
                "id": 3,
                "input": "外螺纹加工，M10螺纹",
                "expected_main": "螺纹工艺",
                "expected_sub": "外直螺纹",
                "difficulty": "medium",
                "has_params": True
            },
            {
                "id": 4,
                "input": "切槽深度5mm，宽度3mm",
                "expected_main": "端面工艺",
                "expected_sub": "切槽",
                "difficulty": "medium",
                "has_params": True
            },
            
            # 困难案例（模糊表达）
            {
                "id": 5,
                "input": "加工一个圆",
                "expected_main": "外圆工艺",  # 或里孔工艺
                "expected_sub": None,
                "difficulty": "hard",
                "has_params": False
            },
            {
                "id": 6,
                "input": "做个螺纹",
                "expected_main": "螺纹工艺",
                "expected_sub": None,
                "difficulty": "hard",
                "has_params": False
            },
            
            # 口语化表达
            {
                "id": 7,
                "input": "帮我车个外圆，大概50毫米长",
                "expected_main": "外圆工艺",
                "expected_sub": "外圆",
                "difficulty": "medium",
                "has_params": True
            },
            {
                "id": 8,
                "input": "镗孔，孔径要求25",
                "expected_main": "里孔工艺",
                "expected_sub": "内圆",
                "difficulty": "medium",
                "has_params": True
            },
            
            # 复杂表达
            {
                "id": 9,
                "input": "我需要在工件上加工一个外圆，要求圆柱度好，长度100，进给速度300",
                "expected_main": "外圆工艺",
                "expected_sub": "外圆",
                "difficulty": "hard",
                "has_params": True
            },
            {
                "id": 10,
                "input": "端面车平，然后切个槽",
                "expected_main": "端面工艺",
                "expected_sub": "端面",  # 或切槽
                "difficulty": "hard",
                "has_params": False
            },
            
            # 非工艺输入
            {
                "id": 11,
                "input": "你好",
                "expected_main": "NO_PROCESS",
                "expected_sub": None,
                "difficulty": "easy",
                "has_params": False
            },
            {
                "id": 12,
                "input": "G00指令是什么意思",
                "expected_main": "NO_PROCESS",
                "expected_sub": None,
                "difficulty": "easy",
                "has_params": False
            }
        ]
    
    def evaluate_single_case(self, classifier, test_case: Dict) -> Dict:
        """评估单个测试案例"""
        start_time = time.time()
        
        try:
            # 根据分类器类型调用不同方法
            if hasattr(classifier, 'classify'):
                # 基线方法
                result = classifier.classify(test_case['input'])
                main_process = result.main_process
                sub_process = result.sub_process
                confidence = result.confidence
                method = result.method
                parameters = result.parameters or {}
            else:
                # LLM方法
                result = classifier.classify(test_case['input'])
                main_process = result['main_process']
                sub_process = result.get('sub_process')
                confidence = result.get('confidence', 0)
                method = result.get('method', 'Unknown')
                parameters = {e['type']: e['value'] for e in result.get('entities', [])}
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # 评估准确性
            main_correct = main_process == test_case['expected_main']
            # 子工艺可能为None，特殊处理
            if test_case['expected_sub'] is None:
                sub_correct = True  # 如果期望是None，任何结果都算对
            else:
                sub_correct = sub_process == test_case['expected_sub']
            
            # 参数提取评估
            param_extracted = len(parameters) > 0 if test_case['has_params'] else True
            
            return {
                'success': True,
                'main_correct': main_correct,
                'sub_correct': sub_correct,
                'param_extracted': param_extracted,
                'confidence': confidence,
                'response_time': response_time,
                'predicted_main': main_process,
                'predicted_sub': sub_process,
                'parameters': parameters,
                'method': method
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'main_correct': False,
                'sub_correct': False,
                'param_extracted': False,
                'confidence': 0,
                'response_time': time.time() - start_time
            }
    
    def run_experiment(self) -> Dict:
        """运行完整实验"""
        print("🧪 开始意图识别对比实验")
        print("=" * 80)
        
        # 创建测试数据集
        test_dataset = self.create_test_dataset()
        print(f"📊 测试数据集大小: {len(test_dataset)} 个案例")
        
        # 存储所有结果
        all_results = {}
        
        # 对每个分类器进行测试
        for classifier_name, classifier in self.classifiers.items():
            print(f"\n🔍 测试分类器: {classifier_name}")
            print("-" * 60)
            
            results = []
            
            for test_case in test_dataset:
                result = self.evaluate_single_case(classifier, test_case)
                result['test_id'] = test_case['id']
                result['difficulty'] = test_case['difficulty']
                results.append(result)
                
                # 打印进度
                if test_case['id'] % 3 == 0:
                    print(f"  进度: {test_case['id']}/{len(test_dataset)}")
            
            all_results[classifier_name] = results
            
            # 计算统计指标
            stats = self.calculate_statistics(results)
            print(f"\n📈 {classifier_name} 统计结果:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"  {key}: {value:.2f}")
                else:
                    print(f"  {key}: {value}")
        
        return all_results
    
    def calculate_statistics(self, results: List[Dict]) -> Dict:
        """计算统计指标"""
        total = len(results)
        successful = sum(1 for r in results if r['success'])
        
        # 基础指标
        stats = {
            'total_cases': total,
            'successful_cases': successful,
            'success_rate': successful / total if total > 0 else 0
        }
        
        # 只统计成功的案例
        if successful > 0:
            successful_results = [r for r in results if r['success']]
            
            # 准确率
            main_correct = sum(1 for r in successful_results if r['main_correct'])
            sub_correct = sum(1 for r in successful_results if r['sub_correct'])
            param_correct = sum(1 for r in successful_results if r['param_extracted'])
            
            stats.update({
                'main_accuracy': main_correct / successful,
                'sub_accuracy': sub_correct / successful,
                'param_accuracy': param_correct / successful,
                'avg_confidence': sum(r['confidence'] for r in successful_results) / successful,
                'avg_response_time': sum(r['response_time'] for r in successful_results) / successful
            })
            
            # 按难度分组统计
            for difficulty in ['easy', 'medium', 'hard']:
                diff_results = [r for r in successful_results if r['difficulty'] == difficulty]
                if diff_results:
                    diff_correct = sum(1 for r in diff_results if r['main_correct'])
                    stats[f'{difficulty}_accuracy'] = diff_correct / len(diff_results)
        
        return stats
    
    def generate_report(self, results: Dict) -> str:
        """生成实验报告"""
        report = []
        report.append("# 意图识别对比实验报告")
        report.append(f"实验时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 汇总表格
        report.append("## 性能对比汇总")
        report.append("")
        report.append("| 方法 | 主工艺准确率 | 子工艺准确率 | 参数提取率 | 平均置信度 | 平均响应时间(s) |")
        report.append("|------|------------|------------|-----------|-----------|----------------|")
        
        for method, method_results in results.items():
            stats = self.calculate_statistics(method_results)
            if stats['successful_cases'] > 0:
                report.append(f"| {method} | "
                            f"{stats.get('main_accuracy', 0):.2%} | "
                            f"{stats.get('sub_accuracy', 0):.2%} | "
                            f"{stats.get('param_accuracy', 0):.2%} | "
                            f"{stats.get('avg_confidence', 0):.2f} | "
                            f"{stats.get('avg_response_time', 0):.3f} |")
        
        # 难度分析
        report.append("")
        report.append("## 不同难度下的表现")
        report.append("")
        report.append("| 方法 | 简单案例 | 中等案例 | 困难案例 |")
        report.append("|------|---------|---------|---------|")
        
        for method, method_results in results.items():
            stats = self.calculate_statistics(method_results)
            report.append(f"| {method} | "
                        f"{stats.get('easy_accuracy', 0):.2%} | "
                        f"{stats.get('medium_accuracy', 0):.2%} | "
                        f"{stats.get('hard_accuracy', 0):.2%} |")
        
        # 详细案例分析
        report.append("")
        report.append("## 典型案例分析")
        report.append("")
        
        # 选择几个有代表性的案例
        test_dataset = self.create_test_dataset()
        representative_ids = [1, 5, 9]  # 简单、困难、复杂
        
        for test_id in representative_ids:
            test_case = next(tc for tc in test_dataset if tc['id'] == test_id)
            report.append(f"### 案例 {test_id}: {test_case['input']}")
            report.append(f"期望结果: {test_case['expected_main']} / {test_case['expected_sub']}")
            report.append("")
            
            for method, method_results in results.items():
                result = next(r for r in method_results if r['test_id'] == test_id)
                if result['success']:
                    report.append(f"- **{method}**: {result['predicted_main']} / {result['predicted_sub']} "
                                f"(置信度: {result['confidence']:.2f})")
        
        return "\n".join(report)
    
    def save_results(self, results: Dict, filename: str = "experiment_results.json"):
        """保存实验结果"""
        output_dir = "experiments/results"
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {output_path}")
        
        # 同时保存报告
        report = self.generate_report(results)
        report_path = output_path.replace('.json', '_report.md')
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 报告已保存到: {report_path}")


def main():
    """主函数"""
    experiment = IntentRecognitionExperiment()
    results = experiment.run_experiment()
    
    # 保存结果
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    experiment.save_results(results, f"intent_recognition_{timestamp}.json")
    
    # 打印最终报告
    print("\n" + "=" * 80)
    print(experiment.generate_report(results))


if __name__ == "__main__":
    main()