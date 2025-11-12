"""
API Path Filter

Filters OpenAPI paths based on feature configuration.
"""

import re
from typing import Dict, Any, List, Set
from rich.console import Console


console = Console()


class ContractFilter:
    """Filter OpenAPI paths based on feature configuration"""

    def __init__(self, filter_config: Dict[str, Any]):
        """
        Initialize contract filter.

        Args:
            filter_config: Filter configuration from feature
                {
                    'type': 'exact' | 'prefix' | 'regex',
                    'pattern': '/api/user'
                }
        """
        self.filter_type = filter_config.get('type', 'prefix')
        self.pattern = filter_config.get('pattern', '')

        # Compile regex pattern if needed
        self.regex_pattern = None
        if self.filter_type == 'regex':
            try:
                self.regex_pattern = re.compile(self.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern '{self.pattern}': {e}")

    def matches(self, path: str) -> bool:
        """
        Check if a path matches the filter.

        Args:
            path: API path to check

        Returns:
            True if path matches, False otherwise
        """
        if self.filter_type == 'exact':
            return path == self.pattern

        elif self.filter_type == 'prefix':
            return path.startswith(self.pattern)

        elif self.filter_type == 'regex':
            return self.regex_pattern.match(path) is not None

        else:
            raise ValueError(f"Unknown filter type: {self.filter_type}")

    def filter_paths(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter OpenAPI specification paths based on filter configuration.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            Filtered OpenAPI specification
        """
        console.print(f"\n[cyan]🔍 正在过滤接口...[/cyan]")
        console.print(f"[dim]过滤类型: {self.filter_type}[/dim]")
        console.print(f"[dim]过滤规则: {self.pattern}[/dim]\n")

        original_paths = openapi_spec.get('paths', {})
        filtered_paths = {}
        matched_count = 0

        for path, path_item in original_paths.items():
            if self.matches(path):
                filtered_paths[path] = path_item
                matched_count += 1

        # Create filtered spec
        filtered_spec = openapi_spec.copy()
        filtered_spec['paths'] = filtered_paths

        # Clean up unused components (optional, can be enhanced later)
        # For now, keep all components to avoid breaking references

        console.print(f"[green]✅ 过滤完成！[/green]")
        console.print(f"  原始接口数: [cyan]{len(original_paths)}[/cyan]")
        console.print(f"  匹配接口数: [cyan]{matched_count}[/cyan]")
        console.print(f"  过滤掉: [yellow]{len(original_paths) - matched_count}[/yellow] 个\n")

        if matched_count == 0:
            console.print("[yellow]⚠️  警告: 没有匹配的接口！请检查过滤规则。[/yellow]\n")

        return filtered_spec

    def list_matched_paths(self, openapi_spec: Dict[str, Any]) -> List[str]:
        """
        List all paths that match the filter.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            List of matched paths
        """
        paths = openapi_spec.get('paths', {})
        return [path for path in paths.keys() if self.matches(path)]

    def get_path_methods(self, openapi_spec: Dict[str, Any], path: str) -> List[str]:
        """
        Get all HTTP methods for a specific path.

        Args:
            openapi_spec: OpenAPI specification dictionary
            path: API path

        Returns:
            List of HTTP methods (e.g., ['get', 'post'])
        """
        path_item = openapi_spec.get('paths', {}).get(path, {})
        methods = []

        for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head', 'trace']:
            if method in path_item:
                methods.append(method)

        return methods

    def get_statistics(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get filtering statistics.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            Statistics dictionary with counts and details
        """
        all_paths = openapi_spec.get('paths', {})
        matched_paths = self.list_matched_paths(openapi_spec)

        # Count operations (method + path combinations)
        total_operations = 0
        matched_operations = 0

        for path, path_item in all_paths.items():
            path_ops = len(self.get_path_methods(openapi_spec, path))
            total_operations += path_ops

            if path in matched_paths:
                matched_operations += path_ops

        return {
            'total_paths': len(all_paths),
            'matched_paths': len(matched_paths),
            'filtered_paths': len(all_paths) - len(matched_paths),
            'total_operations': total_operations,
            'matched_operations': matched_operations,
            'filtered_operations': total_operations - matched_operations,
            'filter_type': self.filter_type,
            'pattern': self.pattern
        }
