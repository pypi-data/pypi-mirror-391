"""
Extract command - Extract outputs (images, data) from notebook variables
"""
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
import nbformat
import base64
import json
import re
from typing import Dict, List, Any

console = Console()


@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              default='outputs',
              help='Output directory (default: outputs/)')
@click.option('--data', is_flag=True,
              help='Extract only data outputs (CSV, JSON, text)')
@click.option('--images', is_flag=True,
              help='Extract only image outputs (PNG, JPEG, SVG)')
@click.option('--all', 'extract_all', is_flag=True, default=False,
              help='Extract all outputs without prompting')
def extract(notebook, output, data, images, extract_all):
    """Extract outputs (images, graphs, data) from notebook variables
    
    Extracts all outputs stored in variables from Jupyter notebook cells
    and saves them to organized folders.
    
    Output Structure:
    - outputs/data/    - CSV, JSON, text files
    - outputs/images/  - PNG, JPEG, SVG images
    
    Examples:
        nbutils extract notebook.ipynb                    # Interactive mode
        nbutils extract notebook.ipynb --all              # Extract everything
        nbutils extract notebook.ipynb --output my_outputs/
        nbutils extract notebook.ipynb --data             # Only data
        nbutils extract notebook.ipynb --images           # Only images
        nbutils extract notebook.ipynb --data --images    # Both
    """
    # If no specific flags are set, prompt user interactively
    if not data and not images and not extract_all:
        console.print("\n[cyan]What would you like to extract?[/cyan]")
        choice = Prompt.ask(
            "Choose an option",
            choices=["both", "data", "images", "all"],
            default="both"
        )
        
        if choice == "both" or choice == "all":
            extract_all = True
        elif choice == "data":
            data = True
        elif choice == "images":
            images = True
    
    # If flags were explicitly set
    if data or images:
        extract_all = False
    
    # Load notebook
    nb_path = Path(notebook)
    nb = nbformat.read(nb_path, as_version=4)
    
    # Create output directories
    output_path = Path(output)
    data_path = output_path / 'data'
    images_path = output_path / 'images'
    
    if extract_all or data:
        data_path.mkdir(parents=True, exist_ok=True)
    if extract_all or images:
        images_path.mkdir(parents=True, exist_ok=True)
    
    # Counters
    image_count = 0
    data_count = 0
    
    console.print(f"[cyan]Extracting outputs from:[/cyan] {nb_path.name}")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Processing cells...", total=None)
        
        # Process each cell
        for cell_idx, cell in enumerate(nb.cells):
            if cell.cell_type != 'code':
                continue
            
            if not hasattr(cell, 'outputs') or not cell.outputs:
                continue
            
            # Process each output in the cell
            for output_idx, output in enumerate(cell.outputs):
                # Handle display_data and execute_result outputs
                if output.output_type in ['display_data', 'execute_result']:
                    if hasattr(output, 'data'):
                        # Extract images
                        if extract_all or images:
                            image_count += _extract_images(
                                output.data, 
                                images_path, 
                                cell_idx, 
                                output_idx,
                                image_count
                            )
                        
                        # Extract data
                        if extract_all or data:
                            data_count += _extract_data(
                                output.data,
                                data_path,
                                cell_idx,
                                output_idx,
                                data_count
                            )
                
                # Handle stream outputs (text data)
                elif output.output_type == 'stream' and (extract_all or data):
                    if hasattr(output, 'text'):
                        data_count += _extract_stream_text(
                            output.text,
                            data_path,
                            cell_idx,
                            output_idx,
                            data_count
                        )
        
        progress.update(task, completed=True)
    
    # Print summary
    console.print("\n[green]Extraction complete![/green]")
    if extract_all or images:
        console.print(f"[blue]  Images extracted:[/blue] {image_count}")
    if extract_all or data:
        console.print(f"[blue]  Data files extracted:[/blue] {data_count}")
    console.print(f"[blue]  Output directory:[/blue] {output_path.absolute()}")


