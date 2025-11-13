"""
Tests for the info command
"""
import pytest
import nbformat
from nbutils.core.notebook import Notebook

@pytest.fixture
def sample_notebook(tmp_path):
    """Create a sample notebook with outputs, code, and imports"""
    nb = nbformat.v4.new_notebook()
    
    # Add a code cell with imports
    code_cell1 = nbformat.v4.new_code_cell(
        source="import numpy as np\nimport pandas as pd\nfrom pathlib import Path",
        execution_count=1,
        outputs=[
            nbformat.v4.new_output(
                output_type='stream',
                name='stdout',
                text='hello\n'
            )
        ]
    )
    nb.cells.append(code_cell1)
    
    # Add a code cell with more code
    code_cell2 = nbformat.v4.new_code_cell(
        source="# This is a comment\ndata = np.array([1, 2, 3])\nprint(data)",
        execution_count=2
    )
    nb.cells.append(code_cell2)
    
    # Add an empty code cell
    code_cell3 = nbformat.v4.new_code_cell(source="")
    nb.cells.append(code_cell3)
    
    # Add a markdown cell
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    
    # Add metadata
    nb.metadata['custom_field'] = 'should be removed'
    code_cell1.metadata['custom_cell_field'] = 'should be removed'
    
    # Save notebook
    nb_path = tmp_path / "test.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def simple_notebook(tmp_path):
    """Create a simple notebook with just one code cell"""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(source="x = 1\ny = 2\nz = x + y"))
    
    nb_path = tmp_path / "simple.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def empty_notebook(tmp_path):
    """Create an empty notebook"""
    nb = nbformat.v4.new_notebook()
    
    nb_path = tmp_path / "empty.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_get_stats(sample_notebook):
    """Test that get_stats returns correct statistics"""
    nb = Notebook(sample_notebook)
    stats = nb.get_stats()
    
    assert stats['total_cells'] == 4
    assert stats['code_cells'] == 3
    assert stats['markdown_cells'] == 1
    assert stats['raw_cells'] == 0
    assert stats['file_size'] > 0


def test_get_imports(sample_notebook):
    """Test that get_imports finds all import statements"""
    nb = Notebook(sample_notebook)
    imports = nb.get_imports()
    
    assert len(imports) == 3
    assert 'import numpy as np' in imports
    assert 'import pandas as pd' in imports
    assert 'from pathlib import Path' in imports


def test_get_imports_no_imports(simple_notebook):
    """Test get_imports with no imports"""
    nb = Notebook(simple_notebook)
    imports = nb.get_imports()
    
    assert len(imports) == 0


def test_get_code_metrics(sample_notebook):
    """Test that get_code_metrics returns correct metrics"""
    nb = Notebook(sample_notebook)
    metrics = nb.get_code_metrics()
    
    assert metrics['code_cells_count'] == 3
    assert metrics['total_lines'] == 6  # 3 imports + 3 lines in second cell
    assert metrics['avg_lines_per_cell'] == 2.0  # 6 lines / 3 cells
    assert metrics['empty_cells'] == 1
    assert metrics['largest_cell']['index'] is not None
    assert metrics['largest_cell']['lines'] == 3
    assert metrics['smallest_cell']['index'] is not None


def test_get_code_metrics_simple(simple_notebook):
    """Test code metrics on a simple notebook"""
    nb = Notebook(simple_notebook)
    metrics = nb.get_code_metrics()
    
    assert metrics['code_cells_count'] == 1
    assert metrics['total_lines'] == 3
    assert metrics['avg_lines_per_cell'] == 3.0
    assert metrics['empty_cells'] == 0
    assert metrics['largest_cell']['lines'] == 3
    assert metrics['smallest_cell']['lines'] == 3


def test_get_code_metrics_empty(empty_notebook):
    """Test code metrics on an empty notebook"""
    nb = Notebook(empty_notebook)
    metrics = nb.get_code_metrics()
    
    assert metrics['code_cells_count'] == 0
    assert metrics['total_lines'] == 0
    assert metrics['avg_lines_per_cell'] == 0.0
    assert metrics['empty_cells'] == 0
    assert metrics['largest_cell']['index'] is None
    assert metrics['smallest_cell']['index'] is None