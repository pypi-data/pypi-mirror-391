"""
ML Split command - Split ML notebook into structured Python files
"""
from pathlib import Path
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import nbformat
import re
from typing import Dict, List, Tuple
from collections import defaultdict

console = Console()


# Common ML section patterns
ML_SECTION_PATTERNS = {
    'data_collection': [
        r'data\s*collection',
        r'load\s*data',
        r'data\s*loading',
        r'import\s*data',
        r'read\s*data',
        r'fetch\s*data'
    ],
    'data_preprocessing': [
        r'preprocess',
        r'data\s*cleaning',
        r'clean\s*data',
        r'data\s*preparation',
        r'prepare\s*data',
        r'feature\s*cleaning'
    ],
    'feature_engineering': [
        r'feature\s*engineering',
        r'feature\s*creation',
        r'feature\s*extraction',
        r'create\s*features',
        r'feature\s*generation'
    ],
    'data_splitting': [
        r'split\s*data',
        r'train\s*test\s*split',
        r'data\s*split',
        r'validation\s*split'
    ],
    'model_training': [
        r'train\s*model',
        r'model\s*training',
        r'training',
        r'fit\s*model',
        r'train'
    ],
    'model_evaluation': [
        r'evaluat',
        r'test\s*model',
        r'model\s*evaluation',
        r'assess\s*model',
        r'validation',
        r'metrics',
        r'performance'
    ],
    'model_saving': [
        r'save\s*model',
        r'export\s*model',
        r'model\s*persistence',
        r'serialize\s*model'
    ]
}


@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              default='ml_pipeline',
              help='Output directory (default: ml_pipeline/)')
@click.option('--create-main/--no-create-main', default=True,
              help='Create main.py to run the pipeline')
def ml_split(notebook, output, create_main):
    """Split ML notebook into structured Python pipeline files
    
    Automatically detects ML workflow sections and creates organized
    Python modules for each stage of your ML pipeline.
    
    Detected Sections:
    - Data Collection
    - Data Preprocessing
    - Feature Engineering
    - Data Splitting
    - Model Training
    - Model Evaluation
    - Model Saving
    
    Examples:
        nbutils ml-split ml_notebook.ipynb
        nbutils ml-split ml_notebook.ipynb --output src/ml/
    """
    # Load notebook
    nb_path = Path(notebook)
    nb = nbformat.read(nb_path, as_version=4)
    
    # Create output directory
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    console.print(f"[cyan]Analyzing ML notebook:[/cyan] {nb_path.name}")
    
    # Parse notebook sections
    sections = _parse_ml_sections(nb)
    
    if not sections:
        console.print("[yellow]Warning: No ML sections detected. Creating generic split...[/yellow]")
        sections = _create_generic_sections(nb)
    
    # Display detected sections
    console.print(f"\n[green]Detected {len(sections)} sections:[/green]")
    for section_name, cells in sections.items():
        console.print(f"  • {section_name}: {len(cells)} code cells")
    
    # Extract all imports
    all_imports = _extract_imports(nb)
    
    # Generate Python files
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Generating Python files...", total=len(sections))
        
        for section_name, cells in sections.items():
            if cells:  # Only create file if there are cells
                _create_python_file(
                    output_path,
                    section_name,
                    cells,
                    all_imports
                )
                progress.advance(task)
    
    # Create __init__.py
    _create_init_file(output_path, list(sections.keys()))
    
    # Create main.py pipeline runner
    if create_main:
        _create_main_file(output_path, list(sections.keys()), nb_path.stem)
    
    # Create requirements.txt
    _create_requirements_file(output_path, all_imports)
    
    # Print summary
    console.print(f"\n[green]ML pipeline created successfully![/green]")
    console.print(f"[blue]  Output directory:[/blue] {output_path.absolute()}")
    console.print(f"[blue]  Files created:[/blue] {len(sections)} modules + __init__.py + main.py")
    console.print(f"\n[cyan]To run the pipeline:[/cyan]")
    console.print(f"  cd {output_path}")
    console.print(f"  python main.py")


def _parse_ml_sections(nb: nbformat.NotebookNode) -> Dict[str, List[nbformat.NotebookNode]]:
    """Parse notebook into ML sections based on markdown headers"""
    sections = defaultdict(list)
    current_section = None
    
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            # Check if this markdown cell defines a new section
            section_name = _identify_section(cell.source)
            if section_name:
                current_section = section_name
        elif cell.cell_type == 'code' and current_section:
            # Add code cell to current section
            if cell.source.strip():  # Skip empty cells
                sections[current_section].append(cell)
    
    return dict(sections)


def _identify_section(markdown_text: str) -> str:
    """Identify ML section from markdown text"""
    text_lower = markdown_text.lower()
    
    # Check each pattern
    for section_name, patterns in ML_SECTION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return section_name
    
    return None


def _create_generic_sections(nb: nbformat.NotebookNode) -> Dict[str, List[nbformat.NotebookNode]]:
    """Create generic sections if no ML sections detected"""
    sections = defaultdict(list)
    
    for idx, cell in enumerate(nb.cells):
        if cell.cell_type == 'code' and cell.source.strip():
            section_name = f"section_{idx // 5 + 1}"  # Group every 5 cells
            sections[section_name].append(cell)
    
    return dict(sections)


def _extract_imports(nb: nbformat.NotebookNode) -> List[str]:
    """Extract all import statements from notebook"""
    imports = []
    seen = set()
    
    for cell in nb.cells:
        if cell.cell_type == 'code':
            for line in cell.source.split('\n'):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    if line not in seen:
                        imports.append(line)
                        seen.add(line)
    
    return imports


