"""
Tests for the resolve command (3-way merge with conflict detection)
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.resolve import resolve
from nbutils.core.merger import NotebookMerger, MergeConflict


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


@pytest.fixture
def base_notebook(tmp_path):
    """Create base notebook (common ancestor)"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np"))
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    
    nb_path = tmp_path / "base.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def ours_notebook(tmp_path):
    """Create our version (modified from base)"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np"))
    nb.cells.append(nbformat.v4.new_code_cell("x = 2"))  # Changed
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    
    nb_path = tmp_path / "ours.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def theirs_notebook(tmp_path):
    """Create their version (modified from base)"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np\nimport pandas as pd"))  # Changed
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    
    nb_path = tmp_path / "theirs.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def conflicting_ours(tmp_path):
    """Create our version with conflicting changes"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np"))
    nb.cells.append(nbformat.v4.new_code_cell("x = 2\ny = 3"))  # Changed same cell
    
    nb_path = tmp_path / "ours_conflict.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def conflicting_theirs(tmp_path):
    """Create their version with conflicting changes"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np"))
    nb.cells.append(nbformat.v4.new_code_cell("x = 5\ny = 6"))  # Changed same cell differently
    
    nb_path = tmp_path / "theirs_conflict.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def simple_base(tmp_path):
    """Create simple base for conflict testing"""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("import numpy as np"))
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    
    nb_path = tmp_path / "simple_base.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


# Core merger tests (using nbdime backend)

def test_merger_auto_merge_no_conflicts(base_notebook, ours_notebook, theirs_notebook):
    """Test automatic merge with no conflicts"""
    merger = NotebookMerger(base_notebook, ours_notebook, theirs_notebook)
    merged = merger.merge(strategy='auto')
    
    assert merged is not None
    assert len(merged.cells) > 0


def test_merger_detects_conflicts(simple_base, conflicting_ours, conflicting_theirs):
    """Test that merger detects conflicts"""
    merger = NotebookMerger(simple_base, conflicting_ours, conflicting_theirs)
    merged = merger.merge(strategy='auto')
    
    assert merger.has_conflicts()
    assert len(merger.conflicts) > 0


def test_merger_no_conflicts_different_cells(base_notebook, ours_notebook, theirs_notebook):
    """Test merge when different cells are modified"""
    merger = NotebookMerger(base_notebook, ours_notebook, theirs_notebook)
    merged = merger.merge(strategy='auto')
    
    # Should merge successfully without conflicts
    # (ours changed cell 2, theirs changed cell 1)
    stats = merger.get_statistics()
    assert stats['cells_from_ours'] > 0 or stats['cells_from_theirs'] > 0


def test_merger_strategy_ours(base_notebook, ours_notebook, theirs_notebook):
    """Test merge with 'ours' strategy"""
    merger = NotebookMerger(base_notebook, ours_notebook, theirs_notebook)
    merged = merger.merge(strategy='ours')
    
    assert merged is not None
    assert len(merged.cells) == len(merger.ours_nb.cells)


def test_merger_strategy_theirs(base_notebook, ours_notebook, theirs_notebook):
    """Test merge with 'theirs' strategy"""
    merger = NotebookMerger(base_notebook, ours_notebook, theirs_notebook)
    merged = merger.merge(strategy='theirs')
    
    assert merged is not None
    assert len(merged.cells) == len(merger.theirs_nb.cells)


def test_merger_strategy_cell_append(base_notebook, ours_notebook, theirs_notebook):
    """Test merge with 'cell-append' strategy"""
    merger = NotebookMerger(base_notebook, ours_notebook, theirs_notebook)
    merged = merger.merge(strategy='cell-append')
    
    assert merged is not None
    # Should have cells from both + separator
    assert len(merged.cells) >= len(merger.ours_nb.cells) + len(merger.theirs_nb.cells)


def test_merger_statistics(base_notebook, ours_notebook, theirs_notebook):
    """Test that merger computes correct statistics"""
    merger = NotebookMerger(base_notebook, ours_notebook, theirs_notebook)
    merger.merge(strategy='auto')
    stats = merger.get_statistics()
    
    assert 'cells_merged' in stats
    assert 'conflicts' in stats
    assert 'cells_from_ours' in stats
    assert 'cells_from_theirs' in stats
    assert 'cells_unchanged' in stats


def test_merge_conflict_creates_markers(simple_base, conflicting_ours, conflicting_theirs):
    """Test that conflicts create proper markers"""
    merger = NotebookMerger(simple_base, conflicting_ours, conflicting_theirs)
    merged = merger.merge(strategy='auto')
    
    if merger.has_conflicts():
        # Check that at least one cell has conflict markers (nbdime uses 'local' and 'remote')
        has_conflict_marker = any(
            ('<<<<<<< local' in cell.source or '<<<<<<< OURS' in cell.source or 
             '>>>>>>> remote' in cell.source or '>>>>>>> THEIRS' in cell.source)
            for cell in merged.cells
        )
        assert has_conflict_marker


