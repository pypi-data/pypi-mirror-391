"""
Tests for the ml-split command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.ml_split import ml_split


@pytest.fixture
def ml_notebook(tmp_path):
    """Create a sample ML notebook"""
    nb = nbformat.v4.new_notebook()
    
    # Data Collection section
    nb.cells.append(nbformat.v4.new_markdown_cell("# Data Collection"))
    nb.cells.append(nbformat.v4.new_code_cell(
        "import pandas as pd\n"
        "import numpy as np\n"
        "df = pd.read_csv('data.csv')"
    ))
    
    # Feature Engineering section
    nb.cells.append(nbformat.v4.new_markdown_cell("## Feature Engineering"))
    nb.cells.append(nbformat.v4.new_code_cell(
        "from sklearn.preprocessing import StandardScaler\n"
        "scaler = StandardScaler()\n"
        "X = scaler.fit_transform(df)"
    ))
    
    # Model Training section
    nb.cells.append(nbformat.v4.new_markdown_cell("### Model Training"))
    nb.cells.append(nbformat.v4.new_code_cell(
        "from sklearn.ensemble import RandomForestClassifier\n"
        "model = RandomForestClassifier()\n"
        "model.fit(X_train, y_train)"
    ))
    
    # Model Evaluation section
    nb.cells.append(nbformat.v4.new_markdown_cell("## Model Evaluation"))
    nb.cells.append(nbformat.v4.new_code_cell(
        "from sklearn.metrics import accuracy_score\n"
        "y_pred = model.predict(X_test)\n"
        "accuracy = accuracy_score(y_test, y_pred)"
    ))
    
    # Save notebook
    nb_path = tmp_path / "ml_notebook.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


def test_ml_split_basic(ml_notebook, tmp_path):
    """Test basic ML split functionality"""
    output_dir = tmp_path / "ml_pipeline"
    
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        str(ml_notebook),
        '--output', str(output_dir)
    ])
    
    # Check command succeeded
    assert result.exit_code == 0
    
    # Check output directory was created
    assert output_dir.exists()
    
    # Check essential files exist
    assert (output_dir / '__init__.py').exists()
    assert (output_dir / 'main.py').exists()
    assert (output_dir / 'requirements.txt').exists()


def test_ml_split_detects_sections(ml_notebook, tmp_path):
    """Test that ML sections are correctly detected"""
    output_dir = tmp_path / "ml_pipeline"
    
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        str(ml_notebook),
        '--output', str(output_dir)
    ])
    
    assert result.exit_code == 0
    
    # Check specific section files were created
    assert (output_dir / 'data_collection.py').exists()
    assert (output_dir / 'feature_engineering.py').exists()
    assert (output_dir / 'model_training.py').exists()
    assert (output_dir / 'model_evaluation.py').exists()


def test_ml_split_file_content(ml_notebook, tmp_path):
    """Test that generated files have correct content"""
    output_dir = tmp_path / "ml_pipeline"
    
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        str(ml_notebook),
        '--output', str(output_dir)
    ])
    
    assert result.exit_code == 0
    
    # Check data_collection.py content
    data_collection_file = output_dir / 'data_collection.py'
    content = data_collection_file.read_text()
    
    assert 'def run(context=None):' in content
    assert 'import pandas as pd' in content
    assert 'read_csv' in content


def test_ml_split_main_file(ml_notebook, tmp_path):
    """Test that main.py is correctly generated"""
    output_dir = tmp_path / "ml_pipeline"
    
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        str(ml_notebook),
        '--output', str(output_dir)
    ])
    
    assert result.exit_code == 0
    
    # Check main.py content
    main_file = output_dir / 'main.py'
    content = main_file.read_text()
    
    assert 'def run_pipeline():' in content
    assert 'import data_collection' in content
    assert 'import model_training' in content
    assert 'data_collection.run()' in content


def test_ml_split_requirements(ml_notebook, tmp_path):
    """Test that requirements.txt is generated"""
    output_dir = tmp_path / "ml_pipeline"
    
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        str(ml_notebook),
        '--output', str(output_dir)
    ])
    
    assert result.exit_code == 0
    
    # Check requirements.txt content
    req_file = output_dir / 'requirements.txt'
    content = req_file.read_text()
    
    assert 'pandas' in content
    assert 'numpy' in content
    assert 'scikit-learn' in content


def test_ml_split_empty_notebook(tmp_path):
    """Test with an empty notebook"""
    nb = nbformat.v4.new_notebook()
    nb_path = tmp_path / "empty.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    output_dir = tmp_path / "ml_pipeline"
    
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        str(nb_path),
        '--output', str(output_dir)
    ])
    
    # Should handle gracefully
    assert result.exit_code == 0


def test_ml_split_custom_output_dir(ml_notebook, tmp_path):
    """Test with custom output directory"""
    output_dir = tmp_path / "custom" / "ml_pipeline"
    
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        str(ml_notebook),
        '--output', str(output_dir)
    ])
    
    assert result.exit_code == 0
    assert output_dir.exists()
    assert (output_dir / 'main.py').exists()


def test_ml_split_nonexistent_notebook():
    """Test with non-existent notebook"""
    runner = CliRunner()
    result = runner.invoke(ml_split, [
        'nonexistent.ipynb'
    ])
    
    # Should fail because file doesn't exist
    assert result.exit_code != 0

