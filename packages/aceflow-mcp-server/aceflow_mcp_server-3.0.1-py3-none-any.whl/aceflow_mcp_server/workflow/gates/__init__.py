"""
Decision Gates - 质量门系统

实现3个质量门检查点，确保工作流质量:
- DG1: 开发就绪度检查 (Development Readiness Gate) - 在S3后
- DG2: 实现质量检查 (Implementation Quality Gate) - 在S5后
- DG3: 发布就绪度检查 (Release Readiness Gate) - 在S7后
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Any
from datetime import datetime


class GateResult(Enum):
    """质量门检查结果"""
    PASS = "pass"               # 通过
    CONDITIONAL_PASS = "conditional_pass"  # 有条件通过
    WARNING = "warning"         # 警告
    FAIL = "fail"               # 未通过


@dataclass
class GateEvaluation:
    """质量门评估结果"""
    gate_id: str
    gate_name: str
    result: GateResult
    score: float                # 总分 (0.0-1.0)
    confidence: float           # 置信度 (0.0-1.0)
    criteria_scores: Dict[str, float]  # 各项标准得分
    recommendations: List[str]  # 改进建议
    risk_factors: List[str]     # 风险因素
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'gate_id': self.gate_id,
            'gate_name': self.gate_name,
            'result': self.result.value,
            'score': self.score,
            'confidence': self.confidence,
            'criteria_scores': self.criteria_scores,
            'recommendations': self.recommendations,
            'risk_factors': self.risk_factors,
            'timestamp': self.timestamp.isoformat()
        }


class DecisionGate:
    """质量门基类"""

    def __init__(self, gate_id: str, name: str, description: str):
        self.gate_id = gate_id
        self.name = name
        self.description = description

    def evaluate(self, context: Dict[str, Any]) -> GateEvaluation:
        """
        评估质量门

        Args:
            context: 评估上下文，包含项目状态、测试结果等信息

        Returns:
            质量门评估结果
        """
        # 评估各项标准
        criteria_scores = self._evaluate_criteria(context)

        # 计算总分
        overall_score = sum(criteria_scores.values()) / len(criteria_scores)

        # 计算置信度
        confidence = self._calculate_confidence(criteria_scores)

        # 确定结果
        result = self._determine_result(overall_score, confidence)

        # 生成建议和风险
        recommendations = self._generate_recommendations(criteria_scores, context)
        risk_factors = self._identify_risk_factors(criteria_scores, context)

        return GateEvaluation(
            gate_id=self.gate_id,
            gate_name=self.name,
            result=result,
            score=overall_score,
            confidence=confidence,
            criteria_scores=criteria_scores,
            recommendations=recommendations,
            risk_factors=risk_factors,
            timestamp=datetime.now()
        )

    def _evaluate_criteria(self, context: Dict[str, Any]) -> Dict[str, float]:
        """评估各项标准 - 子类实现"""
        raise NotImplementedError

    def _calculate_confidence(self, criteria_scores: Dict[str, float]) -> float:
        """计算置信度"""
        if not criteria_scores:
            return 0.5

        # 基于标准分数的一致性计算置信度
        scores = list(criteria_scores.values())
        avg_score = sum(scores) / len(scores)
        variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
        consistency = max(0.0, 1.0 - variance)

        return min(0.95, avg_score * 0.7 + consistency * 0.3)

    def _determine_result(self, score: float, confidence: float) -> GateResult:
        """确定检查结果"""
        if score >= 0.8 and confidence >= 0.7:
            return GateResult.PASS
        elif score >= 0.6 and confidence >= 0.6:
            return GateResult.CONDITIONAL_PASS
        elif score >= 0.4:
            return GateResult.WARNING
        else:
            return GateResult.FAIL

    def _generate_recommendations(self, criteria_scores: Dict[str, float],
                                  context: Dict[str, Any]) -> List[str]:
        """生成改进建议 - 子类实现"""
        return []

    def _identify_risk_factors(self, criteria_scores: Dict[str, float],
                               context: Dict[str, Any]) -> List[str]:
        """识别风险因素 - 子类实现"""
        return []


class DG1_DevelopmentReadinessGate(DecisionGate):
    """DG1: 开发就绪度检查 (在S3测试用例设计后)"""

    def __init__(self):
        super().__init__(
            gate_id="DG1",
            name="开发就绪度检查",
            description="确保开发前的准备工作已完成"
        )

    def _evaluate_criteria(self, context: Dict[str, Any]) -> Dict[str, float]:
        """评估开发就绪度标准"""
        scores = {}

        # 1. 用户故事完整性 (0.0-1.0)
        user_stories = context.get('user_stories', [])
        if user_stories:
            complete_stories = sum(1 for s in user_stories if s.get('has_acceptance_criteria'))
            scores['user_stories_completeness'] = complete_stories / len(user_stories)
        else:
            scores['user_stories_completeness'] = 0.0

        # 2. 任务拆分合理性
        tasks = context.get('tasks', [])
        if tasks:
            detailed_tasks = sum(1 for t in tasks if t.get('subtasks'))
            scores['task_breakdown_quality'] = detailed_tasks / len(tasks) if tasks else 0.5
        else:
            scores['task_breakdown_quality'] = 0.3

        # 3. 测试用例覆盖度
        test_cases = context.get('test_cases', [])
        required_coverage = context.get('required_test_coverage', 80)
        if test_cases:
            coverage = min(100, len(test_cases) * 10)  # 简化计算
            scores['test_case_coverage'] = coverage / required_coverage
        else:
            scores['test_case_coverage'] = 0.0

        # 4. 依赖明确性
        dependencies = context.get('dependencies_identified', False)
        scores['dependency_clarity'] = 1.0 if dependencies else 0.5

        # 5. 技术方案可行性
        technical_design = context.get('technical_design_complete', False)
        scores['technical_feasibility'] = 1.0 if technical_design else 0.6

        return scores

    def _generate_recommendations(self, criteria_scores: Dict[str, float],
                                  context: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if criteria_scores.get('user_stories_completeness', 0) < 0.8:
            recommendations.append("补充用户故事的验收标准")

        if criteria_scores.get('task_breakdown_quality', 0) < 0.7:
            recommendations.append("进一步细化任务拆分，添加子任务")

        if criteria_scores.get('test_case_coverage', 0) < 0.8:
            recommendations.append("补充测试用例，确保覆盖所有验收标准")

        if criteria_scores.get('dependency_clarity', 0) < 0.8:
            recommendations.append("明确标注任务依赖关系和技术依赖")

        return recommendations

    def _identify_risk_factors(self, criteria_scores: Dict[str, float],
                               context: Dict[str, Any]) -> List[str]:
        """识别风险因素"""
        risks = []

        if criteria_scores.get('user_stories_completeness', 0) < 0.5:
            risks.append("需求不清晰，可能导致开发返工")

        if criteria_scores.get('task_breakdown_quality', 0) < 0.5:
            risks.append("任务拆分不足，可能低估工作量")

        if criteria_scores.get('test_case_coverage', 0) < 0.5:
            risks.append("测试准备不足，可能遗漏缺陷")

        return risks


class DG2_ImplementationQualityGate(DecisionGate):
    """DG2: 实现质量检查 (在S5测试与调试后)"""

    def __init__(self):
        super().__init__(
            gate_id="DG2",
            name="实现质量检查",
            description="确保实现质量达标"
        )

    def _evaluate_criteria(self, context: Dict[str, Any]) -> Dict[str, float]:
        """评估实现质量标准"""
        scores = {}

        # 1. 测试通过率
        test_results = context.get('test_results', {})
        total_tests = test_results.get('total', 0)
        passed_tests = test_results.get('passed', 0)
        if total_tests > 0:
            scores['test_pass_rate'] = passed_tests / total_tests
        else:
            scores['test_pass_rate'] = 0.0

        # 2. 测试覆盖率
        coverage = context.get('code_coverage', 0.0)
        target_coverage = context.get('target_coverage', 0.8)
        scores['code_coverage'] = min(1.0, coverage / target_coverage)

        # 3. Bug严重程度
        bugs = context.get('bugs', [])
        critical_bugs = sum(1 for b in bugs if b.get('severity') == 'critical')
        major_bugs = sum(1 for b in bugs if b.get('severity') == 'major')

        if critical_bugs > 0:
            scores['bug_severity'] = 0.0
        elif major_bugs > 2:
            scores['bug_severity'] = 0.5
        elif major_bugs > 0:
            scores['bug_severity'] = 0.7
        else:
            scores['bug_severity'] = 1.0

        # 4. 性能指标
        performance_met = context.get('performance_benchmarks_met', True)
        scores['performance'] = 1.0 if performance_met else 0.6

        # 5. 代码规范
        code_quality_score = context.get('code_quality_score', 0.7)
        scores['code_standards'] = code_quality_score

        return scores

    def _generate_recommendations(self, criteria_scores: Dict[str, float],
                                  context: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if criteria_scores.get('test_pass_rate', 0) < 1.0:
            recommendations.append("修复所有失败的测试用例")

        if criteria_scores.get('code_coverage', 0) < 0.8:
            recommendations.append("提升代码测试覆盖率至80%以上")

        if criteria_scores.get('bug_severity', 0) < 0.8:
            recommendations.append("修复所有严重和主要Bug")

        if criteria_scores.get('performance', 0) < 0.8:
            recommendations.append("优化性能以满足基准要求")

        if criteria_scores.get('code_standards', 0) < 0.7:
            recommendations.append("改进代码质量，遵循代码规范")

        return recommendations

    def _identify_risk_factors(self, criteria_scores: Dict[str, Any],
                               context: Dict[str, Any]) -> List[str]:
        """识别风险因素"""
        risks = []

        bugs = context.get('bugs', [])
        critical_bugs = sum(1 for b in bugs if b.get('severity') == 'critical')

        if critical_bugs > 0:
            risks.append(f"存在{critical_bugs}个严重Bug，必须修复")

        if criteria_scores.get('test_pass_rate', 0) < 0.9:
            risks.append("测试通过率低，代码质量存疑")

        if criteria_scores.get('code_coverage', 0) < 0.6:
            risks.append("测试覆盖率严重不足，可能遗漏缺陷")

        return risks


class DG3_ReleaseReadinessGate(DecisionGate):
    """DG3: 发布就绪度检查 (在S7验收与演示后)"""

    def __init__(self):
        super().__init__(
            gate_id="DG3",
            name="发布就绪度检查",
            description="确保可以正式发布"
        )

    def _evaluate_criteria(self, context: Dict[str, Any]) -> Dict[str, float]:
        """评估发布就绪度标准"""
        scores = {}

        # 1. UAT测试通过
        uat_passed = context.get('uat_passed', False)
        scores['uat_status'] = 1.0 if uat_passed else 0.0

        # 2. 验收标准满足
        acceptance_criteria = context.get('acceptance_criteria', [])
        if acceptance_criteria:
            met_criteria = sum(1 for c in acceptance_criteria if c.get('met'))
            scores['acceptance_criteria_met'] = met_criteria / len(acceptance_criteria)
        else:
            scores['acceptance_criteria_met'] = 0.5

        # 3. 文档完整性
        docs = context.get('documentation', {})
        required_docs = ['readme', 'api_doc', 'user_guide', 'changelog']
        available_docs = [doc for doc in required_docs if docs.get(doc)]
        scores['documentation_completeness'] = len(available_docs) / len(required_docs)

        # 4. 部署就绪
        deployment_ready = context.get('deployment_plan_ready', False)
        scores['deployment_readiness'] = 1.0 if deployment_ready else 0.5

        # 5. 回滚方案
        rollback_plan = context.get('rollback_plan_exists', False)
        scores['rollback_preparedness'] = 1.0 if rollback_plan else 0.6

        return scores

    def _generate_recommendations(self, criteria_scores: Dict[str, float],
                                  context: Dict[str, Any]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        if criteria_scores.get('uat_status', 0) < 1.0:
            recommendations.append("完成用户验收测试")

        if criteria_scores.get('acceptance_criteria_met', 0) < 1.0:
            recommendations.append("确保所有验收标准都已满足")

        if criteria_scores.get('documentation_completeness', 0) < 0.8:
            recommendations.append("补充完整文档(README、API文档、用户手册、变更日志)")

        if criteria_scores.get('deployment_readiness', 0) < 1.0:
            recommendations.append("准备详细的部署方案")

        if criteria_scores.get('rollback_preparedness', 0) < 1.0:
            recommendations.append("制定回滚方案")

        return recommendations

    def _identify_risk_factors(self, criteria_scores: Dict[str, float],
                               context: Dict[str, Any]) -> List[str]:
        """识别风险因素"""
        risks = []

        if criteria_scores.get('uat_status', 0) < 1.0:
            risks.append("UAT未通过，不建议发布")

        if criteria_scores.get('acceptance_criteria_met', 0) < 0.8:
            risks.append("验收标准未完全满足")

        if criteria_scores.get('deployment_readiness', 0) < 0.8:
            risks.append("部署准备不足，可能影响发布")

        if criteria_scores.get('rollback_preparedness', 0) < 0.8:
            risks.append("缺少回滚方案，发布风险较高")

        return risks


# 质量门管理器
class GateManager:
    """质量门管理器"""

    def __init__(self):
        self.gates = {
            'DG1': DG1_DevelopmentReadinessGate(),
            'DG2': DG2_ImplementationQualityGate(),
            'DG3': DG3_ReleaseReadinessGate()
        }

    def evaluate_gate(self, gate_id: str, context: Dict[str, Any]) -> GateEvaluation:
        """评估指定质量门"""
        if gate_id not in self.gates:
            raise ValueError(f"未知的质量门: {gate_id}")

        gate = self.gates[gate_id]
        return gate.evaluate(context)

    def get_gate_info(self, gate_id: str) -> Dict[str, str]:
        """获取质量门信息"""
        if gate_id not in self.gates:
            raise ValueError(f"未知的质量门: {gate_id}")

        gate = self.gates[gate_id]
        return {
            'gate_id': gate.gate_id,
            'name': gate.name,
            'description': gate.description
        }

    def list_gates(self) -> List[Dict[str, str]]:
        """列出所有质量门"""
        return [
            self.get_gate_info(gate_id)
            for gate_id in ['DG1', 'DG2', 'DG3']
        ]
