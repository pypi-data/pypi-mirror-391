"""
Run command - Execute Jupyter notebooks from command line
"""
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor, CellExecutionError
from datetime import datetime
import time

console = Console()


@click.command()
@click.argument('notebooks', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--order', is_flag=True, 
              help='Run notebooks in alphabetical order')
@click.option('--timeout', '-t', type=int, default=None,
              help='Timeout per cell in seconds (default: None - no timeout)')
@click.option('--allow-errors', is_flag=True,
              help='Continue execution even if cells fail')
@click.option('--save-output', '-o', type=click.Path(),
              help='Directory to save executed notebooks (default: overwrite)')
@click.option('--kernel', '-k', default='python3',
              help='Kernel name to use (default: python3)')
def run(notebooks, order, timeout, allow_errors, save_output, kernel):
    """Execute Jupyter notebooks from command line
    
    Run one or more notebooks sequentially with full execution.
    
    Features:
    - Execute notebooks in specified or alphabetical order
    - Capture cell outputs and errors
    - No timeout by default (perfect for long ML training)
    - Save executed notebooks with outputs
    - Detailed execution reporting
    
    Examples:
        # Run notebooks in specified order
        nbutils run analysis.ipynb
        nbutils run 01_load.ipynb 02_process.ipynb 03_analyze.ipynb
        
        # Run all notebooks in alphabetical order
        nbutils run *.ipynb --order
        
        # Continue on errors
        nbutils run notebook.ipynb --allow-errors
        
        # Save executed notebooks to directory
        nbutils run *.ipynb --save-output executed/
        
        # Set timeout only if needed (e.g. prevent infinite loops)
        nbutils run notebook.ipynb --timeout 600
    """
    notebook_paths = [Path(nb) for nb in notebooks]
    
    if order:
        notebook_paths = sorted(notebook_paths, key=lambda p: p.name.lower())
        console.print(f"[cyan]Running {len(notebook_paths)} notebooks in alphabetical order[/cyan]\n")
    else:
        console.print(f"[cyan]Running {len(notebook_paths)} notebooks in specified order[/cyan]\n")
    
    output_dir = None
    if save_output:
        output_dir = Path(save_output)
        output_dir.mkdir(parents=True, exist_ok=True)
        console.print(f"[blue]Output directory:[/blue] {output_dir.absolute()}\n")
    
    results = []
    total_start_time = time.time()
    
    for idx, nb_path in enumerate(notebook_paths, 1):
        console.print(f"[bold cyan][{idx}/{len(notebook_paths)}][/bold cyan] Executing: {nb_path.name}")
        
        result = _execute_notebook(
            nb_path, 
            timeout=timeout,
            allow_errors=allow_errors,
            kernel_name=kernel
        )
        
        results.append(result)
        
        if output_dir and result['success']:
            output_path = output_dir / nb_path.name
            with open(output_path, 'w', encoding='utf-8') as f:
                nbformat.write(result['nb'], f)
            console.print(f"  [green]Saved to:[/green] {output_path}")
        elif not output_dir and result['success']:
            with open(nb_path, 'w', encoding='utf-8') as f:
                nbformat.write(result['nb'], f)
            console.print(f"  [green]Updated:[/green] {nb_path}")
        
        console.print()
    
    total_time = time.time() - total_start_time
    
    _display_summary(results, notebook_paths, total_time)
    
    if not all(r['success'] for r in results):
        raise SystemExit(1)


def _execute_notebook(nb_path, timeout, allow_errors, kernel_name):
    """Execute a single notebook"""
    start_time = time.time()
    
    try:
        with open(nb_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        ep = ExecutePreprocessor(
            timeout=timeout,
            kernel_name=kernel_name,
            allow_errors=allow_errors
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task(
                f"  Executing cells...",
                total=100
            )
            
            executed_nb, resources = ep.preprocess(
                nb,
                {'metadata': {'path': str(nb_path.parent)}}
            )
            
            progress.update(task, completed=100)
            
            cell_outputs = []
            for idx, cell in enumerate(executed_nb.cells):
                if cell.cell_type == 'code':
                    cell_outputs.append({'cell': idx, 'success': True})
        
        execution_time = time.time() - start_time
        
        console.print(f"  [green]Completed successfully[/green] ({execution_time:.1f}s)")
        
        return {
            'path': nb_path,
            'success': True,
            'nb': executed_nb,
            'execution_time': execution_time,
            'cell_outputs': cell_outputs
        }
        
    except CellExecutionError as e:
        execution_time = time.time() - start_time
        console.print(f"  [red]Failed:[/red] Cell execution error")
        console.print(f"    [dim]{str(e)[:200]}...[/dim]")
        
        return {
            'path': nb_path,
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }
    
    except Exception as e:
        execution_time = time.time() - start_time
        console.print(f"  [red]Failed:[/red] {type(e).__name__}: {str(e)}")
        
        return {
            'path': nb_path,
            'success': False,
            'error': str(e),
            'execution_time': execution_time
        }


def _display_summary(results, notebook_paths, total_time):
    """Display execution summary"""
    console.print("\n" + "=" * 60)
    console.print("[bold cyan]Execution Summary[/bold cyan]")
    console.print("=" * 60 + "\n")
    
    # Create summary table
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Notebook", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right")
    
    successful = 0
    failed = 0
    
    for result, nb_path in zip(results, notebook_paths):
        if result['success']:
            status = "[green]Success[/green]"
            successful += 1
        else:
            status = "[red]Failed[/red]"
            failed += 1
        
        time_str = f"{result['execution_time']:.1f}s"
        table.add_row(nb_path.name, status, time_str)
    
    console.print(table)
    
    # Summary stats
    console.print(f"\n[bold]Total:[/bold] {len(results)} notebooks")
    console.print(f"[green]Successful:[/green] {successful}")
    if failed > 0:
        console.print(f"[red]Failed:[/red] {failed}")
    console.print(f"[blue]Total time:[/blue] {total_time:.1f}s")
    
    if successful == len(results):
        console.print(f"\n[bold green]All notebooks executed successfully![/bold green]")
    else:
        console.print(f"\n[bold red]{failed} notebook(s) failed execution[/bold red]")

