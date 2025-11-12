"""
Memory Models - 记忆数据模型

定义工作流记忆系统的核心数据结构
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path


class MemoryType(Enum):
    """记忆类型"""
    STAGE_OUTPUT = "stage_output"       # 阶段输出
    DECISION = "decision"               # 决策记录
    ISSUE = "issue"                     # 问题记录
    LEARNING = "learning"               # 经验教训
    CONTEXT = "context"                 # 上下文信息
    GATE_RESULT = "gate_result"         # 质量门结果


class MemoryPriority(Enum):
    """记忆优先级"""
    CRITICAL = "critical"   # 关键信息 (必须保留)
    HIGH = "high"          # 高优先级
    MEDIUM = "medium"      # 中等优先级
    LOW = "low"            # 低优先级


@dataclass
class Memory:
    """记忆对象"""
    # 基本信息
    memory_id: str                      # 记忆ID
    type: MemoryType                    # 记忆类型
    content: str                        # 记忆内容
    priority: MemoryPriority = MemoryPriority.MEDIUM  # 优先级

    # 上下文
    iteration_id: Optional[str] = None  # 迭代ID
    stage_id: Optional[str] = None      # 阶段ID
    mode: Optional[str] = None          # 工作流模式

    # 元数据
    tags: List[str] = field(default_factory=list)  # 标签
    metadata: Dict[str, Any] = field(default_factory=dict)  # 元数据

    # 时间戳
    created_at: datetime = field(default_factory=datetime.now)
    accessed_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0

    def access(self):
        """标记访问"""
        self.accessed_at = datetime.now()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'memory_id': self.memory_id,
            'type': self.type.value,
            'content': self.content,
            'priority': self.priority.value,
            'iteration_id': self.iteration_id,
            'stage_id': self.stage_id,
            'mode': self.mode,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'access_count': self.access_count
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """从字典创建"""
        return cls(
            memory_id=data['memory_id'],
            type=MemoryType(data['type']),
            content=data['content'],
            priority=MemoryPriority(data.get('priority', 'medium')),
            iteration_id=data.get('iteration_id'),
            stage_id=data.get('stage_id'),
            mode=data.get('mode'),
            tags=data.get('tags', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']),
            accessed_at=datetime.fromisoformat(data.get('accessed_at', data['created_at'])),
            access_count=data.get('access_count', 0)
        )


@dataclass
class MemoryQuery:
    """记忆查询条件"""
    # 类型过滤
    types: Optional[List[MemoryType]] = None

    # 上下文过滤
    iteration_id: Optional[str] = None
    stage_id: Optional[str] = None
    mode: Optional[str] = None

    # 标签过滤
    tags: Optional[List[str]] = None

    # 优先级过滤
    min_priority: Optional[MemoryPriority] = None

    # 文本搜索
    search_text: Optional[str] = None

    # 时间过滤
    since: Optional[datetime] = None
    until: Optional[datetime] = None

    # 排序和限制
    sort_by: str = "accessed_at"  # created_at, accessed_at, access_count, priority
    sort_desc: bool = True
    limit: Optional[int] = None

    def matches(self, memory: Memory) -> bool:
        """检查记忆是否匹配查询条件"""
        # 类型过滤
        if self.types and memory.type not in self.types:
            return False

        # 上下文过滤
        if self.iteration_id and memory.iteration_id != self.iteration_id:
            return False

        if self.stage_id and memory.stage_id != self.stage_id:
            return False

        if self.mode and memory.mode != self.mode:
            return False

        # 标签过滤 (任意匹配)
        if self.tags:
            if not any(tag in memory.tags for tag in self.tags):
                return False

        # 优先级过滤
        if self.min_priority:
            priority_order = {
                MemoryPriority.LOW: 0,
                MemoryPriority.MEDIUM: 1,
                MemoryPriority.HIGH: 2,
                MemoryPriority.CRITICAL: 3
            }
            if priority_order[memory.priority] < priority_order[self.min_priority]:
                return False

        # 文本搜索 (简单包含搜索)
        if self.search_text:
            search_lower = self.search_text.lower()
            if search_lower not in memory.content.lower():
                # 也检查标签
                if not any(search_lower in tag.lower() for tag in memory.tags):
                    return False

        # 时间过滤
        if self.since and memory.created_at < self.since:
            return False

        if self.until and memory.created_at > self.until:
            return False

        return True
