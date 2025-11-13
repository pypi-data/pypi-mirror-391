"""
Tests for the extract command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.extract import extract
import base64
import json


@pytest.fixture
def sample_notebook_with_outputs(tmp_path):
    """Create a sample notebook with various output types"""
    nb = nbformat.v4.new_notebook()
    
    # Cell 1: Code cell with PNG image output
    # Creating a simple 1x1 pixel PNG (base64 encoded)
    png_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    
    code_cell_1 = nbformat.v4.new_code_cell(
        source="import matplotlib.pyplot as plt\nplt.plot([1, 2, 3])",
        execution_count=1,
        outputs=[
            nbformat.v4.new_output(
                output_type='display_data',
                data={
                    'image/png': png_data,
                    'text/plain': '<Figure size 640x480 with 1 Axes>'
                }
            )
        ]
    )
    nb.cells.append(code_cell_1)
    
    # Cell 2: Code cell with JSON data output
    json_data = {'name': 'test', 'values': [1, 2, 3]}
    code_cell_2 = nbformat.v4.new_code_cell(
        source="import json\ndata = {'name': 'test', 'values': [1, 2, 3]}\ndata",
        execution_count=2,
        outputs=[
            nbformat.v4.new_output(
                output_type='execute_result',
                data={
                    'application/json': json_data,
                    'text/plain': str(json_data)
                },
                execution_count=2
            )
        ]
    )
    nb.cells.append(code_cell_2)
    
    # Cell 3: Code cell with HTML output (pandas DataFrame)
    html_data = '<table><tr><th>A</th><th>B</th></tr><tr><td>1</td><td>2</td></tr></table>'
    code_cell_3 = nbformat.v4.new_code_cell(
        source="import pandas as pd\ndf = pd.DataFrame({'A': [1], 'B': [2]})\ndf",
        execution_count=3,
        outputs=[
            nbformat.v4.new_output(
                output_type='execute_result',
                data={
                    'text/html': html_data,
                    'text/plain': '   A  B\n0  1  2'
                },
                execution_count=3
            )
        ]
    )
    nb.cells.append(code_cell_3)
    
    # Cell 4: Code cell with stream output
    code_cell_4 = nbformat.v4.new_code_cell(
        source="print('Hello, World!')",
        execution_count=4,
        outputs=[
            nbformat.v4.new_output(
                output_type='stream',
                name='stdout',
                text='Hello, World!\n'
            )
        ]
    )
    nb.cells.append(code_cell_4)
    
    # Cell 5: Code cell with SVG output
    svg_data = '<svg width="100" height="100"><circle cx="50" cy="50" r="40" fill="red"/></svg>'
    code_cell_5 = nbformat.v4.new_code_cell(
        source="from IPython.display import SVG\nSVG('<svg>...</svg>')",
        execution_count=5,
        outputs=[
            nbformat.v4.new_output(
                output_type='display_data',
                data={
                    'image/svg+xml': svg_data
                }
            )
        ]
    )
    nb.cells.append(code_cell_5)
    
    # Save notebook
    nb_path = tmp_path / "test_outputs.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def empty_notebook(tmp_path):
    """Create a notebook with no outputs"""
    nb = nbformat.v4.new_notebook()
    
    # Add a code cell with no output
    code_cell = nbformat.v4.new_code_cell(
        source="x = 1",
        execution_count=1
    )
    nb.cells.append(code_cell)
    
    # Save notebook
    nb_path = tmp_path / "empty.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_extract_all_outputs(sample_notebook_with_outputs, tmp_path):
    """Test extracting all outputs"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir),
        '--all'
    ])
    
    # Check command succeeded
    assert result.exit_code == 0
    
    # Check output directories were created
    assert output_dir.exists()
    assert (output_dir / 'data').exists()
    assert (output_dir / 'images').exists()
    
    # Check that files were extracted
    data_files = list((output_dir / 'data').glob('*'))
    image_files = list((output_dir / 'images').glob('*'))
    
    assert len(data_files) > 0, "Should extract data files"
    assert len(image_files) > 0, "Should extract image files"


def test_extract_images_only(sample_notebook_with_outputs, tmp_path):
    """Test extracting only images"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir),
        '--images'
    ])
    
    assert result.exit_code == 0
    
    # Check that images directory exists
    assert (output_dir / 'images').exists()
    
    # Check that images were extracted
    image_files = list((output_dir / 'images').glob('*'))
    assert len(image_files) > 0, "Should extract image files"
    
    # Check PNG file was created
    png_files = list((output_dir / 'images').glob('*.png'))
    assert len(png_files) > 0, "Should extract PNG files"
    
    # Check SVG file was created
    svg_files = list((output_dir / 'images').glob('*.svg'))
    assert len(svg_files) > 0, "Should extract SVG files"


def test_extract_data_only(sample_notebook_with_outputs, tmp_path):
    """Test extracting only data"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir),
        '--data'
    ])
    
    assert result.exit_code == 0
    
    # Check that data directory exists
    assert (output_dir / 'data').exists()
    
    # Check that data files were extracted
    data_files = list((output_dir / 'data').glob('*'))
    assert len(data_files) > 0, "Should extract data files"
    
    # Check specific file types
    json_files = list((output_dir / 'data').glob('*.json'))
    html_files = list((output_dir / 'data').glob('*.html'))
    txt_files = list((output_dir / 'data').glob('*.txt'))
    
    assert len(json_files) > 0, "Should extract JSON files"
    assert len(html_files) > 0, "Should extract HTML files"


