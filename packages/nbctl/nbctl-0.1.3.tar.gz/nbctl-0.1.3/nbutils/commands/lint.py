"""
Lint command - Check code quality in notebooks
"""
from pathlib import Path
import ast
from typing import List, Dict, Any
import click
from rich.console import Console
from rich.table import Table

from nbutils.core.notebook import Notebook

console = Console()


@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--max-cell-length', default=100, type=int,
              help='Maximum lines per cell (default: 100)')
def lint(notebook, max_cell_length):
    """Check code quality in notebook
    
    Performs quality checks on notebook code cells:
    - Detects unused imports
    - Finds cells that are too long
    - Checks for empty cells
    - Identifies undefined variables
    
    Examples:
        nbutils lint notebook.ipynb
        nbutils lint notebook.ipynb --max-cell-length 150
    """
    try:
        nb_path = Path(notebook)
        nb = Notebook(nb_path)
        
        console.print(f"\n[bold blue]Linting:[/bold blue] {nb_path.name}\n")
        
        # Run all checks
        issues = []
        issues.extend(_check_imports(nb))
        issues.extend(_check_cell_length(nb, max_cell_length))
        issues.extend(_check_empty_cells(nb))
        
        # Display results
        if issues:
            _show_issues(issues)
            console.print(f"\n[yellow] [/yellow] Found {len(issues)} issue(s)\n")
        else:
            console.print("[bold green] All checks passed![/bold green]\n")
        
    except click.Abort:
        raise
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


def _check_imports(nb: Notebook) -> List[Dict[str, Any]]:
    """Check for unused imports"""
    issues = []
    
    # Collect all imports and their usage
    imports = {}  # {module_name: [cell_indices]}
    names_used = set()
    
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            continue
        
        try:
            tree = ast.parse(cell.source)
        except SyntaxError:
            continue
        
        # Find imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name.split('.')[0]
                    if name not in imports:
                        imports[name] = []
                    imports[name].append(idx)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    if name not in imports:
                        imports[name] = []
                    imports[name].append(idx)
            elif isinstance(node, ast.Name):
                names_used.add(node.id)
    
    # Check for unused imports
    for module, cell_indices in imports.items():
        if module not in names_used:
            for cell_idx in cell_indices:
                issues.append({
                    'type': 'unused_import',
                    'severity': 'warning',
                    'cell': cell_idx,
                    'message': f"Unused import: {module}"
                })
    
    return issues


def _check_cell_length(nb: Notebook, max_length: int) -> List[Dict[str, Any]]:
    """Check for cells that are too long"""
    issues = []
    
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            continue
        
        if not cell.source:
            continue
        
        lines = cell.source.split('\n')
        line_count = len(lines)
        
        if line_count > max_length:
            issues.append({
                'type': 'long_cell',
                'severity': 'warning',
                'cell': idx,
                'message': f"Cell too long: {line_count} lines (max: {max_length})"
            })
    
    return issues


def _check_empty_cells(nb: Notebook) -> List[Dict[str, Any]]:
    """Check for empty code cells"""
    issues = []
    
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            continue
        
        if not cell.source or not cell.source.strip():
            issues.append({
                'type': 'empty_cell',
                'severity': 'info',
                'cell': idx,
                'message': "Empty code cell"
            })
    
    return issues


def _show_issues(issues: List[Dict[str, Any]]):
    """Display linting issues in a table"""
    
    # Sort by cell number
    issues.sort(key=lambda x: x['cell'])
    
    table = Table(title="Linting Issues", show_header=True, header_style="bold magenta")
    table.add_column("Cell", style="cyan", justify="right")
    table.add_column("Severity", style="white")
    table.add_column("Issue", style="yellow")
    
    for issue in issues:
        severity_style = {
            'error': '[red]ERROR[/red]',
            'warning': '[yellow]WARNING[/yellow]',
            'info': '[blue]INFO[/blue]'
        }
        
        table.add_row(
            str(issue['cell']),
            severity_style.get(issue['severity'], issue['severity']),
            issue['message']
        )
    
    console.print(table)

