"""
Tests for the export command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.export import export


@pytest.fixture
def sample_notebook(tmp_path):
    """Create a sample notebook for export testing"""
    nb = nbformat.v4.new_notebook()
    
    # Add a markdown cell
    nb.cells.append(nbformat.v4.new_markdown_cell("# Test Notebook\n\nThis is a test."))
    
    # Add a code cell
    code_cell = nbformat.v4.new_code_cell(
        source="x = 1\ny = 2\nprint(x + y)",
        execution_count=1,
        outputs=[
            nbformat.v4.new_output(
                output_type='stream',
                name='stdout',
                text='3\n'
            )
        ]
    )
    nb.cells.append(code_cell)
    
    # Save notebook
    nb_path = tmp_path / "test.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_export_html(sample_notebook):
    """Test exporting to HTML format"""
    runner = CliRunner()
    result = runner.invoke(export, [
        str(sample_notebook),
        '--format', 'html'
    ])
    
    # Check command succeeded
    assert result.exit_code == 0
    
    # Check output file was created
    html_file = sample_notebook.parent / "test.html"
    assert html_file.exists()
    
    # Check file has content
    assert html_file.stat().st_size > 0
    
    # Verify it's HTML
    content = html_file.read_text()
    assert '<html>' in content.lower() or '<!doctype html>' in content.lower()


def test_export_markdown(sample_notebook):
    """Test exporting to Markdown format"""
    runner = CliRunner()
    result = runner.invoke(export, [
        str(sample_notebook),
        '--format', 'markdown'
    ])
    
    assert result.exit_code == 0
    
    # Check output file was created
    md_file = sample_notebook.parent / "test.md"
    assert md_file.exists()
    assert md_file.stat().st_size > 0
    
    # Verify it's Markdown
    content = md_file.read_text()
    assert '# Test Notebook' in content


def test_export_latex(sample_notebook):
    """Test exporting to LaTeX format"""
    runner = CliRunner()
    result = runner.invoke(export, [
        str(sample_notebook),
        '--format', 'latex'
    ])
    
    assert result.exit_code == 0
    
    # Check output file was created
    tex_file = sample_notebook.parent / "test.tex"
    assert tex_file.exists()
    assert tex_file.stat().st_size > 0
    
    # Verify it's LaTeX
    content = tex_file.read_text()
    assert '\\documentclass' in content or '\\begin{document}' in content


def test_export_multiple_formats(sample_notebook):
    """Test exporting to multiple formats at once"""
    runner = CliRunner()
    result = runner.invoke(export, [
        str(sample_notebook),
        '--format', 'html,markdown,latex'
    ])
    
    assert result.exit_code == 0
    
    # Check all output files were created
    html_file = sample_notebook.parent / "test.html"
    md_file = sample_notebook.parent / "test.md"
    tex_file = sample_notebook.parent / "test.tex"
    
    assert html_file.exists()
    assert md_file.exists()
    assert tex_file.exists()
    
    assert html_file.stat().st_size > 0
    assert md_file.stat().st_size > 0
    assert tex_file.stat().st_size > 0


def test_export_with_output_dir(sample_notebook, tmp_path):
    """Test exporting to a specific output directory"""
    output_dir = tmp_path / "exports"
    
    runner = CliRunner()
    result = runner.invoke(export, [
        str(sample_notebook),
        '--format', 'html',
        '--output-dir', str(output_dir)
    ])
    
    assert result.exit_code == 0
    
    # Check output directory was created
    assert output_dir.exists()
    
    # Check output file is in the directory
    html_file = output_dir / "test.html"
    assert html_file.exists()


def test_export_invalid_format(sample_notebook):
    """Test exporting with an invalid format"""
    runner = CliRunner()
    result = runner.invoke(export, [
        str(sample_notebook),
        '--format', 'invalid_format'
    ])
    
    # Command runs but shows error message (exit code 0 but with error output)
    assert 'Unsupported format' in result.output or 'Error' in result.output


def test_export_missing_notebook():
    """Test exporting a non-existent notebook"""
    runner = CliRunner()
    result = runner.invoke(export, [
        'nonexistent.ipynb',
        '--format', 'html'
    ])
    
    # Should fail because file doesn't exist
    assert result.exit_code != 0
