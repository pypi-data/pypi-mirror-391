"""
Smart Completion for OpenAPI Examples

Automatically adds example values to schema properties based on naming patterns.
"""

import re
from typing import Dict, Any, List, Optional
from rich.console import Console


console = Console()


class SmartCompletion:
    """Smart completion for OpenAPI schema examples"""

    def __init__(self, rules: List[Dict[str, str]], enabled: bool = True):
        """
        Initialize smart completion.

        Args:
            rules: List of completion rules, each with 'pattern' and 'example'
                [
                    {'pattern': '.*[Dd]ate$', 'example': '2025-01-01'},
                    {'pattern': '.*[Uu]uid$', 'example': '550e8400-e29b-41d4-a716-446655440000'}
                ]
            enabled: Whether smart completion is enabled
        """
        self.enabled = enabled
        self.rules = []

        # Compile regex patterns
        for rule in rules:
            pattern = rule.get('pattern', '')
            example = rule.get('example', '')
            try:
                compiled_pattern = re.compile(pattern)
                self.rules.append({
                    'pattern': compiled_pattern,
                    'example': example,
                    'pattern_str': pattern
                })
            except re.error as e:
                console.print(f"[yellow]⚠️  跳过无效的正则规则 '{pattern}': {e}[/yellow]")

    def get_example_for_property(self, property_name: str, schema: Dict[str, Any]) -> Optional[str]:
        """
        Get example value for a property based on rules.

        Args:
            property_name: Property name
            schema: Property schema

        Returns:
            Example value if rule matches, None otherwise
        """
        if not self.enabled:
            return None

        # Skip if example already exists
        if 'example' in schema:
            return None

        # Try to match rules
        for rule in self.rules:
            if rule['pattern'].match(property_name):
                return rule['example']

        return None

    def apply_to_schema(self, schema: Dict[str, Any], path: str = '') -> int:
        """
        Apply smart completion to a schema recursively.

        Args:
            schema: OpenAPI schema object
            path: Current path for debugging (optional)

        Returns:
            Number of examples added
        """
        if not self.enabled:
            return 0

        added_count = 0

        # Handle object properties
        if schema.get('type') == 'object' and 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                # Add example for this property
                example = self.get_example_for_property(prop_name, prop_schema)
                if example is not None:
                    prop_schema['example'] = example
                    added_count += 1

                # Recursively process nested schemas
                added_count += self.apply_to_schema(prop_schema, f"{path}.{prop_name}")

        # Handle array items
        elif schema.get('type') == 'array' and 'items' in schema:
            added_count += self.apply_to_schema(schema['items'], f"{path}[]")

        # Handle allOf, anyOf, oneOf
        for key in ['allOf', 'anyOf', 'oneOf']:
            if key in schema:
                for i, sub_schema in enumerate(schema[key]):
                    added_count += self.apply_to_schema(sub_schema, f"{path}.{key}[{i}]")

        return added_count

    def apply_to_openapi(self, openapi_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply smart completion to entire OpenAPI specification.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            OpenAPI specification with examples added
        """
        if not self.enabled:
            console.print("[dim]智能补全已禁用[/dim]\n")
            return openapi_spec

        console.print("\n[cyan]🤖 正在应用智能补全...[/cyan]")
        console.print(f"[dim]规则数量: {len(self.rules)}[/dim]\n")

        total_added = 0

        # Apply to request bodies and responses in paths
        paths = openapi_spec.get('paths', {})
        for path, path_item in paths.items():
            for method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                if method not in path_item:
                    continue

                operation = path_item[method]

                # Apply to request body
                if 'requestBody' in operation:
                    content = operation['requestBody'].get('content', {})
                    for media_type, media_schema in content.items():
                        if 'schema' in media_schema:
                            total_added += self.apply_to_schema(
                                media_schema['schema'],
                                f"{path}.{method}.requestBody.{media_type}"
                            )

                # Apply to responses
                if 'responses' in operation:
                    for status_code, response in operation['responses'].items():
                        content = response.get('content', {})
                        for media_type, media_schema in content.items():
                            if 'schema' in media_schema:
                                total_added += self.apply_to_schema(
                                    media_schema['schema'],
                                    f"{path}.{method}.responses.{status_code}.{media_type}"
                                )

                # Apply to parameters
                if 'parameters' in operation:
                    for param in operation['parameters']:
                        if 'schema' in param:
                            example = self.get_example_for_property(param.get('name', ''), param['schema'])
                            if example is not None:
                                param['schema']['example'] = example
                                total_added += 1

        # Apply to components/schemas
        components = openapi_spec.get('components', {})
        if 'schemas' in components:
            for schema_name, schema in components['schemas'].items():
                total_added += self.apply_to_schema(schema, f"components.schemas.{schema_name}")

        if total_added > 0:
            console.print(f"[green]✅ 智能补全完成！[/green]")
            console.print(f"  添加示例: [cyan]{total_added}[/cyan] 个\n")
        else:
            console.print(f"[dim]未添加示例（可能已存在或无匹配规则）[/dim]\n")

        return openapi_spec

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get smart completion statistics.

        Returns:
            Statistics dictionary
        """
        return {
            'enabled': self.enabled,
            'rules_count': len(self.rules),
            'rules': [
                {
                    'pattern': rule['pattern_str'],
                    'example': rule['example']
                }
                for rule in self.rules
            ]
        }
