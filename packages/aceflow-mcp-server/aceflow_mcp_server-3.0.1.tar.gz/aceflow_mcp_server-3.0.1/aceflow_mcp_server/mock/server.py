"""
Mock Server Management Module

Manages Prism mock servers for contract files.
"""

import subprocess
import json
import psutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console


console = Console()


class MockServer:
    """Mock server manager using Prism"""

    def __init__(self, contract_file: Path, port: int = 4010):
        """
        Initialize mock server manager.

        Args:
            contract_file: Path to OpenAPI contract file
            port: Port to run mock server on (default: 4010)
        """
        self.contract_file = contract_file
        self.port = port
        self.process = None
        self.pid_file = Path.cwd() / ".aceflow" / "mock" / f"prism_{port}.pid"

    def check_prism_installed(self) -> bool:
        """
        Check if Prism is installed.

        Returns:
            True if Prism is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["prism", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def start(self, dynamic: bool = True, validate: bool = True) -> bool:
        """
        Start mock server.

        Args:
            dynamic: Enable dynamic response generation (default: True)
            validate: Enable request/response validation (default: True)

        Returns:
            True if started successfully, False otherwise
        """
        console.print(f"\n[cyan]🚀 启动 Mock Server...[/cyan]")
        console.print(f"[dim]契约文件: {self.contract_file}[/dim]")
        console.print(f"[dim]端口: {self.port}[/dim]\n")

        # Check if Prism is installed
        if not self.check_prism_installed():
            console.print("[red]❌ Prism 未安装[/red]")
            console.print("[yellow]请安装 Prism: npm install -g @stoplight/prism-cli[/yellow]\n")
            return False

        # Check if contract file exists
        if not self.contract_file.exists():
            console.print(f"[red]❌ 契约文件不存在: {self.contract_file}[/red]\n")
            return False

        # Check if port is already in use
        if self._is_port_in_use(self.port):
            console.print(f"[yellow]⚠️  端口 {self.port} 已被占用[/yellow]")
            console.print(f"[yellow]请使用 --port 指定其他端口[/yellow]\n")
            return False

        # Build command
        cmd = [
            "prism",
            "mock",
            str(self.contract_file),
            "--port", str(self.port),
            "--host", "0.0.0.0"
        ]

        if dynamic:
            cmd.append("--dynamic")

        if validate:
            cmd.extend(["--errors"])  # Show validation errors

        try:
            # Start Prism in background as daemon process
            # Use start_new_session to detach from parent process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )

            # Save PID
            self.pid_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.pid_file, 'w') as f:
                json.dump({
                    'pid': self.process.pid,
                    'port': self.port,
                    'contract': str(self.contract_file),
                    'dynamic': dynamic,
                    'validate': validate
                }, f)

            console.print(f"[green]✅ Mock Server 已启动！[/green]")
            console.print(f"[bold]PID:[/bold] {self.process.pid}")
            console.print(f"[bold]URL:[/bold] http://localhost:{self.port}\n")

            console.print("[bold]使用示例:[/bold]")
            console.print(f"  curl http://localhost:{self.port}/api/user/login\n")

            return True

        except Exception as e:
            console.print(f"[red]❌ 启动失败: {e}[/red]\n")
            return False

    def stop(self) -> bool:
        """
        Stop mock server.

        Returns:
            True if stopped successfully, False otherwise
        """
        console.print(f"\n[cyan]⏹️  停止 Mock Server (端口 {self.port})...[/cyan]\n")

        # Read PID from file
        if not self.pid_file.exists():
            console.print(f"[yellow]⚠️  未找到 Mock Server (端口 {self.port})[/yellow]\n")
            return False

        try:
            with open(self.pid_file, 'r') as f:
                data = json.load(f)
                pid = data['pid']

            # Kill process
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=5)
                console.print(f"[green]✅ Mock Server 已停止 (PID: {pid})[/green]\n")
            except psutil.NoSuchProcess:
                console.print(f"[yellow]⚠️  进程不存在 (PID: {pid})[/yellow]\n")
            except psutil.TimeoutExpired:
                # Force kill if not terminated
                process.kill()
                console.print(f"[green]✅ Mock Server 已强制停止 (PID: {pid})[/green]\n")

            # Remove PID file
            self.pid_file.unlink()
            return True

        except Exception as e:
            console.print(f"[red]❌ 停止失败: {e}[/red]\n")
            return False

    def _is_port_in_use(self, port: int) -> bool:
        """
        Check if port is in use.

        Args:
            port: Port number

        Returns:
            True if port is in use, False otherwise
        """
        for conn in psutil.net_connections():
            if conn.laddr.port == port and conn.status == 'LISTEN':
                return True
        return False

    @staticmethod
    def list_running() -> List[Dict[str, Any]]:
        """
        List all running mock servers.

        Returns:
            List of running mock server info
        """
        mock_dir = Path.cwd() / ".aceflow" / "mock"
        if not mock_dir.exists():
            return []

        running_servers = []
        for pid_file in mock_dir.glob("prism_*.pid"):
            try:
                with open(pid_file, 'r') as f:
                    data = json.load(f)

                # Check if process is still running
                try:
                    process = psutil.Process(data['pid'])
                    if process.is_running():
                        running_servers.append(data)
                    else:
                        # Clean up stale PID file
                        pid_file.unlink()
                except psutil.NoSuchProcess:
                    # Clean up stale PID file
                    pid_file.unlink()

            except Exception:
                continue

        return running_servers

    @staticmethod
    def stop_all() -> int:
        """
        Stop all running mock servers.

        Returns:
            Number of servers stopped
        """
        console.print("\n[cyan]⏹️  停止所有 Mock Servers...[/cyan]\n")

        servers = MockServer.list_running()
        if not servers:
            console.print("[yellow]没有运行中的 Mock Server[/yellow]\n")
            return 0

        stopped = 0
        for server_info in servers:
            mock = MockServer(Path(server_info['contract']), server_info['port'])
            if mock.stop():
                stopped += 1

        console.print(f"[green]✅ 已停止 {stopped} 个 Mock Server[/green]\n")
        return stopped
