# nbctl

**The Swiss Army Knife for Jupyter Notebooks**

A comprehensive, production-ready CLI toolkit for Jupyter notebooks that solves all major pain points: version control, collaboration, code quality, security, and workflow automation.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## Features

- **Clean** - Remove outputs and metadata for git
- **Info** - Analyze notebook statistics and dependencies
- **Export** - Convert to HTML, PDF, Markdown, Python, etc.
- **Extract** - Extract outputs (images, graphs, data) from notebooks
- **ML-Split** - Split ML notebooks into production Python pipelines
- **Run** - Execute notebooks from command line
- **Lint** - Check code quality and best practices
- **Format** - Auto-format with black
- **Git Setup** - Configure git for notebooks
- **Diff** - Compare notebooks intelligently
- **Combine** - Concatenate notebooks
- **Resolve** - 3-way merge with conflict detection (powered by nbdime)
- **Security** - Find security vulnerabilities

## Installation

```bash
pip install nbctl
```

Or install from source:

```bash
git clone https://github.com/VenkatachalamSubramanianPeriyaSubbu/nbctl.git
cd nbctl
pip install -e .
```

## Quick Start

### Clean notebooks for git

```bash
nbctl clean notebook.ipynb
```

**Removes:** Outputs, execution counts, metadata
**Result:** Smaller files, cleaner diffs, fewer conflicts

### Get notebook insights

```bash
nbctl info notebook.ipynb
```

**Shows:** Statistics, code metrics, dependencies, imports

### Scan for security issues

```bash
nbctl security notebook.ipynb
```

**Detects:** Hardcoded secrets, SQL injection, unsafe pickle, and more

### Extract outputs from notebooks

```bash
nbctl extract notebook.ipynb
```

**Extracts:** Images (PNG, JPEG, SVG), data (JSON, CSV, DataFrames)
**Saves to:** `outputs/data/` and `outputs/images/`

### Split ML notebook into Python pipeline

```bash
nbctl ml-split ml_notebook.ipynb
cd ml_pipeline && python main.py
```

**Creates:** Production-ready Python modules with automatic context passing

### Compare notebooks

```bash
nbctl diff notebook1.ipynb notebook2.ipynb
```

**Compares:** Only source code (ignores outputs/metadata)

### Resolve merge conflicts

```bash
nbctl resolve base.ipynb ours.ipynb theirs.ipynb -o merged.ipynb
```

**Uses:** nbdime's intelligent 3-way merge with conflict detection

## 📚 Commands Reference

### `nbutils clean`

Remove outputs and metadata from notebooks for version control.

```bash
nbutils clean notebook.ipynb [OPTIONS]
```

**Options:**
- `--output, -o PATH` - Save to different file
- `--keep-outputs` - Preserve cell outputs
- `--keep-execution-count` - Preserve execution counts
- `--keep-metadata` - Preserve metadata
- `--dry-run` - Preview changes without modifying

**Examples:**
```bash
# Clean in place
nbutils clean notebook.ipynb

# Preview changes
nbutils clean notebook.ipynb --dry-run

# Save to new file
nbutils clean notebook.ipynb -o clean.ipynb
```

---

### `nbutils info`

Display comprehensive notebook statistics and analysis.

```bash
nbutils info notebook.ipynb [OPTIONS]
```

**Options:**
- `--code-metrics` - Show only code metrics
- `--imports` - Show only import statements

**Shows:**
- Cell counts (code, markdown, raw)
- File size
- Code metrics (lines, complexity, empty cells)
- All import statements and dependencies

**Examples:**
```bash
# Full analysis
nbutils info notebook.ipynb

# Just imports
nbutils info notebook.ipynb --imports
```

---

### `nbutils export`

Convert notebooks to multiple formats simultaneously.

```bash
nbutils export notebook.ipynb --format FORMATS [OPTIONS]
```

**Supported Formats:**
- `html` - HTML document
- `pdf` - PDF (requires LaTeX)
- `markdown`, `md` - Markdown
- `python`, `py` - Python script
- `latex`, `tex` - LaTeX
- `rst` - reStructuredText
- `slides` - Reveal.js presentations

**Options:**
- `--format, -f` - Output formats (comma-separated, required)
- `--output-dir, -o` - Output directory
- `--no-input` - Exclude input cells
- `--no-prompt` - Exclude prompts

**Examples:**
```bash
# Export to multiple formats
nbutils export notebook.ipynb -f html,pdf,py

# Export without input cells
nbutils export notebook.ipynb -f html --no-input

# Export presentation
nbutils export notebook.ipynb -f slides
```

---

### `nbutils extract`

Extract outputs (images, graphs, data) from notebook cells.

```bash
nbutils extract notebook.ipynb [OPTIONS]
```

