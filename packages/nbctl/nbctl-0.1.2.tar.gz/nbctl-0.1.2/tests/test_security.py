"""
Tests for the security command
"""
import pytest
import nbformat
from pathlib import Path
from click.testing import CliRunner
from nbutils.commands.security import security


@pytest.fixture
def runner():
    """Create a CLI runner"""
    return CliRunner()


@pytest.fixture
def notebook_with_secrets(tmp_path):
    """Create notebook with hardcoded secrets"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import requests

# Hardcoded API key (DUMMY FOR TESTING)
api_key = "FAKE_KEY_FOR_TESTING_ONLY_1234567890"
password = "dummy_password_for_tests"
'''))
    
    nb_path = tmp_path / "secrets.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_pickle(tmp_path):
    """Create notebook with unsafe pickle usage"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import pickle

with open('data.pkl', 'rb') as f:
    data = pickle.load(f)
'''))
    
    nb_path = tmp_path / "pickle.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_sql_injection(tmp_path):
    """Create notebook with SQL injection risk"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import sqlite3

user_input = input('Enter username: ')
cursor.execute('SELECT * FROM users WHERE name = "' + user_input + '"')
'''))
    
    nb_path = tmp_path / "sql.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_command_injection(tmp_path):
    """Create notebook with command injection risks"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import os
import subprocess

filename = input('Enter filename: ')
os.system(f'cat {filename}')

# Also eval/exec
user_code = input('Enter code: ')
eval(user_code)
'''))
    
    nb_path = tmp_path / "command.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_unsafe_yaml(tmp_path):
    """Create notebook with unsafe YAML parsing"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import yaml

with open('config.yaml') as f:
    config = yaml.load(f)
'''))
    
    nb_path = tmp_path / "yaml.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_ssl_issues(tmp_path):
    """Create notebook with disabled SSL verification"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import requests

# Disabled SSL verification
response = requests.get('https://api.example.com', verify=False)
'''))
    
    nb_path = tmp_path / "ssl.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_weak_crypto(tmp_path):
    """Create notebook with weak cryptographic algorithms"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import hashlib

# Weak hash algorithms
hash1 = hashlib.md5(b'data').hexdigest()
hash2 = hashlib.sha1(b'data').hexdigest()
'''))
    
    nb_path = tmp_path / "crypto.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def safe_notebook(tmp_path):
    """Create notebook with no security issues"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
import pandas as pd
import os

# Safe: Using environment variables
api_key = os.environ.get('API_KEY')

# Safe: Parameterized SQL
cursor.execute('SELECT * FROM users WHERE username = ?', (username,))

# Safe: No shell=True
import subprocess
subprocess.run(['cat', filename], check=True)

# Safe: Strong crypto
import hashlib
hash = hashlib.sha256(b'data').hexdigest()
'''))
    
    nb_path = tmp_path / "safe.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


@pytest.fixture
def notebook_with_mixed_issues(tmp_path):
    """Create notebook with multiple security issues"""
    nb = nbformat.v4.new_notebook()
    
    # Cell with secrets
    nb.cells.append(nbformat.v4.new_code_cell('''
api_key = "DUMMY_API_KEY_FOR_TEST_ONLY_123456"
'''))
    
    # Cell with pickle
    nb.cells.append(nbformat.v4.new_code_cell('''
import pickle
data = pickle.load(open('file.pkl', 'rb'))
'''))
    
    # Safe cell
    nb.cells.append(nbformat.v4.new_code_cell('''
import pandas as pd
df = pd.read_csv('data.csv')
'''))
    
    # Cell with SQL injection
    nb.cells.append(nbformat.v4.new_code_cell('''
