"""AceFlow MCP Server implementation using FastMCP framework."""

import click
from fastmcp import FastMCP
from typing import Dict, Any, Optional

# Create global FastMCP instance
mcp = FastMCP("AceFlow")

# Initialize components (import after mcp creation to avoid circular imports)
def get_tools():
    from .tools import AceFlowTools
    return AceFlowTools()

def get_contract_tools():
    from .contract_tools import ContractWorkflowTools
    return ContractWorkflowTools()

def get_resources():
    from .resources import AceFlowResources
    return AceFlowResources()

def get_prompts():
    from .prompts import AceFlowPrompts
    return AceFlowPrompts()

# Register tools with decorators
@mcp.tool
def aceflow_init(
    mode: str,
    project_name: Optional[str] = None,
    directory: Optional[str] = None
) -> Dict[str, Any]:
    """Initialize AceFlow project with specified mode."""
    tools = get_tools()
    return tools.aceflow_init(mode, project_name, directory)

@mcp.tool
def aceflow_stage(
    action: str,
    stage: Optional[str] = None
) -> Dict[str, Any]:
    """Manage project stages and workflow."""
    tools = get_tools()
    return tools.aceflow_stage(action, stage)

@mcp.tool
def aceflow_validate(
    mode: str = "basic",
    fix: bool = False,
    report: bool = False
) -> Dict[str, Any]:
    """Validate project compliance and quality."""
    tools = get_tools()
    return tools.aceflow_validate(mode, fix, report)

@mcp.tool
def aceflow_template(
    action: str,
    template: Optional[str] = None
) -> Dict[str, Any]:
    """Manage workflow templates."""
    tools = get_tools()
    return tools.aceflow_template(action, template)

# Contract Workflow Tools
@mcp.tool
def aceflow_init_project(
    project_name: str,
    workflow_mode: str = "contract_first",
    openapi_url: Optional[str] = None,
    repo_url: Optional[str] = None,
    smtp_config: Optional[Dict] = None
) -> Dict[str, Any]:
    """Initialize AceFlow project with contract management."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_init_project(
        project_name, workflow_mode, openapi_url, repo_url, smtp_config
    )

@mcp.tool
def aceflow_define_feature(
    feature_name: str,
    description: str,
    api_scope: Dict[str, str],
    requirements: list,
    dev_team: Optional[list] = None
) -> Dict[str, Any]:
    """Define new feature requirements and API boundary."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_define_feature(
        feature_name, description, api_scope, requirements, dev_team
    )

@mcp.tool
def aceflow_design_api(
    feature: str,
    endpoints: list,
    base_url: Optional[str] = None
) -> Dict[str, Any]:
    """Design API contract endpoints (AI-assisted design)."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_design_api(feature, endpoints, base_url)

@mcp.tool
def aceflow_contract_generate(
    feature: str,
    apply_smart_completion: bool = True,
    output_format: str = "json"
) -> Dict[str, Any]:
    """Generate contract from Spring Boot OpenAPI Spec."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_contract_generate(
        feature, apply_smart_completion, output_format
    )

@mcp.tool
def aceflow_contract_push(
    feature: str,
    message: Optional[str] = None,
    notify_team: bool = True
) -> Dict[str, Any]:
    """Push contract to Git repository and notify team."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_contract_push(feature, message, notify_team)

@mcp.tool
def aceflow_contract_pull(
    feature: str,
    branch: str = "main"
) -> Dict[str, Any]:
    """Pull contract from Git repository to local."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_contract_pull(feature, branch)

@mcp.tool
def aceflow_mock_start(
    feature: str,
    port: int = 4010,
    dynamic: bool = True,
    validate: bool = True
) -> Dict[str, Any]:
    """Start Mock Server for frontend development."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_mock_start(feature, port, dynamic, validate)

@mcp.tool
def aceflow_mock_stop(
    port: Optional[int] = None,
    stop_all: bool = False
) -> Dict[str, Any]:
    """Stop Mock Server."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_mock_stop(port, stop_all)

@mcp.tool
def aceflow_validate_contract(
    feature: str,
    actual_openapi_url: str
) -> Dict[str, Any]:
    """Validate backend implementation against contract."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_validate_contract(feature, actual_openapi_url)

# Workflow State Management Tools
@mcp.tool
def aceflow_workflow_status() -> Dict[str, Any]:
    """Get current workflow status and progress."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_workflow_status()

@mcp.tool
def aceflow_workflow_advance(
    next_stage: str,
    feature_name: Optional[str] = None
) -> Dict[str, Any]:
    """Advance workflow to the next stage."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_workflow_advance(next_stage, feature_name)

@mcp.tool
def aceflow_workflow_checkpoint(
    stage: str,
    checkpoint: str,
    value: bool
) -> Dict[str, Any]:
    """Update a checkpoint for a workflow stage."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_workflow_checkpoint(stage, checkpoint, value)

@mcp.tool
def aceflow_workflow_recommendations() -> Dict[str, Any]:
    """Get intelligent recommendations for next actions."""
    contract_tools = get_contract_tools()
    return contract_tools.aceflow_workflow_recommendations()

# Register resources with decorators
@mcp.resource("aceflow://project/state/{project_id}")
def project_state(project_id: str = "current") -> str:
    """Get current project state."""
    resources = get_resources()
    return resources.project_state(project_id)

@mcp.resource("aceflow://workflow/config/{config_id}")
def workflow_config(config_id: str = "default") -> str:
    """Get workflow configuration."""
    resources = get_resources()
    return resources.workflow_config(config_id)

@mcp.resource("aceflow://stage/guide/{stage}")
def stage_guide(stage: str) -> str:
    """Get stage-specific guidance."""
    resources = get_resources()
    return resources.stage_guide(stage)

# Register prompts with decorators
@mcp.prompt
def workflow_assistant(
    task: Optional[str] = None,
    context: Optional[str] = None
) -> str:
    """Generate workflow assistance prompt."""
    prompts = get_prompts()
    return prompts.workflow_assistant(task, context)

@mcp.prompt
def stage_guide_prompt(stage: str) -> str:
    """Generate stage-specific guidance prompt."""
    prompts = get_prompts()
    return prompts.stage_guide(stage)


class AceFlowMCPServer:
    """Main AceFlow MCP Server class."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.mcp = mcp
    
    def run(self, host: str = "localhost", port: int = 8000, log_level: str = "INFO"):
        """Start the MCP server."""
        self.mcp.run(host=host, port=port, log_level=log_level)


@click.command()
@click.option('--host', default=None, help='Host to bind to (for HTTP mode)')
@click.option('--port', default=None, type=int, help='Port to bind to (for HTTP mode)')
@click.option('--transport', default='stdio', help='Transport mode: stdio, sse, or streamable-http')
@click.option('--log-level', default='INFO', help='Log level')
@click.version_option(version="1.0.3")
def main(host: str, port: int, transport: str, log_level: str):
    """Start AceFlow MCP Server."""
    import os
    import logging
    
    # Set up logging
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    
    # For stdio mode, run directly with FastMCP
    if transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        # For HTTP modes, use host and port
        if host and port:
            mcp.run(transport=transport, host=host, port=port)
        else:
            mcp.run(transport=transport)


if __name__ == "__main__":
    main()