**Features:**
- Extract data: JSON, CSV, HTML tables (DataFrames), text
- Extract images: PNG, JPEG, SVG (matplotlib plots, graphs)
- Organized folders: `outputs/data/` and `outputs/images/`
- Traceable filenames: `cell_{idx}_output_{idx}_type_{counter}.ext`

**Options:**
- `--output, -o PATH` - Output directory (default: outputs/)
- `--data` - Extract only data outputs
- `--images` - Extract only image outputs
- `--all` - Extract all outputs without prompting

**Interactive Mode:**
```bash
# Prompts you to choose: both/data/images/all
nbutils extract notebook.ipynb
```

**Examples:**
```bash
# Interactive mode
nbutils extract ml_analysis.ipynb

# Extract everything
nbutils extract ml_analysis.ipynb --all

# Only images (plots, graphs)
nbutils extract ml_analysis.ipynb --images

# Only data (CSV, JSON, DataFrames)
nbutils extract ml_analysis.ipynb --data

# Custom output directory
nbutils extract ml_analysis.ipynb --output my_outputs/
```

**Output Structure:**
```
outputs/
├── data/
│ ├── cell_0_output_0_data_0.json
│ ├── cell_1_output_0_data_1.html # DataFrame
│ └── cell_2_output_0_data_2.csv
└── images/
 ├── cell_3_output_0_img_0.png # Matplotlib plot
 ├── cell_4_output_0_img_1.svg # Vector graphic
 └── cell_5_output_0_img_2.jpeg
```

---

### `nbutils ml-split`

Split ML notebooks into production-ready Python pipeline modules.

```bash
nbutils ml-split notebook.ipynb [OPTIONS]
```

**Features:**
- **Intelligent section detection** - Recognizes 7 ML workflow patterns
- **Context passing** - Variables flow between pipeline steps
- **Complete package** - Generates `__init__.py` + `main.py` runner
- **Auto-dependencies** - Creates `requirements.txt` from imports

**Detected Sections:**
- Data Collection
- Data Preprocessing/Cleaning
- Feature Engineering
- Data Splitting (train/test)
- Model Training
- Model Evaluation
- Model Saving

**Options:**
- `--output, -o PATH` - Output directory (default: ml_pipeline/)
- `--create-main` - Create main.py runner (default: True)

**Examples:**
```bash
# Split ML notebook into pipeline
nbutils ml-split ml_notebook.ipynb

# Custom output directory
nbutils ml-split ml_notebook.ipynb --output src/ml/

# Run the generated pipeline
cd ml_pipeline
python main.py
```

**Generated Structure:**
```
ml_pipeline/
├── data_collection.py # Module for each section
├── data_preprocessing.py
├── feature_engineering.py
├── data_splitting.py
├── model_training.py
├── model_evaluation.py
├── model_saving.py
├── __init__.py # Package init
├── main.py # Pipeline runner
└── requirements.txt # Auto-generated deps
```

**How It Works:**
1. Analyzes markdown headers in your notebook
2. Groups code cells by ML workflow section
3. Generates Python modules with `run(context)` functions
4. Creates main.py that executes the entire pipeline
5. Variables pass automatically between steps

**Each Module:**
```python
def run(context=None):
 """Execute pipeline step with context from previous steps"""
 # Your notebook code here
 return locals() # Pass variables to next step
```

**Main Pipeline:**
```python
# Executes all steps in sequence
context = data_collection.run()
context = data_preprocessing.run(context) # Gets 'df' from step 1
context = feature_engineering.run(context) # Gets 'df' from step 2
# ... and so on
```

---

### `nbutils run`

Execute Jupyter notebooks from the command line.

```bash
nbutils run notebook1.ipynb notebook2.ipynb [OPTIONS]
```

**Features:**
- Execute notebooks in specified or alphabetical order
- No timeout by default (perfect for long ML training)
- Save executed notebooks with all outputs
- Detailed execution summary
- Error handling and reporting

**Options:**
- `--order` - Run notebooks in alphabetical order
- `--timeout, -t INT` - Timeout per cell in seconds (default: None)
- `--allow-errors` - Continue execution even if cells fail
- `--save-output, -o PATH` - Directory to save executed notebooks
- `--kernel, -k TEXT` - Kernel name to use (default: python3)

**Examples:**
```bash
# Run single notebook
nbutils run analysis.ipynb

# Run multiple notebooks in specified order
nbutils run 01_load.ipynb 02_process.ipynb 03_analyze.ipynb

# Run all notebooks alphabetically
nbutils run *.ipynb --order

# Save executed notebooks to directory
nbutils run *.ipynb --save-output executed/

# Continue on errors
nbutils run notebook.ipynb --allow-errors

# Set timeout for safety (e.g., prevent infinite loops)
nbutils run notebook.ipynb --timeout 600
```

