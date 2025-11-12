"""
Complete Workflow Mode - 完整工作流模式

最完整的工作流: S1→S2→S3→S4→S5→S6→S7→S8 (8个阶段 + 3个质量门)
适用场景: 大型项目、关键系统、需要严格质量控制的项目
预计时长: 1-4周
"""

from typing import List
from datetime import datetime

from ..models import Stage, StageStatus


class CompleteWorkflow:
    """完整工作流模式实现: S1→S2→S3→S4→S5→S6→S7→S8"""

    def __init__(self):
        self.mode_name = "complete"
        self.description = "完整的8阶段工作流，包含3个质量门"
        self.estimated_duration = "1-4周"

    def create_stages(self) -> List[Stage]:
        """创建完整模式的8个阶段"""
        return [
            # S1: 用户故事定义
            Stage(
                stage_id="S1",
                name="用户故事定义 (User Story Definition)",
                description="编写详细的用户故事和验收标准",
                tasks=[
                    "编写用户故事 (使用标准格式)",
                    "定义每个故事的验收标准",
                    "标注优先级和依赖关系",
                    "评估每个故事的工作量",
                    "与相关方确认需求"
                ],
                deliverables=[
                    "用户故事文档 (user_stories.md)",
                    "验收标准清单",
                    "优先级排序",
                    "依赖关系图"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": None
                }
            ),

            # S2: 任务拆分
            Stage(
                stage_id="S2",
                name="任务拆分 (Task Breakdown)",
                description="将用户故事拆分为具体的开发任务",
                tasks=[
                    "拆分主要技术任务",
                    "定义每个任务的输入和输出",
                    "估算任务工作量",
                    "识别技术依赖",
                    "详细拆分每个任务的子步骤",
                    "制定实施顺序"
                ],
                deliverables=[
                    "主任务列表 (tasks_main.md)",
                    "详细任务拆分 (tasks_detail.md)",
                    "技术依赖分析",
                    "实施时间表"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": None
                }
            ),

            # S3: 测试用例设计 (DG1之前)
            Stage(
                stage_id="S3",
                name="测试用例设计 (Test Case Design)",
                description="设计完整的测试用例，确保测试覆盖",
                tasks=[
                    "基于验收标准设计测试用例",
                    "设计单元测试用例",
                    "设计集成测试用例",
                    "设计边界测试和异常测试",
                    "准备测试数据",
                    "定义测试环境需求"
                ],
                deliverables=[
                    "测试用例文档 (test_cases.md)",
                    "测试数据准备",
                    "测试环境规范",
                    "测试覆盖率计划"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": "DG1",  # 开发就绪度检查
                    "next_gate": "DG1: Development Readiness Gate"
                }
            ),

            # S4: 功能实现
            Stage(
                stage_id="S4",
                name="功能实现 (Implementation)",
                description="实现所有计划的功能",
                tasks=[
                    "按任务列表实现功能",
                    "编写单元测试",
                    "进行代码自查",
                    "编写代码注释和文档",
                    "处理技术难点",
                    "实现错误处理"
                ],
                deliverables=[
                    "完整的功能代码",
                    "单元测试代码",
                    "代码注释和文档",
                    "实现笔记"
                ],
                metadata={
                    "estimated_hours": "40-80小时",
                    "quality_gate": None,
                    "test_coverage_target": "70%"
                }
            ),

            # S5: 测试与调试 (DG2之前)
            Stage(
                stage_id="S5",
                name="测试与调试 (Testing & Debugging)",
                description="执行全面测试并修复问题",
                tasks=[
                    "执行所有单元测试",
                    "执行集成测试",
                    "执行性能测试",
                    "记录和修复Bug",
                    "回归测试",
                    "测试覆盖率验证"
                ],
                deliverables=[
                    "测试报告",
                    "Bug修复记录",
                    "测试覆盖率报告",
                    "性能测试结果"
                ],
                metadata={
                    "estimated_hours": "16-32小时",
                    "quality_gate": "DG2",  # 实现质量检查
                    "next_gate": "DG2: Implementation Quality Gate",
                    "test_coverage_target": "80%"
                }
            ),

            # S6: 代码审查
            Stage(
                stage_id="S6",
                name="代码审查 (Code Review)",
                description="同行代码审查和质量评估",
                tasks=[
                    "准备Code Review材料",
                    "提交代码审查请求",
                    "参与审查讨论",
                    "修改审查意见",
                    "二次审查确认",
                    "代码质量工具检查"
                ],
                deliverables=[
                    "Code Review报告",
                    "审查意见修改记录",
                    "代码质量分析报告"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": None
                }
            ),

            # S7: 验收与演示 (DG3之前)
            Stage(
                stage_id="S7",
                name="验收与演示 (Acceptance & Demo)",
                description="用户验收测试和功能演示",
                tasks=[
                    "准备演示环境",
                    "编写演示脚本",
                    "执行用户验收测试 (UAT)",
                    "进行功能演示",
                    "收集用户反馈",
                    "确认验收标准"
                ],
                deliverables=[
                    "UAT测试报告",
                    "演示录屏/文档",
                    "用户反馈记录",
                    "验收确认书"
                ],
                metadata={
                    "estimated_hours": "8-16小时",
                    "quality_gate": "DG3",  # 发布就绪度检查
                    "next_gate": "DG3: Release Readiness Gate"
                }
            ),

            # S8: 总结与回顾
            Stage(
                stage_id="S8",
                name="总结与回顾 (Summary & Retrospective)",
                description="项目总结和经验回顾",
                tasks=[
                    "编写项目总结报告",
                    "整理项目文档",
                    "记录经验教训",
                    "识别改进点",
                    "归档项目资料",
                    "规划后续优化"
                ],
                deliverables=[
                    "项目总结报告",
                    "经验教训文档",
                    "改进建议清单",
                    "完整的项目文档包"
                ],
                metadata={
                    "estimated_hours": "4-8小时",
                    "quality_gate": None
                }
            )
        ]

    def get_decision_gates(self) -> List[dict]:
        """获取3个质量门的信息"""
        return [
            {
                "gate_id": "DG1",
                "name": "开发就绪度检查 (Development Readiness Gate)",
                "position": "after_S3",
                "description": "确保开发前的准备工作已完成",
                "criteria": [
                    "用户故事清晰完整",
                    "任务拆分合理详细",
                    "测试用例设计完整",
                    "依赖关系已明确",
                    "技术方案可行"
                ]
            },
            {
                "gate_id": "DG2",
                "name": "实现质量检查 (Implementation Quality Gate)",
                "position": "after_S5",
                "description": "确保实现质量达标",
                "criteria": [
                    "所有单元测试通过",
                    "测试覆盖率 ≥ 80%",
                    "无严重Bug遗留",
                    "性能指标达标",
                    "代码规范符合要求"
                ]
            },
            {
                "gate_id": "DG3",
                "name": "发布就绪度检查 (Release Readiness Gate)",
                "position": "after_S7",
                "description": "确保可以正式发布",
                "criteria": [
                    "UAT测试通过",
                    "所有验收标准满足",
                    "文档完整",
                    "部署方案就绪",
                    "回滚方案已准备"
                ]
            }
        ]

    def get_next_action_prompt(self, current_stage_id: str) -> str:
        """根据当前阶段获取下一步行动提示"""
        prompts = {
            "S1": """
# S1: 用户故事定义 (Complete Mode)

## 🎯 目标
编写清晰、可测试的用户故事

## 📋 任务清单
1. **编写用户故事**
   - 使用格式: "As a [用户角色], I want [功能], so that [目的]"
   - 每个故事聚焦单一功能点
   - 故事之间保持独立性

2. **定义验收标准**
   - 使用 Given-When-Then 格式
   - 确保可测试性
   - 覆盖正常流程和异常情况

3. **优先级排序**
   - P0: 核心必须功能
   - P1: 重要功能
   - P2: 辅助功能

4. **依赖分析**
   - 标注故事间依赖
   - 识别技术依赖
   - 确定实施顺序

## 📄 交付物
- `user_stories.md` - 详细用户故事
- 验收标准清单
- 优先级和依赖关系图

## ⏱️ 时间框架: 8-16小时

## ✅ 完成标准
- [ ] 所有故事符合INVEST原则
- [ ] 验收标准清晰可测试
- [ ] 优先级合理
""",
            "S2": """
# S2: 任务拆分 (Complete Mode)

## 🎯 目标
将用户故事拆分为可执行的技术任务

## 📋 任务清单
1. **主任务拆分**
   - 基于用户故事拆分技术任务
   - 每个任务可在1-2天内完成
   - 明确任务的输入和输出

2. **详细任务拆分**
   - 将主任务拆分为具体步骤
   - 每个步骤控制在2-4小时
   - 定义清晰的完成标准

3. **技术依赖分析**
   - 识别任务间依赖
   - 标注技术风险
   - 规划实施顺序

## 📄 交付物
- `tasks_main.md` - 主任务列表
- `tasks_detail.md` - 详细任务拆分
- 技术依赖图
- 实施时间表

## ⏱️ 时间框架: 8-16小时

## ✅ 完成标准
- [ ] 任务拆分细致合理
- [ ] 工作量估算准确
- [ ] 依赖关系清晰
""",
            "S3": """
# S3: 测试用例设计 (Complete Mode)

## 🎯 目标
设计完整的测试用例，为DG1做准备

## 📋 任务清单
1. **单元测试用例**
   - 基于代码模块设计测试
   - 覆盖正常和异常情况
   - 设计边界测试

2. **集成测试用例**
   - 设计模块间交互测试
   - 设计端到端场景测试
   - 准备测试数据

3. **测试环境**
   - 定义测试环境需求
   - 准备测试数据
   - 配置测试工具

## 📄 交付物
- `test_cases.md` - 完整测试用例
- 测试数据准备
- 测试环境规范

## ⏱️ 时间框架: 8-16小时

## ⚠️ 质量门: DG1 - 开发就绪度检查
完成本阶段后，将进行DG1质量门检查：
- ✅ 用户故事完整清晰
- ✅ 任务拆分合理
- ✅ 测试用例设计完整
- ✅ 依赖关系明确

## ✅ 完成标准
- [ ] 测试用例覆盖所有验收标准
- [ ] 测试数据准备完整
- [ ] 通过DG1质量门检查
""",
            "S4": """
# S4: 功能实现 (Complete Mode)

## 🎯 目标
按计划实现所有功能

## 📋 任务清单
1. **按任务列表开发**
   - 遵循任务拆分顺序
   - 实现核心功能
   - 处理边界情况

2. **同步编写测试**
   - 单元测试 (覆盖率目标: 70%)
   - 基础集成测试
   - 持续验证功能

3. **代码质量**
   - 遵循代码规范
   - 添加必要注释
   - 进行代码自查

## 📄 交付物
- 完整功能代码
- 单元测试代码
- 代码文档

## ⏱️ 时间框架: 40-80小时

## ✅ 完成标准
- [ ] 所有计划功能已实现
- [ ] 单元测试覆盖率 ≥ 70%
- [ ] 代码可编译运行
""",
            "S5": """
# S5: 测试与调试 (Complete Mode)

## 🎯 目标
全面测试并修复问题，为DG2做准备

## 📋 任务清单
1. **执行测试**
   - 运行所有单元测试
   - 执行集成测试
   - 进行性能测试

2. **Bug修复**
   - 记录所有发现的Bug
   - 按优先级修复
   - 进行回归测试

3. **测试覆盖率**
   - 补充测试用例
   - 提升覆盖率至80%
   - 生成覆盖率报告

## 📄 交付物
- 测试报告
- Bug修复记录
- 覆盖率报告

## ⏱️ 时间框架: 16-32小时

## ⚠️ 质量门: DG2 - 实现质量检查
完成本阶段后，将进行DG2质量门检查：
- ✅ 所有测试通过
- ✅ 测试覆盖率 ≥ 80%
- ✅ 无严重Bug
- ✅ 性能达标

## ✅ 完成标准
- [ ] 所有测试通过
- [ ] 测试覆盖率 ≥ 80%
- [ ] 通过DG2质量门检查
""",
            "S6": """
# S6: 代码审查 (Complete Mode)

## 🎯 目标
通过同行审查提升代码质量

## 📋 任务清单
1. **准备审查**
   - 整理代码变更
   - 编写审查说明
   - 提交审查请求

2. **审查过程**
   - 参与审查讨论
   - 解释设计决策
   - 记录审查意见

3. **改进实施**
   - 修改审查发现的问题
   - 二次审查确认
   - 更新文档

## 📄 交付物
- Code Review报告
- 修改记录
- 代码质量报告

## ⏱️ 时间框架: 8-16小时

## ✅ 完成标准
- [ ] Code Review通过
- [ ] 所有审查意见已处理
- [ ] 代码质量达标
""",
            "S7": """
# S7: 验收与演示 (Complete Mode)

## 🎯 目标
通过用户验收测试，为DG3做准备

## 📋 任务清单
1. **UAT准备**
   - 准备演示环境
   - 编写演示脚本
   - 准备演示数据

2. **执行UAT**
   - 按验收标准测试
   - 记录测试结果
   - 收集用户反馈

3. **功能演示**
   - 向相关方演示
   - 展示关键功能
   - 回答疑问

## 📄 交付物
- UAT测试报告
- 演示文档/录屏
- 验收确认书

## ⏱️ 时间框架: 8-16小时

## ⚠️ 质量门: DG3 - 发布就绪度检查
完成本阶段后，将进行DG3质量门检查：
- ✅ UAT测试通过
- ✅ 验收标准满足
- ✅ 文档完整
- ✅ 部署就绪

## ✅ 完成标准
- [ ] UAT测试通过
- [ ] 所有验收标准满足
- [ ] 通过DG3质量门检查
""",
            "S8": """
# S8: 总结与回顾 (Complete Mode)

## 🎯 目标
总结项目经验，持续改进

## 📋 任务清单
1. **项目总结**
   - 编写项目报告
   - 整理关键指标
   - 总结技术亮点

2. **经验回顾**
   - 团队回顾会议
   - 记录经验教训
   - 识别改进点

3. **资料归档**
   - 整理项目文档
   - 归档代码和配置
   - 准备交接材料

## 📄 交付物
- 项目总结报告
- 经验教训文档
- 完整项目文档包

## ⏱️ 时间框架: 4-8小时

## ✅ 完成标准
- [ ] 总结报告完整
- [ ] 经验已记录
- [ ] 资料已归档
- [ ] 改进计划明确
"""
        }
        return prompts.get(current_stage_id, "未知阶段")
