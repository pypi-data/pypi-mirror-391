"""
CLI command: aceflow mock

Manage Mock Servers for contract files.
"""

import click
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional

from ..mock.server import MockServer
from ..contract.config import ContractConfig


console = Console()


@click.group(name='mock')
def mock_group():
    """
    Manage Mock Servers for contract development.
    """
    pass


@mock_group.command(name='start')
@click.option('--feature', required=True, help='Feature name to start mock server for')
@click.option('--port', default=4010, help='Port to run mock server on (default: 4010)')
@click.option('--no-dynamic', is_flag=True, help='Disable dynamic response generation')
@click.option('--no-validate', is_flag=True, help='Disable request/response validation')
def start_mock(feature: str, port: int, no_dynamic: bool, no_validate: bool):
    """
    Start Mock Server for a feature.

    Example:
        aceflow mock start --feature user-management
        aceflow mock start --feature user-management --port 4011
    """
    console.print("\n[bold cyan]🚀 启动 Mock Server[/bold cyan]\n")

    # Find contract file
    contracts_dir = Path.cwd() / "aceflow_result" / "contracts"
    contract_file = None

    for ext in ['.json', '.yaml', '.yml']:
        potential_file = contracts_dir / f"{feature}{ext}"
        if potential_file.exists():
            contract_file = potential_file
            break

    if not contract_file:
        console.print(f"[red]❌ 错误: 契约文件不存在: {feature}[/red]")
        console.print(f"[yellow]请先生成: aceflow contract generate --feature {feature}[/yellow]\n")
        return

    # Start mock server
    mock = MockServer(contract_file, port)
    success = mock.start(dynamic=not no_dynamic, validate=not no_validate)

    if not success:
        raise click.Abort()


@mock_group.command(name='stop')
@click.option('--port', type=int, help='Port of mock server to stop')
@click.option('--all', 'stop_all', is_flag=True, help='Stop all running mock servers')
def stop_mock(port: Optional[int], stop_all: bool):
    """
    Stop Mock Server(s).

    Example:
        aceflow mock stop --port 4010
        aceflow mock stop --all
    """
    if stop_all:
        MockServer.stop_all()
    elif port:
        # Find contract file from PID file
        pid_file = Path.cwd() / ".aceflow" / "mock" / f"prism_{port}.pid"
        if not pid_file.exists():
            console.print(f"[red]❌ 错误: 未找到端口 {port} 的 Mock Server[/red]\n")
            return

        import json
        with open(pid_file, 'r') as f:
            data = json.load(f)

        mock = MockServer(Path(data['contract']), port)
        if not mock.stop():
            raise click.Abort()
    else:
        console.print("[red]❌ 错误: 请指定 --port 或 --all[/red]\n")
        raise click.Abort()


@mock_group.command(name='list')
def list_mocks():
    """
    List all running Mock Servers.

    Example:
        aceflow mock list
    """
    console.print("\n[bold cyan]📋 运行中的 Mock Servers[/bold cyan]\n")

    servers = MockServer.list_running()

    if not servers:
        console.print("[yellow]暂无运行中的 Mock Server[/yellow]")
        console.print("\n[bold]启动 Mock Server:[/bold]")
        console.print("  [cyan]aceflow mock start --feature <name>[/cyan]\n")
        return

    # Create table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("PID", style="yellow")
    table.add_column("端口", style="cyan")
    table.add_column("契约文件", style="green")
    table.add_column("动态响应", style="magenta")
    table.add_column("验证", style="magenta")

    for server in servers:
        contract_name = Path(server['contract']).stem
        dynamic = "✓" if server.get('dynamic', True) else "✗"
        validate = "✓" if server.get('validate', True) else "✗"

        table.add_row(
            str(server['pid']),
            str(server['port']),
            contract_name,
            dynamic,
            validate
        )

    console.print(table)
    console.print()

    # Display usage info
    console.print("[bold]访问 Mock Server:[/bold]")
    for server in servers:
        console.print(f"  http://localhost:{server['port']}")
    console.print()


@mock_group.command(name='logs')
@click.option('--port', required=True, type=int, help='Port of mock server')
def show_logs(port: int):
    """
    Show Mock Server logs (placeholder).

    Example:
        aceflow mock logs --port 4010
    """
    console.print(f"\n[yellow]⚠️  日志功能尚未实现[/yellow]")
    console.print(f"[dim]您可以手动查看 Prism 输出[/dim]\n")


if __name__ == '__main__':
    mock_group()
