"""
Template Registry - 模板注册表

自动发现和注册项目中的所有模板文件
"""

from pathlib import Path
from typing import Dict, List, Optional
import re

from .models import Template, TemplateType, TemplateVariable, COMMON_VARIABLES


class TemplateRegistry:
    """模板注册表 - 管理所有可用模板"""

    def __init__(self, template_root: Optional[Path] = None):
        """
        初始化模板注册表

        Args:
            template_root: 模板根目录，默认为 aceflow/templates/
        """
        if template_root is None:
            # 默认模板目录
            current_file = Path(__file__)
            aceflow_root = current_file.parent.parent.parent  # aceflow/workflow/templates -> aceflow
            template_root = aceflow_root / "templates"

        self.template_root = template_root
        self.templates: Dict[str, Template] = {}
        self._discover_templates()

    def _discover_templates(self):
        """自动发现所有模板"""
        if not self.template_root.exists():
            return

        # 扫描四种模式的模板
        for mode in ['minimal', 'standard', 'complete', 'smart']:
            mode_dir = self.template_root / mode
            if mode_dir.exists():
                self._discover_mode_templates(mode, mode_dir)

        # 扫描根目录的通用模板 (Complete 模式的遗留模板)
        self._discover_root_templates()

        # 扫描文档模板
        doc_templates_dir = self.template_root / "document_templates"
        if doc_templates_dir.exists():
            self._discover_document_templates(doc_templates_dir)

    def _discover_mode_templates(self, mode: str, mode_dir: Path):
        """发现某个模式的所有模板"""
        # 阶段模板 (直接在模式目录下的 .md 文件)
        for template_file in mode_dir.glob("*.md"):
            if template_file.name == "README.md":
                continue

            template = self._create_template_from_file(
                template_file,
                mode=mode,
                template_type=TemplateType.STAGE
            )
            if template:
                self.templates[template.template_id] = template

        # 工作流模板 (workflows 子目录)
        workflows_dir = mode_dir / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.md"):
                template = self._create_template_from_file(
                    workflow_file,
                    mode=mode,
                    template_type=TemplateType.WORKFLOW
                )
                if template:
                    self.templates[template.template_id] = template

    def _discover_root_templates(self):
        """发现根目录的通用模板 (主要是 Complete 模式的遗留模板)"""
        for template_file in self.template_root.glob("s*.md"):
            # s1_user_story.md, s2_tasks_main.md 等
            template = self._create_template_from_file(
                template_file,
                mode="complete",
                template_type=TemplateType.STAGE
            )
            if template:
                # 避免重复 (如果 complete/ 目录下已经有了)
                if template.template_id not in self.templates:
                    self.templates[template.template_id] = template

        # task-status-table.md
        task_status_file = self.template_root / "task-status-table.md"
        if task_status_file.exists():
            template = self._create_template_from_file(
                task_status_file,
                mode="common",
                template_type=TemplateType.DOCUMENT
            )
            if template:
                self.templates[template.template_id] = template

    def _discover_document_templates(self, doc_dir: Path):
        """发现文档模板"""
        for doc_file in doc_dir.glob("*.md"):
            template = self._create_template_from_file(
                doc_file,
                mode="common",
                template_type=TemplateType.DOCUMENT
            )
            if template:
                self.templates[template.template_id] = template

    def _create_template_from_file(self, file_path: Path, mode: str,
                                    template_type: TemplateType) -> Optional[Template]:
        """从文件创建模板对象"""
        try:
            # 生成模板ID: mode_filename (不含扩展名)
            filename_without_ext = file_path.stem
            template_id = f"{mode}_{filename_without_ext}"

            # 提取阶段ID (如果是阶段模板)
            stage_id = None
            if template_type == TemplateType.STAGE:
                stage_id = self._extract_stage_id(filename_without_ext)

            # 生成模板名称
            name = self._generate_template_name(filename_without_ext)

            # 读取文件并提取变量
            variables = self._extract_variables_from_file(file_path)

            # 创建模板对象
            template = Template(
                template_id=template_id,
                name=name,
                mode=mode,
                type=template_type,
                file_path=file_path,
                stage_id=stage_id,
                variables=variables,
                metadata={
                    'filename': file_path.name,
                    'relative_path': str(file_path.relative_to(self.template_root))
                }
            )

            return template

        except Exception as e:
            print(f"警告: 无法创建模板 {file_path}: {e}")
            return None

    def _extract_stage_id(self, filename: str) -> Optional[str]:
        """从文件名提取阶段ID"""
        # s1_user_story -> S1
        # p1_requirements -> P1
        # d1_implementation -> D1
        # r1_release -> R1
        match = re.match(r'([a-z])(\d+)_', filename, re.IGNORECASE)
        if match:
            prefix = match.group(1).upper()
            number = match.group(2)
            return f"{prefix}{number}"
        return None

    def _generate_template_name(self, filename: str) -> str:
        """生成友好的模板名称"""
        # s1_user_story -> 用户故事 (S1)
        # p1_requirements -> 需求分析 (P1)

        name_mapping = {
            # Complete mode (S1-S8)
            's1_user_story': '用户故事 (S1)',
            's2_tasks_main': '主任务清单 (S2)',
            's2_tasks_group': '任务分组 (S2)',
            's3_testcases': '测试用例汇总 (S3)',
            's3_testcases_main': '单个测试用例 (S3)',
            's4_implementation': '功能实现汇总 (S4)',
            's4_implementation_report': '任务实现报告 (S4)',
            's5_test_report': '测试报告 (S5)',
            's6_codereview': '代码评审 (S6)',
            's7_demo_script': '演示脚本 (S7)',
            's8_summary_report': '迭代总结 (S8)',
            's8_learning_summary': '经验总结 (S8)',

            # Standard mode (P1-P2-D1-D2-R1)
            'p1_requirements': '需求分析 (P1)',
            'p2_design': '技术设计 (P2)',
            'd1_implementation': '核心实现 (D1)',
            'd2_testing': '测试与完善 (D2)',
            'r1_release': '评审与发布 (R1)',

            # Minimal mode (P-D-R)
            'planning': '规划 (P)',
            'requirements': '需求 (P)',
            'development': '开发 (D)',
            'review': '评审 (R)',
            'summary': '总结',

            # Workflows
            'bug_fix': 'Bug修复工作流',
            'feature_quick': '快速功能开发',
            'prototype': '原型开发流程',

            # Documents
            'task-status-table': '任务状态表',
            'config_guide': '配置指南',
            'process_spec': '流程规范',

            # Smart mode
            'dynamic_prompts': '动态提示模板',
            'decision_engine': '决策引擎',
        }

        return name_mapping.get(filename, filename.replace('_', ' ').title())

    def _extract_variables_from_file(self, file_path: Path) -> List[TemplateVariable]:
        """从模板文件中提取变量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 查找所有 {variable} 和 {{variable}} 格式的变量
            pattern = r'\{+([a-zA-Z_][a-zA-Z0-9_]*)\}+'
            matches = re.findall(pattern, content)

            # 去重
            unique_vars = set(matches)

            # 创建变量对象
            variables = []
            for var_name in unique_vars:
                # 检查是否是通用变量
                common_var = self._find_common_variable(var_name)
                if common_var:
                    variables.append(common_var)
                else:
                    # 创建新变量
                    variables.append(TemplateVariable(
                        name=var_name,
                        description=f"变量: {var_name}",
                        required=False  # 默认非必需
                    ))

            return variables

        except Exception as e:
            print(f"警告: 无法从 {file_path} 提取变量: {e}")
            return []

    def _find_common_variable(self, var_name: str) -> Optional[TemplateVariable]:
        """查找通用变量定义"""
        for var in COMMON_VARIABLES:
            if var.name == var_name:
                return var
        return None

    # === 查询方法 ===

    def get_template(self, template_id: str) -> Optional[Template]:
        """根据ID获取模板"""
        return self.templates.get(template_id)

    def get_templates_by_mode(self, mode: str) -> List[Template]:
        """获取指定模式的所有模板"""
        return [t for t in self.templates.values() if t.mode == mode]

    def get_templates_by_type(self, template_type: TemplateType) -> List[Template]:
        """获取指定类型的所有模板"""
        return [t for t in self.templates.values() if t.type == template_type]

    def get_template_by_stage(self, mode: str, stage_id: str) -> Optional[Template]:
        """
        根据模式和阶段ID获取模板

        Args:
            mode: 模式 (minimal/standard/complete/smart)
            stage_id: 阶段ID (P1, S1, etc.)

        Returns:
            模板对象或 None
        """
        for template in self.templates.values():
            if template.mode == mode and template.stage_id == stage_id:
                return template
        return None

    def list_all_templates(self) -> List[Template]:
        """列出所有模板"""
        return list(self.templates.values())

    def validate_all_templates(self) -> Dict[str, List[str]]:
        """
        验证所有模板

        Returns:
            {template_id: [问题列表]} 字典，只包含有问题的模板
        """
        issues_by_template = {}

        for template_id, template in self.templates.items():
            issues = template.validate()
            if issues:
                issues_by_template[template_id] = issues

        return issues_by_template

    def get_summary(self) -> Dict[str, any]:
        """获取注册表摘要"""
        by_mode = {}
        by_type = {}

        for template in self.templates.values():
            # 按模式统计
            if template.mode not in by_mode:
                by_mode[template.mode] = 0
            by_mode[template.mode] += 1

            # 按类型统计
            type_key = template.type.value
            if type_key not in by_type:
                by_type[type_key] = 0
            by_type[type_key] += 1

        return {
            'total_templates': len(self.templates),
            'by_mode': by_mode,
            'by_type': by_type,
            'template_root': str(self.template_root)
        }
