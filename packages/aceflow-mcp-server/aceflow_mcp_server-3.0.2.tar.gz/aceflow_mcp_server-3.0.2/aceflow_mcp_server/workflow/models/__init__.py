"""
Workflow Data Models

Defines core data structures for workflow management.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
import uuid


class WorkflowMode(Enum):
    """Workflow execution modes"""
    MINIMAL = "minimal"      # P→D→R (Fast prototyping)
    STANDARD = "standard"    # P1→P2→D1→D2→R1 (Balanced)
    COMPLETE = "complete"    # S1-S8 (Comprehensive)
    SMART = "smart"          # AI-driven adaptive mode


class StageStatus(Enum):
    """Stage execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


class IterationStatus(Enum):
    """Iteration execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Stage:
    """Represents a workflow stage"""
    stage_id: str
    name: str
    description: str
    status: StageStatus = StageStatus.PENDING
    progress: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tasks: List[str] = field(default_factory=list)
    deliverables: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'stage_id': self.stage_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'progress': self.progress,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'tasks': self.tasks,
            'deliverables': self.deliverables,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stage':
        """Create from dictionary"""
        return cls(
            stage_id=data['stage_id'],
            name=data['name'],
            description=data['description'],
            status=StageStatus(data.get('status', 'pending')),
            progress=data.get('progress', 0.0),
            start_time=datetime.fromisoformat(data['start_time']) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data['end_time']) if data.get('end_time') else None,
            tasks=data.get('tasks', []),
            deliverables=data.get('deliverables', []),
            metadata=data.get('metadata', {}),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now()
        )


@dataclass
class Iteration:
    """Represents a workflow iteration"""
    iteration_id: str = field(default_factory=lambda: f"iter_{uuid.uuid4().hex[:8]}")
    mode: WorkflowMode = WorkflowMode.SMART
    status: IterationStatus = IterationStatus.IN_PROGRESS
    stages: List[Stage] = field(default_factory=list)
    current_stage_index: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def current_stage(self) -> Optional[Stage]:
        """Get current stage"""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None

    @property
    def overall_progress(self) -> float:
        """Calculate overall progress"""
        if not self.stages:
            return 0.0
        completed = sum(1 for stage in self.stages if stage.status == StageStatus.COMPLETED)
        return completed / len(self.stages)

    def get_stage_by_id(self, stage_id: str) -> Optional['Stage']:
        """根据stage_id获取阶段"""
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'iteration_id': self.iteration_id,
            'mode': self.mode.value,
            'status': self.status.value,
            'stages': [stage.to_dict() for stage in self.stages],
            'current_stage_index': self.current_stage_index,
            'current_stage_id': self.current_stage.stage_id if self.current_stage else None,
            'overall_progress': self.overall_progress,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Iteration':
        """Create from dictionary"""
        iteration = cls(
            iteration_id=data.get('iteration_id'),
            mode=WorkflowMode(data.get('mode', 'smart')),
            status=IterationStatus(data.get('status', 'in_progress')),
            current_stage_index=data.get('current_stage_index', 0),
            created_at=datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if 'updated_at' in data else datetime.now(),
            metadata=data.get('metadata', {})
        )

        # Reconstruct stages
        for stage_data in data.get('stages', []):
            stage = Stage(
                stage_id=stage_data['stage_id'],
                name=stage_data['name'],
                description=stage_data['description'],
                status=StageStatus(stage_data.get('status', 'pending')),
                progress=stage_data.get('progress', 0.0),
                start_time=datetime.fromisoformat(stage_data['start_time']) if stage_data.get('start_time') else None,
                end_time=datetime.fromisoformat(stage_data['end_time']) if stage_data.get('end_time') else None,
                tasks=stage_data.get('tasks', []),
                deliverables=stage_data.get('deliverables', []),
                metadata=stage_data.get('metadata', {})
            )
            iteration.stages.append(stage)

        return iteration


@dataclass
class StateTransition:
    """Represents a state transition"""
    from_stage: str
    to_stage: str
    timestamp: datetime = field(default_factory=datetime.now)
    trigger: str = "manual"
    success: bool = True
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'from_stage': self.from_stage,
            'to_stage': self.to_stage,
            'timestamp': self.timestamp.isoformat(),
            'trigger': self.trigger,
            'success': self.success,
            'reasoning': self.reasoning,
            'metadata': self.metadata
        }
