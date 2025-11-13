"""
Tests for the format command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.format import format


@pytest.fixture
def unformatted_notebook(tmp_path):
    """Create a notebook with unformatted code"""
    nb = nbformat.v4.new_notebook()
    
    # Add a cell with poorly formatted code
    nb.cells.append(nbformat.v4.new_code_cell(
        source="x=1+2\ny  =   3+4\nz=x+y"
    ))
    
    # Add another cell with long lines
    nb.cells.append(nbformat.v4.new_code_cell(
        source='result = some_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10)'
    ))
    
    # Add a markdown cell
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    
    # Save notebook
    nb_path = tmp_path / "unformatted.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def formatted_notebook(tmp_path):
    """Create a notebook with already formatted code"""
    nb = nbformat.v4.new_notebook()
    
    # Add a cell with properly formatted code
    nb.cells.append(nbformat.v4.new_code_cell(
        source="x = 1 + 2\ny = 3 + 4\nz = x + y\n"
    ))
    
    # Save notebook
    nb_path = tmp_path / "formatted.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def empty_cell_notebook(tmp_path):
    """Create a notebook with empty cells"""
    nb = nbformat.v4.new_notebook()
    
    # Add an empty cell
    nb.cells.append(nbformat.v4.new_code_cell(source=""))
    
    # Add a cell with code
    nb.cells.append(nbformat.v4.new_code_cell(source="x=1"))
    
    # Save notebook
    nb_path = tmp_path / "empty.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_format_notebook(unformatted_notebook):
    """Test formatting a notebook"""
    runner = CliRunner()
    result = runner.invoke(format, [str(unformatted_notebook)])
    
    assert result.exit_code == 0
    assert "Formatted" in result.output
    
    # Read the formatted notebook
    import nbformat
    with open(unformatted_notebook, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Check that code is formatted
    first_cell = nb.cells[0].source
    assert "x = 1 + 2" in first_cell  # Should have spaces


def test_format_with_output_dir(unformatted_notebook, tmp_path):
    """Test formatting to a different directory"""
    output_dir = tmp_path / "formatted"
    
    runner = CliRunner()
    result = runner.invoke(format, [
        str(unformatted_notebook),
        '--output-dir', str(output_dir)
    ])
    
    assert result.exit_code == 0
    
    # Check output file exists in the directory
    output_file = output_dir / "unformatted.ipynb"
    assert output_file.exists()
    
    # Original should be unchanged
    import nbformat
    with open(unformatted_notebook, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    assert "x=1+2" in nb.cells[0].source  # Still unformatted


def test_format_already_formatted(formatted_notebook):
    """Test formatting an already formatted notebook"""
    runner = CliRunner()
    result = runner.invoke(format, [str(formatted_notebook)])
    
    assert result.exit_code == 0
    assert "already formatted" in result.output


def test_format_with_custom_line_length(unformatted_notebook):
    """Test with custom line length"""
    runner = CliRunner()
    result = runner.invoke(format, [
        str(unformatted_notebook),
        '--line-length', '100'
    ])
    
    assert result.exit_code == 0


def test_format_empty_cells(empty_cell_notebook):
    """Test formatting notebook with empty cells"""
    runner = CliRunner()
    result = runner.invoke(format, [str(empty_cell_notebook)])
    
    # Should not fail on empty cells
    assert result.exit_code == 0


def test_format_missing_notebook():
    """Test formatting a non-existent notebook"""
    runner = CliRunner()
    result = runner.invoke(format, ['nonexistent.ipynb'])
    
    # Should fail
    assert result.exit_code != 0

