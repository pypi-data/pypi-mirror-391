"""
Security command - Find security issues in notebooks
"""
import re
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import nbformat

console = Console()


# Security patterns to detect
SECURITY_PATTERNS = {
    'hardcoded_secret': {
        'patterns': [
            r'(?i)(api[_-]?key|apikey|api[_-]?secret)\s*=\s*["\'][^"\']{8,}["\']',
            r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']',
            r'(?i)(token|auth[_-]?token)\s*=\s*["\'][^"\']{8,}["\']',
            r'(?i)(secret[_-]?key|access[_-]?key)\s*=\s*["\'][^"\']{8,}["\']',
            r'(?i)(aws[_-]?access|aws[_-]?secret)\s*=\s*["\'][^"\']{8,}["\']',
            r'(?i)(private[_-]?key)\s*=\s*["\'][^"\']{20,}["\']',
        ],
        'severity': 'high',
        'description': 'Hardcoded secrets (API keys, passwords, tokens)',
        'recommendation': 'Use environment variables or secure vaults instead',
    },
    'unsafe_pickle': {
        'patterns': [
            r'pickle\.load\s*\(',
            r'pickle\.loads\s*\(',
            r'cPickle\.load\s*\(',
            r'dill\.load\s*\(',
        ],
        'severity': 'high',
        'description': 'Unsafe deserialization (pickle)',
        'recommendation': 'Only load pickles from trusted sources; consider using safer formats like JSON',
    },
    'sql_injection': {
        'patterns': [
            r'execute\s*\([^)]*[+%]\s*["\']',  # String concatenation in execute
            r'\.execute\s*\(\s*f["\']',  # f-strings in execute
            r'\.execute\s*\(\s*["\'][^"\']*%[sd]',  # % formatting in execute
        ],
        'severity': 'high',
        'description': 'Potential SQL injection',
        'recommendation': 'Use parameterized queries instead of string concatenation',
    },
    'command_injection': {
        'patterns': [
            r'os\.system\s*\(',
            r'subprocess\.call\s*\([^)]*shell\s*=\s*True',
            r'subprocess\.run\s*\([^)]*shell\s*=\s*True',
            r'subprocess\.Popen\s*\([^)]*shell\s*=\s*True',
            r'eval\s*\(',
            r'exec\s*\(',
        ],
        'severity': 'medium',
        'description': 'Potential command injection',
        'recommendation': 'Avoid shell=True and validate all inputs; avoid eval/exec',
    },
    'unsafe_yaml': {
        'patterns': [
            r'yaml\.load\s*\([^,)]*\)',  # yaml.load without Loader
            r'yaml\.unsafe_load\s*\(',
        ],
        'severity': 'medium',
        'description': 'Unsafe YAML parsing',
        'recommendation': 'Use yaml.safe_load() instead of yaml.load()',
    },
    'unsafe_request': {
        'patterns': [
            r'requests\.\w+\s*\([^)]*verify\s*=\s*False',
            r'urllib\.request\.urlopen\s*\([^)]*context\s*=\s*ssl\._create_unverified_context',
        ],
        'severity': 'medium',
        'description': 'Disabled SSL/TLS verification',
        'recommendation': 'Keep SSL verification enabled in production',
    },
    'weak_crypto': {
        'patterns': [
            r'md5\s*\(',
            r'hashlib\.md5\s*\(',
            r'hashlib\.sha1\s*\(',
        ],
        'severity': 'low',
        'description': 'Weak cryptographic hash',
        'recommendation': 'Use SHA-256 or stronger algorithms for security-critical operations',
    },
}


class SecurityIssue:
    """Represents a security issue found in a cell"""
    
    def __init__(self, cell_index, cell_type, issue_type, line_number, code_snippet, severity):
        self.cell_index = cell_index
        self.cell_type = cell_type
        self.issue_type = issue_type
        self.line_number = line_number
        self.code_snippet = code_snippet
        self.severity = severity


@click.command()
@click.argument('notebook', type=click.Path(exists=True))
@click.option('--severity', type=click.Choice(['low', 'medium', 'high', 'all']),
              default='all', help='Filter by severity level')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed information')
def security(notebook, severity, output_json, verbose):
    """Find security issues in notebooks
    
    Scans notebooks for common security issues including:
    - Hardcoded secrets (API keys, passwords, tokens)
    - Unsafe deserialization (pickle)
    - SQL injection risks
    - Command injection risks
    - Unsafe YAML parsing
    - Disabled SSL verification
    - Weak cryptographic algorithms
    
    \b
    Examples:
      # Scan for all security issues
      nbutils security notebook.ipynb
      
      # Only show high severity issues
      nbutils security notebook.ipynb --severity high
      
      # Verbose output with recommendations
      nbutils security notebook.ipynb --verbose
    """
    try:
        notebook_path = Path(notebook)
        
        # Load notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        
        # Scan for security issues
        with console.status("[bold blue]Scanning for security issues...[/bold blue]"):
            issues = _scan_notebook(nb, severity)
        
        # Display results
        if output_json:
            _display_json(issues, notebook_path)
        else:
            _display_results(issues, notebook_path, verbose)
    
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.Abort()


