"""
Standard Workflow Mode - 标准工作流模式

平衡的工作流: P1→P2→D1→D2→R1 (5个阶段)
适用场景: 大多数常规开发任务
预计时长: 3-7天
"""

from typing import List
from datetime import datetime

from ..models import Stage, StageStatus


class StandardWorkflow:
    """标准工作流模式实现: P1→P2→D1→D2→R1"""

    def __init__(self):
        self.mode_name = "standard"
        self.description = "平衡的工作流模式，适合大多数开发任务"
        self.estimated_duration = "3-7天"

    def create_stages(self) -> List[Stage]:
        """创建标准模式的5个阶段"""
        return [
            # P1: 需求分析阶段
            Stage(
                stage_id="P1",
                name="需求分析 (Requirements Analysis)",
                description="详细分析和定义需求",
                tasks=[
                    "收集和整理用户需求",
                    "编写用户故事 (User Stories)",
                    "定义验收标准 (Acceptance Criteria)",
                    "识别关键依赖和风险",
                    "确定项目范围和边界"
                ],
                deliverables=[
                    "需求文档 (requirements.md)",
                    "用户故事列表 (user_stories.md)",
                    "验收标准清单"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": None
                }
            ),

            # P2: 技术设计阶段
            Stage(
                stage_id="P2",
                name="技术设计 (Technical Design)",
                description="设计系统架构和技术方案",
                tasks=[
                    "设计系统架构",
                    "选择技术栈",
                    "设计数据模型",
                    "定义接口规范 (如果适用)",
                    "制定实施计划"
                ],
                deliverables=[
                    "技术设计文档 (design.md)",
                    "架构图",
                    "API规范 (如果适用)",
                    "数据库设计"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": None
                }
            ),

            # D1: 核心实现阶段
            Stage(
                stage_id="D1",
                name="核心实现 (Core Implementation)",
                description="实现主要功能和核心逻辑",
                tasks=[
                    "搭建项目基础结构",
                    "实现核心业务逻辑",
                    "实现主要功能模块",
                    "编写基础单元测试",
                    "处理关键技术难点"
                ],
                deliverables=[
                    "核心功能代码",
                    "基础单元测试",
                    "技术文档更新"
                ],
                metadata={
                    "estimated_hours": "24-40小时",
                    "quality_gate": None,
                    "test_coverage_target": "60%"
                }
            ),

            # D2: 测试与完善阶段
            Stage(
                stage_id="D2",
                name="测试与完善 (Testing & Refinement)",
                description="全面测试和优化代码",
                tasks=[
                    "编写完整的单元测试",
                    "编写集成测试",
                    "进行性能测试",
                    "修复发现的Bug",
                    "代码优化和重构",
                    "更新文档"
                ],
                deliverables=[
                    "完整的测试套件",
                    "测试报告",
                    "优化后的代码",
                    "完整的技术文档"
                ],
                metadata={
                    "estimated_hours": "16-32小时",
                    "quality_gate": None,
                    "test_coverage_target": "80%"
                }
            ),

            # R1: 评审与发布阶段
            Stage(
                stage_id="R1",
                name="评审与发布 (Review & Release)",
                description="代码评审和正式发布",
                tasks=[
                    "代码审查 (Code Review)",
                    "用户验收测试 (UAT)",
                    "准备发布说明",
                    "部署准备",
                    "正式发布",
                    "收集反馈"
                ],
                deliverables=[
                    "Code Review报告",
                    "UAT测试报告",
                    "发布说明 (CHANGELOG)",
                    "部署文档",
                    "用户手册 (如需要)"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": None
                }
            )
        ]

    def get_next_action_prompt(self, current_stage_id: str) -> str:
        """根据当前阶段获取下一步行动提示"""
        prompts = {
            "P1": """
# P1: 需求分析阶段 (Standard Mode)

## 🎯 目标
深入理解用户需求，明确项目目标和范围

## 📋 任务清单
1. **需求收集**
   - 与相关方沟通确认需求
   - 记录功能需求和非功能需求
   - 识别约束条件和限制

2. **用户故事编写**
   - 使用 "As a [用户角色], I want [功能], so that [目的]" 格式
   - 为每个用户故事定义验收标准
   - 标注优先级 (P0/P1/P2)

3. **需求分析**
   - 识别依赖关系
   - 评估技术风险
   - 确定项目边界

## 📄 交付物
- `requirements.md` - 详细需求文档
- `user_stories.md` - 用户故事列表
- `acceptance_criteria.md` - 验收标准

## ⏱️ 时间框架
8-16 小时

## ✅ 完成标准
- [ ] 所有功能需求已清晰定义
- [ ] 用户故事完整且具有可测试的验收标准
- [ ] 技术风险已识别
- [ ] 项目范围已明确
""",
            "P2": """
# P2: 技术设计阶段 (Standard Mode)

## 🎯 目标
设计可行的技术方案，为开发做好准备

## 📋 任务清单
1. **架构设计**
   - 设计系统整体架构
   - 定义模块划分
   - 设计数据流向

2. **技术选型**
   - 确定技术栈
   - 选择框架和库
   - 评估技术可行性

3. **详细设计**
   - 设计数据模型
   - 定义API接口 (如适用)
   - 设计关键算法

4. **计划制定**
   - 拆分开发任务
   - 估算工作量
   - 确定里程碑

## 📄 交付物
- `design.md` - 技术设计文档
- `architecture.png` - 架构图
- `api_spec.yaml` - API规范 (如适用)
- `implementation_plan.md` - 实施计划

## ⏱️ 时间框架
8-16 小时

## ✅ 完成标准
- [ ] 技术方案清晰可行
- [ ] 架构设计合理
- [ ] 接口定义完整 (如适用)
- [ ] 实施计划详细
""",
            "D1": """
# D1: 核心实现阶段 (Standard Mode)

## 🎯 目标
实现核心功能，构建可运行的MVP

## 📋 任务清单
1. **项目搭建**
   - 初始化项目结构
   - 配置开发环境
   - 搭建基础框架

2. **核心开发**
   - 实现核心业务逻辑
   - 实现主要功能模块
   - 处理技术难点

3. **基础测试**
   - 编写单元测试 (覆盖率目标: 60%)
   - 进行基本功能测试
   - 修复关键Bug

## 📄 交付物
- 可运行的核心代码
- 基础单元测试
- 技术实现笔记

## ⏱️ 时间框架
24-40 小时

## ✅ 完成标准
- [ ] 核心功能已实现
- [ ] 代码可编译/运行
- [ ] 基础测试通过
- [ ] 测试覆盖率 ≥ 60%
""",
            "D2": """
# D2: 测试与完善阶段 (Standard Mode)

## 🎯 目标
全面测试，优化代码质量

## 📋 任务清单
1. **完善测试**
   - 补充单元测试 (覆盖率目标: 80%)
   - 编写集成测试
   - 进行边界测试

2. **质量提升**
   - 代码审查和自查
   - 性能优化
   - 代码重构

3. **问题修复**
   - 修复所有已知Bug
   - 处理边界情况
   - 提升错误处理

4. **文档完善**
   - 更新API文档
   - 补充注释
   - 编写使用说明

## 📄 交付物
- 完整的测试套件
- 测试报告
- 优化后的代码
- 完整的技术文档

## ⏱️ 时间框架
16-32 小时

## ✅ 完成标准
- [ ] 所有测试通过
- [ ] 测试覆盖率 ≥ 80%
- [ ] 无关键Bug遗留
- [ ] 代码质量达标
- [ ] 文档完整
""",
            "R1": """
# R1: 评审与发布阶段 (Standard Mode)

## 🎯 目标
确保代码质量，准备正式发布

## 📋 任务清单
1. **代码评审**
   - 提交Code Review
   - 修改评审意见
   - 确保代码规范

2. **验收测试**
   - 执行UAT测试
   - 确认所有验收标准
   - 收集用户反馈

3. **发布准备**
   - 编写发布说明
   - 准备部署文档
   - 进行部署演练

4. **正式发布**
   - 部署到生产环境
   - 发布公告
   - 监控运行状态

5. **总结**
   - 收集使用反馈
   - 记录经验教训
   - 规划后续优化

## 📄 交付物
- Code Review报告
- UAT测试报告
- CHANGELOG.md
- 部署文档
- 用户手册 (如需要)

## ⏱️ 时间框架
8-16 小时

## ✅ 完成标准
- [ ] Code Review通过
- [ ] UAT测试通过
- [ ] 发布文档完整
- [ ] 成功部署
- [ ] 运行稳定
"""
        }
        return prompts.get(current_stage_id, "未知阶段")
