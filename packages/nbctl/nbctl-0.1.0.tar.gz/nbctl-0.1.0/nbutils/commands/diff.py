"""
Diff command - Show meaningful differences between notebooks
"""
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from nbutils.core.differ import NotebookDiffer

console = Console()


@click.command()
@click.argument('old_notebook', type=click.Path(exists=True))
@click.argument('new_notebook', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['table', 'unified', 'json']), 
              default='table', help='Output format')
@click.option('--code-only', is_flag=True, help='Show only code cell changes')
@click.option('--stats', is_flag=True, help='Show only statistics')
def diff(old_notebook, new_notebook, format, code_only, stats):
    """Show differences between two notebooks
    
    Compares code and markdown content only. Outputs and metadata are always ignored.
    """
    try:
        old_path = Path(old_notebook)
        new_path = Path(new_notebook)
        
        # Create differ and compare (always ignore outputs and metadata)
        differ = NotebookDiffer(old_path, new_path)
        diffs = differ.compare(ignore_outputs=True, ignore_metadata=True)
        
        # Filter by code-only if requested
        if code_only:
            diffs = [d for d in diffs if d.cell_type == 'code']
        
        # Show statistics if requested
        if stats:
            _show_statistics(differ)
            return
        
        # Show no changes message
        if not differ.has_changes():
            console.print("[green]✓ No differences found[/green]")
            return
        
        # Display based on format
        if format == 'table':
            _display_table_format(diffs, old_path, new_path)
        elif format == 'unified':
            _display_unified_format(diffs, old_path, new_path)
        elif format == 'json':
            _display_json_format(diffs, differ)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


def _show_statistics(differ: NotebookDiffer):
    """Display diff statistics"""
    stats = differ.get_statistics()
    
    table = Table(title="📊 Diff Statistics", show_header=False)
    table.add_column("Metric", style="cyan")
    table.add_column("Count", style="bold")
    
    table.add_row("Total Changes", str(stats['total_changes']))
    table.add_row("Cells Added", f"[green]+{stats['cells_added']}[/green]")
    table.add_row("Cells Deleted", f"[red]-{stats['cells_deleted']}[/red]")
    table.add_row("Cells Modified", f"[yellow]~{stats['cells_modified']}[/yellow]")
    table.add_row("Cells Unchanged", f"[dim]{stats['cells_unchanged']}[/dim]")
    
    console.print(table)


def _display_table_format(diffs, old_path, new_path):
    """Display differences in table format"""
    console.print(f"\n[bold]Comparing:[/bold] {old_path.name} → {new_path.name}\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Cell", style="dim", width=6)
    table.add_column("Type", width=10)
    table.add_column("Status", width=12)
    table.add_column("Changes", width=50)
    
    for diff in diffs:
        if diff.status == 'unchanged':
            continue
        
        # Status with color
        if diff.status == 'added':
            status = "[green]+ Added[/green]"
            cell_num = f"[green]{diff.index + 1}[/green]"
        elif diff.status == 'deleted':
            status = "[red]- Deleted[/red]"
            cell_num = f"[red]{diff.index + 1}[/red]"
        elif diff.status == 'modified':
            status = "[yellow]~ Modified[/yellow]"
            cell_num = f"[yellow]{diff.index + 1}[/yellow]"
        else:
            status = diff.status
            cell_num = str(diff.index + 1)
        
        # Preview of changes
        if diff.status == 'added':
            preview = diff.new_content[:80].replace('\n', ' ') + '...' if len(diff.new_content) > 80 else diff.new_content.replace('\n', ' ')
        elif diff.status == 'deleted':
            preview = diff.old_content[:80].replace('\n', ' ') + '...' if len(diff.old_content) > 80 else diff.old_content.replace('\n', ' ')
        else:
            preview = f"{len(diff.changes)} lines changed"
        
        table.add_row(cell_num, diff.cell_type, status, preview)
    
    console.print(table)


def _display_unified_format(diffs, old_path, new_path):
    """Display differences in unified diff format"""
    console.print(f"\n[bold]--- {old_path}[/bold]")
    console.print(f"[bold]+++ {new_path}[/bold]\n")
    
    for diff in diffs:
        if diff.status == 'unchanged':
            continue
        
        console.print(f"\n[bold cyan]Cell {diff.index + 1} ({diff.cell_type}):[/bold cyan]")
        
        if diff.status == 'added':
            console.print(Panel(
                Syntax(diff.new_content, "python" if diff.cell_type == "code" else "markdown"),
                title=f"[green]+ Added[/green]",
                border_style="green"
            ))
        elif diff.status == 'deleted':
            console.print(Panel(
                Syntax(diff.old_content, "python" if diff.cell_type == "code" else "markdown"),
                title=f"[red]- Deleted[/red]",
                border_style="red"
            ))
        elif diff.status == 'modified':
            # Show old content
            console.print("[dim]Old:[/dim]")
            console.print(Panel(
                Syntax(diff.old_content, "python" if diff.cell_type == "code" else "markdown"),
                border_style="red"
            ))
            
            # Show new content
            console.print("[dim]New:[/dim]")
            console.print(Panel(
                Syntax(diff.new_content, "python" if diff.cell_type == "code" else "markdown"),
                border_style="green"
            ))


def _display_json_format(diffs, differ: NotebookDiffer):
    """Display differences in JSON format"""
    import json
    
    output = {
        'statistics': differ.get_statistics(),
        'changes': []
    }
    
    for diff in diffs:
        if diff.status == 'unchanged':
            continue
        
        change = {
            'cell_index': diff.index,
            'cell_type': diff.cell_type,
            'status': diff.status,
        }
        
        if diff.status == 'added':
            change['new_content'] = diff.new_content
        elif diff.status == 'deleted':
            change['old_content'] = diff.old_content
        elif diff.status == 'modified':
            change['old_content'] = diff.old_content
            change['new_content'] = diff.new_content
        
        output['changes'].append(change)
    
    console.print_json(data=output)

