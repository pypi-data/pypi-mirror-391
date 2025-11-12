"""
Main CLI entry point for AceFlow contract management commands.
"""

import click
from rich.console import Console

from .init import init
from .feature import feature_group
from .contract import contract_group
from .mock import mock_group


console = Console()


@click.group()
@click.version_option(version='2.2.0', prog_name='aceflow')
def cli():
    """
    AceFlow - AI Programming Assistant with Contract Management

    前后端协作的契约管理工具
    """
    pass


# Register commands
cli.add_command(init)
cli.add_command(feature_group)
cli.add_command(contract_group)
cli.add_command(mock_group)


def main():
    """Main entry point"""
    cli()


if __name__ == '__main__':
    main()