def _extract_images(data: Dict, output_path: Path, cell_idx: int, output_idx: int, counter: int) -> int:
    """Extract image data from cell output"""
    extracted = 0
    
    # PNG images
    if 'image/png' in data:
        img_data = data['image/png']
        filename = f"cell_{cell_idx}_output_{output_idx}_img_{counter}.png"
        filepath = output_path / filename
        
        # Decode base64 and save
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(img_data))
        
        console.print(f"  [green]Saved image:[/green] {filename}")
        extracted += 1
    
    # JPEG images
    if 'image/jpeg' in data:
        img_data = data['image/jpeg']
        filename = f"cell_{cell_idx}_output_{output_idx}_img_{counter}.jpeg"
        filepath = output_path / filename
        
        with open(filepath, 'wb') as f:
            f.write(base64.b64decode(img_data))
        
        console.print(f"  [green]Saved image:[/green] {filename}")
        extracted += 1
    
    # SVG images
    if 'image/svg+xml' in data:
        svg_data = data['image/svg+xml']
        filename = f"cell_{cell_idx}_output_{output_idx}_img_{counter}.svg"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(svg_data, list):
                f.write(''.join(svg_data))
            else:
                f.write(svg_data)
        
        console.print(f"  [green]Saved image:[/green] {filename}")
        extracted += 1
    
    return extracted


def _extract_data(data: Dict, output_path: Path, cell_idx: int, output_idx: int, counter: int) -> int:
    """Extract data (CSV, JSON, etc.) from cell output"""
    extracted = 0
    
    # Application/json data
    if 'application/json' in data:
        json_data = data['application/json']
        filename = f"cell_{cell_idx}_output_{output_idx}_data_{counter}.json"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        console.print(f"  [green]Saved data:[/green] {filename}")
        extracted += 1
    
    # Text/csv data
    if 'text/csv' in data:
        csv_data = data['text/csv']
        filename = f"cell_{cell_idx}_output_{output_idx}_data_{counter}.csv"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(csv_data, list):
                f.write(''.join(csv_data))
            else:
                f.write(csv_data)
        
        console.print(f"  [green]Saved data:[/green] {filename}")
        extracted += 1
    
    # Text/html (tables from pandas DataFrames)
    if 'text/html' in data:
        html_data = data['text/html']
        filename = f"cell_{cell_idx}_output_{output_idx}_data_{counter}.html"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(html_data, list):
                f.write(''.join(html_data))
            else:
                f.write(html_data)
        
        console.print(f"  [green]Saved data:[/green] {filename}")
        extracted += 1
    
    # Plain text data (excluding representations that are primarily for display)
    if 'text/plain' in data and 'text/html' not in data:
        text_data = data['text/plain']
        
        # Check if it looks like structured data
        text_str = ''.join(text_data) if isinstance(text_data, list) else text_data
        
        # Skip if it's just a simple representation like "<Figure size ...>" or memory addresses
        if _is_structured_data(text_str):
            filename = f"cell_{cell_idx}_output_{output_idx}_data_{counter}.txt"
            filepath = output_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_str)
            
            console.print(f"  [green]Saved data:[/green] {filename}")
            extracted += 1
    
    return extracted


def _extract_stream_text(text: str, output_path: Path, cell_idx: int, output_idx: int, counter: int) -> int:
    """Extract stream text output"""
    text_str = ''.join(text) if isinstance(text, list) else text
    
    # Only save if it contains substantial data
    if len(text_str.strip()) > 10:
        filename = f"cell_{cell_idx}_stream_{output_idx}_data_{counter}.txt"
        filepath = output_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text_str)
        
        console.print(f"  [green]Saved stream:[/green] {filename}")
        return 1
    
    return 0


def _is_structured_data(text: str) -> bool:
    """Check if text looks like structured data worth saving"""
    # Skip empty or very short text
    if len(text.strip()) < 20:
        return False
    
    # Skip matplotlib/figure representations
    if re.match(r'<.*Figure.*>', text.strip()):
        return False
    
    # Skip memory address representations
    if re.match(r'<.*at 0x[0-9a-fA-F]+>', text.strip()):
        return False
    
    # Skip single-line simple outputs
    lines = text.strip().split('\n')
    if len(lines) == 1 and not any(sep in text for sep in [',', '\t', ':', '=']):
        return False
    
    return True

