"""
Memory - 工作流记忆管理系统

为工作流引擎提供上下文记忆能力:
- 阶段间信息传递
- 迭代间经验积累
- 决策历史追踪
- 智能上下文召回

与 aceflow/pateoas/memory_system.py 的区别:
- 专注于工作流状态和阶段上下文
- 简化的接口，更适合工作流场景
- 与 StateManager 紧密集成
"""

from .manager import MemoryManager
from .models import (
    Memory,
    MemoryType,
    MemoryPriority,
    MemoryQuery
)
from .store import MemoryStore

__all__ = [
    'MemoryManager',
    'Memory',
    'MemoryType',
    'MemoryPriority',
    'MemoryQuery',
    'MemoryStore'
]
