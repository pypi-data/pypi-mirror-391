"""
MCP Tool Models - MCP 工具数据模型

定义 MCP 工具的数据结构
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable


class MCPToolCategory(Enum):
    """MCP 工具分类"""
    WORKFLOW = "workflow"       # 工作流管理
    STATE = "state"            # 状态管理
    TEMPLATE = "template"      # 模板操作
    MEMORY = "memory"          # 记忆管理
    CONTRACT = "contract"      # 契约管理
    GATE = "gate"              # 质量门
    ANALYSIS = "analysis"      # 分析工具


@dataclass
class MCPToolParameter:
    """MCP 工具参数定义"""
    name: str                  # 参数名
    type: str                  # 参数类型 (string/number/boolean/object/array)
    description: str           # 参数说明
    required: bool = False     # 是否必需
    default: Optional[Any] = None  # 默认值
    enum: Optional[List[Any]] = None  # 枚举值

    def to_schema(self) -> Dict[str, Any]:
        """转换为 JSON Schema 格式"""
        schema = {
            "type": self.type,
            "description": self.description
        }

        if self.enum:
            schema["enum"] = self.enum

        if self.default is not None:
            schema["default"] = self.default

        return schema


@dataclass
class MCPTool:
    """MCP 工具定义"""
    name: str                  # 工具名称 (唯一标识)
    description: str           # 工具描述
    category: MCPToolCategory  # 工具分类
    parameters: List[MCPToolParameter] = field(default_factory=list)  # 参数列表
    handler: Optional[Callable] = None  # 处理函数
    examples: List[Dict[str, Any]] = field(default_factory=list)  # 使用示例

    def get_required_params(self) -> List[str]:
        """获取必需参数列表"""
        return [p.name for p in self.parameters if p.required]

    def get_optional_params(self) -> List[str]:
        """获取可选参数列表"""
        return [p.name for p in self.parameters if not p.required]

    def to_mcp_schema(self) -> Dict[str, Any]:
        """
        转换为 MCP 工具 schema 格式

        Returns:
            MCP 工具定义字典
        """
        # 构建参数 schema
        properties = {}
        required = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        # MCP 工具 schema
        schema = {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties
            }
        }

        if required:
            schema["inputSchema"]["required"] = required

        return schema

    def validate_arguments(self, arguments: Dict[str, Any]) -> List[str]:
        """
        验证参数

        Args:
            arguments: 参数字典

        Returns:
            错误信息列表，如果为空则验证通过
        """
        errors = []

        # 检查必需参数
        for param in self.parameters:
            if param.required and param.name not in arguments:
                errors.append(f"缺少必需参数: {param.name}")

        # 检查枚举值
        for param in self.parameters:
            if param.enum and param.name in arguments:
                value = arguments[param.name]
                if value not in param.enum:
                    errors.append(
                        f"参数 {param.name} 的值 '{value}' 不在允许的枚举值中: {param.enum}"
                    )

        return errors


@dataclass
class MCPToolResult:
    """MCP 工具执行结果"""
    success: bool              # 是否成功
    data: Optional[Dict[str, Any]] = None  # 返回数据
    error: Optional[str] = None            # 错误信息
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "success": self.success
        }

        if self.data is not None:
            result["data"] = self.data

        if self.error:
            result["error"] = self.error

        if self.metadata:
            result["metadata"] = self.metadata

        return result

    @classmethod
    def success_result(cls, data: Dict[str, Any],
                      metadata: Optional[Dict[str, Any]] = None) -> 'MCPToolResult':
        """创建成功结果"""
        return cls(
            success=True,
            data=data,
            metadata=metadata or {}
        )

    @classmethod
    def error_result(cls, error: str,
                     metadata: Optional[Dict[str, Any]] = None) -> 'MCPToolResult':
        """创建错误结果"""
        return cls(
            success=False,
            error=error,
            metadata=metadata or {}
        )
