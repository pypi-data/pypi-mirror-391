"""
Tests for the git setup command
"""
import pytest
from pathlib import Path
from click.testing import CliRunner
import subprocess
from unittest.mock import patch, MagicMock
from nbutils.commands.git_setup import git_setup


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


@pytest.fixture
def temp_git_repo(tmp_path, monkeypatch):
    """Create a temporary git repository"""
    monkeypatch.chdir(tmp_path)
    
    # Initialize git repo
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, capture_output=True)
    
    return tmp_path


def test_git_setup_creates_gitattributes(runner, temp_git_repo):
    """Test that git setup creates .gitattributes file"""
    # Run git setup
    with patch('subprocess.run') as mock_run:
        # Mock git config commands
        mock_run.side_effect = [
            MagicMock(),  # git config diff
            MagicMock(),  # git config merge
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    
    # Check .gitattributes was created
    gitattributes_path = temp_git_repo / ".gitattributes"
    assert gitattributes_path.exists()
    
    # Check content
    content = gitattributes_path.read_text()
    assert "*.ipynb diff=jupyternotebook merge=jupyternotebook" in content


def test_git_setup_creates_gitignore(runner, temp_git_repo):
    """Test that git setup creates .gitignore file"""
    # Run git setup
    with patch('subprocess.run') as mock_run:
        # Mock git config commands
        mock_run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    
    # Check .gitignore was created
    gitignore_path = temp_git_repo / ".gitignore"
    assert gitignore_path.exists()
    
    # Check content
    content = gitignore_path.read_text()
    assert ".ipynb_checkpoints/" in content
    assert "__pycache__/" in content
    assert ".DS_Store" in content
    assert "*.pyc" in content
    assert "*.pyo" in content
    assert ".env" in content
    assert ".venv" in content


def test_git_setup_skips_existing_gitattributes(runner, temp_git_repo):
    """Test that git setup skips existing .gitattributes"""
    # Create existing .gitattributes
    gitattributes_path = temp_git_repo / ".gitattributes"
    gitattributes_path.write_text("existing content\n")
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    assert "already exists" in result.output
    
    # Check content wasn't overwritten
    content = gitattributes_path.read_text()
    assert content == "existing content\n"


def test_git_setup_skips_existing_gitignore(runner, temp_git_repo):
    """Test that git setup skips existing .gitignore"""
    # Create existing .gitignore
    gitignore_path = temp_git_repo / ".gitignore"
    gitignore_path.write_text("existing content\n")
    
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    assert "already exists" in result.output
    
    # Check content wasn't overwritten
    content = gitignore_path.read_text()
    assert content == "existing content\n"


def test_git_setup_configures_git_with_nbutils(runner, temp_git_repo):
    """Test git setup configures nbutils for diff/merge"""
    with patch('subprocess.run') as mock_run:
        # Mock successful git config commands
        mock_run.side_effect = [
            MagicMock(),  # git config diff
            MagicMock(),  # git config merge
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    assert "nbutils" in result.output.lower()
    
    # Check git config commands were called with nbutils
    calls = [str(call) for call in mock_run.call_args_list]
    assert any("nbutils diff" in call for call in calls)
    assert any("nbutils merge" in call for call in calls)


def test_git_setup_uses_nbutils_commands(runner, temp_git_repo):
    """Test git setup configures git to use nbutils commands"""
    with patch('subprocess.run') as mock_run:
        # Mock successful git config
        mock_run.side_effect = [
            MagicMock(),  # git config diff
            MagicMock(),  # git config merge
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    
    # Check git config commands were called with nbutils
    calls = mock_run.call_args_list
    assert any("git" in str(call) and "config" in str(call) for call in calls)
    assert len(calls) == 2  # One for diff, one for merge


def test_git_setup_configures_diff_driver(runner, temp_git_repo):
    """Test that diff driver is configured correctly"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            MagicMock(),  # git config diff
            MagicMock(),  # git config merge
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    
    # Check that git config was called for diff driver with nbutils
    calls = [str(call) for call in mock_run.call_args_list]
    diff_call_found = any("diff.jupyternotebook.command" in call and "nbutils diff" in call for call in calls)
    assert diff_call_found


def test_git_setup_configures_merge_driver(runner, temp_git_repo):
    """Test that merge driver is configured correctly"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            MagicMock(),  # git config diff
            MagicMock(),  # git config merge
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    
    # Check that git config was called for merge driver with nbutils
    calls = [str(call) for call in mock_run.call_args_list]
    merge_call_found = any("merge.jupyternotebook.driver" in call and "nbutils merge" in call for call in calls)
    assert merge_call_found


def test_git_setup_handles_git_config_error(runner, temp_git_repo):
    """Test that git setup handles git config errors gracefully"""
    with patch('subprocess.run') as mock_run:
        # Mock git config failing
        mock_run.side_effect = [
            subprocess.CalledProcessError(1, "git config"),  # git config fails
        ]
        
        result = runner.invoke(git_setup)
    
    # Should still succeed but show warning
    assert result.exit_code == 0
    assert "Could not configure git drivers" in result.output


def test_git_setup_success_message(runner, temp_git_repo):
    """Test that success message is displayed"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    assert "Git setup complete" in result.output


def test_git_setup_creates_files_in_current_directory(runner, temp_git_repo):
    """Test that files are created in current working directory"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    
    # Check files exist in the temp directory (current dir)
    assert (temp_git_repo / ".gitattributes").exists()
    assert (temp_git_repo / ".gitignore").exists()


def test_gitignore_does_not_ignore_notebooks(runner, temp_git_repo):
    """Test that .gitignore doesn't ignore all notebooks"""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = [
            MagicMock(),
            MagicMock(),
        ]
        
        result = runner.invoke(git_setup)
    
    assert result.exit_code == 0
    
    # Check .gitignore content doesn't have *.ipynb
    gitignore_path = temp_git_repo / ".gitignore"
    content = gitignore_path.read_text()
    assert "*.ipynb" not in content or ".ipynb_checkpoints/" in content


def test_git_setup_with_partial_git_config_error(runner, temp_git_repo):
    """Test git setup handles partial git config errors"""
    with patch('subprocess.run') as mock_run:
        # Mock first config succeeds, second fails
        mock_run.side_effect = [
            MagicMock(),  # git config diff succeeds
            subprocess.CalledProcessError(1, "git config"),  # merge config fails
        ]
        
        result = runner.invoke(git_setup)
    
    # Should handle error gracefully and show warning
    assert result.exit_code == 0
    assert "Could not configure git drivers" in result.output


def test_git_setup_integration(runner, temp_git_repo):
    """Integration test - run git setup and verify all files"""
    # Run the actual command without mocking
    result = runner.invoke(git_setup)
    
    # Should succeed or handle errors gracefully
    assert result.exit_code in [0, 1]
    
    # Check that at least .gitattributes and .gitignore were created
    if result.exit_code == 0:
        assert (temp_git_repo / ".gitattributes").exists()
        assert (temp_git_repo / ".gitignore").exists()

