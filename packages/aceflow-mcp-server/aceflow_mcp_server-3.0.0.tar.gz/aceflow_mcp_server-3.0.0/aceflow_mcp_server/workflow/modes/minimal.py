"""
Minimal Workflow Mode

Fastest workflow for prototyping: P→D→R
Suitable for: Small features, prototypes, quick iterations
Duration: 0.5-2 days
"""

from typing import List
from datetime import datetime

from ..models import Stage, StageStatus


class MinimalWorkflow:
    """Minimal mode implementation: P→D→R"""

    def __init__(self):
        self.mode_name = "minimal"
        self.description = "Fast prototyping mode with minimal stages"
        self.estimated_duration = "0.5-2 days"

    def create_stages(self) -> List[Stage]:
        """Create stages for minimal mode"""
        return [
            Stage(
                stage_id="P",
                name="Planning",
                description="Quick requirements and design",
                tasks=[
                    "Define core functionality",
                    "Sketch basic architecture",
                    "List main tasks"
                ],
                deliverables=[
                    "Quick requirements doc",
                    "Basic design notes"
                ]
            ),
            Stage(
                stage_id="D",
                name="Development",
                description="Rapid implementation",
                tasks=[
                    "Implement core features",
                    "Basic testing",
                    "Fix critical issues"
                ],
                deliverables=[
                    "Working code",
                    "Basic tests"
                ]
            ),
            Stage(
                stage_id="R",
                name="Review",
                description="Quick review and deploy",
                tasks=[
                    "Code review",
                    "Smoke testing",
                    "Deploy/deliver"
                ],
                deliverables=[
                    "Deployed code",
                    "Release notes"
                ]
            )
        ]

    def get_next_action_prompt(self, current_stage_id: str) -> str:
        """Get prompt for next action based on current stage"""
        prompts = {
            "P": """
# Planning Stage (Minimal Mode)

**Goal**: Quickly define what needs to be built

**Actions**:
1. Define the core functionality (what does it do?)
2. Sketch basic architecture (how will it work?)
3. List main implementation tasks

**Output**:
- requirements.md (keep it simple, 1-2 pages max)
- Quick design notes

**Time Box**: 2-4 hours maximum
""",
            "D": """
# Development Stage (Minimal Mode)

**Goal**: Get it working quickly

**Actions**:
1. Implement core features (MVP only)
2. Write basic tests (happy path)
3. Fix critical bugs

**Output**:
- Working code
- Basic test coverage

**Time Box**: 4-12 hours
""",
            "R": """
# Review Stage (Minimal Mode)

**Goal**: Quick check and deploy

**Actions**:
1. Quick code review
2. Smoke testing
3. Deploy/deliver

**Output**:
- Deployed/delivered code
- Brief release notes

**Time Box**: 1-2 hours
"""
        }
        return prompts.get(current_stage_id, "Unknown stage")
