"""
Templates - 模板管理系统

统一管理4种工作流模式的文档模板:
- Minimal: 快速原型模式模板
- Standard: 标准开发模式模板
- Complete: 完整流程模式模板
- Smart: 智能自适应模式模板

功能:
- 模板注册和发现
- 变量替换和渲染
- 模板验证
- 与工作流模式集成
"""

from .manager import TemplateManager
from .registry import TemplateRegistry
from .models import Template, TemplateType, TemplateVariable

__all__ = [
    'TemplateManager',
    'TemplateRegistry',
    'Template',
    'TemplateType',
    'TemplateVariable'
]
