"""
AceFlow Contract Management MCP Tools

Integrates contract management features with the AI workflow,
enabling Contract-First development driven by AI.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import json

from .contract.config import ContractConfig
from .contract.generator import ContractGenerator
from .contract.filter import ContractFilter
from .contract.completion import SmartCompletion
from .contract.repo import ContractRepo
from .mock.server import MockServer
from .notification.email import EmailNotifier
from .core.contract_workflow_engine import ContractFirstWorkflowEngine, WorkflowStage


class ContractWorkflowTools:
    """Contract-First workflow tools for AI-driven development."""

    def __init__(self):
        """Initialize contract workflow tools."""
        self.config = None
        self.workflow_engine = ContractFirstWorkflowEngine()

    def _load_config(self) -> Optional[ContractConfig]:
        """Load configuration from current working directory."""
        config_path = Path.cwd() / ".aceflow" / "config.yaml"
        if not config_path.exists():
            return None
        return ContractConfig(config_path)

    def aceflow_init_project(
        self,
        project_name: str,
        workflow_mode: str = "contract_first",
        openapi_url: Optional[str] = None,
        repo_url: Optional[str] = None,
        smtp_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Initialize AceFlow project with contract management.

        Combines workflow initialization with contract repository setup.

        Args:
            project_name: Project name
            workflow_mode: Workflow mode (minimal|standard|contract_first)
                - minimal: Quick prototyping (Implementation → Test → Demo)
                - standard: Standard flow (User Stories → ... → Demo)
                - contract_first: Contract-First (Define → Design → Implement → Integrate)
            openapi_url: Spring Boot OpenAPI URL (e.g., http://localhost:8080/v3/api-docs)
            repo_url: Git repository URL for contracts
            smtp_config: SMTP configuration for notifications

        Returns:
            {
                "success": True,
                "config_path": ".aceflow/config.yaml",
                "mode": "contract_first",
                "next_steps": [...]
            }
        """
        try:
            # Build aceflow init command
            cmd = [
                "aceflow", "init",
                "--project-name", project_name,
                "--non-interactive"
            ]

            if openapi_url:
                cmd.extend(["--openapi-url", openapi_url])

            if repo_url:
                cmd.extend(["--repo-url", repo_url])

            # Execute CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Load created config
            self.config = self._load_config()

            # Configure SMTP if provided
            if smtp_config and self.config:
                self.config.set_smtp_config(
                    enabled=smtp_config.get('enabled', True),
                    host=smtp_config.get('host'),
                    port=smtp_config.get('port'),
                    user=smtp_config.get('user'),
                    password=smtp_config.get('password'),
                    from_addr=smtp_config.get('from')
                )

            # Initialize workflow state
            workflow_state = self.workflow_engine.initialize_workflow(project_name, workflow_mode)

            # Update workflow context
            if openapi_url or repo_url:
                state = self.workflow_engine.get_state()
                if state:
                    if openapi_url:
                        state["context"]["openapi_url"] = openapi_url
                    if repo_url:
                        state["context"]["repo_url"] = repo_url
                    self.workflow_engine._save_state(state)

            # Mark setup checkpoints
            self.workflow_engine.update_checkpoint(WorkflowStage.SETUP, "config_file_exists", True)
            if openapi_url:
                self.workflow_engine.update_checkpoint(WorkflowStage.SETUP, "openapi_url_valid", True)
            if repo_url:
                self.workflow_engine.update_checkpoint(WorkflowStage.SETUP, "repo_url_valid", True)
            if smtp_config:
                self.workflow_engine.update_checkpoint(WorkflowStage.SETUP, "smtp_configured", True)

            next_steps = []
            if workflow_mode == "contract_first":
                next_steps = [
                    "Define your first feature using aceflow_define_feature",
                    "Design API contract using aceflow_design_api",
                    "Generate contract from Spring Boot using aceflow_contract_generate"
                ]
            else:
                next_steps = [
                    "Start your workflow using existing aceflow_stage tools",
                    "Contract tools are available for API management"
                ]

            return {
                "success": True,
                "config_path": ".aceflow/config.yaml",
                "workflow_file": ".aceflow/workflow.json",
                "mode": workflow_mode,
                "project_name": project_name,
                "openapi_url": openapi_url,
                "repo_url": repo_url,
                "workflow_initialized": True,
                "current_stage": workflow_state["current_stage"],
                "next_steps": next_steps,
                "message": f"Project '{project_name}' initialized successfully in {workflow_mode} mode"
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": "Failed to initialize project"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initialize project"
            }

    def aceflow_define_feature(
        self,
        feature_name: str,
        description: str,
        api_scope: Dict[str, str],
        requirements: List[str],
        dev_team: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Define new feature requirements and API boundary.

        Args:
            feature_name: Feature name in kebab-case (e.g., user-authentication)
            description: Feature description
            api_scope: API scope definition
                {
                    "type": "prefix|exact|regex",
                    "pattern": "/api/user/"
                }
            requirements: List of functional requirements
            dev_team: Development team email list

        Returns:
            {
                "success": True,
                "feature": "user-authentication",
                "config_updated": True,
                "next_step": "Design API contract using aceflow_design_api"
            }
        """
        try:
            # Build aceflow feature add command
            cmd = [
                "aceflow", "feature", "add",
                "--name", feature_name,
                "--api-filter", api_scope['pattern'],
                "--filter-type", api_scope['type'],
                "--description", description,
                "--non-interactive"
            ]

            if dev_team:
                cmd.extend(["--dev-team", ",".join(dev_team)])

            # Execute CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Create requirements document
            requirements_dir = Path.cwd() / "aceflow_result" / "requirements"
            requirements_dir.mkdir(parents=True, exist_ok=True)

            requirements_file = requirements_dir / f"{feature_name}.md"
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write(f"# {feature_name}\n\n")
                f.write(f"## Description\n\n{description}\n\n")
                f.write(f"## API Scope\n\n")
                f.write(f"- Type: {api_scope['type']}\n")
                f.write(f"- Pattern: `{api_scope['pattern']}`\n\n")
                f.write(f"## Requirements\n\n")
                for i, req in enumerate(requirements, 1):
                    f.write(f"{i}. {req}\n")

                if dev_team:
                    f.write(f"\n## Development Team\n\n")
                    for email in dev_team:
                        f.write(f"- {email}\n")

            return {
                "success": True,
                "feature": feature_name,
                "config_updated": True,
                "requirements_file": str(requirements_file),
                "api_scope": api_scope,
                "next_step": "Design API contract using aceflow_design_api",
                "message": f"Feature '{feature_name}' defined successfully"
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": f"Failed to define feature '{feature_name}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to define feature '{feature_name}'"
            }

    def aceflow_design_api(
        self,
        feature: str,
        endpoints: List[Dict[str, Any]],
        base_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Design API contract endpoints (AI-assisted design).

        This tool helps AI design OpenAPI contracts from scratch before implementation.

        Args:
            feature: Feature name
            endpoints: List of API endpoint definitions
                [
                    {
                        "path": "/api/auth/login",
                        "method": "POST",
                        "summary": "User login",
                        "request_body": {
                            "email": "string",
                            "password": "string",
                            "remember_me": "boolean"
                        },
                        "responses": {
                            "200": {"token": "string", "user": "object"},
                            "401": {"error": "string"}
                        }
                    }
                ]
            base_url: Base URL for the API (optional)

        Returns:
            {
                "success": True,
                "endpoints_count": 3,
                "contract_file": ".aceflow/contracts/user-auth.json",
                "preview": "... OpenAPI spec preview ..."
            }
        """
        try:
            # Build OpenAPI spec from endpoint definitions
            openapi_spec = {
                "openapi": "3.0.0",
                "info": {
                    "title": f"{feature} API",
                    "version": "1.0.0",
                    "description": f"API contract for {feature}"
                },
                "paths": {}
            }

            if base_url:
                openapi_spec["servers"] = [{"url": base_url}]

            # Convert endpoint definitions to OpenAPI paths
            for endpoint in endpoints:
                path = endpoint['path']
                method = endpoint['method'].lower()

                if path not in openapi_spec['paths']:
                    openapi_spec['paths'][path] = {}

                operation = {
                    "summary": endpoint.get('summary', ''),
                    "description": endpoint.get('description', ''),
                    "responses": {}
                }

                # Add request body
                if 'request_body' in endpoint:
                    properties = {}
                    for field, field_type in endpoint['request_body'].items():
                        properties[field] = {"type": field_type}

                    operation['requestBody'] = {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": properties
                                }
                            }
                        }
                    }

                # Add responses
                for status_code, response_schema in endpoint.get('responses', {}).items():
                    properties = {}
                    for field, field_type in response_schema.items():
                        properties[field] = {"type": field_type}

                    operation['responses'][status_code] = {
                        "description": f"Response {status_code}",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": properties
                                }
                            }
                        }
                    }

                openapi_spec['paths'][path][method] = operation

            # Apply smart completion
            config = self._load_config()
            if config and config.smart_completion_enabled:
                completion_rules = config.get_completion_rules()
                smart_completion = SmartCompletion(completion_rules, enabled=True)
                openapi_spec = smart_completion.apply_to_openapi(openapi_spec)

            # Save to contracts directory
            contracts_dir = Path.cwd() / "aceflow_result" / "contracts"
            contracts_dir.mkdir(parents=True, exist_ok=True)

            contract_file = contracts_dir / f"{feature}.json"
            with open(contract_file, 'w', encoding='utf-8') as f:
                json.dump(openapi_spec, f, indent=2, ensure_ascii=False)

            # Generate preview
            preview = json.dumps(openapi_spec, indent=2)[:500] + "..."

            return {
                "success": True,
                "endpoints_count": len(endpoints),
                "contract_file": str(contract_file),
                "preview": preview,
                "message": f"API contract designed for '{feature}' with {len(endpoints)} endpoints"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to design API contract for '{feature}'"
            }

    def aceflow_contract_generate(
        self,
        feature: str,
        apply_smart_completion: bool = True,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Generate contract from Spring Boot OpenAPI Spec.

        This is the standard workflow: Spring Boot → Generate Contract → Git Push

        Args:
            feature: Feature name
            apply_smart_completion: Apply smart completion rules
            output_format: Output format (json|yaml)

        Returns:
            {
                "success": True,
                "contract_file": ".aceflow/contracts/user-auth.json",
                "apis_count": 5,
                "examples_added": 12
            }
        """
        try:
            # Build aceflow contract generate command
            cmd = [
                "aceflow", "contract", "generate",
                "--feature", feature,
                "--format", output_format
            ]

            if not apply_smart_completion:
                cmd.append("--no-smart-completion")

            # Execute CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Parse output to extract statistics
            output = result.stdout

            # Find contract file
            contracts_dir = Path.cwd() / "aceflow_result" / "contracts"
            extension = 'yaml' if output_format == 'yaml' else 'json'
            contract_file = contracts_dir / f"{feature}.{extension}"

            # Count APIs
            apis_count = 0
            if contract_file.exists():
                if extension == 'json':
                    with open(contract_file, 'r', encoding='utf-8') as f:
                        spec = json.load(f)
                        apis_count = len(spec.get('paths', {}))

            return {
                "success": True,
                "contract_file": str(contract_file),
                "apis_count": apis_count,
                "smart_completion_applied": apply_smart_completion,
                "format": output_format,
                "message": f"Contract generated for '{feature}' with {apis_count} APIs",
                "next_step": "Push contract to Git using aceflow_contract_push"
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": f"Failed to generate contract for '{feature}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to generate contract for '{feature}'"
            }

    def aceflow_contract_push(
        self,
        feature: str,
        message: Optional[str] = None,
        notify_team: bool = True
    ) -> Dict[str, Any]:
        """
        Push contract to Git repository and notify team.

        Args:
            feature: Feature name
            message: Custom commit message
            notify_team: Send email notification to dev team

        Returns:
            {
                "success": True,
                "commit_hash": "abc1234",
                "notified": ["frontend@example.com"],
                "contract_url": "https://github.com/org/contracts/blob/main/..."
            }
        """
        try:
            # Build aceflow contract push command
            cmd = [
                "aceflow", "contract", "push",
                "--feature", feature
            ]

            if message:
                cmd.extend(["--message", message])

            # Execute CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Parse commit hash from output
            commit_hash = None
            output = result.stdout
            if '(' in output and ')' in output:
                commit_hash = output.split('(')[-1].split(')')[0]

            # Get config for notification info
            config = self._load_config()
            notified = []
            if config:
                feature_config = config.get_feature(feature)
                if feature_config and notify_team:
                    dev_team = feature_config.get('dev_team', [])
                    notified = [member for member in dev_team if '@' in member]

                repo_url = config.contract_repo_url
                contract_url = f"{repo_url}/blob/main/{config.contract_repo_base_path}/{feature}.json"
            else:
                contract_url = None

            return {
                "success": True,
                "commit_hash": commit_hash,
                "notified": notified if notify_team else [],
                "contract_url": contract_url,
                "message": f"Contract for '{feature}' pushed to Git successfully",
                "next_step": "Frontend can now pull contract and start development with Mock Server"
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": f"Failed to push contract for '{feature}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to push contract for '{feature}'"
            }

    def aceflow_contract_pull(
        self,
        feature: str,
        branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Pull contract from Git repository to local.

        Frontend developers use this to get the latest contract.

        Args:
            feature: Feature name
            branch: Git branch (default: main)

        Returns:
            {
                "success": True,
                "contract_file": ".aceflow/contracts/user-auth.json",
                "message": "Contract pulled successfully"
            }
        """
        try:
            # Build aceflow contract pull command
            cmd = [
                "aceflow", "contract", "pull",
                "--feature", feature,
                "--branch", branch
            ]

            # Execute CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Find contract file
            contracts_dir = Path.cwd() / "aceflow_result" / "contracts"
            contract_file = None
            for ext in ['.json', '.yaml', '.yml']:
                potential_file = contracts_dir / f"{feature}{ext}"
                if potential_file.exists():
                    contract_file = potential_file
                    break

            return {
                "success": True,
                "contract_file": str(contract_file) if contract_file else None,
                "message": f"Contract for '{feature}' pulled successfully from Git",
                "next_step": "Start Mock Server using aceflow_mock_start"
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": f"Failed to pull contract for '{feature}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to pull contract for '{feature}'"
            }

    def aceflow_mock_start(
        self,
        feature: str,
        port: int = 4010,
        dynamic: bool = True,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Start Mock Server for frontend development.

        Frontend developers use this to develop against the contract before backend is ready.

        Args:
            feature: Feature name
            port: Port number (default: 4010)
            dynamic: Enable dynamic response generation
            validate: Enable request/response validation

        Returns:
            {
                "success": True,
                "mock_url": "http://localhost:4010",
                "contract": "user-auth.json",
                "pid": 12345,
                "message": "Frontend can now develop against this Mock Server"
            }
        """
        try:
            # Build aceflow mock start command
            cmd = [
                "aceflow", "mock", "start",
                "--feature", feature,
                "--port", str(port)
            ]

            if not dynamic:
                cmd.append("--no-dynamic")

            if not validate:
                cmd.append("--no-validate")

            # Execute CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Find contract file
            contracts_dir = Path.cwd() / "aceflow_result" / "contracts"
            contract_file = None
            for ext in ['.json', '.yaml', '.yml']:
                potential_file = contracts_dir / f"{feature}{ext}"
                if potential_file.exists():
                    contract_file = potential_file.name
                    break

            # Try to extract PID from mock directory
            mock_dir = Path.cwd() / ".aceflow" / "mock"
            pid_file = mock_dir / f"mock_{port}.pid"
            pid = None
            if pid_file.exists():
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())

            return {
                "success": True,
                "mock_url": f"http://localhost:{port}",
                "contract": contract_file,
                "port": port,
                "pid": pid,
                "dynamic_enabled": dynamic,
                "validation_enabled": validate,
                "message": f"Mock Server started for '{feature}' at http://localhost:{port}",
                "frontend_message": "Frontend can now develop against this Mock Server"
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": f"Failed to start Mock Server for '{feature}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to start Mock Server for '{feature}'"
            }

    def aceflow_mock_stop(
        self,
        port: Optional[int] = None,
        stop_all: bool = False
    ) -> Dict[str, Any]:
        """
        Stop Mock Server.

        Args:
            port: Port number to stop (or None with stop_all=True)
            stop_all: Stop all running Mock Servers

        Returns:
            {
                "success": True,
                "stopped_ports": [4010],
                "message": "Mock Server stopped"
            }
        """
        try:
            # Build aceflow mock stop command
            if stop_all:
                cmd = ["aceflow", "mock", "stop", "--all"]
            elif port:
                cmd = ["aceflow", "mock", "stop", "--port", str(port)]
            else:
                return {
                    "success": False,
                    "error": "Must specify either port or stop_all=True",
                    "message": "Invalid parameters"
                }

            # Execute CLI command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            stopped_ports = [port] if port else []

            return {
                "success": True,
                "stopped_ports": stopped_ports,
                "message": "Mock Server stopped successfully"
            }

        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "message": "Failed to stop Mock Server"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to stop Mock Server"
            }

    def aceflow_validate_contract(
        self,
        feature: str,
        actual_openapi_url: str
    ) -> Dict[str, Any]:
        """
        Validate backend implementation against contract.

        Backend developers use this to ensure their implementation matches the contract.

        Args:
            feature: Feature name
            actual_openapi_url: URL of actual backend OpenAPI spec

        Returns:
            {
                "success": True,
                "compliant": True,
                "differences": [],
                "missing_endpoints": [],
                "extra_endpoints": []
            }
        """
        try:
            # Load contract file
            contracts_dir = Path.cwd() / "aceflow_result" / "contracts"
            contract_file = None
            for ext in ['.json', '.yaml', '.yml']:
                potential_file = contracts_dir / f"{feature}{ext}"
                if potential_file.exists():
                    contract_file = potential_file
                    break

            if not contract_file:
                return {
                    "success": False,
                    "error": f"Contract file not found for '{feature}'",
                    "message": "Contract validation failed"
                }

            # Load contract spec
            if contract_file.suffix == '.json':
                with open(contract_file, 'r', encoding='utf-8') as f:
                    contract_spec = json.load(f)
            else:
                import yaml
                with open(contract_file, 'r', encoding='utf-8') as f:
                    contract_spec = yaml.safe_load(f)

            # Fetch actual OpenAPI spec
            generator = ContractGenerator(actual_openapi_url)
            actual_spec = generator.fetch_openapi()

            # Compare specs
            contract_paths = set(contract_spec.get('paths', {}).keys())
            actual_paths = set(actual_spec.get('paths', {}).keys())

            missing_endpoints = list(contract_paths - actual_paths)
            extra_endpoints = list(actual_paths - contract_paths)
            differences = []

            # Check for differences in common endpoints
            for path in contract_paths & actual_paths:
                contract_methods = set(contract_spec['paths'][path].keys())
                actual_methods = set(actual_spec['paths'][path].keys())

                if contract_methods != actual_methods:
                    differences.append({
                        "path": path,
                        "issue": "method_mismatch",
                        "expected": list(contract_methods),
                        "actual": list(actual_methods)
                    })

            compliant = len(missing_endpoints) == 0 and len(extra_endpoints) == 0 and len(differences) == 0

            return {
                "success": True,
                "compliant": compliant,
                "differences": differences,
                "missing_endpoints": missing_endpoints,
                "extra_endpoints": extra_endpoints,
                "message": "Contract validation completed" if compliant else "Contract violations detected"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to validate contract"
            }

    # ==================== Workflow State Management ====================

    def aceflow_workflow_status(self) -> Dict[str, Any]:
        """
        Get current workflow status and progress.

        Returns:
            {
                "success": True,
                "current_stage": "design",
                "overall_progress": 30,
                "completed_stages": 3,
                "total_stages": 10,
                "features": {...},
                "recommendations": [...]
            }
        """
        try:
            # Get workflow state
            state = self.workflow_engine.get_state()

            if not state:
                return {
                    "success": False,
                    "error": "Workflow not initialized",
                    "message": "Please initialize workflow using aceflow_init_project"
                }

            # Get progress
            progress = self.workflow_engine.get_progress()

            # Get recommendations
            recommendations = self.workflow_engine.get_recommendations()

            return {
                "success": True,
                "current_stage": state["current_stage"],
                "workflow_mode": state["workflow_mode"],
                "overall_progress": progress["overall_progress"],
                "completed_stages": progress["completed_stages"],
                "total_stages": progress["total_stages"],
                "features": state.get("features", {}),
                "metrics": state.get("metrics", {}),
                "recommendations": recommendations,
                "message": f"Currently at {state['current_stage']} stage ({progress['overall_progress']}% complete)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get workflow status"
            }

    def aceflow_workflow_advance(
        self,
        next_stage: str,
        feature_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Advance workflow to the next stage.

        Args:
            next_stage: Target stage name (setup/define/design/implement/contract_push/
                       frontend_dev/validate/integration/review/completed)
            feature_name: Optional feature name for tracking

        Returns:
            {
                "success": True,
                "previous_stage": "design",
                "current_stage": "implement",
                "message": "Advanced to implement stage"
            }
        """
        try:
            # Convert string to enum
            try:
                target_stage = WorkflowStage(next_stage)
            except ValueError:
                valid_stages = [s.value for s in WorkflowStage]
                return {
                    "success": False,
                    "error": f"Invalid stage: {next_stage}",
                    "message": f"Valid stages: {valid_stages}"
                }

            # Advance stage
            result = self.workflow_engine.advance_stage(target_stage, feature_name)

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to advance workflow"
            }

    def aceflow_workflow_checkpoint(
        self,
        stage: str,
        checkpoint: str,
        value: bool
    ) -> Dict[str, Any]:
        """
        Update a checkpoint for a workflow stage.

        Used to mark stage completion criteria as met/unmet.

        Args:
            stage: Stage name
            checkpoint: Checkpoint name (e.g., "config_file_exists", "contract_compliant")
            value: Checkpoint value (True/False)

        Returns:
            {
                "success": True,
                "stage": "design",
                "checkpoint": "contract_file_exists",
                "value": True
            }
        """
        try:
            # Convert string to enum
            try:
                stage_enum = WorkflowStage(stage)
            except ValueError:
                valid_stages = [s.value for s in WorkflowStage]
                return {
                    "success": False,
                    "error": f"Invalid stage: {stage}",
                    "message": f"Valid stages: {valid_stages}"
                }

            # Update checkpoint
            result = self.workflow_engine.update_checkpoint(stage_enum, checkpoint, value)

            return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update checkpoint"
            }

    def aceflow_workflow_recommendations(self) -> Dict[str, Any]:
        """
        Get intelligent recommendations for next actions.

        Based on current workflow state, provides context-aware suggestions
        for what to do next.

        Returns:
            {
                "success": True,
                "recommendations": [
                    {
                        "priority": "high",
                        "action": "Push contract to Git",
                        "tool": "aceflow_contract_push",
                        "benefits": [...]
                    }
                ]
            }
        """
        try:
            recommendations = self.workflow_engine.get_recommendations()

            return {
                "success": True,
                "count": len(recommendations),
                "recommendations": recommendations,
                "message": f"Found {len(recommendations)} recommendation(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get recommendations"
            }