def _scan_notebook(nb, severity_filter):
    """Scan notebook for security issues"""
    issues = []
    
    for cell_idx, cell in enumerate(nb.cells):
        if cell.cell_type != 'code':
            continue
        
        source = cell.source
        lines = source.split('\n')
        
        # Check each security pattern
        for issue_type, config in SECURITY_PATTERNS.items():
            # Skip if severity doesn't match filter
            if severity_filter != 'all' and config['severity'] != severity_filter:
                continue
            
            for pattern in config['patterns']:
                for line_idx, line in enumerate(lines, 1):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        # Extract code snippet
                        snippet = line.strip()
                        if len(snippet) > 60:
                            snippet = snippet[:57] + '...'
                        
                        issue = SecurityIssue(
                            cell_index=cell_idx,
                            cell_type=cell.cell_type,
                            issue_type=issue_type,
                            line_number=line_idx,
                            code_snippet=snippet,
                            severity=config['severity']
                        )
                        issues.append(issue)
                        break  # Only report first match per line
    
    return issues


def _display_results(issues, notebook_path, verbose):
    """Display security scan results"""
    console.print(f"\n[bold]Security Scan:[/bold] {notebook_path.name}\n")
    
    if not issues:
        console.print("[green]✓ No security issues found![/green]")
        console.print("[dim]Your notebook looks secure.[/dim]")
        return
    
    # Group by severity
    high_issues = [i for i in issues if i.severity == 'high']
    medium_issues = [i for i in issues if i.severity == 'medium']
    low_issues = [i for i in issues if i.severity == 'low']
    
    # Summary
    console.print(f"[bold red]⚠️  Found {len(issues)} security issue(s):[/bold red]")
    if high_issues:
        console.print(f"  [red]• {len(high_issues)} HIGH severity[/red]")
    if medium_issues:
        console.print(f"  [yellow]• {len(medium_issues)} MEDIUM severity[/yellow]")
    if low_issues:
        console.print(f"  [blue]• {len(low_issues)} LOW severity[/blue]")
    console.print()
    
    # Create table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Cell", style="dim", width=6)
    table.add_column("Severity", width=10)
    table.add_column("Issue", width=30)
    table.add_column("Code Snippet", width=40)
    
    for issue in sorted(issues, key=lambda x: (
        {'high': 0, 'medium': 1, 'low': 2}[x.severity],
        x.cell_index
    )):
        # Severity color
        if issue.severity == 'high':
            severity_str = "[red]HIGH[/red]"
        elif issue.severity == 'medium':
            severity_str = "[yellow]MEDIUM[/yellow]"
        else:
            severity_str = "[blue]LOW[/blue]"
        
        # Issue description
        issue_desc = SECURITY_PATTERNS[issue.issue_type]['description']
        
        table.add_row(
            f"{issue.cell_index + 1}:{issue.line_number}",
            severity_str,
            issue_desc,
            f"[dim]{issue.code_snippet}[/dim]"
        )
    
    console.print(table)
    
    # Show recommendations if verbose
    if verbose:
        console.print("\n[bold cyan]Recommendations:[/bold cyan]\n")
        
        shown_types = set()
        for issue in issues:
            if issue.issue_type not in shown_types:
                shown_types.add(issue.issue_type)
                config = SECURITY_PATTERNS[issue.issue_type]
                
                console.print(Panel(
                    f"[bold]{config['description']}[/bold]\n\n"
                    f"[dim]{config['recommendation']}[/dim]",
                    title=f"[{'red' if config['severity'] == 'high' else 'yellow' if config['severity'] == 'medium' else 'blue'}]{config['severity'].upper()}[/]",
                    border_style="red" if config['severity'] == 'high' else "yellow" if config['severity'] == 'medium' else "blue"
                ))


def _display_json(issues, notebook_path):
    """Display results in JSON format"""
    import json
    
    output = {
        'notebook': str(notebook_path),
        'total_issues': len(issues),
        'issues': []
    }
    
    for issue in issues:
        config = SECURITY_PATTERNS[issue.issue_type]
        output['issues'].append({
            'cell': issue.cell_index + 1,
            'line': issue.line_number,
            'severity': issue.severity,
            'type': issue.issue_type,
            'description': config['description'],
            'code_snippet': issue.code_snippet,
            'recommendation': config['recommendation']
        })
    
    console.print_json(data=output)


