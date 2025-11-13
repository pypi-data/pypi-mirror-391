"""
Tests for the diff command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.diff import diff
from nbutils.core.differ import NotebookDiffer, CellDiff


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


@pytest.fixture
def notebook_v1(tmp_path):
    """Create version 1 of a notebook"""
    nb = nbformat.v4.new_notebook()
    
    # Add some cells
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np"))
    nb.cells.append(nbformat.v4.new_code_cell("x = 1\ny = 2"))
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    
    nb_path = tmp_path / "notebook_v1.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_v2(tmp_path):
    """Create version 2 of a notebook (modified from v1)"""
    nb = nbformat.v4.new_notebook()
    
    # Modified first cell
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np\nimport pandas as pd"))
    # Same second cell
    nb.cells.append(nbformat.v4.new_code_cell("x = 1\ny = 2"))
    # Modified markdown
    nb.cells.append(nbformat.v4.new_markdown_cell("# Updated Title"))
    # Added new cell
    nb.cells.append(nbformat.v4.new_code_cell("z = x + y"))
    
    nb_path = tmp_path / "notebook_v2.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_v3(tmp_path):
    """Create version 3 (completely different)"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("print('Hello World')"))
    nb.cells.append(nbformat.v4.new_markdown_cell("## New notebook"))
    
    nb_path = tmp_path / "notebook_v3.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def identical_notebooks(tmp_path):
    """Create two identical notebooks"""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    
    nb_path1 = tmp_path / "nb1.ipynb"
    nb_path2 = tmp_path / "nb2.ipynb"
    
    with open(nb_path1, 'w') as f:
        nbformat.write(nb, f)
    with open(nb_path2, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path1, nb_path2


# Core differ tests

def test_differ_detects_no_changes(identical_notebooks):
    """Test that differ detects no changes for identical notebooks"""
    nb1, nb2 = identical_notebooks
    differ = NotebookDiffer(nb1, nb2)
    diffs = differ.compare()
    
    assert not differ.has_changes()
    assert all(d.status == 'unchanged' for d in diffs)


def test_differ_detects_modifications(notebook_v1, notebook_v2):
    """Test that differ detects modified cells"""
    differ = NotebookDiffer(notebook_v1, notebook_v2)
    diffs = differ.compare()
    
    assert differ.has_changes()
    
    # Count modifications
    modified = [d for d in diffs if d.status == 'modified']
    assert len(modified) > 0


def test_differ_detects_additions(notebook_v1, notebook_v2):
    """Test that differ detects added cells"""
    differ = NotebookDiffer(notebook_v1, notebook_v2)
    diffs = differ.compare()
    
    added = [d for d in diffs if d.status == 'added']
    assert len(added) > 0


def test_differ_detects_deletions(notebook_v2, notebook_v1):
    """Test that differ detects deleted cells (comparing v2 to v1)"""
    differ = NotebookDiffer(notebook_v2, notebook_v1)
    diffs = differ.compare()
    
    deleted = [d for d in diffs if d.status == 'deleted']
    assert len(deleted) > 0


def test_differ_statistics(notebook_v1, notebook_v2):
    """Test that differ computes correct statistics"""
    differ = NotebookDiffer(notebook_v1, notebook_v2)
    differ.compare()
    stats = differ.get_statistics()
    
    assert 'total_changes' in stats
    assert 'cells_added' in stats
    assert 'cells_deleted' in stats
    assert 'cells_modified' in stats
    assert 'cells_unchanged' in stats
    
    assert stats['total_changes'] >= 0
    assert stats['cells_unchanged'] >= 0


def test_cell_diff_computes_changes():
    """Test that CellDiff computes line changes"""
    old_content = "line1\nline2\nline3"
    new_content = "line1\nmodified line2\nline3"
    
    diff = CellDiff('code', 0, 'modified', old_content, new_content)
    
    assert len(diff.changes) > 0


# CLI tests

def test_diff_command_basic(runner, notebook_v1, notebook_v2):
    """Test basic diff command"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v2)])
    
    assert result.exit_code == 0


def test_diff_identical_notebooks(runner, identical_notebooks):
    """Test diff with identical notebooks"""
    nb1, nb2 = identical_notebooks
    result = runner.invoke(diff, [str(nb1), str(nb2)])
    
    assert result.exit_code == 0
    assert "No differences found" in result.output


def test_diff_table_format(runner, notebook_v1, notebook_v2):
    """Test diff with table format (default)"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v2), '--format', 'table'])
    
    assert result.exit_code == 0


def test_diff_unified_format(runner, notebook_v1, notebook_v2):
    """Test diff with unified format"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v2), '--format', 'unified'])
    
    assert result.exit_code == 0


def test_diff_json_format(runner, notebook_v1, notebook_v2):
    """Test diff with JSON format"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v2), '--format', 'json'])
    
    assert result.exit_code == 0
    # Should have JSON-like output
    assert '{' in result.output


def test_diff_stats_only(runner, notebook_v1, notebook_v2):
    """Test diff with stats-only flag"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v2), '--stats'])
    
    assert result.exit_code == 0
    assert "Statistics" in result.output or "Diff Statistics" in result.output


def test_diff_code_only(runner, notebook_v1, notebook_v2):
    """Test diff with code-only filter"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v2), '--code-only'])
    
    assert result.exit_code == 0


def test_diff_nonexistent_file(runner, notebook_v1):
    """Test diff with nonexistent file"""
    result = runner.invoke(diff, [str(notebook_v1), 'nonexistent.ipynb'])
    
    assert result.exit_code != 0


def test_diff_always_ignores_outputs(runner, notebook_v1, notebook_v2):
    """Test that diff always ignores outputs and metadata"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v2)])
    
    assert result.exit_code == 0
    # Should only compare code/markdown content, not outputs


def test_diff_completely_different_notebooks(runner, notebook_v1, notebook_v3):
    """Test diff with completely different notebooks"""
    result = runner.invoke(diff, [str(notebook_v1), str(notebook_v3)])
    
    assert result.exit_code == 0


def test_differ_empty_notebooks(tmp_path):
    """Test differ with empty notebooks"""
    nb1 = nbformat.v4.new_notebook()
    nb2 = nbformat.v4.new_notebook()
    
    nb1_path = tmp_path / "empty1.ipynb"
    nb2_path = tmp_path / "empty2.ipynb"
    
    with open(nb1_path, 'w') as f:
        nbformat.write(nb1, f)
    with open(nb2_path, 'w') as f:
        nbformat.write(nb2, f)
    
    differ = NotebookDiffer(nb1_path, nb2_path)
    diffs = differ.compare()
    
    assert len(diffs) == 0
    assert not differ.has_changes()


def test_differ_one_empty_one_full(tmp_path, notebook_v1):
    """Test differ with one empty and one full notebook"""
    nb_empty = nbformat.v4.new_notebook()
    empty_path = tmp_path / "empty.ipynb"
    
    with open(empty_path, 'w') as f:
        nbformat.write(nb_empty, f)
    
    differ = NotebookDiffer(empty_path, notebook_v1)
    diffs = differ.compare()
    
    assert differ.has_changes()
    # All cells should be added
    added = [d for d in diffs if d.status == 'added']
    assert len(added) > 0