**Execution Summary:**
```
Execution Summary

┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┓
┃ Notebook        ┃ Status  ┃ Time  ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━┩
│ 01_load.ipynb   │ Success │ 2.3s  │
│ 02_process.ipynb│ Success │ 5.1s  │
│ 03_analyze.ipynb│ Success │ 3.7s  │
└─────────────────┴─────────┴───────┘

Total: 3 notebooks | Successful: 3 | Total time: 11.1s
```

**Use Cases:**
- Execute ML training notebooks overnight
- Run data pipelines in sequence
- Automate report generation
- Batch process multiple notebooks
- CI/CD notebook testing

---

### `nbutils lint`

Check code quality and identify issues.

```bash
nbutils lint notebook.ipynb [OPTIONS]
```

**Checks:**
- Unused imports
- Overly long cells
- Empty code cells
- Code quality issues

**Options:**
- `--max-cell-length INT` - Max lines per cell (default: 100)

**Examples:**
```bash
# Standard linting
nbutils lint notebook.ipynb

# Custom cell length limit
nbutils lint notebook.ipynb --max-cell-length 150
```

---

### `nbutils format`

Auto-format code cells with black.

```bash
nbutils format notebook.ipynb [OPTIONS]
```

**Options:**
- `--output-dir, -o` - Output directory
- `--line-length INT` - Max line length (default: 88)

**Examples:**
```bash
# Format in place
nbutils format notebook.ipynb

# Custom line length
nbutils format notebook.ipynb --line-length 100
```

---

### `nbutils git-setup`

Configure git for optimal notebook workflows.

```bash
nbutils git-setup
```

**Configures:**
- `.gitattributes` for notebook handling
- `.gitignore` for Python projects
- Custom diff driver using nbutils
- Custom merge driver using nbutils

**Run once per repository to enable git integration.**

---

### `nbutils diff`

Compare notebooks intelligently (ignores outputs and metadata).

```bash
nbutils diff notebook1.ipynb notebook2.ipynb [OPTIONS]
```

**Options:**
- `--format, -f` - Output format: `table`, `unified`, `json` (default: table)
- `--code-only` - Show only code cell changes
- `--stats` - Show only statistics

**Features:**
- Ignores outputs and metadata
- Focuses on actual code changes
- Multiple output formats

**Examples:**
```bash
# Table view (default)
nbutils diff old.ipynb new.ipynb

# Unified diff format
nbutils diff old.ipynb new.ipynb --format unified

# Show only code changes
nbutils diff old.ipynb new.ipynb --code-only

# JSON output for automation
nbutils diff old.ipynb new.ipynb --format json
```

---

### `nbutils combine`

Concatenate or combine two notebooks.

```bash
nbutils combine notebook1.ipynb notebook2.ipynb -o output.ipynb [OPTIONS]
```

**Strategies:**
- `append` - Concatenate all cells from both (default)
- `first` - Keep only first notebook
- `second` - Keep only second notebook

**Options:**
- `--output, -o` - Output file (required)
- `--strategy` - Combine strategy
- `--report` - Show detailed report

**Examples:**
```bash
# Concatenate notebooks
nbutils combine analysis1.ipynb analysis2.ipynb -o full.ipynb

# Keep only first notebook (copy)
nbutils combine nb1.ipynb nb2.ipynb -o output.ipynb --strategy first
```

**Note:** For true merging with conflict detection, use `nbutils resolve`.

---

### `nbutils resolve`

Intelligent 3-way merge with conflict detection (powered by nbdime).

```bash
nbutils resolve base.ipynb ours.ipynb theirs.ipynb -o merged.ipynb [OPTIONS]
```

**Arguments:**
- `BASE` - Common ancestor (before changes)
- `OURS` - Your version (local changes)
- `THEIRS` - Other version (remote changes)

**Options:**
- `--output, -o` - Output file (required unless --check-conflicts)
- `--strategy` - Merge strategy: `auto`, `ours`, `theirs`, `cell-append`
- `--check-conflicts` - Check for conflicts only (no output file needed)
- `--report` - Show detailed merge report

**Features:**
- Production-grade merging with nbdime
- Automatic conflict detection
- Conflict markers for manual resolution
- Multiple merge strategies

**Examples:**
```bash
# Check for conflicts first
nbutils resolve base.ipynb ours.ipynb theirs.ipynb --check-conflicts

# Perform merge
nbutils resolve base.ipynb ours.ipynb theirs.ipynb -o merged.ipynb

# Use with Git
git show :1:notebook.ipynb > base.ipynb
git show :2:notebook.ipynb > ours.ipynb
git show :3:notebook.ipynb > theirs.ipynb
nbutils resolve base.ipynb ours.ipynb theirs.ipynb -o notebook.ipynb
```

