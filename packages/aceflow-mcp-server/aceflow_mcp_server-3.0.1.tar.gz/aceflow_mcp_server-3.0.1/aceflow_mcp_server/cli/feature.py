"""
CLI command: aceflow feature add/list/remove

Manage feature configurations for contract generation.
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from pathlib import Path
from typing import Optional, List

from ..contract.config import ContractConfig


console = Console()


@click.group(name='feature')
def feature_group():
    """
    Manage feature configurations for contract generation.
    """
    pass


@feature_group.command(name='add')
@click.option('--name', help='Feature name (e.g., user-management)')
@click.option('--api-filter', help='API filter pattern')
@click.option('--filter-type',
              type=click.Choice(['exact', 'prefix', 'regex']),
              help='Filter type: exact, prefix, or regex')
@click.option('--description', help='Feature description')
@click.option('--dev-team', help='Development team (e.g., "张三,李四")')
@click.option('--non-interactive', is_flag=True, help='Non-interactive mode')
def add_feature(
    name: Optional[str],
    api_filter: Optional[str],
    filter_type: Optional[str],
    description: Optional[str],
    dev_team: Optional[str],
    non_interactive: bool
):
    """
    Add a new feature configuration.

    Example:
        aceflow feature add --name user-management --api-filter "/api/user" --filter-type prefix
    """
    console.print("\n[bold cyan]📦 添加需求配置[/bold cyan]\n")

    # Load configuration
    config_path = Path.cwd() / ".aceflow" / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ 错误: 未找到配置文件[/red]")
        console.print("[yellow]请先运行: aceflow init[/yellow]\n")
        return

    config = ContractConfig(config_path)

    # Interactive mode
    if not non_interactive:
        console.print("[bold]请输入需求配置:[/bold]\n")

        name = Prompt.ask(
            "📝 需求名称 (例如: user-management)",
            default=""
        )

        if not name:
            console.print("[red]❌ 需求名称不能为空[/red]\n")
            return

        description = Prompt.ask(
            "📄 需求描述",
            default=""
        )

        console.print("\n[bold]接口过滤配置:[/bold]")
        console.print("  [cyan]exact[/cyan]  - 精确匹配路径 (例如: /api/user/login)")
        console.print("  [cyan]prefix[/cyan] - 路径前缀匹配 (例如: /api/user)")
        console.print("  [cyan]regex[/cyan]  - 正则表达式 (例如: /api/user/.*)\n")

        filter_type = Prompt.ask(
            "🔍 过滤类型",
            choices=['exact', 'prefix', 'regex'],
            default='prefix'
        )

        api_filter = Prompt.ask(
            f"🔍 API 过滤规则 ({filter_type})",
            default="/api/"
        )

        dev_team = Prompt.ask(
            "👥 开发团队 (逗号分隔)",
            default=""
        )

    # Validate required fields
    if not name:
        console.print("[red]❌ 需求名称不能为空[/red]\n")
        return

    if not api_filter:
        console.print("[red]❌ API 过滤规则不能为空[/red]\n")
        return

    if not filter_type:
        filter_type = 'prefix'  # Default

    # Check if feature already exists
    existing_features = config.get_features()
    if name in existing_features:
        if not non_interactive:
            overwrite = Confirm.ask(
                f"需求 '{name}' 已存在，是否覆盖？",
                default=False
            )
            if not overwrite:
                console.print("[yellow]操作已取消[/yellow]\n")
                return
        else:
            console.print(f"[yellow]⚠️  需求 '{name}' 已存在，将被覆盖[/yellow]")

    # Parse dev team
    team_members = []
    if dev_team:
        team_members = [m.strip() for m in dev_team.split(',') if m.strip()]

    # Create feature configuration
    feature_config = {
        'description': description or '',
        'api_filter': {
            'type': filter_type,
            'pattern': api_filter
        },
        'dev_team': team_members,
        'enabled': True
    }

    # Add feature to configuration
    config.add_feature(name, feature_config)
    config.save()

    # Success message
    console.print("\n[bold green]✅ 需求配置已添加！[/bold green]\n")
    console.print("[bold]配置摘要:[/bold]")
    console.print(f"  需求名称: [cyan]{name}[/cyan]")
    if description:
        console.print(f"  描述: {description}")
    console.print(f"  过滤类型: [cyan]{filter_type}[/cyan]")
    console.print(f"  过滤规则: [cyan]{api_filter}[/cyan]")
    if team_members:
        console.print(f"  开发团队: {', '.join(team_members)}")

    console.print("\n[bold]下一步:[/bold]")
    console.print(f"  生成契约: [cyan]aceflow contract generate --feature {name}[/cyan]")
    console.print(f"  查看需求列表: [cyan]aceflow feature list[/cyan]\n")


@feature_group.command(name='list')
def list_features():
    """
    List all feature configurations.
    """
    console.print("\n[bold cyan]📦 需求配置列表[/bold cyan]\n")

    # Load configuration
    config_path = Path.cwd() / ".aceflow" / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ 错误: 未找到配置文件[/red]")
        console.print("[yellow]请先运行: aceflow init[/yellow]\n")
        return

    config = ContractConfig(config_path)
    features = config.get_features()

    if not features:
        console.print("[yellow]暂无需求配置[/yellow]")
        console.print("\n[bold]添加需求:[/bold]")
        console.print("  [cyan]aceflow feature add[/cyan]\n")
        return

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("需求名称", style="cyan")
    table.add_column("描述")
    table.add_column("过滤类型", style="yellow")
    table.add_column("过滤规则", style="green")
    table.add_column("状态", style="magenta")

    for feature_name, feature_config in features.items():
        description = feature_config.get('description', '')
        api_filter = feature_config.get('api_filter', {})
        filter_type = api_filter.get('type', 'N/A')
        pattern = api_filter.get('pattern', 'N/A')
        enabled = feature_config.get('enabled', True)
        status = "✓ 启用" if enabled else "✗ 禁用"

        table.add_row(
            feature_name,
            description[:30] + "..." if len(description) > 30 else description,
            filter_type,
            pattern,
            status
        )

    console.print(table)
    console.print()


@feature_group.command(name='remove')
@click.argument('name')
@click.option('--yes', is_flag=True, help='Skip confirmation')
def remove_feature(name: str, yes: bool):
    """
    Remove a feature configuration.

    Example:
        aceflow feature remove user-management
    """
    console.print(f"\n[bold cyan]🗑️  删除需求配置: {name}[/bold cyan]\n")

    # Load configuration
    config_path = Path.cwd() / ".aceflow" / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ 错误: 未找到配置文件[/red]")
        console.print("[yellow]请先运行: aceflow init[/yellow]\n")
        return

    config = ContractConfig(config_path)
    features = config.get_features()

    if name not in features:
        console.print(f"[red]❌ 需求 '{name}' 不存在[/red]\n")
        return

    # Confirm deletion
    if not yes:
        confirm = Confirm.ask(
            f"确认删除需求 '{name}'？",
            default=False
        )
        if not confirm:
            console.print("[yellow]操作已取消[/yellow]\n")
            return

    # Remove feature
    config.remove_feature(name)
    config.save()

    console.print(f"[bold green]✅ 需求 '{name}' 已删除[/bold green]\n")


@feature_group.command(name='show')
@click.argument('name')
def show_feature(name: str):
    """
    Show detailed information about a feature.

    Example:
        aceflow feature show user-management
    """
    console.print(f"\n[bold cyan]📦 需求详情: {name}[/bold cyan]\n")

    # Load configuration
    config_path = Path.cwd() / ".aceflow" / "config.yaml"
    if not config_path.exists():
        console.print("[red]❌ 错误: 未找到配置文件[/red]")
        console.print("[yellow]请先运行: aceflow init[/yellow]\n")
        return

    config = ContractConfig(config_path)
    feature = config.get_feature(name)

    if not feature:
        console.print(f"[red]❌ 需求 '{name}' 不存在[/red]\n")
        return

    # Display feature details
    console.print(f"[bold]需求名称:[/bold] [cyan]{name}[/cyan]")

    description = feature.get('description', '')
    if description:
        console.print(f"[bold]描述:[/bold] {description}")

    api_filter = feature.get('api_filter', {})
    filter_type = api_filter.get('type', 'N/A')
    pattern = api_filter.get('pattern', 'N/A')
    console.print(f"[bold]过滤类型:[/bold] [yellow]{filter_type}[/yellow]")
    console.print(f"[bold]过滤规则:[/bold] [green]{pattern}[/green]")

    dev_team = feature.get('dev_team', [])
    if dev_team:
        console.print(f"[bold]开发团队:[/bold] {', '.join(dev_team)}")

    enabled = feature.get('enabled', True)
    status = "[green]✓ 启用[/green]" if enabled else "[red]✗ 禁用[/red]"
    console.print(f"[bold]状态:[/bold] {status}")

    console.print()


if __name__ == '__main__':
    feature_group()
