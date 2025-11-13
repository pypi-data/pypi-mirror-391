"""
Resolve command - 3-way merge for resolving notebook conflicts
"""
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from nbutils.core.merger import NotebookMerger

console = Console()


@click.command()
@click.argument('base', type=click.Path(exists=True))
@click.argument('ours', type=click.Path(exists=True))
@click.argument('theirs', type=click.Path(exists=True))
@click.option('-o', '--output', type=click.Path(),
              help='Output file for merged notebook (required unless --check-conflicts)')
@click.option('--strategy', type=click.Choice(['auto', 'ours', 'theirs', 'cell-append']),
              default='auto', help='Merge strategy')
@click.option('--check-conflicts', is_flag=True, 
              help='Only check for conflicts, do not create merged file')
@click.option('--report', is_flag=True, help='Show detailed merge report')
def resolve(base, ours, theirs, output, strategy, check_conflicts, report):
    """Resolve conflicts using 3-way merge
    
    Performs intelligent 3-way merge with conflict detection.
    Requires a common ancestor (BASE) to detect true conflicts.
    
    \b
    Arguments:
      BASE   - Common ancestor version (original before changes)
      OURS   - Your version (local changes)
      THEIRS - Other version (remote/incoming changes)
    
    \b
    A conflict occurs when both OURS and THEIRS modified the same
    cell compared to BASE. Non-conflicting changes are merged automatically.
    
    \b
    Examples:
      # Check for conflicts only
      nbutils resolve base.ipynb ours.ipynb theirs.ipynb --check-conflicts
      
      # Perform merge
      nbutils resolve base.ipynb ours.ipynb theirs.ipynb -o merged.ipynb
      
      # Use with Git (resolve merge conflict)
      git show :1:notebook.ipynb > base.ipynb
      git show :2:notebook.ipynb > ours.ipynb
      git show :3:notebook.ipynb > theirs.ipynb
      nbutils resolve base.ipynb ours.ipynb theirs.ipynb -o notebook.ipynb
    """
    try:
        # Validate that output is provided unless just checking conflicts
        if not check_conflicts and not output:
            console.print("[bold red]Error:[/bold red] -o/--output is required unless using --check-conflicts")
            raise click.Abort()
        
        base_path = Path(base)
        ours_path = Path(ours)
        theirs_path = Path(theirs)
        output_path = Path(output) if output else None
        
        if not check_conflicts:
            console.print("[dim]Performing 3-way merge with conflict detection...[/dim]")
        
        # Create merger
        merger = NotebookMerger(base_path, ours_path, theirs_path)
        
        # Perform merge
        merged = merger.merge(strategy=strategy if not check_conflicts else 'auto')
        
        # Check conflicts only
        if check_conflicts:
            _display_conflict_check(merger, base_path, ours_path, theirs_path)
            return
        
        # Save merged notebook
        merger.save(output_path)
        
        # Display results
        if report or merger.has_conflicts():
            _display_merge_report(merger, output_path)
        else:
            console.print(f"\n[bold green]✓ Merge successful![/bold green]")
            console.print(f"Output: {output_path}")
            
            # Show brief stats
            stats = merger.get_statistics()
            console.print(f"\n[dim]Merged {stats['cells_merged']} cells, "
                         f"{stats['cells_from_ours']} from ours, "
                         f"{stats['cells_from_theirs']} from theirs[/dim]")
        
        # Exit with code 1 if there are conflicts
        if merger.has_conflicts():
            console.print(f"\n[yellow]⚠ {len(merger.conflicts)} conflict(s) detected. "
                         f"Please resolve manually.[/yellow]")
            raise click.Abort()
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


def _display_conflict_check(merger: NotebookMerger, base_path: Path, ours_path: Path, theirs_path: Path):
    """Display conflict check results"""
    console.print("\n[bold]3-Way Merge Conflict Check:[/bold]\n")
    console.print(f"[dim]BASE:   {base_path.name}[/dim]")
    console.print(f"[dim]OURS:   {ours_path.name}[/dim]")
    console.print(f"[dim]THEIRS: {theirs_path.name}[/dim]\n")
    
    if not merger.has_conflicts():
        console.print("[green]✓ No conflicts detected![/green]")
        console.print("[dim]All changes can be merged automatically.[/dim]")
        
        # Show what will be merged
        stats = merger.get_statistics()
        if stats['cells_from_ours'] > 0 or stats['cells_from_theirs'] > 0:
            console.print(f"\n[dim]Will merge: {stats['cells_from_ours']} cells from OURS, "
                         f"{stats['cells_from_theirs']} cells from THEIRS[/dim]")
    else:
        console.print(f"[yellow]⚠ {len(merger.conflicts)} conflict(s) detected:[/yellow]\n")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Cell", style="dim", width=8)
        table.add_column("Type", width=10)
        table.add_column("Issue", width=60)
        
        for conflict in merger.conflicts:
            table.add_row(
                str(conflict.cell_index + 1),
                conflict.cell_type,
                "Both OURS and THEIRS modified this cell"
            )
        
        console.print(table)
        console.print("\n[dim]Run without --check-conflicts to create merged file with conflict markers.[/dim]")


def _display_merge_report(merger: NotebookMerger, output_path: Path):
    """Display detailed merge report"""
    stats = merger.get_statistics()
    
    console.print("\n[bold cyan]📊 3-Way Merge Report:[/bold cyan]\n")
    
    # Statistics table
    table = Table(show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="bold")
    
    table.add_row("Auto-merged cells", str(stats['cells_merged']))
    table.add_row("From OURS", f"[blue]{stats['cells_from_ours']}[/blue]")
    table.add_row("From THEIRS", f"[magenta]{stats['cells_from_theirs']}[/magenta]")
    table.add_row("Unchanged (from BASE)", f"[dim]{stats['cells_unchanged']}[/dim]")
    table.add_row("Conflicts", f"[{'red' if stats['conflicts'] > 0 else 'green'}]{stats['conflicts']}[/{'red' if stats['conflicts'] > 0 else 'green'}]")
    
    console.print(table)
    
    # Show conflicts if any
    if merger.has_conflicts():
        console.print(f"\n[bold yellow]⚠ Conflicts requiring manual resolution:[/bold yellow]\n")
        
        for i, conflict in enumerate(merger.conflicts, 1):
            console.print(Panel(
                f"[bold]Cell {conflict.cell_index + 1} ({conflict.cell_type})[/bold]\n\n"
                f"[dim]Both OURS and THEIRS modified this cell compared to BASE.\n"
                f"The merged file contains conflict markers.[/dim]",
                title=f"Conflict {i}",
                border_style="yellow"
            ))
    
    console.print(f"\n[bold]Output saved to:[/bold] {output_path}")
    
    if merger.has_conflicts():
        console.print("\n[dim]To resolve conflicts:[/dim]")
        console.print("  1. Open the merged notebook")
        console.print("  2. Find cells with <<<<<<< OURS and >>>>>>> THEIRS markers")
        console.print("  3. Edit to keep desired version")
        console.print("  4. Remove conflict markers")


