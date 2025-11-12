"""
Workflow Engine

Core orchestrator for AceFlow workflow execution.
Manages workflow initialization, execution, and transitions.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime

from ..models import WorkflowMode, Iteration, Stage, StageStatus
from .state import StateManager


class WorkflowEngine:
    """Core workflow execution engine"""

    def __init__(self, project_id: str = "default"):
        self.project_id = project_id
        self.state_manager = StateManager(project_id)
        self._mode_implementations = {}  # Will be registered by mode classes

    def initialize(self, mode: str, metadata: Optional[Dict[str, Any]] = None,
                  iteration_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Initialize a new workflow iteration

        Args:
            mode: Workflow mode ('minimal', 'standard', 'complete', 'smart')
            metadata: Optional metadata for the iteration
            iteration_id: Optional custom iteration ID

        Returns:
            Dict containing iteration information
        """
        # Convert string to enum
        workflow_mode = WorkflowMode(mode.lower())

        # Get mode implementation
        mode_impl = self._get_mode_implementation(workflow_mode)
        if not mode_impl:
            raise ValueError(f"No implementation found for mode: {mode}")

        # Initialize iteration with empty stages
        iteration = self.state_manager.initialize_iteration(workflow_mode, metadata, iteration_id)

        # Let mode implementation create its stages
        stages = mode_impl.create_stages()
        iteration.stages = stages

        # Mark first stage as in progress
        if stages:
            stages[0].status = StageStatus.IN_PROGRESS
            stages[0].start_time = datetime.now()

        # Save updated iteration
        self.state_manager._save_state()

        return {
            'iteration_id': iteration.iteration_id,
            'mode': iteration.mode.value,
            'total_stages': len(iteration.stages),
            'stages': [
                {
                    'stage_id': stage.stage_id,
                    'name': stage.name,
                    'description': stage.description
                }
                for stage in iteration.stages
            ],
            'current_stage': iteration.current_stage.to_dict() if iteration.current_stage else None,
            'status': 'initialized'
        }

    def get_status(self) -> Dict[str, Any]:
        """
        Get current workflow status

        Returns:
            Dict containing workflow status information
        """
        return self.state_manager.get_state_summary()

    def advance(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Advance to next stage

        Args:
            metadata: Optional metadata for the transition

        Returns:
            Dict containing transition result
        """
        success = self.state_manager.advance_stage(metadata)

        if success:
            current_stage = self.state_manager.get_current_stage()
            return {
                'success': True,
                'message': f'Advanced to stage: {current_stage.name}' if current_stage else 'Advanced',
                'current_stage': current_stage.to_dict() if current_stage else None
            }
        else:
            return {
                'success': False,
                'message': 'Cannot advance: already at final stage or no active iteration'
            }

    def update_progress(self, progress: float, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update current stage progress

        Args:
            progress: Progress value (0.0 to 1.0)
            metadata: Optional metadata

        Returns:
            Dict containing update result
        """
        self.state_manager.update_stage_progress(progress, metadata)

        return {
            'success': True,
            'message': f'Progress updated to {progress:.1%}',
            'current_stage': self.state_manager.get_current_stage().to_dict() if self.state_manager.get_current_stage() else None
        }

    def rollback(self) -> Dict[str, Any]:
        """
        Rollback to previous stage

        Returns:
            Dict containing rollback result
        """
        success = self.state_manager.rollback_stage()

        if success:
            current_stage = self.state_manager.get_current_stage()
            return {
                'success': True,
                'message': f'Rolled back to stage: {current_stage.name}' if current_stage else 'Rolled back',
                'current_stage': current_stage.to_dict() if current_stage else None
            }
        else:
            return {
                'success': False,
                'message': 'Cannot rollback: already at first stage or no active iteration'
            }

    def validate(self) -> Dict[str, Any]:
        """
        Validate current workflow state

        Returns:
            Dict containing validation results
        """
        return self.state_manager.validate_state()

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get transition history

        Args:
            limit: Maximum number of transitions to return

        Returns:
            List of transition records
        """
        return self.state_manager.get_transition_history(limit)

    def register_mode_implementation(self, mode: WorkflowMode, implementation):
        """
        Register a mode implementation

        Args:
            mode: WorkflowMode enum
            implementation: Mode implementation instance
        """
        self._mode_implementations[mode] = implementation

    def _get_mode_implementation(self, mode: WorkflowMode):
        """Get mode implementation"""
        return self._mode_implementations.get(mode)