def test_merger_save(base_notebook, ours_notebook, theirs_notebook, tmp_path):
    """Test saving merged notebook"""
    merger = NotebookMerger(base_notebook, ours_notebook, theirs_notebook)
    merger.merge(strategy='auto')
    
    output_path = tmp_path / "merged.ipynb"
    merger.save(output_path)
    
    assert output_path.exists()
    
    # Verify it's a valid notebook
    with open(output_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)
        assert nb is not None


def test_merge_conflict_class():
    """Test MergeConflict class"""
    conflict = MergeConflict(
        cell_index=0,
        cell_type='code',
        base_content='x = 1',
        ours_content='x = 2',
        theirs_content='x = 3'
    )
    
    assert conflict.cell_index == 0
    assert conflict.cell_type == 'code'
    
    # Test creating conflict cell
    cell = conflict.create_conflict_cell()
    assert '<<<<<<< OURS' in cell.source
    assert '>>>>>>> THEIRS' in cell.source
    assert 'x = 2' in cell.source
    assert 'x = 3' in cell.source


# CLI tests

def test_resolve_command_basic(runner, base_notebook, ours_notebook, theirs_notebook, tmp_path):
    """Test basic resolve command"""
    output = tmp_path / "merged.ipynb"
    
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        str(theirs_notebook),
        '--output', str(output),
    ])
    
    assert result.exit_code == 0 or result.exit_code == 1  # May have conflicts
    assert output.exists()


def test_resolve_strategy_ours_cli(runner, base_notebook, ours_notebook, theirs_notebook, tmp_path):
    """Test resolve with ours strategy via CLI"""
    output = tmp_path / "merged.ipynb"
    
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        str(theirs_notebook),
        '--output', str(output),
        '--strategy', 'ours',
    ])
    
    assert result.exit_code == 0
    assert output.exists()


def test_resolve_strategy_theirs_cli(runner, base_notebook, ours_notebook, theirs_notebook, tmp_path):
    """Test resolve with theirs strategy via CLI"""
    output = tmp_path / "merged.ipynb"
    
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        str(theirs_notebook),
        '--output', str(output),
        '--strategy', 'theirs',
    ])
    
    assert result.exit_code == 0
    assert output.exists()


def test_resolve_strategy_cell_append_cli(runner, base_notebook, ours_notebook, theirs_notebook, tmp_path):
    """Test resolve with cell-append strategy via CLI"""
    output = tmp_path / "merged.ipynb"
    
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        str(theirs_notebook),
        '--output', str(output),
        '--strategy', 'cell-append',
    ])
    
    assert result.exit_code == 0
    assert output.exists()


def test_resolve_check_conflicts(runner, simple_base, conflicting_ours, conflicting_theirs):
    """Test resolve conflict checking"""
    result = runner.invoke(resolve, [
        str(simple_base),
        str(conflicting_ours),
        str(conflicting_theirs),
        '--check-conflicts',
    ])
    
    # Should output conflict information
    assert "conflict" in result.output.lower()


def test_resolve_with_report(runner, base_notebook, ours_notebook, theirs_notebook, tmp_path):
    """Test resolve with detailed report"""
    output = tmp_path / "merged.ipynb"
    
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        str(theirs_notebook),
        '--output', str(output),
        '--report',
    ])
    
    assert result.exit_code in [0, 1]
    assert "Report" in result.output or "Merge" in result.output


def test_resolve_missing_output_flag(runner, base_notebook, ours_notebook, theirs_notebook):
    """Test resolve without required output flag (should work with --check-conflicts)"""
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        str(theirs_notebook),
        '--check-conflicts'
    ])
    
    # Should succeed with --check-conflicts
    assert result.exit_code == 0


def test_resolve_nonexistent_file(runner, base_notebook, ours_notebook, tmp_path):
    """Test resolve with nonexistent file"""
    output = tmp_path / "merged.ipynb"
    
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        'nonexistent.ipynb',
        '--output', str(output),
    ])
    
    assert result.exit_code != 0


def test_resolve_identical_notebooks(runner, tmp_path):
    """Test resolving identical notebooks"""
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell("x = 1"))
    
    base = tmp_path / "base.ipynb"
    ours = tmp_path / "ours.ipynb"
    theirs = tmp_path / "theirs.ipynb"
    output = tmp_path / "merged.ipynb"
    
    for path in [base, ours, theirs]:
        with open(path, 'w') as f:
            nbformat.write(nb, f)
    
    result = runner.invoke(resolve, [
        str(base), str(ours), str(theirs),
        '--output', str(output),
    ])
    
    assert result.exit_code == 0
    assert output.exists()


def test_resolve_requires_three_notebooks(runner, base_notebook, ours_notebook, tmp_path):
    """Test that resolve requires all three notebooks"""
    output = tmp_path / "merged.ipynb"
    
    # Try with only two notebooks
    result = runner.invoke(resolve, [
        str(base_notebook),
        str(ours_notebook),
        '--output', str(output),
    ])
    
    assert result.exit_code != 0


