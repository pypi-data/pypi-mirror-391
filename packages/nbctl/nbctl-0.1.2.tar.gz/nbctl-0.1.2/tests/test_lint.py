"""
Tests for the lint command
"""
import pytest
import nbformat
from click.testing import CliRunner
from nbutils.commands.lint import lint


@pytest.fixture
def clean_notebook(tmp_path):
    """Create a clean notebook with no issues"""
    nb = nbformat.v4.new_notebook()
    
    # Add a code cell with imports and usage
    nb.cells.append(nbformat.v4.new_code_cell(
        source="import numpy as np\nimport pandas as pd\n\ndata = np.array([1, 2, 3])\ndf = pd.DataFrame(data)"
    ))
    
    # Add a markdown cell
    nb.cells.append(nbformat.v4.new_markdown_cell("# Clean Notebook"))
    
    # Save notebook
    nb_path = tmp_path / "clean.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_unused_imports(tmp_path):
    """Create a notebook with unused imports"""
    nb = nbformat.v4.new_notebook()
    
    # Add a cell with unused imports
    nb.cells.append(nbformat.v4.new_code_cell(
        source="import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n# Only use numpy\ndata = np.array([1, 2, 3])"
    ))
    
    # Save notebook
    nb_path = tmp_path / "unused_imports.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_long_cell(tmp_path):
    """Create a notebook with a very long cell"""
    nb = nbformat.v4.new_notebook()
    
    # Add a cell with 120 lines
    long_code = "\n".join([f"x{i} = {i}" for i in range(120)])
    nb.cells.append(nbformat.v4.new_code_cell(source=long_code))
    
    # Save notebook
    nb_path = tmp_path / "long_cell.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_empty_cells(tmp_path):
    """Create a notebook with empty cells"""
    nb = nbformat.v4.new_notebook()
    
    # Add an empty cell
    nb.cells.append(nbformat.v4.new_code_cell(source=""))
    
    # Add a cell with only whitespace
    nb.cells.append(nbformat.v4.new_code_cell(source="   \n\n  "))
    
    # Add a normal cell
    nb.cells.append(nbformat.v4.new_code_cell(source="x = 1"))
    
    # Save notebook
    nb_path = tmp_path / "empty_cells.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_lint_clean_notebook(clean_notebook):
    """Test linting a notebook with no issues"""
    runner = CliRunner()
    result = runner.invoke(lint, [str(clean_notebook)])
    
    assert result.exit_code == 0
    assert "All checks passed" in result.output


def test_lint_unused_imports(notebook_with_unused_imports):
    """Test detecting unused imports"""
    runner = CliRunner()
    result = runner.invoke(lint, [str(notebook_with_unused_imports)])
    
    assert result.exit_code == 0
    assert "Unused import" in result.output
    # Should detect pandas and matplotlib as unused
    assert "pd" in result.output or "pandas" in result.output


def test_lint_long_cell(notebook_with_long_cell):
    """Test detecting cells that are too long"""
    runner = CliRunner()
    result = runner.invoke(lint, [str(notebook_with_long_cell)])
    
    assert result.exit_code == 0
    assert "Cell too long" in result.output
    assert "120 lines" in result.output


def test_lint_long_cell_custom_length(notebook_with_long_cell):
    """Test with custom max cell length"""
    runner = CliRunner()
    result = runner.invoke(lint, [
        str(notebook_with_long_cell),
        '--max-cell-length', '150'
    ])
    
    # Should pass with higher limit
    assert result.exit_code == 0
    assert "All checks passed" in result.output


def test_lint_empty_cells(notebook_with_empty_cells):
    """Test detecting empty cells"""
    runner = CliRunner()
    result = runner.invoke(lint, [str(notebook_with_empty_cells)])
    
    assert result.exit_code == 0
    assert "Empty code cell" in result.output


def test_lint_missing_notebook():
    """Test linting a non-existent notebook"""
    runner = CliRunner()
    result = runner.invoke(lint, ['nonexistent.ipynb'])
    
    # Should fail
    assert result.exit_code != 0

