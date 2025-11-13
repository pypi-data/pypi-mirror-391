"""
Tests for the clean command
"""
import json
from pathlib import Path
import pytest
import nbformat
from nbutils.core.notebook import Notebook
from nbutils.core.cleaner import NotebookCleaner


@pytest.fixture
def sample_notebook(tmp_path):
    """Create a sample notebook with outputs"""
    nb = nbformat.v4.new_notebook()
    
    # Add a code cell with output
    code_cell = nbformat.v4.new_code_cell(
        source="print('hello')",
        execution_count=1,
        outputs=[
            nbformat.v4.new_output(
                output_type='stream',
                name='stdout',
                text='hello\n'
            )
        ]
    )
    nb.cells.append(code_cell)
    
    # Add a markdown cell
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    
    # Add metadata
    nb.metadata['custom_field'] = 'should be removed'
    code_cell.metadata['custom_cell_field'] = 'should be removed'
    
    # Save notebook
    nb_path = tmp_path / "test.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_clean_removes_outputs(sample_notebook):
    """Test that clean removes cell outputs"""
    # Load and clean
    nb = Notebook(sample_notebook)
    cleaner = NotebookCleaner(nb.nb)
    stats = cleaner.clean()
    
    # Check outputs were removed
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert len(code_cells[0].outputs) == 0
    assert stats['outputs_removed'] == 1


def test_clean_resets_execution_count(sample_notebook):
    """Test that clean resets execution counts"""
    nb = Notebook(sample_notebook)
    cleaner = NotebookCleaner(nb.nb)
    stats = cleaner.clean()
    
    # Check execution count was reset
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert code_cells[0].execution_count is None
    assert stats['execution_counts_reset'] == 1


def test_clean_removes_metadata(sample_notebook):
    """Test that clean removes unnecessary metadata"""
    nb = Notebook(sample_notebook)
    cleaner = NotebookCleaner(nb.nb)
    stats = cleaner.clean()
    
    # Check metadata was cleaned
    assert 'custom_field' not in nb.nb.metadata
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert 'custom_cell_field' not in code_cells[0].metadata
    assert stats['metadata_cleaned'] is True


def test_clean_keeps_markdown(sample_notebook):
    """Test that clean doesn't modify markdown cells"""
    nb = Notebook(sample_notebook)
    before_markdown = [c for c in nb.cells if c.cell_type == 'markdown'][0].source
    
    cleaner = NotebookCleaner(nb.nb)
    cleaner.clean()
    
    after_markdown = [c for c in nb.cells if c.cell_type == 'markdown'][0].source
    assert before_markdown == after_markdown


def test_clean_with_options(sample_notebook):
    """Test clean with different options"""
    nb = Notebook(sample_notebook)
    cleaner = NotebookCleaner(nb.nb)
    
    # Clean but keep outputs
    stats = cleaner.clean(remove_outputs=False)
    code_cells = [c for c in nb.cells if c.cell_type == 'code']
    assert len(code_cells[0].outputs) > 0
    assert stats['outputs_removed'] == 0