def test_extract_both_flags(sample_notebook_with_outputs, tmp_path):
    """Test extracting with both --data and --images flags"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir),
        '--data',
        '--images'
    ])
    
    assert result.exit_code == 0
    
    # Check both directories exist
    assert (output_dir / 'data').exists()
    assert (output_dir / 'images').exists()
    
    # Check both types of files were extracted
    data_files = list((output_dir / 'data').glob('*'))
    image_files = list((output_dir / 'images').glob('*'))
    
    assert len(data_files) > 0
    assert len(image_files) > 0


def test_extract_empty_notebook(empty_notebook, tmp_path):
    """Test extracting from a notebook with no outputs"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(empty_notebook),
        '--output', str(output_dir),
        '--all'
    ])
    
    # Should succeed even with no outputs
    assert result.exit_code == 0


def test_extract_default_output_dir(sample_notebook_with_outputs):
    """Test extracting with default output directory"""
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--all'
    ])
    
    assert result.exit_code == 0
    
    # Check default 'outputs' directory was created
    output_dir = Path('outputs')
    assert output_dir.exists()
    
    # Clean up
    import shutil
    if output_dir.exists():
        shutil.rmtree(output_dir)


def test_extract_interactive_mode(sample_notebook_with_outputs, tmp_path):
    """Test interactive mode when no flags are provided"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    # Simulate user choosing "images" 
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir)
    ], input='images\n')
    
    assert result.exit_code == 0
    
    # Check that only images directory was created
    assert (output_dir / 'images').exists()
    
    # Check that images were extracted
    image_files = list((output_dir / 'images').glob('*'))
    assert len(image_files) > 0


def test_extract_interactive_mode_both(sample_notebook_with_outputs, tmp_path):
    """Test interactive mode choosing 'both'"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    # Simulate user choosing "both"
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir)
    ], input='both\n')
    
    assert result.exit_code == 0
    
    # Check both directories exist
    assert (output_dir / 'data').exists()
    assert (output_dir / 'images').exists()
    
    # Check both types of files were extracted
    data_files = list((output_dir / 'data').glob('*'))
    image_files = list((output_dir / 'images').glob('*'))
    
    assert len(data_files) > 0
    assert len(image_files) > 0


def test_extract_nonexistent_notebook():
    """Test extracting from a non-existent notebook"""
    runner = CliRunner()
    result = runner.invoke(extract, [
        'nonexistent.ipynb'
    ])
    
    # Should fail because file doesn't exist
    assert result.exit_code != 0


def test_extract_png_content(sample_notebook_with_outputs, tmp_path):
    """Test that extracted PNG file is valid"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir),
        '--images'
    ])
    
    assert result.exit_code == 0
    
    # Find PNG file
    png_files = list((output_dir / 'images').glob('*.png'))
    assert len(png_files) > 0
    
    # Verify it's a valid PNG file (starts with PNG signature)
    with open(png_files[0], 'rb') as f:
        header = f.read(8)
        # PNG signature: 137 80 78 71 13 10 26 10
        assert header == b'\x89PNG\r\n\x1a\n', "Should be a valid PNG file"


def test_extract_json_content(sample_notebook_with_outputs, tmp_path):
    """Test that extracted JSON file is valid"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir),
        '--data'
    ])
    
    assert result.exit_code == 0
    
    # Find JSON file
    json_files = list((output_dir / 'data').glob('*.json'))
    assert len(json_files) > 0
    
    # Verify it's valid JSON
    with open(json_files[0], 'r') as f:
        data = json.load(f)
        assert isinstance(data, dict)
        assert 'name' in data
        assert data['name'] == 'test'


def test_extract_svg_content(sample_notebook_with_outputs, tmp_path):
    """Test that extracted SVG file is valid"""
    output_dir = tmp_path / "outputs"
    
    runner = CliRunner()
    result = runner.invoke(extract, [
        str(sample_notebook_with_outputs),
        '--output', str(output_dir),
        '--images'
    ])
    
    assert result.exit_code == 0
    
    # Find SVG file
    svg_files = list((output_dir / 'images').glob('*.svg'))
    assert len(svg_files) > 0
    
    # Verify it's valid SVG
    with open(svg_files[0], 'r') as f:
        content = f.read()
        assert '<svg' in content, "Should contain SVG tag"