cursor.execute("SELECT * FROM users WHERE id = " + user_id)
'''))
    
    nb_path = tmp_path / "mixed.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    return nb_path


# CLI tests

def test_security_detects_hardcoded_secrets(runner, notebook_with_secrets):
    """Test detection of hardcoded secrets"""
    result = runner.invoke(security, [str(notebook_with_secrets)])
    
    assert result.exit_code == 0
    assert "api_key" in result.output or "password" in result.output
    assert "Hardcoded secrets" in result.output or "security issue" in result.output


def test_security_detects_unsafe_pickle(runner, notebook_with_pickle):
    """Test detection of unsafe pickle usage"""
    result = runner.invoke(security, [str(notebook_with_pickle)])
    
    assert result.exit_code == 0
    assert "pickle" in result.output or "deserialization" in result.output


def test_security_detects_sql_injection(runner, notebook_with_sql_injection):
    """Test detection of SQL injection risks"""
    result = runner.invoke(security, [str(notebook_with_sql_injection)])
    
    assert result.exit_code == 0
    assert "SQL" in result.output or "injection" in result.output


def test_security_detects_command_injection(runner, notebook_with_command_injection):
    """Test detection of command injection risks"""
    result = runner.invoke(security, [str(notebook_with_command_injection)])
    
    assert result.exit_code == 0
    assert "os.system" in result.output or "eval" in result.output or "command" in result.output.lower()


def test_security_detects_unsafe_yaml(runner, notebook_with_unsafe_yaml):
    """Test detection of unsafe YAML parsing"""
    result = runner.invoke(security, [str(notebook_with_unsafe_yaml)])
    
    assert result.exit_code == 0
    assert "yaml" in result.output.lower()


def test_security_detects_ssl_issues(runner, notebook_with_ssl_issues):
    """Test detection of disabled SSL verification"""
    result = runner.invoke(security, [str(notebook_with_ssl_issues)])
    
    assert result.exit_code == 0
    assert "verify" in result.output.lower() or "SSL" in result.output


def test_security_detects_weak_crypto(runner, notebook_with_weak_crypto):
    """Test detection of weak cryptographic algorithms"""
    result = runner.invoke(security, [str(notebook_with_weak_crypto)])
    
    assert result.exit_code == 0
    assert "md5" in result.output or "sha1" in result.output or "crypto" in result.output.lower()


def test_security_clean_notebook(runner, safe_notebook):
    """Test that safe notebooks show no issues"""
    result = runner.invoke(security, [str(safe_notebook)])
    
    assert result.exit_code == 0
    assert "No security issues found" in result.output or "✓" in result.output


def test_security_filter_by_high_severity(runner, notebook_with_mixed_issues):
    """Test filtering by high severity"""
    result = runner.invoke(security, [
        str(notebook_with_mixed_issues),
        '--severity', 'high'
    ])
    
    assert result.exit_code == 0
    assert "HIGH" in result.output
    # Should not show medium/low
    assert "MEDIUM" not in result.output or result.output.count("MEDIUM") == 0


def test_security_filter_by_medium_severity(runner, notebook_with_command_injection):
    """Test filtering by medium severity"""
    result = runner.invoke(security, [
        str(notebook_with_command_injection),
        '--severity', 'medium'
    ])
    
    assert result.exit_code == 0
    # Should show medium severity issues


def test_security_verbose_output(runner, notebook_with_secrets):
    """Test verbose output with recommendations"""
    result = runner.invoke(security, [
        str(notebook_with_secrets),
        '--verbose'
    ])
    
    assert result.exit_code == 0
    assert "Recommendations" in result.output or "recommendation" in result.output.lower()


def test_security_json_output(runner, notebook_with_mixed_issues):
    """Test JSON output format"""
    result = runner.invoke(security, [
        str(notebook_with_mixed_issues),
        '--json'
    ])
    
    assert result.exit_code == 0
    # Should be valid JSON
    import json
    try:
        data = json.loads(result.output)
        assert 'notebook' in data
        assert 'total_issues' in data
        assert 'issues' in data
        assert isinstance(data['issues'], list)
    except json.JSONDecodeError:
        pytest.fail("Output is not valid JSON")


def test_security_multiple_issues_same_cell(runner, tmp_path):
    """Test detection of multiple issues in the same cell"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
# Multiple issues in one cell
api_key = "FAKE_TEST_KEY_123456789"
import pickle
data = pickle.load(open('data.pkl', 'rb'))
os.system('rm -rf /')
'''))
    
    nb_path = tmp_path / "multi.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    result = runner.invoke(security, [str(nb_path)])
    
    assert result.exit_code == 0
    # Should detect multiple issues
    assert "security issue" in result.output.lower()


def test_security_empty_notebook(runner, tmp_path):
    """Test scanning empty notebook"""
    nb = nbformat.v4.new_notebook()
    
    nb_path = tmp_path / "empty.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    result = runner.invoke(security, [str(nb_path)])
    
    assert result.exit_code == 0
    assert "No security issues found" in result.output


def test_security_markdown_only_notebook(runner, tmp_path):
    """Test scanning notebook with only markdown cells"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_markdown_cell("# Title"))
    nb.cells.append(nbformat.v4.new_markdown_cell("Some content"))
    
    nb_path = tmp_path / "markdown.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    result = runner.invoke(security, [str(nb_path)])
    
    assert result.exit_code == 0
    assert "No security issues found" in result.output


def test_security_nonexistent_file(runner):
    """Test with nonexistent file"""
    result = runner.invoke(security, ['nonexistent.ipynb'])
    
    assert result.exit_code != 0


def test_security_cell_line_numbers(runner, notebook_with_secrets):
    """Test that cell and line numbers are reported"""
    result = runner.invoke(security, [str(notebook_with_secrets)])
    
    assert result.exit_code == 0
    # Should show cell numbers (format: "cell:line")
    assert ":" in result.output


def test_security_code_snippets_truncated(runner, tmp_path):
    """Test that long code snippets are truncated"""
    nb = nbformat.v4.new_notebook()
    
    nb.cells.append(nbformat.v4.new_code_cell('''
api_key = "DUMMY_VERY_LONG_KEY_FOR_TESTING_TRUNCATION_BEHAVIOR_IN_OUTPUT_FORMAT_1234567890"
'''))
    
    nb_path = tmp_path / "long.ipynb"
    with open(nb_path, 'w') as f:
        nbformat.write(nb, f)
    
    result = runner.invoke(security, [str(nb_path)])
    
    assert result.exit_code == 0
    # Should truncate (either "..." or "…")
    assert ("..." in result.output or "…" in result.output)


def test_security_all_severity_levels(runner, notebook_with_mixed_issues):
    """Test that all severity levels are shown by default"""
    result = runner.invoke(security, [str(notebook_with_mixed_issues)])
    
    assert result.exit_code == 0
    # Should show statistics about severity levels
    assert "security issue" in result.output.lower()


