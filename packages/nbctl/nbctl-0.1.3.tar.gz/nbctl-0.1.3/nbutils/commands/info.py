"""
Info command - Show statistics and imports about a notebook
"""
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from nbutils.core.notebook import Notebook

console = Console()

@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--code-metrics', is_flag=True, help='Show only code metrics')
@click.option('--imports', 'show_imports', is_flag=True, help='Show only imports')
def info(notebook, code_metrics, show_imports):
    """Show statistics and imports about a notebook"""
    try:
        nb_path = Path(notebook)
        nb = Notebook(nb_path)
        
        show_all = not (code_metrics or show_imports)
        
        console.print(f"\n[bold blue]Loading:[/bold blue] {nb_path.name}")
        
        if show_all or (not code_metrics and not show_imports):
            stats = nb.get_stats()
            table = Table(title=f"Statistics for {nb_path.name}", show_header=True, header_style="bold magenta")
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Value", style="green", justify="right")
            table.add_row("Total Cells", str(stats['total_cells']))
            table.add_row("Code Cells", str(stats['code_cells']))
            table.add_row("Markdown Cells", str(stats['markdown_cells']))
            table.add_row("Raw Cells", str(stats['raw_cells']))
            table.add_row("File Size", f"{stats['file_size']:,} bytes")
            console.print("\n")
            console.print(table)
        
        if code_metrics or show_all:
            metrics = nb.get_code_metrics()
            console.print(f"\n[bold magenta]Code Metrics:[/bold magenta]")
            console.print(f" - Total lines of code: [green]{metrics['total_lines']}[/green]")
            console.print(f" - Average lines per cell: [green]{metrics['avg_lines_per_cell']:.1f}[/green]")
            
            if metrics['largest_cell']['index'] is not None:
                console.print(f" - Largest cell: [yellow]{metrics['largest_cell']['lines']} lines[/yellow] (Cell {metrics['largest_cell']['index']})")
            
            if metrics['smallest_cell']['index'] is not None:
                console.print(f" - Smallest cell: [cyan]{metrics['smallest_cell']['lines']} lines[/cyan] (Cell {metrics['smallest_cell']['index']})")
            
            if metrics['empty_cells'] > 0:
                console.print(f" - Empty code cells: [yellow]{metrics['empty_cells']}[/yellow]")
        
        if show_imports or show_all:
            import_list = nb.get_imports()
            console.print(f"\n[bold magenta]Imports:[/bold magenta]")
            if import_list:
                for import_stmt in import_list:
                    console.print(f"  [dim]-[/dim] [green]{import_stmt}[/green]")
            else:
                console.print(f"  [dim]No imports found[/dim]")
        
        console.print()
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()