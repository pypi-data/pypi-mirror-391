"""
Unified State Manager

Manages workflow state with persistence, caching, and validation.
Consolidates features from both state_manager.py and optimized_state_manager.py
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import OrderedDict
import threading

from ..models import Iteration, Stage, StageStatus, StateTransition, WorkflowMode


class StateManager:
    """Unified state management for workflow"""

    def __init__(self, project_id: str = "default", state_dir: Optional[Path] = None):
        self.project_id = project_id
        self.current_iteration: Optional[Iteration] = None
        self.transition_history: List[StateTransition] = []

        # State storage
        self.state_dir = state_dir or Path.home() / ".aceflow" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / f"{project_id}_state.json"

        # Cache for performance
        self._cache = {}
        self._lock = threading.RLock()

        # Load existing state
        self._load_state()

    def initialize_iteration(self, mode: WorkflowMode, metadata: Optional[Dict[str, Any]] = None,
                           iteration_id: Optional[str] = None) -> Iteration:
        """Initialize a new workflow iteration"""
        with self._lock:
            # 创建迭代，允许自定义 iteration_id
            iter_kwargs = {
                "mode": mode,
                "metadata": metadata or {}
            }
            if iteration_id:
                iter_kwargs["iteration_id"] = iteration_id

            iteration = Iteration(**iter_kwargs)

            # Create stages based on mode (will be populated by mode-specific classes)
            self.current_iteration = iteration

            # Record initialization
            self.transition_history.append(StateTransition(
                from_stage="none",
                to_stage="initialized",
                trigger="initialize_iteration",
                reasoning=f"Initialized {mode.value} mode iteration"
            ))

            self._save_state()
            self._invalidate_cache()

            return iteration

    def get_current_iteration(self) -> Optional[Iteration]:
        """Get current iteration"""
        return self.current_iteration

    def get_current_stage(self) -> Optional[Stage]:
        """Get current stage"""
        if self.current_iteration:
            return self.current_iteration.current_stage
        return None

    def advance_stage(self, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Advance to next stage"""
        with self._lock:
            if not self.current_iteration:
                return False

            current_stage = self.current_iteration.current_stage
            if not current_stage:
                return False

            # Mark current stage as completed
            current_stage.status = StageStatus.COMPLETED
            current_stage.progress = 1.0
            current_stage.end_time = datetime.now()

            # Move to next stage
            next_index = self.current_iteration.current_stage_index + 1
            if next_index < len(self.current_iteration.stages):
                self.current_iteration.current_stage_index = next_index
                next_stage = self.current_iteration.stages[next_index]
                next_stage.status = StageStatus.IN_PROGRESS
                next_stage.start_time = datetime.now()

                # Record transition
                self.transition_history.append(StateTransition(
                    from_stage=current_stage.stage_id,
                    to_stage=next_stage.stage_id,
                    trigger="advance_stage",
                    reasoning=f"Advanced from {current_stage.name} to {next_stage.name}",
                    metadata=metadata or {}
                ))

                self.current_iteration.updated_at = datetime.now()
                self._save_state()
                self._invalidate_cache()
                return True

            return False

    def update_stage_progress(self, progress: float, metadata: Optional[Dict[str, Any]] = None):
        """Update current stage progress"""
        with self._lock:
            if self.current_iteration and self.current_iteration.current_stage:
                self.current_iteration.current_stage.progress = max(0.0, min(1.0, progress))
                if metadata:
                    self.current_iteration.current_stage.metadata.update(metadata)
                self.current_iteration.updated_at = datetime.now()
                self._save_state()
                self._invalidate_cache()

    def get_state_summary(self) -> Dict[str, Any]:
        """Get state summary"""
        cache_key = 'state_summary'

        # Check cache
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        if not self.current_iteration:
            summary = {
                'status': 'no_iteration',
                'message': 'No active iteration'
            }
        else:
            current_stage = self.current_iteration.current_stage
            summary = {
                'status': 'active',
                'iteration_id': self.current_iteration.iteration_id,
                'mode': self.current_iteration.mode.value,
                'current_stage': {
                    'stage_id': current_stage.stage_id if current_stage else None,
                    'name': current_stage.name if current_stage else None,
                    'status': current_stage.status.value if current_stage else None,
                    'progress': current_stage.progress if current_stage else 0.0
                } if current_stage else None,
                'overall_progress': self.current_iteration.overall_progress,
                'total_stages': len(self.current_iteration.stages),
                'completed_stages': sum(1 for s in self.current_iteration.stages if s.status == StageStatus.COMPLETED),
                'created_at': self.current_iteration.created_at.isoformat(),
                'updated_at': self.current_iteration.updated_at.isoformat()
            }

        # Cache the summary
        self._put_to_cache(cache_key, summary)
        return summary

    def get_transition_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get transition history"""
        return [t.to_dict() for t in self.transition_history[-limit:]]

    def validate_state(self) -> Dict[str, Any]:
        """Validate current state"""
        errors = []
        warnings = []

        if not self.current_iteration:
            errors.append("No active iteration")
        else:
            if not self.current_iteration.stages:
                errors.append("Iteration has no stages")

            current_stage = self.current_iteration.current_stage
            if current_stage:
                if not (0 <= current_stage.progress <= 1):
                    errors.append(f"Invalid progress value: {current_stage.progress}")

                if current_stage.status == StageStatus.COMPLETED and current_stage.progress < 1.0:
                    warnings.append(f"Stage {current_stage.name} marked as completed but progress < 100%")

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def rollback_stage(self) -> bool:
        """Rollback to previous stage"""
        with self._lock:
            if not self.current_iteration or self.current_iteration.current_stage_index <= 0:
                return False

            current_stage = self.current_iteration.current_stage
            prev_index = self.current_iteration.current_stage_index - 1
            prev_stage = self.current_iteration.stages[prev_index]

            # Update statuses
            if current_stage:
                current_stage.status = StageStatus.PENDING
                current_stage.progress = 0.0

            prev_stage.status = StageStatus.IN_PROGRESS

            # Update index
            self.current_iteration.current_stage_index = prev_index

            # Record transition
            self.transition_history.append(StateTransition(
                from_stage=current_stage.stage_id if current_stage else "unknown",
                to_stage=prev_stage.stage_id,
                trigger="rollback",
                reasoning=f"Rolled back from {current_stage.name if current_stage else 'unknown'} to {prev_stage.name}"
            ))

            self.current_iteration.updated_at = datetime.now()
            self._save_state()
            self._invalidate_cache()
            return True

    def _load_state(self):
        """Load state from file"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if 'current_iteration' in data and data['current_iteration']:
                    self.current_iteration = Iteration.from_dict(data['current_iteration'])

                # Load transition history
                for transition_data in data.get('transition_history', []):
                    self.transition_history.append(StateTransition(
                        from_stage=transition_data['from_stage'],
                        to_stage=transition_data['to_stage'],
                        timestamp=datetime.fromisoformat(transition_data['timestamp']),
                        trigger=transition_data.get('trigger', 'manual'),
                        success=transition_data.get('success', True),
                        reasoning=transition_data.get('reasoning', ''),
                        metadata=transition_data.get('metadata', {})
                    ))

            except Exception as e:
                print(f"Warning: Failed to load state: {e}")

    def _save_state(self):
        """Save state to file"""
        try:
            data = {
                'project_id': self.project_id,
                'current_iteration': self.current_iteration.to_dict() if self.current_iteration else None,
                'transition_history': [t.to_dict() for t in self.transition_history],
                'last_saved': datetime.now().isoformat()
            }

            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Warning: Failed to save state: {e}")

    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            return self._cache.get(key)

    def _put_to_cache(self, key: str, value: Any):
        """Put value to cache"""
        with self._lock:
            self._cache[key] = value

    def _invalidate_cache(self):
        """Invalidate all cache"""
        with self._lock:
            self._cache.clear()
