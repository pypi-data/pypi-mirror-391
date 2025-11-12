"""
Contract-First Workflow State Machine

Manages workflow stages, transitions, validations, and recommendations
for AI-driven Contract-First development.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from enum import Enum
from datetime import datetime
import json


class WorkflowStage(Enum):
    """Contract-First workflow stages"""

    SETUP = "setup"
    DEFINE = "define"
    DESIGN = "design"
    IMPLEMENT = "implement"
    CONTRACT_PUSH = "contract_push"
    FRONTEND_DEV = "frontend_dev"
    VALIDATE = "validate"
    INTEGRATION = "integration"
    REVIEW = "review"
    COMPLETED = "completed"


class StageStatus(Enum):
    """Stage status"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    SKIPPED = "skipped"


class ContractFirstWorkflowEngine:
    """
    Contract-First Workflow State Machine

    Manages the complete lifecycle of Contract-First development:
    - State tracking and persistence
    - Stage transitions with validation
    - Quality gates and checkpoints
    - Automated recommendations
    """

    def __init__(self, working_directory: Optional[Path] = None):
        """Initialize workflow engine"""
        self.working_directory = working_directory or Path.cwd()
        self.workflow_file = self.working_directory / ".aceflow" / "workflow.json"
        self.config_file = self.working_directory / ".aceflow" / "config.yaml"

        # Quality gates for each stage
        self.quality_gates = {
            "setup": {
                "required": ["config_file_exists", "openapi_url_valid", "repo_url_valid"],
                "optional": ["smtp_configured"]
            },
            "define": {
                "required": ["feature_config_exists", "api_scope_defined", "requirements_documented"]
            },
            "design": {
                "required": ["contract_file_exists", "valid_openapi_spec", "has_endpoints"],
                "optional": ["smart_completion_applied", "examples_provided"]
            },
            "contract_push": {
                "required": ["git_commit_successful", "git_push_successful"],
                "optional": ["team_notified"]
            },
            "validate": {
                "required": ["contract_compliant", "no_missing_endpoints", "no_extra_endpoints"]
            },
            "integration": {
                "required": ["e2e_tests_passing", "no_critical_bugs"],
                "optional": ["performance_acceptable"]
            }
        }

        # Stage transition rules
        self.transitions = {
            WorkflowStage.SETUP: [WorkflowStage.DEFINE],
            WorkflowStage.DEFINE: [WorkflowStage.DESIGN],
            WorkflowStage.DESIGN: [WorkflowStage.IMPLEMENT, WorkflowStage.CONTRACT_PUSH],
            WorkflowStage.IMPLEMENT: [WorkflowStage.CONTRACT_PUSH],
            WorkflowStage.CONTRACT_PUSH: [WorkflowStage.FRONTEND_DEV, WorkflowStage.VALIDATE],
            WorkflowStage.FRONTEND_DEV: [WorkflowStage.INTEGRATION],
            WorkflowStage.VALIDATE: [WorkflowStage.INTEGRATION],
            WorkflowStage.INTEGRATION: [WorkflowStage.REVIEW],
            WorkflowStage.REVIEW: [WorkflowStage.COMPLETED]
        }

    def initialize_workflow(self, project_name: str, workflow_mode: str = "contract_first") -> Dict[str, Any]:
        """
        Initialize a new workflow state file

        Args:
            project_name: Project name
            workflow_mode: Workflow mode (contract_first/standard/minimal)

        Returns:
            Initialized workflow state
        """
        now = datetime.utcnow().isoformat() + "Z"

        workflow_state = {
            "version": "1.0.0",
            "workflow_mode": workflow_mode,
            "current_stage": WorkflowStage.SETUP.value,
            "created_at": now,
            "updated_at": now,

            "stages": {
                stage.value: {
                    "status": StageStatus.PENDING.value if stage != WorkflowStage.SETUP else StageStatus.IN_PROGRESS.value,
                    "started_at": now if stage == WorkflowStage.SETUP else None,
                    "completed_at": None,
                    "duration_minutes": None,
                    "checkpoints": {},
                    "outputs": []
                }
                for stage in WorkflowStage
            },

            "features": {},

            "metrics": {
                "total_features": 0,
                "completed_features": 0,
                "in_progress_features": 0,
                "total_contracts": 0,
                "total_apis": 0,
                "mock_servers_running": 0
            },

            "context": {
                "project_name": project_name,
                "openapi_url": None,
                "repo_url": None,
                "team_size": 0,
                "last_recommendation": None
            }
        }

        # Create .aceflow directory if needed
        self.workflow_file.parent.mkdir(parents=True, exist_ok=True)

        # Save to file
        self._save_state(workflow_state)

        return workflow_state

    def get_state(self) -> Optional[Dict[str, Any]]:
        """
        Load current workflow state

        Returns:
            Workflow state dict or None if not initialized
        """
        if not self.workflow_file.exists():
            return None

        with open(self.workflow_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_state(self, state: Dict[str, Any]) -> None:
        """Save workflow state to file"""
        state["updated_at"] = datetime.utcnow().isoformat() + "Z"

        with open(self.workflow_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)

    def get_current_stage(self) -> Optional[WorkflowStage]:
        """Get current workflow stage"""
        state = self.get_state()
        if not state:
            return None

        stage_str = state.get("current_stage")
        return WorkflowStage(stage_str) if stage_str else None

    def advance_stage(self, next_stage: WorkflowStage, feature_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Advance to the next stage

        Args:
            next_stage: Target stage to advance to
            feature_name: Optional feature name for per-feature tracking

        Returns:
            Result dict with success status and details
        """
        state = self.get_state()
        if not state:
            return {
                "success": False,
                "error": "Workflow not initialized",
                "message": "Please initialize workflow first using aceflow_init_project"
            }

        current_stage = WorkflowStage(state["current_stage"])

        # Validate transition
        allowed_transitions = self.transitions.get(current_stage, [])
        if next_stage not in allowed_transitions:
            return {
                "success": False,
                "error": f"Invalid transition from {current_stage.value} to {next_stage.value}",
                "message": f"Allowed transitions: {[s.value for s in allowed_transitions]}",
                "current_stage": current_stage.value
            }

        # Validate current stage completion
        validation = self.validate_stage(current_stage, state)
        if not validation["can_proceed"]:
            return {
                "success": False,
                "error": "Current stage not ready for transition",
                "message": "Please complete required checkpoints first",
                "validation": validation,
                "current_stage": current_stage.value
            }

        # Update current stage to completed
        now = datetime.utcnow().isoformat() + "Z"
        state["stages"][current_stage.value]["status"] = StageStatus.COMPLETED.value
        state["stages"][current_stage.value]["completed_at"] = now

        # Calculate duration
        started_at = state["stages"][current_stage.value].get("started_at")
        if started_at:
            duration = (datetime.fromisoformat(now.rstrip('Z')) -
                       datetime.fromisoformat(started_at.rstrip('Z')))
            state["stages"][current_stage.value]["duration_minutes"] = int(duration.total_seconds() / 60)

        # Start next stage
        state["current_stage"] = next_stage.value
        state["stages"][next_stage.value]["status"] = StageStatus.IN_PROGRESS.value
        state["stages"][next_stage.value]["started_at"] = now

        # Update feature status if specified
        if feature_name and feature_name in state["features"]:
            state["features"][feature_name]["status"] = next_stage.value

        self._save_state(state)

        return {
            "success": True,
            "previous_stage": current_stage.value,
            "current_stage": next_stage.value,
            "message": f"Advanced from {current_stage.value} to {next_stage.value}",
            "started_at": now
        }

    def validate_stage(self, stage: WorkflowStage, state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Validate stage completion

        Args:
            stage: Stage to validate
            state: Optional workflow state (loads from file if not provided)

        Returns:
            Validation result
        """
        if state is None:
            state = self.get_state()
            if not state:
                return {
                    "can_proceed": False,
                    "error": "Workflow not initialized"
                }

        gates = self.quality_gates.get(stage.value, {})
        stage_data = state["stages"].get(stage.value, {})
        checkpoints = stage_data.get("checkpoints", {})

        results = {
            "stage": stage.value,
            "required_passed": [],
            "required_failed": [],
            "optional_passed": [],
            "optional_failed": [],
            "can_proceed": False
        }

        # Check required checkpoints
        for check in gates.get("required", []):
            if checkpoints.get(check, False):
                results["required_passed"].append(check)
            else:
                results["required_failed"].append(check)

        # Check optional checkpoints
        for check in gates.get("optional", []):
            if checkpoints.get(check, False):
                results["optional_passed"].append(check)
            else:
                results["optional_failed"].append(check)

        # Can proceed if all required checkpoints pass
        results["can_proceed"] = len(results["required_failed"]) == 0

        return results

    def update_checkpoint(self, stage: WorkflowStage, checkpoint: str, value: bool) -> Dict[str, Any]:
        """
        Update a checkpoint value

        Args:
            stage: Stage to update
            checkpoint: Checkpoint name
            value: Checkpoint value (True/False)

        Returns:
            Update result
        """
        state = self.get_state()
        if not state:
            return {
                "success": False,
                "error": "Workflow not initialized"
            }

        if stage.value not in state["stages"]:
            return {
                "success": False,
                "error": f"Invalid stage: {stage.value}"
            }

        # Update checkpoint
        if "checkpoints" not in state["stages"][stage.value]:
            state["stages"][stage.value]["checkpoints"] = {}

        state["stages"][stage.value]["checkpoints"][checkpoint] = value

        self._save_state(state)

        return {
            "success": True,
            "stage": stage.value,
            "checkpoint": checkpoint,
            "value": value,
            "message": f"Checkpoint '{checkpoint}' set to {value} for stage '{stage.value}'"
        }

    def add_feature(self, feature_name: str, feature_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add a new feature to tracking

        Args:
            feature_name: Feature name
            feature_data: Feature metadata

        Returns:
            Result dict
        """
        state = self.get_state()
        if not state:
            return {
                "success": False,
                "error": "Workflow not initialized"
            }

        now = datetime.utcnow().isoformat() + "Z"

        state["features"][feature_name] = {
            "status": WorkflowStage.DEFINE.value,
            "created_at": now,
            "contract_file": None,
            "git_commits": [],
            "mock_server": {
                "running": False,
                "port": None,
                "pid": None
            },
            "validation": {
                "last_validated": None,
                "compliant": None
            },
            **feature_data
        }

        # Update metrics
        state["metrics"]["total_features"] += 1
        state["metrics"]["in_progress_features"] += 1

        self._save_state(state)

        return {
            "success": True,
            "feature": feature_name,
            "message": f"Feature '{feature_name}' added to workflow tracking"
        }

    def update_feature(self, feature_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update feature metadata

        Args:
            feature_name: Feature name
            updates: Updates to apply

        Returns:
            Result dict
        """
        state = self.get_state()
        if not state:
            return {
                "success": False,
                "error": "Workflow not initialized"
            }

        if feature_name not in state["features"]:
            return {
                "success": False,
                "error": f"Feature '{feature_name}' not found"
            }

        # Apply updates
        for key, value in updates.items():
            if isinstance(value, dict) and key in state["features"][feature_name]:
                # Merge dict updates
                state["features"][feature_name][key].update(value)
            else:
                state["features"][feature_name][key] = value

        self._save_state(state)

        return {
            "success": True,
            "feature": feature_name,
            "updates": updates,
            "message": f"Feature '{feature_name}' updated"
        }

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get recommended next actions based on current state

        Returns:
            List of recommendations
        """
        state = self.get_state()
        if not state:
            return [{
                "priority": "critical",
                "action": "Initialize workflow",
                "tool": "aceflow_init_project",
                "message": "Workflow not initialized. Please run aceflow_init_project first."
            }]

        current_stage = WorkflowStage(state["current_stage"])
        context = state.get("context", {})
        recommendations = []

        # Stage-specific recommendations
        if current_stage == WorkflowStage.SETUP:
            if not state.get("features"):
                recommendations.append({
                    "priority": "high",
                    "action": "Define your first feature",
                    "tool": "aceflow_define_feature",
                    "message": "Start by defining what features you want to build",
                    "params_example": {
                        "feature_name": "user-authentication",
                        "description": "User login and registration",
                        "api_scope": {"type": "prefix", "pattern": "/api/auth/"}
                    }
                })

        elif current_stage == WorkflowStage.DEFINE:
            recommendations.append({
                "priority": "high",
                "action": "Design API contract",
                "tool": "aceflow_design_api",
                "alternatives": [
                    {
                        "description": "AI-assisted design from scratch (recommended for new features)",
                        "tool": "aceflow_design_api"
                    },
                    {
                        "description": "Generate from existing backend (requires implemented backend)",
                        "tool": "aceflow_contract_generate"
                    }
                ]
            })

        elif current_stage == WorkflowStage.DESIGN:
            recommendations.append({
                "priority": "high",
                "action": "Push contract to Git and notify team",
                "tool": "aceflow_contract_push",
                "benefits": [
                    "Notify frontend team",
                    "Enable parallel development",
                    "Version control for contracts"
                ]
            })

        elif current_stage == WorkflowStage.CONTRACT_PUSH:
            # Backend recommendation
            recommendations.append({
                "priority": "high",
                "audience": "backend",
                "action": "Implement backend APIs",
                "message": "Write Spring Boot controllers and add OpenAPI annotations"
            })

            # Frontend recommendation
            recommendations.append({
                "priority": "high",
                "audience": "frontend",
                "action": "Start frontend development with Mock Server",
                "tools": ["aceflow_contract_pull", "aceflow_mock_start"],
                "message": "Pull contract and start Mock Server to develop without waiting for backend"
            })

        elif current_stage == WorkflowStage.VALIDATE:
            # Check validation results
            for feature_name, feature_data in state.get("features", {}).items():
                validation = feature_data.get("validation", {})
                if not validation.get("compliant"):
                    recommendations.append({
                        "priority": "critical",
                        "feature": feature_name,
                        "action": "Fix contract violations",
                        "message": f"Contract validation failed for '{feature_name}'. Please fix implementation."
                    })

        elif current_stage == WorkflowStage.INTEGRATION:
            # Check for running mock servers
            mock_count = state["metrics"].get("mock_servers_running", 0)
            if mock_count > 0:
                recommendations.append({
                    "priority": "medium",
                    "action": "Stop Mock Servers and switch to real backend",
                    "tool": "aceflow_mock_stop",
                    "message": "Stop mock servers before integration testing"
                })

        # Context-based recommendations
        if state["metrics"].get("mock_servers_running", 0) > 0:
            # Check if mock has been running for a while
            for feature_name, feature_data in state.get("features", {}).items():
                mock = feature_data.get("mock_server", {})
                if mock.get("running"):
                    recommendations.append({
                        "priority": "low",
                        "feature": feature_name,
                        "action": "Consider switching to real backend",
                        "message": f"Mock Server for '{feature_name}' is running. Backend might be ready for integration."
                    })

        return recommendations

    def get_progress(self) -> Dict[str, Any]:
        """
        Get overall workflow progress

        Returns:
            Progress information
        """
        state = self.get_state()
        if not state:
            return {
                "overall_progress": 0,
                "current_stage": None,
                "message": "Workflow not initialized"
            }

        stages = list(WorkflowStage)
        completed_count = sum(
            1 for stage in stages
            if state["stages"][stage.value]["status"] == StageStatus.COMPLETED.value
        )

        overall_progress = int((completed_count / len(stages)) * 100)

        return {
            "overall_progress": overall_progress,
            "current_stage": state["current_stage"],
            "completed_stages": completed_count,
            "total_stages": len(stages),
            "features": state.get("metrics", {}).get("total_features", 0),
            "in_progress_features": state.get("metrics", {}).get("in_progress_features", 0),
            "completed_features": state.get("metrics", {}).get("completed_features", 0)
        }

    def reset_workflow(self) -> Dict[str, Any]:
        """
        Reset workflow to initial state

        Returns:
            Reset result
        """
        state = self.get_state()
        if not state:
            return {
                "success": False,
                "error": "Workflow not initialized"
            }

        project_name = state.get("context", {}).get("project_name", "Unknown")
        workflow_mode = state.get("workflow_mode", "contract_first")

        # Re-initialize
        new_state = self.initialize_workflow(project_name, workflow_mode)

        return {
            "success": True,
            "message": "Workflow reset to initial state",
            "current_stage": new_state["current_stage"]
        }
