"""
Combine command - Combine/concatenate two notebooks
"""
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table

from nbutils.core.merger import NotebookMerger

console = Console()


@click.command()
@click.argument('notebook1', type=click.Path(exists=True))
@click.argument('notebook2', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(), required=True,
              help='Output file for combined notebook')
@click.option('--strategy', type=click.Choice(['append', 'first', 'second']),
              default='append', help='Combine strategy')
@click.option('--report', is_flag=True, help='Show detailed report')
def combine(notebook1, notebook2, output, strategy, report):
    """Combine two notebooks into one
    
    Simple utility to concatenate or combine two notebooks.
    NO conflict detection - for that use 'nbutils resolve'.
    
    \b
    Strategies:
      append - Append all cells from both notebooks (default, safest)
      first  - Keep only the first notebook
      second - Keep only the second notebook
    
    \b
    Examples:
      # Concatenate two notebooks
      nbutils combine nb1.ipynb nb2.ipynb -o combined.ipynb
      
      # Just keep the first notebook (copy)
      nbutils combine nb1.ipynb nb2.ipynb -o output.ipynb --strategy first
    
    \b
    Note: This is NOT a true merge! For Git conflicts with proper conflict
    detection, use 'nbutils resolve' with a common ancestor (base) notebook.
    """
    try:
        console.print("[dim]Combining notebooks...[/dim]")
        nb1_path = Path(notebook1)
        nb2_path = Path(notebook2)
        output_path = Path(output)
        
        # Map user-friendly strategy names to merger strategies
        strategy_map = {
            'append': 'cell-append',
            'first': 'ours',
            'second': 'theirs',
        }
        merger_strategy = strategy_map[strategy]
        
        # For combining, use first notebook as both base and ours
        base_path = nb1_path
        ours_path = nb1_path
        theirs_path = nb2_path
        
        # Create merger
        merger = NotebookMerger(base_path, ours_path, theirs_path)
        
        # Perform combine
        with console.status(f"[bold green]Combining notebooks...[/bold green]"):
            merged = merger.merge(strategy=merger_strategy)
        
        # Save combined notebook
        merger.save(output_path)
        
        # Display results
        if report:
            _display_report(merger, output_path, strategy)
        else:
            console.print(f"\n[bold green]✓ Notebooks combined![/bold green]")
            console.print(f"Output: {output_path}")
            
            # Show brief stats
            stats = merger.get_statistics()
            if strategy == 'append':
                total = stats['cells_from_ours'] + stats['cells_from_theirs']
                console.print(f"\n[dim]Combined {total} cells total "
                             f"({stats['cells_from_ours']} + {stats['cells_from_theirs']})[/dim]")
            elif strategy == 'first':
                console.print(f"\n[dim]Kept {stats['cells_from_ours']} cells from first notebook[/dim]")
            else:
                console.print(f"\n[dim]Kept {stats['cells_from_theirs']} cells from second notebook[/dim]")
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


def _display_report(merger: NotebookMerger, output_path: Path, strategy: str):
    """Display detailed combine report"""
    stats = merger.get_statistics()
    
    console.print("\n[bold cyan]📊 Combine Report:[/bold cyan]\n")
    
    # Statistics table
    table = Table(show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="bold")
    
    table.add_row("Strategy", strategy)
    table.add_row("From first notebook", f"[blue]{stats['cells_from_ours']}[/blue]")
    table.add_row("From second notebook", f"[magenta]{stats['cells_from_theirs']}[/magenta]")
    
    if strategy == 'append':
        total = stats['cells_from_ours'] + stats['cells_from_theirs']
        table.add_row("Total cells", f"[bold]{total}[/bold]")
    
    console.print(table)
    console.print(f"\n[bold]Output saved to:[/bold] {output_path}")


