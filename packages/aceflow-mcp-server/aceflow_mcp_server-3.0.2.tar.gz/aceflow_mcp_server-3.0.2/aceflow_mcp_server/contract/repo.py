"""
Contract Repository Management

Manages contract repository operations (clone, commit, push).
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from rich.console import Console


console = Console()


class ContractRepo:
    """Contract repository manager"""

    def __init__(self, repo_url: str, local_path: Optional[Path] = None):
        """
        Initialize contract repository manager.

        Args:
            repo_url: Git repository URL (e.g., git@github.com:org/contracts.git)
            local_path: Local path for repository (default: .aceflow/repo)
        """
        self.repo_url = repo_url
        self.local_path = local_path or (Path.cwd() / ".aceflow" / "repo")

    def is_cloned(self) -> bool:
        """
        Check if repository is already cloned.

        Returns:
            True if repository exists and is a git repository
        """
        git_dir = self.local_path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def clone(self, branch: str = "main") -> None:
        """
        Clone contract repository.

        Args:
            branch: Branch to checkout (default: main)

        Raises:
            subprocess.CalledProcessError: If git clone fails
        """
        console.print(f"\n[cyan]📦 克隆契约仓库...[/cyan]")
        console.print(f"[dim]URL: {self.repo_url}[/dim]")
        console.print(f"[dim]分支: {branch}[/dim]\n")

        try:
            # Remove existing directory if it exists and is not a git repo
            if self.local_path.exists() and not self.is_cloned():
                console.print("[yellow]⚠️  目录已存在但不是 Git 仓库，正在清理...[/yellow]")
                shutil.rmtree(self.local_path)

            if self.is_cloned():
                console.print("[yellow]仓库已存在，跳过克隆[/yellow]\n")
                return

            # Create parent directory
            self.local_path.parent.mkdir(parents=True, exist_ok=True)

            # Clone repository
            result = subprocess.run(
                ["git", "clone", "-b", branch, self.repo_url, str(self.local_path)],
                capture_output=True,
                text=True,
                check=True
            )

            console.print(f"[green]✅ 克隆成功！[/green]\n")

        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ 克隆失败: {e.stderr}[/red]\n")
            raise

    def pull(self, branch: str = "main") -> None:
        """
        Pull latest changes from remote.

        Args:
            branch: Branch to pull

        Raises:
            subprocess.CalledProcessError: If git pull fails
        """
        console.print(f"\n[cyan]⬇️  拉取最新变更...[/cyan]")

        if not self.is_cloned():
            console.print("[yellow]仓库未克隆，正在克隆...[/yellow]")
            self.clone(branch)
            return

        try:
            result = subprocess.run(
                ["git", "-C", str(self.local_path), "pull", "origin", branch],
                capture_output=True,
                text=True,
                check=True
            )

            console.print(f"[green]✅ 拉取成功！[/green]\n")

        except subprocess.CalledProcessError as e:
            console.print(f"[red]❌ 拉取失败: {e.stderr}[/red]\n")
            raise

    def copy_contract(self, contract_file: Path, target_path: str) -> Path:
        """
        Copy contract file to repository.

        Args:
            contract_file: Source contract file path
            target_path: Target path in repository (e.g., "contracts/active/user-api.json")

        Returns:
            Path to copied file in repository
        """
        target_file = self.local_path / target_path
        target_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(contract_file, target_file)
        console.print(f"[dim]已复制: {contract_file.name} -> {target_path}[/dim]")

        return target_file

    def git_add(self, file_path: str) -> None:
        """
        Stage file for commit.

        Args:
            file_path: File path relative to repository root
        """
        subprocess.run(
            ["git", "-C", str(self.local_path), "add", file_path],
            capture_output=True,
            text=True,
            check=True
        )

    def git_commit(self, message: str, author: Optional[str] = None) -> str:
        """
        Commit staged changes.

        Args:
            message: Commit message
            author: Optional author name and email (e.g., "Name <email@example.com>")

        Returns:
            Commit hash

        Raises:
            subprocess.CalledProcessError: If git commit fails
        """
        cmd = ["git", "-C", str(self.local_path), "commit", "-m", message]

        if author:
            cmd.extend(["--author", author])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )

        # Get commit hash
        hash_result = subprocess.run(
            ["git", "-C", str(self.local_path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )

        return hash_result.stdout.strip()[:7]

    def git_push(self, branch: str = "main") -> None:
        """
        Push commits to remote.

        Args:
            branch: Branch to push to

        Raises:
            subprocess.CalledProcessError: If git push fails
        """
        subprocess.run(
            ["git", "-C", str(self.local_path), "push", "origin", branch],
            capture_output=True,
            text=True,
            check=True
        )

    def has_changes(self) -> bool:
        """
        Check if there are uncommitted changes.

        Returns:
            True if there are changes to commit
        """
        if not self.is_cloned():
            return False

        result = subprocess.run(
            ["git", "-C", str(self.local_path), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )

        return bool(result.stdout.strip())

    def get_status(self) -> List[str]:
        """
        Get git status output.

        Returns:
            List of status lines
        """
        if not self.is_cloned():
            return ["Repository not cloned"]

        result = subprocess.run(
            ["git", "-C", str(self.local_path), "status", "--short"],
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout.strip().split('\n') if result.stdout.strip() else []

    def push_contract(
        self,
        contract_file: Path,
        feature_name: str,
        base_path: str = "contracts/active",
        branch: str = "main",
        commit_message: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Push contract file to repository (clone/pull -> copy -> commit -> push).

        Args:
            contract_file: Contract file to push
            feature_name: Feature name
            base_path: Base path in repository
            branch: Git branch
            commit_message: Custom commit message

        Returns:
            Tuple of (success, message)
        """
        try:
            # Step 1: Clone or pull
            if not self.is_cloned():
                self.clone(branch)
            else:
                self.pull(branch)

            # Step 2: Copy contract file
            target_path = f"{base_path}/{contract_file.name}"
            self.copy_contract(contract_file, target_path)

            # Step 3: Check if there are changes
            if not self.has_changes():
                return True, "契约文件未变更，无需提交"

            # Step 4: Stage changes
            console.print(f"\n[cyan]📝 提交变更...[/cyan]")
            self.git_add(target_path)

            # Step 5: Commit
            if not commit_message:
                commit_message = f"feat: update contract for {feature_name}\n\nGenerated by AceFlow"

            commit_hash = self.git_commit(commit_message)
            console.print(f"[green]✅ 已提交: {commit_hash}[/green]")

            # Step 6: Push
            console.print(f"\n[cyan]⬆️  推送到远程仓库...[/cyan]")
            self.git_push(branch)
            console.print(f"[green]✅ 推送成功！[/green]\n")

            return True, f"契约已推送到仓库 ({commit_hash})"

        except subprocess.CalledProcessError as e:
            error_msg = f"Git 操作失败: {e.stderr if e.stderr else str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]\n")
            return False, error_msg

        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            console.print(f"[red]❌ {error_msg}[/red]\n")
            return False, error_msg
