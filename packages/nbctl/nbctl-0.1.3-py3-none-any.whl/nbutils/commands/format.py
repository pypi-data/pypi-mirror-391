"""
Format command - Auto-format code cells with black
"""
from pathlib import Path
import click
from rich.console import Console

from nbutils.core.notebook import Notebook

console = Console()


@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(),
              help='Output directory (default: same as notebook)')
@click.option('--line-length', default=88, type=int,
              help='Maximum line length (default: 88)')
def format(notebook, output_dir, line_length):
    """Auto-format code cells with black
    
    Formats Python code in notebook cells using black formatter.
    Preserves markdown cells and cell metadata.
    
    Examples:
        nbutils format notebook.ipynb
        nbutils format notebook.ipynb --output-dir formatted/
    """
    try:
        # Import black here for better error message
        try:
            import black
        except ImportError:
            console.print("\n[bold red]Error:[/bold red] black is not installed")
            console.print("Install it with: [cyan]pip install black[/cyan]")
            raise click.Abort()
        
        nb_path = Path(notebook)
        nb = Notebook(nb_path)
        
        # Determine output path
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            output_file = output_path / nb_path.name
        else:
            output_file = nb_path
        
        console.print(f"\n[bold blue]Formatting:[/bold blue] {nb_path.name}\n")

        formatted_count = 0
        unchanged_count = 0
        error_count = 0
        
        for idx, cell in enumerate(nb.cells):
            if cell.cell_type != 'code':
                continue
            
            if not cell.source or not cell.source.strip():
                continue
            
            try:
                mode = black.Mode(line_length=line_length)
                formatted_code = black.format_str(cell.source, mode=mode)
                
                if formatted_code != cell.source:
                    cell.source = formatted_code
                    formatted_count += 1
                else:
                    unchanged_count += 1
                    
            except Exception as e:
                error_count += 1
                console.print(f"[yellow]Warning:[/yellow] Could not format cell {idx}: {str(e)}")
        
        if formatted_count > 0:
            nb.save(output_file)
            
            console.print(f"[green] Formatted {formatted_count} cell(s)[/green]")
            console.print(f"[dim]{unchanged_count} cell(s) unchanged[/dim]")
            if error_count > 0:
                console.print(f"[yellow]{error_count} cell(s) had errors[/yellow]")
            console.print(f"\n[bold green] Saved to:[/bold green] {output_file}\n")
        else:
            console.print("[bold green] All cells already formatted![/bold green]\n")
        
    except click.Abort:
        raise
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()

