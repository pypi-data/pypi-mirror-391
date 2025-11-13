"""
Tests for the combine command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.combine import combine


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


@pytest.fixture
def notebook1(tmp_path):
    """Create first notebook"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np"))
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    nb.cells.append(nbformat.v4.new_markdown_cell("# Notebook 1"))
    
    nb_path = tmp_path / "notebook1.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook2(tmp_path):
    """Create second notebook"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("import pandas as pd"))
    nb.cells.append(nbformat.v4.new_code_cell("y = 2"))
    nb.cells.append(nbformat.v4.new_markdown_cell("# Notebook 2"))
    
    nb_path = tmp_path / "notebook2.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


# CLI tests

def test_combine_append_strategy(runner, notebook1, notebook2, tmp_path):
    """Test combine with append strategy (default)"""
    output = tmp_path / "combined.ipynb"
    
    result = runner.invoke(combine, [
        str(notebook1),
        str(notebook2),
        '--output', str(output),
    ])
    
    assert result.exit_code == 0
    assert output.exists()
    
    # Verify combined notebook has cells from both
    with open(output, 'r') as f:
        nb = nbformat.read(f, as_version=4)
        # Should have cells from both notebooks + separator
        assert len(nb.cells) >= 6  # 3 from each + separator


def test_combine_append_explicit(runner, notebook1, notebook2, tmp_path):
    """Test combine with explicit append strategy"""
    output = tmp_path / "combined.ipynb"
    
    result = runner.invoke(combine, [
        str(notebook1),
        str(notebook2),
        '--output', str(output),
        '--strategy', 'append',
    ])
    
    assert result.exit_code == 0
    assert output.exists()


def test_combine_first_strategy(runner, notebook1, notebook2, tmp_path):
    """Test combine with 'first' strategy"""
    output = tmp_path / "combined.ipynb"
    
    result = runner.invoke(combine, [
        str(notebook1),
        str(notebook2),
        '--output', str(output),
        '--strategy', 'first',
    ])
    
    assert result.exit_code == 0
    assert output.exists()
    
    # Verify only first notebook content
    with open(output, 'r') as f:
        nb = nbformat.read(f, as_version=4)
        assert len(nb.cells) == 3  # Only from notebook1
        assert 'numpy' in nb.cells[0].source


def test_combine_second_strategy(runner, notebook1, notebook2, tmp_path):
    """Test combine with 'second' strategy"""
    output = tmp_path / "combined.ipynb"
    
    result = runner.invoke(combine, [
        str(notebook1),
        str(notebook2),
        '--output', str(output),
        '--strategy', 'second',
    ])
    
    assert result.exit_code == 0
    assert output.exists()
    
    # Verify only second notebook content
    with open(output, 'r') as f:
        nb = nbformat.read(f, as_version=4)
        assert len(nb.cells) == 3  # Only from notebook2
        assert 'pandas' in nb.cells[0].source


def test_combine_with_report(runner, notebook1, notebook2, tmp_path):
    """Test combine with detailed report"""
    output = tmp_path / "combined.ipynb"
    
    result = runner.invoke(combine, [
        str(notebook1),
        str(notebook2),
        '--output', str(output),
        '--report',
    ])
    
    assert result.exit_code == 0
    assert "Report" in result.output or "Combine" in result.output


def test_combine_missing_output_flag(runner, notebook1, notebook2):
    """Test combine without required output flag"""
    result = runner.invoke(combine, [
        str(notebook1),
        str(notebook2)
    ])
    
    assert result.exit_code != 0


def test_combine_nonexistent_file(runner, notebook1, tmp_path):
    """Test combine with nonexistent file"""
    output = tmp_path / "combined.ipynb"
    
    result = runner.invoke(combine, [
        str(notebook1),
        'nonexistent.ipynb',
        '--output', str(output),
    ])
    
    assert result.exit_code != 0


def test_combine_identical_notebooks(runner, tmp_path):
    """Test combining identical notebooks"""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    
    nb1 = tmp_path / "nb1.ipynb"
    nb2 = tmp_path / "nb2.ipynb"
    output = tmp_path / "combined.ipynb"
    
    for path in [nb1, nb2]:
        with open(path, 'w') as f:
            nbformat.write(nb, f)
    
    result = runner.invoke(combine, [
        str(nb1), str(nb2),
        '--output', str(output),
    ])
    
    assert result.exit_code == 0
    assert output.exists()


def test_combine_empty_notebooks(runner, tmp_path):
    """Test combining empty notebooks"""
    nb1 = tmp_path / "empty1.ipynb"
    nb2 = tmp_path / "empty2.ipynb"
    output = tmp_path / "combined.ipynb"
    
    empty = nbformat.v4.new_notebook()
    
    for path in [nb1, nb2]:
        with open(path, 'w') as f:
            nbformat.write(empty, f)
    
    result = runner.invoke(combine, [
        str(nb1), str(nb2),
        '--output', str(output),
    ])
    
    assert result.exit_code == 0
    assert output.exists()


def test_combine_preserves_cell_types(runner, tmp_path):
    """Test that combine preserves different cell types"""
    nb1 = nbformat.v4.new_notebook()
    nb1.cells.append(nbformat.v4.new_code_cell("code1"))
    nb1.cells.append(nbformat.v4.new_markdown_cell("# markdown1"))
    
    nb2 = nbformat.v4.new_notebook()
    nb2.cells.append(nbformat.v4.new_code_cell("code2"))
    nb2.cells.append(nbformat.v4.new_markdown_cell("# markdown2"))
    
    nb1_path = tmp_path / "nb1.ipynb"
    nb2_path = tmp_path / "nb2.ipynb"
    output = tmp_path / "combined.ipynb"
    
    with open(nb1_path, 'w') as f:
        nbformat.write(nb1, f)
    with open(nb2_path, 'w') as f:
        nbformat.write(nb2, f)
    
    result = runner.invoke(combine, [
        str(nb1_path), str(nb2_path),
        '--output', str(output),
    ])
    
    assert result.exit_code == 0
    
    # Check that all cell types are preserved
    with open(output, 'r') as f:
        nb = nbformat.read(f, as_version=4)
        code_cells = [c for c in nb.cells if c.cell_type == 'code']
        markdown_cells = [c for c in nb.cells if c.cell_type == 'markdown']
        
        assert len(code_cells) >= 2
        assert len(markdown_cells) >= 2