---

### `nbutils security`

Scan notebooks for security vulnerabilities.

```bash
nbutils security notebook.ipynb [OPTIONS]
```

**Detects:**
- **HIGH**: Hardcoded secrets (API keys, passwords, tokens)
- **HIGH**: Unsafe pickle deserialization
- **HIGH**: SQL injection risks
- **MEDIUM**: Command injection (os.system, eval, exec)
- **MEDIUM**: Unsafe YAML parsing
- **MEDIUM**: Disabled SSL verification
- **LOW**: Weak cryptographic algorithms (MD5, SHA1)

**Options:**
- `--severity` - Filter by severity: `low`, `medium`, `high`, `all` (default: all)
- `--json` - Output as JSON
- `--verbose, -v` - Show detailed recommendations

**Examples:**
```bash
# Scan for all issues
nbutils security notebook.ipynb

# Only high severity
nbutils security notebook.ipynb --severity high

# With recommendations
nbutils security notebook.ipynb --verbose

# JSON output for CI/CD
nbutils security notebook.ipynb --json
```

---

## Common Workflows

### Setting up a new repository

```bash
# 1. Configure git for notebooks
nbutils git-setup

# 2. Clean notebooks before committing
nbutils clean *.ipynb

# 3. Check code quality
nbutils lint notebook.ipynb
nbutils format notebook.ipynb

# 4. Scan for security issues
nbutils security notebook.ipynb
```

### Reviewing notebook changes

```bash
# Compare versions
nbutils diff old.ipynb new.ipynb --format unified

# Check what changed (code only)
nbutils diff old.ipynb new.ipynb --code-only
```

### Resolving merge conflicts

```bash
# Check if there are conflicts
nbutils resolve base.ipynb ours.ipynb theirs.ipynb --check-conflicts

# Perform merge
nbutils resolve base.ipynb ours.ipynb theirs.ipynb -o merged.ipynb --report

# If conflicts exist, manually resolve in the merged file
```

### Pre-commit checks

```bash
# Quality checks
nbutils lint notebook.ipynb
nbutils format notebook.ipynb
nbutils security notebook.ipynb --severity high

# Clean for commit
nbutils clean notebook.ipynb
```

### ML Workflow - From Notebook to Production

```bash
# 1. Develop ML model in notebook
# (work on ml_model.ipynb)

# 2. Extract outputs for reports
nbutils extract ml_model.ipynb --images
# → Gets all plots and visualizations

# 3. Split into production pipeline
nbutils ml-split ml_model.ipynb --output ml_pipeline/

# 4. Test the pipeline
cd ml_pipeline
python main.py

# 5. Deploy the pipeline modules
# Each module is a standalone Python file ready for production!
```

---

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/nbutils.git
cd nbutils

# Create virtual environment
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_security.py -v

# With coverage
pytest tests/ --cov=nbutils --cov-report=html
```

### Code Quality

```bash
# Format code
black nbutils/ tests/

# Type checking
mypy nbutils/
```

---

## Why nbutils?

Jupyter notebooks are powerful but have challenges:

| Problem | nbutils Solution |
|---------|------------------|
| Massive git diffs | `clean` - Remove outputs |
| Merge conflicts | `resolve` - Intelligent 3-way merge |
| Hard to compare | `diff` - Smart comparison |
| Code quality issues | `lint` + `format` |
| Security risks | `security` - Vulnerability scanning |
| Manual workflows | Comprehensive CLI automation |

**One tool. All solutions. Production-ready.**

---

## Roadmap

- [x] Basic clean command
- [x] Info command (statistics, metrics, imports)
- [x] Export command (HTML, PDF, Markdown, etc.)
- [x] Extract command (extract outputs, images, data)
- [x] ML-Split command (ML notebook → Python pipeline)
- [x] Lint command (code quality)
- [x] Format command (black auto-format)
- [x] Git setup (integration)
- [x] Diff command (intelligent comparison)
- [x] Combine command (2-way merge)
- [x] Resolve command (3-way merge with nbdime)
- [x] Security command (vulnerability scanning)
- [ ] Test runner (execute and validate)
- [ ] Split command (general notebook splitting)
- [ ] Template system
- [ ] Cloud integration

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

## Author

Built with for the Jupyter community by [Venkatachalam Subramanian Periya Subbu](https://github.com/VenkatachalamSubramanianPeriyaSubbu)

---

## Status

**Version:** 0.1.0
**Status:** Production-ready with comprehensive test coverage
**New:** Extract outputs & ML pipeline splitting

---

** Star this repo if you find it useful!**
