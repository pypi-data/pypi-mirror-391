"""
Tests for the run command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.run import run


@pytest.fixture
def simple_notebook(tmp_path):
    """Create a simple executable notebook"""
    nb = nbformat.v4.new_notebook()
    
    # Add a code cell with simple execution
    nb.cells.append(nbformat.v4.new_code_cell(
        "x = 1 + 1\nprint(f'Result: {x}')"
    ))
    
    nb.cells.append(nbformat.v4.new_code_cell(
        "y = x * 2\nprint(f'Double: {y}')"
    ))
    
    # Save notebook
    nb_path = tmp_path / "simple.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def multiple_notebooks(tmp_path):
    """Create multiple simple notebooks"""
    notebooks = []
    
    for i in range(1, 4):
        nb = nbformat.v4.new_notebook()
        nb.cells.append(nbformat.v4.new_code_cell(
            f"result = {i} * 10\nprint(f'Notebook {i}: {{result}}')"
        ))
        
        nb_path = tmp_path / f"notebook_{i}.ipynb"
        with open(nb_path, 'w') as f:
            nbformat.write(nb, f)
        notebooks.append(nb_path)
    
    return notebooks


@pytest.fixture
def notebook_with_error(tmp_path):
    """Create a notebook that will fail"""
    nb = nbformat.v4.new_notebook()
    
    # Add a cell that will raise an error
    nb.cells.append(nbformat.v4.new_code_cell(
        "raise ValueError('Test error')"
    ))
    
    nb_path = tmp_path / "error.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_run_single_notebook(simple_notebook):
    """Test running a single notebook"""
    runner = CliRunner()
    result = runner.invoke(run, [str(simple_notebook)])
    
    # Check command succeeded
    assert result.exit_code == 0
    
    # Check output contains execution messages
    assert 'Executing' in result.output
    assert 'Completed successfully' in result.output
    assert 'Success' in result.output


def test_run_multiple_notebooks_specified_order(multiple_notebooks):
    """Test running multiple notebooks in specified order"""
    runner = CliRunner()
    result = runner.invoke(run, [str(nb) for nb in multiple_notebooks])
    
    assert result.exit_code == 0
    
    # Check all notebooks were executed
    assert 'notebook_1.ipynb' in result.output
    assert 'notebook_2.ipynb' in result.output
    assert 'notebook_3.ipynb' in result.output
    
    # Check summary
    assert 'Execution Summary' in result.output
    assert '3 notebooks' in result.output


def test_run_with_order_flag(multiple_notebooks, tmp_path):
    """Test running with alphabetical order"""
    # Create notebooks with non-alphabetical names
    nb_c = tmp_path / "c_notebook.ipynb"
    nb_a = tmp_path / "a_notebook.ipynb"
    nb_b = tmp_path / "b_notebook.ipynb"
    
    for nb_path in [nb_c, nb_a, nb_b]:
        nb = nbformat.v4.new_notebook()
        nb.cells.append(nbformat.v4.new_code_cell("print('test')"))
        with open(nb_path, 'w') as f:
            nbformat.write(nb, f)
    
    runner = CliRunner()
    # Pass in non-alphabetical order
    result = runner.invoke(run, [
        str(nb_c), str(nb_a), str(nb_b),
        '--order'
    ])
    
    assert result.exit_code == 0
    assert 'alphabetical order' in result.output


def test_run_with_save_output(simple_notebook, tmp_path):
    """Test saving executed notebooks to output directory"""
    output_dir = tmp_path / "executed"
    
    runner = CliRunner()
    result = runner.invoke(run, [
        str(simple_notebook),
        '--save-output', str(output_dir)
    ])
    
    assert result.exit_code == 0
    
    # Check output directory was created
    assert output_dir.exists()
    
    # Check executed notebook was saved
    output_file = output_dir / simple_notebook.name
    assert output_file.exists()
    
    # Load and verify it has outputs
    with open(output_file, 'r') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Check that cells have outputs
    assert len(nb.cells) > 0
    assert any(hasattr(cell, 'outputs') and cell.outputs for cell in nb.cells)


def test_run_with_error(notebook_with_error):
    """Test running a notebook that fails"""
    runner = CliRunner()
    result = runner.invoke(run, [str(notebook_with_error)])
    
    # Should fail
    assert result.exit_code != 0
    
    # Check error is reported
    assert 'Failed' in result.output


def test_run_with_allow_errors(notebook_with_error):
    """Test running with --allow-errors flag"""
    runner = CliRunner()
    result = runner.invoke(run, [
        str(notebook_with_error),
        '--allow-errors'
    ])
    
    # Should succeed despite errors
    assert result.exit_code == 0
    assert 'Completed successfully' in result.output


def test_run_with_timeout(tmp_path):
    """Test timeout handling"""
    # Create a notebook with a long-running cell
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(
        "import time\ntime.sleep(5)"
    ))
    
    nb_path = tmp_path / "slow.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    runner = CliRunner()
    # Set very short timeout
    result = runner.invoke(run, [
        str(nb_path),
        '--timeout', '1'
    ])
    
    # Should fail due to timeout
    assert result.exit_code != 0


def test_run_without_timeout(tmp_path):
    """Test running without timeout (default behavior)"""
    # Create a notebook with a slightly long cell
    nb = nbformat.v4.new_notebook()
    nb.cells.append(nbformat.v4.new_code_cell(
        "import time\ntime.sleep(0.5)\nprint('Done')"
    ))
    
    nb_path = tmp_path / "slow.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    runner = CliRunner()
    # No timeout specified - should complete
    result = runner.invoke(run, [str(nb_path)])
    
    # Should succeed - no timeout
    assert result.exit_code == 0
    assert 'Completed successfully' in result.output


def test_run_updates_original_notebook(simple_notebook):
    """Test that running without save-output updates the original"""
    # Read original (should have no outputs)
    with open(simple_notebook, 'r') as f:
        nb_before = nbformat.read(f, as_version=4)
    
    has_outputs_before = any(
        hasattr(cell, 'outputs') and cell.outputs 
        for cell in nb_before.cells
    )
    
    runner = CliRunner()
    result = runner.invoke(run, [str(simple_notebook)])
    
    assert result.exit_code == 0
    
    # Read after execution
    with open(simple_notebook, 'r') as f:
        nb_after = nbformat.read(f, as_version=4)
    
    has_outputs_after = any(
        hasattr(cell, 'outputs') and cell.outputs 
        for cell in nb_after.cells
    )
    
    # Should now have outputs
    assert has_outputs_after


def test_run_nonexistent_notebook():
    """Test running a non-existent notebook"""
    runner = CliRunner()
    result = runner.invoke(run, ['nonexistent.ipynb'])
    
    # Should fail
    assert result.exit_code != 0


def test_run_execution_summary(multiple_notebooks):
    """Test that execution summary is displayed"""
    runner = CliRunner()
    result = runner.invoke(run, [str(nb) for nb in multiple_notebooks])
    
    assert result.exit_code == 0
    
    # Check summary components
    assert 'Execution Summary' in result.output
    assert 'Notebook' in result.output
    assert 'Status' in result.output
    assert 'Time' in result.output
    assert 'Total' in result.output
    assert 'Successful' in result.output

