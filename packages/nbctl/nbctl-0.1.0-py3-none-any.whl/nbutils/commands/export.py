"""
Export command - Convert notebooks to multiple formats
"""
from pathlib import Path
import click
from rich.console import Console
from nbconvert import HTMLExporter, PDFExporter, MarkdownExporter, LatexExporter
import nbformat

console = Console()


@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--format', '-f', 'formats', required=True,
              help='Output formats (comma-separated): html,pdf,markdown,latex')
@click.option('--output-dir', '-o', type=click.Path(),
              help='Output directory (default: same as notebook)')
def export(notebook, formats, output_dir):
    """Export notebook to multiple formats
    
    Converts Jupyter notebooks to various output formats using nbconvert.
    
    Supported formats:
    - html: HTML document
    - pdf: PDF document (requires LaTeX)
    - markdown: Markdown file
    - latex: LaTeX document
    
    Examples:
        nbutils export notebook.ipynb -f html,pdf
        nbutils export notebook.ipynb -f markdown --output-dir exports/
    """
    # Load notebook
    nb_path = Path(notebook)
    nb = nbformat.read(nb_path, as_version=nbformat.NO_CONVERT)
    
    # Determine output directory
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = nb_path.parent
    
    # Export to multiple formats
    for format in formats.split(','):
        format = format.strip()
        if format == 'html':
            exporter = HTMLExporter()
            output, _ = exporter.from_notebook_node(nb)
            out_file = output_path / nb_path.with_suffix('.html').name
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(output)
            console.print(f"[green] Exported to [/green] {out_file}")
        elif format == 'pdf':
            exporter = PDFExporter()
            output, _ = exporter.from_notebook_node(nb)
            out_file = output_path / nb_path.with_suffix('.pdf').name
            with open(out_file, 'wb') as f:
                f.write(output)
            console.print(f"[green] Exported to [/green] {out_file}")
        elif format == 'markdown':
            exporter = MarkdownExporter()
            output, _ = exporter.from_notebook_node(nb)
            out_file = output_path / nb_path.with_suffix('.md').name
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(output)
            console.print(f"[green] Exported to [/green] {out_file}")
        elif format == 'latex':
            exporter = LatexExporter()
            output, _ = exporter.from_notebook_node(nb)
            out_file = output_path / nb_path.with_suffix('.tex').name
            with open(out_file, 'w', encoding='utf-8') as f:
                f.write(output)
            console.print(f"[green] Exported to [/green] {out_file}")
        else:
            console.print(f"[red] Error: Unsupported format: {format}[/red]")
            console.print(f"Supported formats: html, pdf, markdown, latex")