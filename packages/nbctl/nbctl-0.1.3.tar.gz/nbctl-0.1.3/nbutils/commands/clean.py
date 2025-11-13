"""
Clean command - Remove outputs and metadata from notebooks
"""
from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nbutils.core.notebook import Notebook
from nbutils.core.cleaner import NotebookCleaner

console = Console()


@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), 
              help='Output path (default: overwrites input)')
@click.option('--keep-outputs', is_flag=True, 
              help='Keep cell outputs')
@click.option('--keep-execution-count', is_flag=True,
              help='Keep execution counts')
@click.option('--keep-metadata', is_flag=True,
              help='Keep all metadata')
@click.option('--dry-run', is_flag=True,
              help='Show what would be cleaned without making changes')
def clean(notebook, output, keep_outputs, keep_execution_count, keep_metadata, dry_run):
    """Clean notebook by removing outputs and metadata"""
    try:
        # Load notebook
        nb_path = Path(notebook)
        console.print(f"\n[bold blue]Loading:[/bold blue] {nb_path.name}")
        
        nb = Notebook(nb_path)
        
        # Get initial stats
        before_size = nb_path.stat().st_size
        before_stats = nb.get_stats()
        
        # Create cleaner and clean
        cleaner = NotebookCleaner(nb.nb)
        clean_stats = cleaner.clean(
            remove_outputs=not keep_outputs,
            reset_execution_count=not keep_execution_count,
            clean_metadata=not keep_metadata
        )
        
        # Save if not dry run
        if not dry_run:
            output_path = Path(output) if output else nb_path
            nb.save(output_path)
            after_size = output_path.stat().st_size
            
            # Show results
            _show_results(
                nb_path.name,
                before_stats,
                clean_stats,
                before_size,
                after_size,
                output_path
            )
        else:
            console.print("\n[yellow]DRY RUN - No changes made[/yellow]")
            _show_dry_run_results(nb_path.name, before_stats, clean_stats)
        
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


def _show_results(filename, before_stats, clean_stats, before_size, after_size, output_path):
    """Display cleaning results"""
    
    # Create summary table
    table = Table(title="Cleaning Summary", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Before", justify="right", style="yellow")
    table.add_column("After", justify="right", style="green")
    table.add_column("Change", justify="right", style="blue")
    
    # File size
    size_reduction = before_size - after_size
    size_reduction_pct = (size_reduction / before_size * 100) if before_size > 0 else 0
    table.add_row(
        "File Size",
        f"{before_size:,} bytes",
        f"{after_size:,} bytes",
        f"-{size_reduction:,} bytes ({size_reduction_pct:.1f}%)"
    )
    
    # Cells cleaned
    table.add_row(
        "Cells Cleaned",
        "-",
        f"{clean_stats['cells_cleaned']}",
        f"{clean_stats['cells_cleaned']} modified"
    )
    
    # Outputs removed
    if clean_stats['outputs_removed'] > 0:
        table.add_row(
            "Outputs Removed",
            "-",
            f"{clean_stats['outputs_removed']}",
            "✓"
        )
    
    # Execution counts
    if clean_stats['execution_counts_reset'] > 0:
        table.add_row(
            "Execution Counts Reset",
            "-",
            f"{clean_stats['execution_counts_reset']}",
            "✓"
        )
    
    # Metadata
    if clean_stats['metadata_cleaned']:
        table.add_row(
            "Metadata Cleaned",
            "-",
            "-",
            "✓"
        )
    
    console.print("\n")
    console.print(table)
    
    # Success message
    success_msg = f"Cleaned notebook saved to: {output_path}"
    console.print(Panel(success_msg, style="bold green", expand=False))


def _show_dry_run_results(filename, before_stats, clean_stats):
    """Display dry run results"""
    console.print(f"\n[bold]Would clean:[/bold] {filename}")
    console.print(f" - Cells to clean: {clean_stats['cells_cleaned']}")
    console.print(f" - Outputs to remove: {clean_stats['outputs_removed']}")
    console.print(f" - Execution counts to reset: {clean_stats['execution_counts_reset']}")
    if clean_stats['metadata_cleaned']:
        console.print(f" - Metadata: would be cleaned")