"""
OpenAPI Contract Generator

Fetches OpenAPI specification from backend service.
"""

import requests
from typing import Dict, Any, Optional
from rich.console import Console


console = Console()


class ContractGenerator:
    """OpenAPI contract generator"""

    def __init__(self, openapi_url: str):
        """
        Initialize contract generator.

        Args:
            openapi_url: OpenAPI specification URL (e.g., http://localhost:8080/v3/api-docs)
        """
        self.openapi_url = openapi_url

    def fetch_openapi(self, timeout: int = 30) -> Dict[str, Any]:
        """
        Fetch OpenAPI specification from backend service.

        Args:
            timeout: Request timeout in seconds

        Returns:
            OpenAPI specification as dictionary

        Raises:
            requests.RequestException: If request fails
            ValueError: If response is not valid JSON
        """
        console.print(f"\n[cyan]📥 正在获取 OpenAPI 规范...[/cyan]")
        console.print(f"[dim]URL: {self.openapi_url}[/dim]\n")

        try:
            response = requests.get(
                self.openapi_url,
                timeout=timeout,
                headers={
                    'Accept': 'application/json',
                    'User-Agent': 'AceFlow-Contract-Manager/2.2.0'
                }
            )
            response.raise_for_status()

            openapi_spec = response.json()

            # Validate basic OpenAPI structure
            if 'openapi' not in openapi_spec and 'swagger' not in openapi_spec:
                raise ValueError("Invalid OpenAPI specification: missing 'openapi' or 'swagger' field")

            if 'paths' not in openapi_spec:
                raise ValueError("Invalid OpenAPI specification: missing 'paths' field")

            # Display summary
            version = openapi_spec.get('openapi') or openapi_spec.get('swagger')
            info = openapi_spec.get('info', {})
            title = info.get('title', 'Unknown')
            api_version = info.get('version', 'Unknown')
            paths_count = len(openapi_spec.get('paths', {}))

            console.print(f"[green]✅ 获取成功！[/green]\n")
            console.print(f"[bold]API 信息:[/bold]")
            console.print(f"  标题: [cyan]{title}[/cyan]")
            console.print(f"  版本: [cyan]{api_version}[/cyan]")
            console.print(f"  OpenAPI: [cyan]{version}[/cyan]")
            console.print(f"  接口数量: [cyan]{paths_count}[/cyan] 个\n")

            return openapi_spec

        except requests.Timeout:
            console.print(f"[red]❌ 请求超时（{timeout}秒）[/red]\n")
            raise

        except requests.ConnectionError as e:
            console.print(f"[red]❌ 连接失败: {e}[/red]\n")
            raise

        except requests.HTTPError as e:
            console.print(f"[red]❌ HTTP 错误: {e}[/red]\n")
            raise

        except ValueError as e:
            console.print(f"[red]❌ {e}[/red]\n")
            raise

        except Exception as e:
            console.print(f"[red]❌ 未知错误: {e}[/red]\n")
            raise

    def save_to_file(self, openapi_spec: Dict[str, Any], output_path: str) -> None:
        """
        Save OpenAPI specification to file.

        Args:
            openapi_spec: OpenAPI specification dictionary
            output_path: Output file path (supports .json and .yaml/.yml)
        """
        import json
        import yaml
        from pathlib import Path

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if output_file.suffix in ['.yaml', '.yml']:
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(openapi_spec, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            console.print(f"[green]✅ 已保存到: {output_path} (YAML)[/green]\n")
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(openapi_spec, f, ensure_ascii=False, indent=2)
            console.print(f"[green]✅ 已保存到: {output_path} (JSON)[/green]\n")

    def get_all_paths(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get all paths from OpenAPI specification.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            Dictionary of all paths
        """
        return openapi_spec.get('paths', {})

    def get_path_count(self, openapi_spec: Dict[str, Any]) -> int:
        """
        Get total number of paths.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            Number of paths
        """
        return len(self.get_all_paths(openapi_spec))
