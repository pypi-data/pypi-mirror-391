"""
nbctl - A comprehensive, modern CLI toolkit that solves all major Jupyter notebook pain points in one unified interface.
Main CLI entry point
"""
import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="0.1.2")
def cli():
    """nbctl - The Swiss Army Knife for Jupyter Notebooks"""
    pass


# Import commands
from nbutils.commands.clean import clean
from nbutils.commands.info import info
from nbutils.commands.export import export
from nbutils.commands.extract import extract
from nbutils.commands.ml_split import ml_split
from nbutils.commands.run import run
from nbutils.commands.lint import lint
from nbutils.commands.format import format
from nbutils.commands.git_setup import git_setup
from nbutils.commands.diff import diff
from nbutils.commands.combine import combine
from nbutils.commands.resolve import resolve
from nbutils.commands.security import security

cli.add_command(clean)
cli.add_command(info)
cli.add_command(export)
cli.add_command(extract)
cli.add_command(ml_split)
cli.add_command(run)
cli.add_command(lint)
cli.add_command(format)
cli.add_command(git_setup)
cli.add_command(diff)
cli.add_command(combine)
cli.add_command(resolve)
cli.add_command(security)

if __name__ == "__main__":
    cli()