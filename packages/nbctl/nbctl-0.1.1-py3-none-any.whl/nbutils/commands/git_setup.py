"""
Git setup command - Configure git for notebooks
"""
from pathlib import Path
import click
from rich.console import Console
import subprocess

console = Console()

@click.command()
def git_setup():
    """Setup git for notebooks"""
    try:
        # create .gitattributes file
        gitattributes_path = Path(".gitattributes")
        if not gitattributes_path.exists():
            with open(".gitattributes", "w") as f:
                f.write("*.ipynb diff=jupyternotebook merge=jupyternotebook\n")
            console.print("[bold green].gitattributes file created[/bold green]")
        else:
            console.print("[yellow].gitattributes already exists — skipped[/yellow]")

        # create .gitignore file
        gitignore_path = Path(".gitignore")
        default_gitignore_content = [
            ".ipynb_checkpoints/",
            "__pycache__/",
            ".DS_Store",
            "*.pyc",
            "*.pyo",
            ".env",
            ".venv",
        ]
        if not gitignore_path.exists():
            with open(".gitignore", "w") as f:
                for line in default_gitignore_content:
                    f.write(f"{line}\n")
            console.print("[bold green].gitignore file created[/bold green]")
        else:
             console.print("[yellow].gitignore already exists — skipped[/yellow]")

        # Configure git diff and merge drivers for notebooks
        try:
            # Configure diff driver to use nbutils diff
            subprocess.run([
                "git", "config", "--local", 
                "diff.jupyternotebook.command", 
                "nbutils diff"
            ], check=True, capture_output=True)
            
            # Configure merge driver to use nbutils merge
            subprocess.run([
                "git", "config", "--local",
                "merge.jupyternotebook.driver",
                "nbutils merge %O %A %B -o %A"
            ], check=True, capture_output=True)
            
            console.print("[bold green] Configured git to use nbutils for notebook diff/merge[/bold green]")
            
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow] Could not configure git drivers: {e}[/yellow]")

        console.print("\n[bold green] Git setup complete![/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()