def _create_python_file(
    output_path: Path,
    section_name: str,
    cells: List[nbformat.NotebookNode],
    all_imports: List[str]
):
    """Create Python file for a section"""
    filename = f"{section_name}.py"
    filepath = output_path / filename
    
    # Filter relevant imports for this section
    section_code = '\n\n'.join(cell.source for cell in cells)
    relevant_imports = _filter_relevant_imports(all_imports, section_code)
    
    # Use repr() to safely embed the code as a string literal
    code_repr = repr(section_code)
    
    # Generate file content
    content = f'''"""
{section_name.replace('_', ' ').title()} Module

Automatically generated from notebook.
"""

{chr(10).join(relevant_imports)}


def run(context=None):
    """Execute {section_name.replace('_', ' ')} pipeline step
    
    Args:
        context: Dictionary containing variables from previous steps
        
    Returns:
        Dictionary of variables for next steps
    """
    # Import variables from context
    if context is None:
        context = {{}}
    
    # Create execution namespace with context variables
    exec_globals = globals().copy()
    exec_locals = context.copy()
    
    # The code to execute
    _code = {code_repr}
    
    # Execute the code in the namespace
    exec(_code, exec_globals, exec_locals)
    
    # Return all variables (context + newly created)
    return exec_locals


if __name__ == "__main__":
    result = run()
    print(f"\\n{section_name} completed successfully!")
    variables = [k for k in result.keys() if not k.startswith('_')]
    if variables:
        print(f"Variables created: {{', '.join(variables[:10])}}")
'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    console.print(f"  Created: {filename}")


def _filter_relevant_imports(all_imports: List[str], code: str) -> List[str]:
    """Filter imports that are actually used in the code"""
    relevant = []
    
    for imp in all_imports:
        # Extract module/alias name
        if imp.startswith('import '):
            module = imp.replace('import ', '').split(' as ')[0].split('.')[0]
        elif imp.startswith('from '):
            module = imp.split(' import ')[0].replace('from ', '').split('.')[0]
        else:
            continue
        
        # Check if module is used in code
        if module in code:
            relevant.append(imp)
    
    return relevant


def _indent_code(code: str, spaces: int) -> str:
    """Indent code by specified number of spaces"""
    indent = ' ' * spaces
    return '\n'.join(indent + line if line.strip() else '' for line in code.split('\n'))


def _create_init_file(output_path: Path, section_names: List[str]):
    """Create __init__.py file"""
    filepath = output_path / '__init__.py'
    
    imports = '\n'.join(f"from . import {name}" for name in section_names)
    
    content = f'''"""
ML Pipeline Package

Automatically generated from notebook.
"""

{imports}

__all__ = {section_names}
'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def _create_main_file(output_path: Path, section_names: List[str], notebook_name: str):
    """Create main.py pipeline runner"""
    filepath = output_path / 'main.py'
    
    # Generate pipeline execution code with context passing
    pipeline_steps = []
    for idx, name in enumerate(section_names):
        if idx == 0:
            # First step has no context
            pipeline_steps.append(
                f"print('\\n[Step {idx+1}] Running {name}...')\n    "
                f"context = {name}.run()\n    "
                f"print(f'  ✓ Completed')"
            )
        else:
            # Subsequent steps receive context from previous step
            pipeline_steps.append(
                f"print('\\n[Step {idx+1}] Running {name}...')\n    "
                f"context = {name}.run(context)\n    "
                f"print(f'  ✓ Completed')"
            )
    
    pipeline_steps_str = '\n    '.join(pipeline_steps)
    imports = '\n'.join(f"import {name}" for name in section_names)
    
    content = f'''"""
ML Pipeline Runner

Automatically generated from: {notebook_name}.ipynb

Run this script to execute the entire ML pipeline in sequence.
Each step receives variables from the previous step via context.
"""

{imports}


def run_pipeline():
    """Execute the complete ML pipeline"""
    print("=" * 60)
    print("Starting ML Pipeline")
    print("=" * 60)
    
    {pipeline_steps_str}
    
    print("\\n" + "=" * 60)
    print("Pipeline completed successfully!")
    print("=" * 60)
    
    return context


if __name__ == "__main__":
    try:
        final_context = run_pipeline()
        print(f"\\nFinal variables available: {{', '.join(k for k in final_context.keys() if not k.startswith('_'))}}")
    except Exception as e:
        print(f"\\nError in pipeline: {{e}}")
        import traceback
        traceback.print_exc()
        raise
'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    console.print(f"  Created: main.py")


def _create_requirements_file(output_path: Path, imports: List[str]):
    """Create requirements.txt from imports"""
    filepath = output_path / 'requirements.txt'
    
    # Map common imports to package names
    package_map = {
        'sklearn': 'scikit-learn',
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
    }
    
    packages = set()
    for imp in imports:
        if imp.startswith('import '):
            pkg = imp.replace('import ', '').split(' as ')[0].split('.')[0]
        elif imp.startswith('from '):
            pkg = imp.split(' import ')[0].replace('from ', '').split('.')[0]
        else:
            continue
        
        # Skip standard library
        if pkg not in ['os', 'sys', 're', 'json', 'time', 'datetime', 'pathlib', 'collections', 'typing']:
            packages.add(package_map.get(pkg, pkg))
    
    content = '# ML Pipeline Requirements\n# Generated from notebook imports\n\n'
    content += '\n'.join(sorted(packages))
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    console.print(f"  Created: requirements.txt")

