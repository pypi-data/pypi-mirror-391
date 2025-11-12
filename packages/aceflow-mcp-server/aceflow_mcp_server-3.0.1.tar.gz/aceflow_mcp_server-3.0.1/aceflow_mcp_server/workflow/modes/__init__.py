"""
Workflow Modes - 工作流模式

提供4种工作流模式:
- Minimal: 快速原型模式 (P→D→R)
- Standard: 标准平衡模式 (P1→P2→D1→D2→R1)
- Complete: 完整严格模式 (S1-S8 + 3个质量门)
- Smart: AI驱动自适应模式
"""

from .minimal import MinimalWorkflow
from .standard import StandardWorkflow
from .complete import CompleteWorkflow
from .smart import SmartWorkflow

__all__ = [
    'MinimalWorkflow',
    'StandardWorkflow',
    'CompleteWorkflow',
    'SmartWorkflow'
]
