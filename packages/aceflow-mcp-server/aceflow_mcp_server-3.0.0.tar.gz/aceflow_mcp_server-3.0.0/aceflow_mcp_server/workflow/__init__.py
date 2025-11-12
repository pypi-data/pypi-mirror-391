"""
AceFlow Workflow Module

Unified workflow engine for AI-driven development process management.

This module provides:
- 4 workflow modes (Minimal, Standard, Complete, Smart)
- State management with PATEOAS (Prompt as the Engine of AI State)
- Decision gates for quality control
- Stage-based execution
"""

from .core.engine import WorkflowEngine
from .core.state import StateManager
from .modes.minimal import MinimalWorkflow
from .modes.standard import StandardWorkflow
from .modes.complete import CompleteWorkflow
from .modes.smart import SmartWorkflow

__all__ = [
    'WorkflowEngine',
    'StateManager',
    'MinimalWorkflow',
    'StandardWorkflow',
    'CompleteWorkflow',
    'SmartWorkflow'
]

__version__ = '3.0.0'
