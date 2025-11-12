"""
Template Models - 模板数据模型

定义模板系统的核心数据结构
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class TemplateType(Enum):
    """模板类型枚举"""
    STAGE = "stage"              # 阶段模板 (如 P1, S1 等)
    WORKFLOW = "workflow"        # 工作流模板 (如 bug_fix, feature_quick)
    DOCUMENT = "document"        # 文档模板 (如 config_guide)
    CHECKLIST = "checklist"      # 检查清单模板
    REPORT = "report"            # 报告模板


@dataclass
class TemplateVariable:
    """模板变量定义"""
    name: str                    # 变量名 (如 "iteration_id")
    description: str             # 变量说明
    required: bool = True        # 是否必需
    default_value: Optional[str] = None  # 默认值
    example: Optional[str] = None        # 示例值

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'required': self.required,
            'default_value': self.default_value,
            'example': self.example
        }


@dataclass
class Template:
    """模板定义"""
    template_id: str             # 模板ID (如 "standard_p1_requirements")
    name: str                    # 模板名称
    mode: str                    # 所属模式 (minimal/standard/complete/smart)
    type: TemplateType           # 模板类型
    file_path: Path              # 模板文件路径
    description: str = ""        # 模板描述
    stage_id: Optional[str] = None       # 关联的阶段ID (如 "P1", "S1")
    variables: List[TemplateVariable] = field(default_factory=list)  # 模板变量
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    @property
    def exists(self) -> bool:
        """检查模板文件是否存在"""
        return self.file_path.exists()

    def read_content(self) -> str:
        """读取模板内容"""
        if not self.exists:
            raise FileNotFoundError(f"模板文件不存在: {self.file_path}")

        with open(self.file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def render(self, variables: Dict[str, str]) -> str:
        """
        渲染模板，替换变量

        Args:
            variables: 变量字典，如 {"iteration_id": "iter_001", "owner": "张三"}

        Returns:
            渲染后的内容
        """
        content = self.read_content()

        # 验证必需变量
        required_vars = {v.name for v in self.variables if v.required}
        provided_vars = set(variables.keys())
        missing_vars = required_vars - provided_vars

        if missing_vars:
            raise ValueError(f"缺少必需变量: {missing_vars}")

        # 替换变量
        for var_name, var_value in variables.items():
            # 支持两种格式: {variable} 和 {{variable}}
            content = content.replace(f"{{{var_name}}}", var_value)
            content = content.replace(f"{{{{{var_name}}}}}", var_value)

        return content

    def get_variable_info(self, var_name: str) -> Optional[TemplateVariable]:
        """获取变量信息"""
        for var in self.variables:
            if var.name == var_name:
                return var
        return None

    def validate(self) -> List[str]:
        """
        验证模板

        Returns:
            问题列表，如果为空则验证通过
        """
        issues = []

        # 检查文件是否存在
        if not self.exists:
            issues.append(f"模板文件不存在: {self.file_path}")
            return issues  # 文件不存在就不继续验证了

        # 读取内容
        try:
            content = self.read_content()
        except Exception as e:
            issues.append(f"无法读取模板文件: {e}")
            return issues

        # 检查变量是否在内容中
        for var in self.variables:
            var_pattern_1 = f"{{{var.name}}}"
            var_pattern_2 = f"{{{{{var.name}}}}}"

            if var_pattern_1 not in content and var_pattern_2 not in content:
                if var.required:
                    issues.append(f"必需变量 '{var.name}' 未在模板中使用")

        return issues

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'mode': self.mode,
            'type': self.type.value,
            'file_path': str(self.file_path),
            'description': self.description,
            'stage_id': self.stage_id,
            'variables': [v.to_dict() for v in self.variables],
            'metadata': self.metadata,
            'exists': self.exists
        }


# 通用模板变量定义
COMMON_VARIABLES = [
    TemplateVariable(
        name="iteration_id",
        description="迭代ID",
        required=True,
        example="iter_001"
    ),
    TemplateVariable(
        name="project_name",
        description="项目名称",
        required=False,
        example="用户管理系统"
    ),
    TemplateVariable(
        name="start_time",
        description="开始时间",
        required=False,
        default_value=datetime.now().strftime("%Y-%m-%d %H:%M"),
        example="2025-11-08 10:00"
    ),
    TemplateVariable(
        name="completion_time",
        description="完成时间",
        required=False,
        example="2025-11-08 18:00"
    ),
    TemplateVariable(
        name="owner",
        description="负责人",
        required=False,
        example="张三"
    ),
    TemplateVariable(
        name="reviewer",
        description="审核人",
        required=False,
        example="李四"
    ),
    TemplateVariable(
        name="version",
        description="版本号",
        required=False,
        example="v1.0.0"
    ),
]
