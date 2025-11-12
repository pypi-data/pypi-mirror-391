"""
Template Manager - 模板管理器

提供模板的高级操作:
- 模板渲染和变量替换
- 模板输出到文件
- 与工作流集成
- 批量模板处理
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .registry import TemplateRegistry
from .models import Template, TemplateType, TemplateVariable
from ..models import WorkflowMode, Stage


class TemplateManager:
    """模板管理器 - 提供模板相关的高级功能"""

    def __init__(self, template_root: Optional[Path] = None,
                 output_root: Optional[Path] = None):
        """
        初始化模板管理器

        Args:
            template_root: 模板根目录
            output_root: 输出根目录，默认为当前目录的 aceflow_result/
        """
        self.registry = TemplateRegistry(template_root)

        if output_root is None:
            output_root = Path.cwd() / "aceflow_result"
        self.output_root = output_root

    # === 模板查询 ===

    def get_template(self, template_id: str) -> Optional[Template]:
        """获取模板"""
        return self.registry.get_template(template_id)

    def get_templates_for_mode(self, mode: str) -> List[Template]:
        """获取某个模式的所有模板"""
        return self.registry.get_templates_by_mode(mode)

    def get_template_for_stage(self, mode: str, stage_id: str) -> Optional[Template]:
        """
        获取某个阶段的模板

        Args:
            mode: 工作流模式 (minimal/standard/complete/smart)
            stage_id: 阶段ID (P1, S1, D1, etc.)

        Returns:
            模板对象或 None
        """
        return self.registry.get_template_by_stage(mode, stage_id)

    def list_templates(self, mode: Optional[str] = None,
                      template_type: Optional[TemplateType] = None) -> List[Template]:
        """
        列出模板

        Args:
            mode: 按模式过滤 (可选)
            template_type: 按类型过滤 (可选)

        Returns:
            模板列表
        """
        templates = self.registry.list_all_templates()

        if mode:
            templates = [t for t in templates if t.mode == mode]

        if template_type:
            templates = [t for t in templates if t.type == template_type]

        return templates

    # === 模板渲染 ===

    def render_template(self, template_id: str,
                       variables: Dict[str, str]) -> str:
        """
        渲染模板

        Args:
            template_id: 模板ID
            variables: 变量字典

        Returns:
            渲染后的内容

        Raises:
            ValueError: 如果模板不存在或变量缺失
        """
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"模板不存在: {template_id}")

        return template.render(variables)

    def render_template_for_stage(self, mode: str, stage_id: str,
                                  variables: Dict[str, str]) -> str:
        """
        渲染阶段模板

        Args:
            mode: 工作流模式
            stage_id: 阶段ID
            variables: 变量字典

        Returns:
            渲染后的内容
        """
        template = self.get_template_for_stage(mode, stage_id)
        if not template:
            raise ValueError(f"未找到模板: mode={mode}, stage={stage_id}")

        return template.render(variables)

    # === 模板输出 ===

    def write_template(self, template_id: str,
                      output_file: Path,
                      variables: Dict[str, str],
                      create_dirs: bool = True) -> Path:
        """
        渲染模板并写入文件

        Args:
            template_id: 模板ID
            output_file: 输出文件路径
            variables: 变量字典
            create_dirs: 是否自动创建目录

        Returns:
            输出文件的完整路径
        """
        # 渲染模板
        content = self.render_template(template_id, variables)

        # 确保目录存在
        if create_dirs:
            output_file.parent.mkdir(parents=True, exist_ok=True)

        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return output_file

    def write_stage_template(self, mode: str, stage: Stage,
                            iteration_id: str,
                            extra_variables: Optional[Dict[str, str]] = None) -> Optional[Path]:
        """
        为某个阶段生成模板文件

        Args:
            mode: 工作流模式
            stage: 阶段对象
            iteration_id: 迭代ID
            extra_variables: 额外变量

        Returns:
            输出文件路径，如果没有找到模板则返回 None
        """
        # 查找模板
        template = self.get_template_for_stage(mode, stage.stage_id)
        if not template:
            return None

        # 构建变量
        variables = self._build_stage_variables(stage, iteration_id, extra_variables)

        # 确定输出路径
        output_file = self._get_stage_output_path(mode, stage, iteration_id, template)

        # 写入文件
        return self.write_template(template.template_id, output_file, variables)

    def _build_stage_variables(self, stage: Stage, iteration_id: str,
                               extra_variables: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """构建阶段模板变量"""
        variables = {
            'iteration_id': iteration_id,
            'stage_id': stage.stage_id,
            'stage_name': stage.name,
            'start_time': datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # 添加阶段元数据中的变量
        if stage.metadata:
            for key, value in stage.metadata.items():
                if isinstance(value, str):
                    variables[key] = value

        # 添加额外变量
        if extra_variables:
            variables.update(extra_variables)

        return variables

    def _get_stage_output_path(self, mode: str, stage: Stage,
                               iteration_id: str, template: Template) -> Path:
        """确定阶段输出文件路径"""
        # aceflow_result/iter_001/P1_需求分析/requirements.md
        iter_dir = self.output_root / iteration_id

        # 阶段目录名: "P1_需求分析"
        stage_dir_name = f"{stage.stage_id}_{stage.name.split('(')[0].strip()}"
        stage_dir = iter_dir / stage_dir_name

        # 文件名: 使用模板的原始文件名
        filename = template.file_path.name

        return stage_dir / filename

    # === 批量操作 ===

    def init_iteration(self, mode: str, iteration_id: str,
                      stages: List[Stage],
                      variables: Optional[Dict[str, str]] = None) -> List[Path]:
        """
        初始化一个迭代的所有阶段模板

        Args:
            mode: 工作流模式
            iteration_id: 迭代ID
            stages: 阶段列表
            variables: 公共变量

        Returns:
            创建的文件路径列表
        """
        created_files = []

        for stage in stages:
            output_file = self.write_stage_template(
                mode=mode,
                stage=stage,
                iteration_id=iteration_id,
                extra_variables=variables
            )

            if output_file:
                created_files.append(output_file)

        return created_files

    # === 工作流集成 ===

    def get_mode_templates_summary(self, mode: str) -> Dict[str, Any]:
        """
        获取某个模式的模板摘要

        Args:
            mode: 工作流模式

        Returns:
            包含模板信息的字典
        """
        templates = self.get_templates_for_mode(mode)

        stage_templates = [t for t in templates if t.type == TemplateType.STAGE]
        workflow_templates = [t for t in templates if t.type == TemplateType.WORKFLOW]
        other_templates = [t for t in templates if t.type not in [TemplateType.STAGE, TemplateType.WORKFLOW]]

        return {
            'mode': mode,
            'total': len(templates),
            'stage_templates': [
                {
                    'template_id': t.template_id,
                    'name': t.name,
                    'stage_id': t.stage_id,
                    'file': t.file_path.name
                }
                for t in sorted(stage_templates, key=lambda x: x.stage_id or "")
            ],
            'workflow_templates': [
                {
                    'template_id': t.template_id,
                    'name': t.name,
                    'file': t.file_path.name
                }
                for t in workflow_templates
            ],
            'other_templates': [
                {
                    'template_id': t.template_id,
                    'name': t.name,
                    'type': t.type.value
                }
                for t in other_templates
            ]
        }

    def validate_templates(self, mode: Optional[str] = None) -> Dict[str, List[str]]:
        """
        验证模板

        Args:
            mode: 只验证特定模式的模板 (可选)

        Returns:
            {template_id: [问题列表]} 字典
        """
        all_issues = self.registry.validate_all_templates()

        if mode:
            # 只返回特定模式的问题
            mode_issues = {}
            for template_id, issues in all_issues.items():
                template = self.get_template(template_id)
                if template and template.mode == mode:
                    mode_issues[template_id] = issues
            return mode_issues

        return all_issues

    # === 统计信息 ===

    def get_summary(self) -> Dict[str, Any]:
        """获取模板管理器摘要"""
        registry_summary = self.registry.get_summary()

        return {
            **registry_summary,
            'output_root': str(self.output_root),
            'modes_available': list(registry_summary['by_mode'].keys())
        }

    def get_template_info(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        获取模板详细信息

        Args:
            template_id: 模板ID

        Returns:
            模板信息字典或 None
        """
        template = self.get_template(template_id)
        if not template:
            return None

        return template.to_dict()
