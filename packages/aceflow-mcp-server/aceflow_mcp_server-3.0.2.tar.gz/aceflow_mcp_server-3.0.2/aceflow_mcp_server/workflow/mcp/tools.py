"""
Workflow MCP Tools - 工作流 MCP 工具集

提供完整的工作流管理 MCP 工具
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .models import (
    MCPTool,
    MCPToolCategory,
    MCPToolParameter,
    MCPToolResult
)
from ..core.engine import WorkflowEngine  # 修正: 从 core.engine 导入
from ..core.state import StateManager     # 修正: 从 core.state 导入
from ..templates import TemplateManager
from ..memory import MemoryManager
from ..gates import GateManager
from ..models import WorkflowMode, StageStatus


class WorkflowMCPTools:
    """工作流 MCP 工具集合"""

    def __init__(self, working_directory: Optional[Path] = None):
        """
        初始化 MCP 工具

        Args:
            working_directory: 工作目录，默认为当前目录
        """
        if working_directory is None:
            working_directory = Path.cwd()

        self.working_directory = working_directory

        # 初始化核心组件 (修正: StateManager 需要 project_id 和 state_dir)
        self.state_manager = StateManager(
            project_id="mcp_default",
            state_dir=working_directory / ".aceflow"
        )
        self.template_manager = TemplateManager()
        self.memory_manager = MemoryManager()
        self.gate_manager = GateManager()

        # 注册所有工具
        self.tools: Dict[str, MCPTool] = {}
        self._register_tools()

    def _register_tools(self):
        """注册所有 MCP 工具"""
        # 工作流管理工具
        self._register_workflow_tools()

        # 状态管理工具
        self._register_state_tools()

        # 模板工具
        self._register_template_tools()

        # 记忆工具
        self._register_memory_tools()

        # 质量门工具
        self._register_gate_tools()

        # 导出工具 (新增)
        self._register_export_tools()

    # === 工作流管理工具 ===

    def _register_workflow_tools(self):
        """注册工作流管理工具"""

        # 1. 开始新迭代
        self.tools["workflow_start_iteration"] = MCPTool(
            name="workflow_start_iteration",
            description="开始一个新的工作流迭代",
            category=MCPToolCategory.WORKFLOW,
            parameters=[
                MCPToolParameter(
                    name="mode",
                    type="string",
                    description="工作流模式",
                    required=True,
                    enum=["minimal", "standard", "complete", "smart"]
                ),
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID (可选，不提供则自动生成)",
                    required=False
                ),
                MCPToolParameter(
                    name="metadata",
                    type="object",
                    description="迭代元数据 (如目标、负责人等)",
                    required=False
                )
            ],
            handler=self._start_iteration
        )

        # 2. 进入下一阶段
        self.tools["workflow_next_stage"] = MCPTool(
            name="workflow_next_stage",
            description="进入工作流的下一个阶段",
            category=MCPToolCategory.WORKFLOW,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="current_stage_output",
                    type="string",
                    description="当前阶段的输出内容",
                    required=False
                )
            ],
            handler=self._next_stage
        )

        # 3. 完成阶段 (新增)
        self.tools["workflow_complete_stage"] = MCPTool(
            name="workflow_complete_stage",
            description="完成当前阶段并进入下一阶段",
            category=MCPToolCategory.WORKFLOW,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="stage_id",
                    type="string",
                    description="阶段ID",
                    required=True
                ),
                MCPToolParameter(
                    name="metadata",
                    type="object",
                    description="阶段元数据 (可选)",
                    required=False
                )
            ],
            handler=self._complete_stage
        )

        # 4. 完成迭代
        self.tools["workflow_complete_iteration"] = MCPTool(
            name="workflow_complete_iteration",
            description="完成当前迭代",
            category=MCPToolCategory.WORKFLOW,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="summary",
                    type="string",
                    description="迭代总结",
                    required=False
                )
            ],
            handler=self._complete_iteration
        )

    # === 状态管理工具 ===

    def _register_state_tools(self):
        """注册状态管理工具"""

        # 1. 获取当前状态
        self.tools["state_get_current"] = MCPTool(
            name="state_get_current",
            description="获取当前工作流状态",
            category=MCPToolCategory.STATE,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID (可选，不提供则返回最新迭代)",
                    required=False
                )
            ],
            handler=self._get_current_state
        )

        # 2. 列出所有迭代
        self.tools["state_list_iterations"] = MCPTool(
            name="state_list_iterations",
            description="列出所有迭代",
            category=MCPToolCategory.STATE,
            parameters=[
                MCPToolParameter(
                    name="limit",
                    type="number",
                    description="返回数量限制",
                    required=False,
                    default=10
                )
            ],
            handler=self._list_iterations
        )

        # 3. 获取状态历史 (新增)
        self.tools["state_get_history"] = MCPTool(
            name="state_get_history",
            description="获取工作流状态转换历史",
            category=MCPToolCategory.STATE,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="limit",
                    type="number",
                    description="返回数量限制",
                    required=False,
                    default=10
                )
            ],
            handler=self._get_history
        )

        # 4. 更新阶段状态
        self.tools["state_update_stage"] = MCPTool(
            name="state_update_stage",
            description="更新阶段状态",
            category=MCPToolCategory.STATE,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="stage_id",
                    type="string",
                    description="阶段ID",
                    required=True
                ),
                MCPToolParameter(
                    name="status",
                    type="string",
                    description="新状态",
                    required=True,
                    enum=["pending", "in_progress", "completed", "skipped", "failed"]
                )
            ],
            handler=self._update_stage_status
        )

    # === 模板工具 ===

    def _register_template_tools(self):
        """注册模板工具"""

        # 1. 获取阶段模板
        self.tools["template_get_stage"] = MCPTool(
            name="template_get_stage",
            description="获取指定阶段的模板内容",
            category=MCPToolCategory.TEMPLATE,
            parameters=[
                MCPToolParameter(
                    name="mode",
                    type="string",
                    description="工作流模式",
                    required=True,
                    enum=["minimal", "standard", "complete", "smart"]
                ),
                MCPToolParameter(
                    name="stage_id",
                    type="string",
                    description="阶段ID (如 P1, S1)",
                    required=True
                )
            ],
            handler=self._get_stage_template
        )

        # 2. 渲染模板
        self.tools["template_render"] = MCPTool(
            name="template_render",
            description="渲染模板并替换变量",
            category=MCPToolCategory.TEMPLATE,
            parameters=[
                MCPToolParameter(
                    name="template_id",
                    type="string",
                    description="模板ID",
                    required=True
                ),
                MCPToolParameter(
                    name="variables",
                    type="object",
                    description="变量字典",
                    required=True
                )
            ],
            handler=self._render_template
        )

        # 3. 列出可用模板
        self.tools["template_list"] = MCPTool(
            name="template_list",
            description="列出所有可用模板",
            category=MCPToolCategory.TEMPLATE,
            parameters=[
                MCPToolParameter(
                    name="mode",
                    type="string",
                    description="按模式过滤 (可选)",
                    required=False,
                    enum=["minimal", "standard", "complete", "smart"]
                )
            ],
            handler=self._list_templates
        )

    # === 记忆工具 ===

    def _register_memory_tools(self):
        """注册记忆工具"""

        # 1. 记录阶段输出
        self.tools["memory_record_stage_output"] = MCPTool(
            name="memory_record_stage_output",
            description="记录阶段输出到记忆系统",
            category=MCPToolCategory.MEMORY,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="stage_id",
                    type="string",
                    description="阶段ID",
                    required=True
                ),
                MCPToolParameter(
                    name="output",
                    type="string",
                    description="阶段输出内容",
                    required=True
                ),
                MCPToolParameter(
                    name="mode",
                    type="string",
                    description="工作流模式",
                    required=True
                )
            ],
            handler=self._record_stage_output
        )

        # 2. 召回相关记忆
        self.tools["memory_recall_for_stage"] = MCPTool(
            name="memory_recall_for_stage",
            description="为当前阶段召回相关记忆",
            category=MCPToolCategory.MEMORY,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="stage_id",
                    type="string",
                    description="阶段ID",
                    required=True
                ),
                MCPToolParameter(
                    name="limit",
                    type="number",
                    description="返回数量",
                    required=False,
                    default=10
                )
            ],
            handler=self._recall_for_stage
        )

        # 3. 记录问题
        self.tools["memory_record_issue"] = MCPTool(
            name="memory_record_issue",
            description="记录遇到的问题",
            category=MCPToolCategory.MEMORY,
            parameters=[
                MCPToolParameter(
                    name="issue",
                    type="string",
                    description="问题描述",
                    required=True
                ),
                MCPToolParameter(
                    name="severity",
                    type="string",
                    description="严重程度",
                    required=True,
                    enum=["low", "medium", "high", "critical"]
                ),
                MCPToolParameter(
                    name="solution",
                    type="string",
                    description="解决方案 (可选)",
                    required=False
                ),
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID (可选)",
                    required=False
                ),
                MCPToolParameter(
                    name="stage_id",
                    type="string",
                    description="阶段ID (可选)",
                    required=False
                )
            ],
            handler=self._record_issue
        )

        # 4. 记录决策 (新增)
        self.tools["memory_record_decision"] = MCPTool(
            name="memory_record_decision",
            description="记录技术决策",
            category=MCPToolCategory.MEMORY,
            parameters=[
                MCPToolParameter(
                    name="decision",
                    type="string",
                    description="决策内容",
                    required=True
                ),
                MCPToolParameter(
                    name="context",
                    type="object",
                    description="决策上下文",
                    required=False
                ),
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID (可选)",
                    required=False
                ),
                MCPToolParameter(
                    name="stage_id",
                    type="string",
                    description="阶段ID (可选)",
                    required=False
                )
            ],
            handler=self._record_decision
        )

        # 5. 记录经验教训 (新增)
        self.tools["memory_record_learning"] = MCPTool(
            name="memory_record_learning",
            description="记录经验教训",
            category=MCPToolCategory.MEMORY,
            parameters=[
                MCPToolParameter(
                    name="learning",
                    type="string",
                    description="经验教训内容",
                    required=True
                ),
                MCPToolParameter(
                    name="category",
                    type="string",
                    description="分类 (如技术、流程等)",
                    required=False
                ),
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID (可选)",
                    required=False
                )
            ],
            handler=self._record_learning
        )

        # 6. 召回记忆 (新增)
        self.tools["memory_recall"] = MCPTool(
            name="memory_recall",
            description="召回指定条件的记忆",
            category=MCPToolCategory.MEMORY,
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="memory_type",
                    type="string",
                    description="记忆类型 (可选)",
                    required=False,
                    enum=["decision", "issue", "learning", "stage_output"]
                ),
                MCPToolParameter(
                    name="limit",
                    type="number",
                    description="返回数量",
                    required=False,
                    default=10
                )
            ],
            handler=self._recall_memories
        )

        # 7. 搜索记忆 (新增)
        self.tools["memory_search"] = MCPTool(
            name="memory_search",
            description="搜索记忆内容",
            category=MCPToolCategory.MEMORY,
            parameters=[
                MCPToolParameter(
                    name="query",
                    type="string",
                    description="搜索关键词",
                    required=True
                ),
                MCPToolParameter(
                    name="limit",
                    type="number",
                    description="返回数量",
                    required=False,
                    default=10
                )
            ],
            handler=self._search_memories
        )

    # === 质量门工具 ===

    def _register_gate_tools(self):
        """注册质量门工具"""

        # 1. 评估质量门
        self.tools["gate_evaluate"] = MCPTool(
            name="gate_evaluate",
            description="评估质量门",
            category=MCPToolCategory.GATE,
            parameters=[
                MCPToolParameter(
                    name="gate_id",
                    type="string",
                    description="质量门ID",
                    required=True,
                    enum=["DG1", "DG2", "DG3"]
                ),
                MCPToolParameter(
                    name="context",
                    type="object",
                    description="评估上下文 (包含项目状态、测试结果等)",
                    required=True
                )
            ],
            handler=self._evaluate_gate
        )

        # 2. 获取质量门信息
        self.tools["gate_get_info"] = MCPTool(
            name="gate_get_info",
            description="获取质量门信息",
            category=MCPToolCategory.GATE,
            parameters=[
                MCPToolParameter(
                    name="gate_id",
                    type="string",
                    description="质量门ID",
                    required=True,
                    enum=["DG1", "DG2", "DG3"]
                )
            ],
            handler=self._get_gate_info
        )

    # === 导出工具 ===

    def _register_export_tools(self):
        """注册导出工具 (新增)"""

        # 1. 导出迭代
        self.tools["export_iteration"] = MCPTool(
            name="export_iteration",
            description="导出迭代文档",
            category=MCPToolCategory.ANALYSIS,  # 使用 ANALYSIS 分类
            parameters=[
                MCPToolParameter(
                    name="iteration_id",
                    type="string",
                    description="迭代ID",
                    required=True
                ),
                MCPToolParameter(
                    name="format",
                    type="string",
                    description="导出格式",
                    required=False,
                    default="markdown",
                    enum=["markdown", "html", "json"]
                ),
                MCPToolParameter(
                    name="output_path",
                    type="string",
                    description="输出路径",
                    required=False
                )
            ],
            handler=self._export_iteration
        )

    # === 工具处理函数 (Handlers) ===

    # 工作流工具处理函数
    def _start_iteration(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """开始新迭代"""
        try:
            mode_str = arguments["mode"]
            mode = WorkflowMode(mode_str)
            iteration_id = arguments.get("iteration_id")
            metadata = arguments.get("metadata", {})

            # 创建工作流引擎 (使用 project_id 初始化)
            engine = WorkflowEngine(project_id=self.state_manager.project_id)
            engine.state_manager = self.state_manager  # 使用共享的 state_manager

            # 注册所有 mode implementations
            from ..modes import MinimalWorkflow, StandardWorkflow, CompleteWorkflow, SmartWorkflow
            engine.register_mode_implementation(WorkflowMode.MINIMAL, MinimalWorkflow())
            engine.register_mode_implementation(WorkflowMode.STANDARD, StandardWorkflow())
            engine.register_mode_implementation(WorkflowMode.COMPLETE, CompleteWorkflow())
            engine.register_mode_implementation(WorkflowMode.SMART, SmartWorkflow())

            # 开始迭代 (使用 initialize 方法)
            result = engine.initialize(mode=mode_str, metadata=metadata, iteration_id=iteration_id)

            return MCPToolResult.success_result({
                "iteration_id": result['iteration_id'],
                "mode": result['mode'],
                "stages_count": result['total_stages'],
                "current_stage": result.get('current_stage'),  # 返回完整的 current_stage 字典
                "message": f"成功开始 {mode_str} 模式迭代"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"开始迭代失败: {str(e)}")

    def _next_stage(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """进入下一阶段"""
        try:
            iteration_id = arguments["iteration_id"]
            current_stage_output = arguments.get("current_stage_output")

            # 获取当前迭代 (StateManager 只管理当前迭代)
            iteration = self.state_manager.get_current_iteration()
            if not iteration:
                return MCPToolResult.error_result(f"未找到迭代: {iteration_id}")

            # 记录当前阶段输出到元数据
            metadata = {}
            if current_stage_output:
                metadata["stage_output"] = current_stage_output

            # 前进到下一阶段
            success = self.state_manager.advance_stage(metadata)

            if not success:
                return MCPToolResult.success_result({
                    "message": "所有阶段已完成",
                    "iteration_completed": True
                })

            # 获取新的当前阶段
            new_iteration = self.state_manager.get_current_iteration()
            current_stage = new_iteration.current_stage if new_iteration else None

            if not current_stage:
                return MCPToolResult.success_result({
                    "message": "所有阶段已完成",
                    "iteration_completed": True
                })

            return MCPToolResult.success_result({
                "stage_id": current_stage.stage_id,  # 添加 stage_id 字段
                "current_stage": current_stage.stage_id,
                "stage_name": current_stage.name,
                "iteration_completed": False,
                "message": f"已进入阶段: {current_stage.name}"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"进入下一阶段失败: {str(e)}")

    def _complete_stage(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """完成当前阶段 (新增)"""
        try:
            iteration_id = arguments["iteration_id"]
            stage_id = arguments["stage_id"]
            metadata = arguments.get("metadata", {})

            # 验证当前阶段
            iteration = self.state_manager.get_current_iteration()
            if not iteration:
                return MCPToolResult.error_result(f"未找到迭代: {iteration_id}")

            if not iteration.current_stage or iteration.current_stage.stage_id != stage_id:
                return MCPToolResult.error_result(
                    f"阶段 {stage_id} 不是当前阶段 (当前: {iteration.current_stage.stage_id if iteration.current_stage else 'None'})"
                )

            # 前进到下一阶段
            success = self.state_manager.advance_stage(metadata)

            if success:
                return MCPToolResult.success_result({
                    "stage_id": stage_id,
                    "message": f"阶段 {stage_id} 已完成"
                })
            else:
                return MCPToolResult.error_result("完成阶段失败")

        except Exception as e:
            return MCPToolResult.error_result(f"完成阶段失败: {str(e)}")

    def _complete_iteration(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """完成迭代"""
        try:
            iteration_id = arguments["iteration_id"]
            summary = arguments.get("summary")

            # 获取迭代摘要
            iteration_summary = self.memory_manager.get_iteration_summary(iteration_id)

            return MCPToolResult.success_result({
                "iteration_id": iteration_id,
                "summary": iteration_summary,
                "message": "迭代已完成"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"完成迭代失败: {str(e)}")

    # 状态工具处理函数
    def _get_current_state(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """获取当前状态"""
        try:
            # StateManager 只管理当前迭代
            iteration = self.state_manager.get_current_iteration()

            if not iteration:
                return MCPToolResult.error_result("未找到迭代")

            # 使用 to_dict() 并添加额外的字段
            data = iteration.to_dict()

            # 添加 progress 字段（整体进度）
            if 'overall_progress' in data:
                data['progress'] = data['overall_progress']

            # 添加单独的 current_stage 字段（完整对象）
            if iteration.current_stage:
                data['current_stage'] = iteration.current_stage.to_dict()

            return MCPToolResult.success_result(data)

        except Exception as e:
            return MCPToolResult.error_result(f"获取状态失败: {str(e)}")

    def _list_iterations(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """列出所有迭代"""
        try:
            limit = arguments.get("limit", 10)
            iterations = self.state_manager.list_iterations()[:limit]

            return MCPToolResult.success_result({
                "iterations": [it.to_dict() for it in iterations],
                "total": len(iterations)
            })

        except Exception as e:
            return MCPToolResult.error_result(f"列出迭代失败: {str(e)}")

    def _get_history(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """获取状态转换历史 (新增)"""
        try:
            iteration_id = arguments["iteration_id"]
            limit = arguments.get("limit", 10)

            # 获取转换历史
            transitions = self.state_manager.get_transition_history(limit)

            return MCPToolResult.success_result({
                "transitions": transitions,
                "count": len(transitions)
            })

        except Exception as e:
            return MCPToolResult.error_result(f"获取历史失败: {str(e)}")

    def _update_stage_status(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """更新阶段状态"""
        try:
            iteration_id = arguments["iteration_id"]
            stage_id = arguments["stage_id"]
            status_str = arguments["status"]
            status = StageStatus(status_str)

            success = self.state_manager.update_stage_status(iteration_id, stage_id, status)

            if success:
                return MCPToolResult.success_result({
                    "message": f"阶段 {stage_id} 状态已更新为 {status.value}"
                })
            else:
                return MCPToolResult.error_result("更新状态失败")

        except Exception as e:
            return MCPToolResult.error_result(f"更新阶段状态失败: {str(e)}")

    # 模板工具处理函数
    def _get_stage_template(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """获取阶段模板"""
        try:
            mode = arguments["mode"]
            stage_id = arguments["stage_id"]

            template = self.template_manager.get_template_for_stage(mode, stage_id)

            if not template:
                return MCPToolResult.error_result(f"未找到模板: mode={mode}, stage={stage_id}")

            return MCPToolResult.success_result({
                "template_id": template.template_id,
                "name": template.name,
                "content": template.read_content(),
                "variables": [v.to_dict() for v in template.variables]
            })

        except Exception as e:
            return MCPToolResult.error_result(f"获取模板失败: {str(e)}")

    def _render_template(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """渲染模板"""
        try:
            template_id = arguments["template_id"]
            variables = arguments["variables"]

            rendered = self.template_manager.render_template(template_id, variables)

            return MCPToolResult.success_result({
                "rendered_content": rendered
            })

        except Exception as e:
            return MCPToolResult.error_result(f"渲染模板失败: {str(e)}")

    def _list_templates(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """列出模板"""
        try:
            mode = arguments.get("mode")
            templates = self.template_manager.list_templates(mode=mode)

            return MCPToolResult.success_result({
                "templates": [t.to_dict() for t in templates],
                "total": len(templates)
            })

        except Exception as e:
            return MCPToolResult.error_result(f"列出模板失败: {str(e)}")

    # 记忆工具处理函数
    def _record_stage_output(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """记录阶段输出"""
        try:
            iteration_id = arguments["iteration_id"]
            stage_id = arguments["stage_id"]
            output = arguments["output"]
            mode = arguments["mode"]

            # 获取当前迭代和阶段对象 (StateManager 只管理当前迭代)
            iteration = self.state_manager.get_current_iteration()
            if not iteration:
                return MCPToolResult.error_result(f"未找到迭代: {iteration_id}")

            stage = next((s for s in iteration.stages if s.stage_id == stage_id), None)
            if not stage:
                return MCPToolResult.error_result(f"未找到阶段: {stage_id}")

            # 记录记忆
            memory = self.memory_manager.record_stage_output(
                iteration_id, stage, output, mode
            )

            return MCPToolResult.success_result({
                "memory_id": memory.memory_id,
                "message": "阶段输出已记录"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"记录阶段输出失败: {str(e)}")

    def _recall_for_stage(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """召回阶段记忆"""
        try:
            iteration_id = arguments["iteration_id"]
            stage_id = arguments["stage_id"]
            limit = arguments.get("limit", 10)

            memories = self.memory_manager.recall_for_stage(iteration_id, stage_id, limit)

            return MCPToolResult.success_result({
                "memories": [m.to_dict() for m in memories],
                "total": len(memories)
            })

        except Exception as e:
            return MCPToolResult.error_result(f"召回记忆失败: {str(e)}")

    def _record_issue(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """记录问题"""
        try:
            issue = arguments["issue"]
            severity = arguments["severity"]
            solution = arguments.get("solution")
            iteration_id = arguments.get("iteration_id")
            stage_id = arguments.get("stage_id")

            memory = self.memory_manager.record_issue(
                issue, severity, iteration_id, stage_id, solution
            )

            return MCPToolResult.success_result({
                "memory_id": memory.memory_id,
                "message": "问题已记录"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"记录问题失败: {str(e)}")

    def _record_decision(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """记录决策 (新增)"""
        try:
            decision = arguments["decision"]
            context = arguments.get("context", {})
            iteration_id = arguments.get("iteration_id")
            stage_id = arguments.get("stage_id")

            memory = self.memory_manager.record_decision(
                decision, context, iteration_id, stage_id
            )

            return MCPToolResult.success_result({
                "memory_id": memory.memory_id,
                "message": "决策已记录"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"记录决策失败: {str(e)}")

    def _record_learning(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """记录经验教训 (新增)"""
        try:
            learning = arguments["learning"]
            category = arguments.get("category", "general")
            iteration_id = arguments.get("iteration_id")

            memory = self.memory_manager.record_learning(
                learning, category, iteration_id
            )

            return MCPToolResult.success_result({
                "memory_id": memory.memory_id,
                "message": "经验教训已记录"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"记录经验教训失败: {str(e)}")

    def _recall_memories(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """召回记忆 (新增)"""
        try:
            iteration_id = arguments["iteration_id"]
            memory_type = arguments.get("memory_type")
            limit = arguments.get("limit", 10)

            # 使用 MemoryQuery 查询记忆
            from ..memory.models import MemoryQuery, MemoryType

            types = None
            if memory_type:
                type_map = {
                    "decision": MemoryType.DECISION,
                    "issue": MemoryType.ISSUE,
                    "learning": MemoryType.LEARNING,
                    "stage_output": MemoryType.STAGE_OUTPUT
                }
                types = [type_map.get(memory_type)]

            query = MemoryQuery(
                iteration_id=iteration_id,
                types=types,
                limit=limit
            )

            memories = self.memory_manager.store.query(query)

            return MCPToolResult.success_result({
                "memories": [m.to_dict() for m in memories],
                "count": len(memories)
            })

        except Exception as e:
            return MCPToolResult.error_result(f"召回记忆失败: {str(e)}")

    def _search_memories(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """搜索记忆 (新增)"""
        try:
            query = arguments["query"]
            limit = arguments.get("limit", 10)

            memories = self.memory_manager.store.search(query, limit)

            return MCPToolResult.success_result({
                "memories": [m.to_dict() for m in memories],
                "count": len(memories)
            })

        except Exception as e:
            return MCPToolResult.error_result(f"搜索记忆失败: {str(e)}")

    # 质量门工具处理函数
    def _evaluate_gate(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """评估质量门"""
        try:
            gate_id = arguments["gate_id"]
            context = arguments["context"]

            evaluation = self.gate_manager.evaluate_gate(gate_id, context)

            return MCPToolResult.success_result(evaluation.to_dict())

        except Exception as e:
            return MCPToolResult.error_result(f"评估质量门失败: {str(e)}")

    def _get_gate_info(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """获取质量门信息"""
        try:
            gate_id = arguments["gate_id"]
            info = self.gate_manager.get_gate_info(gate_id)

            return MCPToolResult.success_result(info)

        except Exception as e:
            return MCPToolResult.error_result(f"获取质量门信息失败: {str(e)}")

    # 导出工具处理函数
    def _export_iteration(self, arguments: Dict[str, Any]) -> MCPToolResult:
        """导出迭代 (新增)"""
        try:
            from ..exporter import DocumentExporter, ExportFormat, ExportOptions

            iteration_id = arguments["iteration_id"]
            format_str = arguments.get("format", "markdown")
            output_path = arguments.get("output_path")

            # 创建导出器
            exporter = DocumentExporter(
                state_manager=self.state_manager,
                memory_manager=self.memory_manager
            )

            # 转换格式
            format_map = {
                "markdown": ExportFormat.MARKDOWN,
                "html": ExportFormat.HTML,
                "json": ExportFormat.JSON
            }
            export_format = format_map.get(format_str, ExportFormat.MARKDOWN)

            # 导出选项
            options = ExportOptions(format=export_format)
            if output_path:
                options.output_dir = Path(output_path)

            # 执行导出
            result = exporter.export_iteration(iteration_id, options)

            return MCPToolResult.success_result({
                "success": result.success,
                "output_path": str(result.output_path) if result.output_path else None,
                "files_created": [str(f) for f in result.files_created] if result.files_created else [],
                "message": "导出成功" if result.success else "导出失败"
            })

        except Exception as e:
            return MCPToolResult.error_result(f"导出迭代失败: {str(e)}")

    # === 工具管理 ===

    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """
        执行 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 参数字典

        Returns:
            工具执行结果
        """
        # 查找工具
        tool = self.tools.get(tool_name)
        if not tool:
            return MCPToolResult.error_result(f"未找到工具: {tool_name}")  # 修改为"未找到"

        # 验证参数
        validation_errors = tool.validate_arguments(arguments)
        if validation_errors:
            return MCPToolResult.error_result(
                f"参数验证失败: {', '.join(validation_errors)}"
            )

        # 执行工具
        if tool.handler:
            return tool.handler(arguments)
        else:
            return MCPToolResult.error_result(f"工具 {tool_name} 没有处理函数")

    def list_tools(self, category: Optional[MCPToolCategory] = None) -> List[MCPTool]:
        """
        列出所有工具

        Args:
            category: 按分类过滤 (可选)

        Returns:
            工具列表
        """
        tools = list(self.tools.values())

        if category:
            tools = [t for t in tools if t.category == category]

        return tools

    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的 MCP schema

        Returns:
            MCP schema 列表
        """
        return [tool.to_mcp_schema() for tool in self.tools.values()]

    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具信息

        Args:
            tool_name: 工具名称

        Returns:
            工具信息字典，如果不存在返回 None
        """
        tool = self.tools.get(tool_name)
        if not tool:
            return None

        return {
            "name": tool.name,
            "description": tool.description,
            "category": tool.category.value,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default
                }
                for p in tool.parameters
            ]
        }
