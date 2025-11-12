"""
Smart Workflow Mode - 智能自适应工作流模式

AI驱动的自适应工作流
适用场景: 所有场景 - 由AI根据任务复杂度自动选择最优模式
预计时长: 根据任务自动判断
"""

from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models import Stage, StageStatus, WorkflowMode


class SmartWorkflow:
    """智能自适应工作流模式 - AI驱动"""

    def __init__(self):
        self.mode_name = "smart"
        self.description = "AI驱动的自适应工作流，根据任务自动选择最优模式"
        self.estimated_duration = "根据任务自动判断"

        # 当前推荐的实际模式
        self.recommended_mode: Optional[WorkflowMode] = None
        self.recommendation_reason: str = ""
        self.confidence: float = 0.0

    def create_stages(self) -> List[Stage]:
        """
        Smart模式默认创建一个分析阶段
        在这个阶段会分析任务并推荐具体模式
        """
        return [
            Stage(
                stage_id="ANALYSIS",
                name="智能分析 (Smart Analysis)",
                description="分析任务特征，推荐最优工作流模式",
                tasks=[
                    "分析任务描述和需求",
                    "评估项目复杂度",
                    "识别技术栈和团队经验",
                    "评估时间约束",
                    "推荐最优工作流模式"
                ],
                deliverables=[
                    "任务分析报告",
                    "推荐工作流模式",
                    "推荐理由说明"
                ],
                metadata={
                    "estimated_hours": "1-2小时",
                    "is_smart_analysis": True
                }
            )
        ]

    def analyze_task_and_recommend(self, task_description: str,
                                   context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        分析任务并推荐最优模式

        Args:
            task_description: 任务描述
            context: 上下文信息（项目复杂度、团队规模、时间约束等）

        Returns:
            包含推荐模式和理由的字典
        """
        if context is None:
            context = {}

        # 分析任务复杂度
        complexity_analysis = self._analyze_complexity(task_description, context)

        # 分析时间约束
        time_constraints = self._analyze_time_constraints(context)

        # 分析质量要求
        quality_requirements = self._analyze_quality_requirements(context)

        # 分析团队情况
        team_analysis = self._analyze_team(context)

        # 综合决策
        recommendation = self._make_recommendation(
            complexity_analysis,
            time_constraints,
            quality_requirements,
            team_analysis
        )

        self.recommended_mode = recommendation['mode']
        self.recommendation_reason = recommendation['reason']
        self.confidence = recommendation['confidence']

        return {
            'recommended_mode': recommendation['mode'].value,
            'reason': recommendation['reason'],
            'confidence': recommendation['confidence'],
            'analysis': {
                'complexity': complexity_analysis,
                'time_constraints': time_constraints,
                'quality_requirements': quality_requirements,
                'team_analysis': team_analysis
            },
            'alternatives': recommendation.get('alternatives', [])
        }

    def _analyze_complexity(self, task_description: str,
                           context: Dict[str, Any]) -> Dict[str, Any]:
        """分析任务复杂度"""
        description_lower = task_description.lower()

        # 复杂度指标
        complexity_indicators = {
            'high': [
                '架构', '系统', '框架', 'architecture', 'system', 'framework',
                '重构', 'refactor', '迁移', 'migration',
                '集成', 'integration', '分布式', 'distributed'
            ],
            'medium': [
                '功能', 'feature', '模块', 'module',
                '��化', 'optimize', '改进', 'improve',
                'api', '接口', 'interface'
            ],
            'low': [
                '修复', 'fix', 'bug', '小', 'small',
                '调整', 'adjust', '更新', 'update'
            ]
        }

        # 计算复杂度得分
        scores = {'high': 0, 'medium': 0, 'low': 0}
        for level, keywords in complexity_indicators.items():
            scores[level] = sum(1 for kw in keywords if kw in description_lower)

        # 考虑上下文中的复杂度信息
        if 'complexity' in context:
            explicit_complexity = context['complexity']
            if explicit_complexity in scores:
                scores[explicit_complexity] += 3  # 增加权重

        # 确定最终复杂度
        complexity_level = max(scores, key=scores.get)
        if all(score == 0 for score in scores.values()):
            complexity_level = 'medium'  # 默认中等复杂度

        return {
            'level': complexity_level,
            'scores': scores,
            'factors': self._identify_complexity_factors(description_lower)
        }

    def _identify_complexity_factors(self, description: str) -> List[str]:
        """识别复杂度影响因素"""
        factors = []

        factor_keywords = {
            '多模块交互': ['集成', 'integration', '多个模块', 'multiple modules'],
            '性能要求高': ['性能', 'performance', '优化', 'optimize'],
            '安全性要求': ['安全', 'security', '认证', 'authentication'],
            '需要测试覆盖': ['测试', 'test', '覆盖', 'coverage'],
            '涉及数据迁移': ['迁移', 'migration', '数据', 'data'],
            '需要文档': ['文档', 'document', 'documentation']
        }

        for factor, keywords in factor_keywords.items():
            if any(kw in description for kw in keywords):
                factors.append(factor)

        return factors

    def _analyze_time_constraints(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析时间约束"""
        urgency = context.get('urgency', 'normal')
        deadline = context.get('deadline')

        # 紧急程度评分
        urgency_scores = {
            'emergency': 1.0,  # 紧急
            'high': 0.7,       # 高优先级
            'normal': 0.4,     # 正常
            'low': 0.2         # 低优先级
        }

        urgency_score = urgency_scores.get(urgency, 0.4)

        return {
            'urgency': urgency,
            'urgency_score': urgency_score,
            'has_deadline': deadline is not None,
            'deadline': deadline,
            'time_pressure': 'high' if urgency_score > 0.6 else 'medium' if urgency_score > 0.3 else 'low'
        }

    def _analyze_quality_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析质量要求"""
        quality_priority = context.get('quality_priority', 'medium')
        is_production = context.get('is_production', True)
        requires_review = context.get('requires_review', True)

        # 质量要求评分
        quality_scores = {
            'critical': 1.0,   # 关键系统
            'high': 0.8,       # 高质量要求
            'medium': 0.5,     # 中等质量要求
            'low': 0.3         # 低质量要求（原型等）
        }

        quality_score = quality_scores.get(quality_priority, 0.5)

        # 生产环境增加质量要求
        if is_production:
            quality_score = min(1.0, quality_score + 0.2)

        return {
            'priority': quality_priority,
            'score': quality_score,
            'is_production': is_production,
            'requires_review': requires_review,
            'level': 'high' if quality_score > 0.7 else 'medium' if quality_score > 0.4 else 'low'
        }

    def _analyze_team(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析团队情况"""
        team_size = context.get('team_size', 1)
        team_experience = context.get('team_experience', 'medium')

        # 经验评分
        experience_scores = {
            'senior': 0.9,     # 资深团队
            'medium': 0.6,     # 中等经验
            'junior': 0.3      # 初级团队
        }

        experience_score = experience_scores.get(team_experience, 0.6)

        return {
            'size': team_size,
            'experience': team_experience,
            'experience_score': experience_score,
            'is_solo': team_size == 1,
            'is_large_team': team_size > 5
        }

    def _make_recommendation(self, complexity_analysis: Dict[str, Any],
                            time_constraints: Dict[str, Any],
                            quality_requirements: Dict[str, Any],
                            team_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """综合分析并给出推荐"""

        complexity = complexity_analysis['level']
        time_pressure = time_constraints['time_pressure']
        quality_level = quality_requirements['level']
        team_exp = team_analysis['experience_score']

        # 决策逻辑
        reasons = []
        alternatives = []

        # 紧急情况 -> Minimal
        if time_pressure == 'high' or time_constraints['urgency'] == 'emergency':
            recommended = WorkflowMode.MINIMAL
            confidence = 0.9
            reasons.append("时间紧迫，建议使用快速原型模式")
            alternatives = [
                {'mode': 'standard', 'reason': '如果质量要求较高，可考虑标准模式'}
            ]

        # 高复杂度 + 高质量要求 -> Complete
        elif complexity == 'high' and quality_level == 'high':
            recommended = WorkflowMode.COMPLETE
            confidence = 0.85
            reasons.append("项目复杂度高且质量要求严格")
            reasons.append("建议使用完整的8阶段流程，包含质量门控制")
            alternatives = [
                {'mode': 'standard', 'reason': '如果时间有限，可降级为标准模式'}
            ]

        # 中等复杂度 或 常规场景 -> Standard
        elif complexity == 'medium' or (complexity == 'low' and quality_level in ['medium', 'high']):
            recommended = WorkflowMode.STANDARD
            confidence = 0.8
            reasons.append("项目复杂度适中，适合标准流程")
            alternatives = [
                {'mode': 'minimal', 'reason': '如果时间紧迫，可简化为快速模式'},
                {'mode': 'complete', 'reason': '如果质量要求更高，可升级为完整模式'}
            ]

        # 低复杂度 + 低质量要求 -> Minimal
        elif complexity == 'low' and quality_level == 'low':
            recommended = WorkflowMode.MINIMAL
            confidence = 0.85
            reasons.append("项目简单，适合快速迭代")
            alternatives = [
                {'mode': 'standard', 'reason': '如果需要更规范的流程，可考虑标准模式'}
            ]

        # 默认 -> Standard
        else:
            recommended = WorkflowMode.STANDARD
            confidence = 0.7
            reasons.append("基于综合评估，推荐使用标准模式")
            alternatives = [
                {'mode': 'minimal', 'reason': '快速原型场景'},
                {'mode': 'complete', 'reason': '严格质量控制场景'}
            ]

        # 根据团队经验调整置信度
        if team_exp < 0.5 and recommended == WorkflowMode.COMPLETE:
            confidence *= 0.9  # 降低置信度
            reasons.append("注意: 团队经验较少，执行完整流程可能有挑战")

        return {
            'mode': recommended,
            'confidence': confidence,
            'reason': '; '.join(reasons),
            'alternatives': alternatives,
            'decision_factors': {
                'complexity': complexity,
                'time_pressure': time_pressure,
                'quality_level': quality_level,
                'team_experience': team_analysis['experience']
            }
        }

    def get_next_action_prompt(self, current_stage_id: str = "ANALYSIS") -> str:
        """获取下一步行动提示"""
        if current_stage_id == "ANALYSIS":
            return """
# Smart Mode: 智能分析阶段

## 🎯 目标
分析任务特征，推荐最优工作���模式

## 📋 任务清单
1. **任务分析**
   - 分析任务描述和需求
   - 评估项目复杂度（高/中/低）
   - 识别技术栈和依赖

2. **上下文评估**
   - 时间约束（紧急/正常/宽松）
   - 质量要求（高/中/低）
   - 团队规模和经验

3. **模式推荐**
   - 基于分析结果推荐模式
   - 给出推荐理由
   - 提供备选方案

## 🤖 AI推荐决策逻辑

### Minimal模式 (P→D→R)
**适用场景:**
- 时间紧迫或紧急任务
- 低复杂度 + 低质量要求
- 快速原型验证

**预计时长:** 0.5-2天

### Standard模式 (P1→P2→D1→D2→R1)
**适用场景:**
- 中等复杂度项目
- 常规开发任务
- 平衡质量和速度

**预计时长:** 3-7天

### Complete模式 (S1-S8 + 3个质量门)
**适用场景:**
- 高复杂度项目
- 严格质量要求
- 关键系统开发

**预计时长:** 1-4周

## 📄 输出
- 推荐的工作流模式
- 详细推荐理由
- 置信度评分
- 备选方案

## ⏱️ 时间框架
1-2小时

## ✅ 完成标准
- [ ] 任务特征分析完成
- [ ] 工作流模式已推荐
- [ ] 推荐理由清晰
- [ ] 用户确认接受推荐
"""
        else:
            return "未知阶段"
