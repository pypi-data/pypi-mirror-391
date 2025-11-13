"""
Core notebook handling functionality
"""
from pathlib import Path
from typing import Dict, Any, List
import nbformat
from nbformat.notebooknode import NotebookNode


class Notebook:
    """Represents a Jupyter notebook with utility methods"""
    
    def __init__(self, path: Path):
        self.path = path
        self.nb: NotebookNode = self._load()
    
    def _load(self) -> NotebookNode:
        """Load notebook from file"""
        with open(self.path, 'r', encoding='utf-8') as f:
            return nbformat.read(f, as_version=4)
    
    def save(self, output_path: Path = None) -> None:
        """Save notebook to file"""
        target = output_path or self.path
        with open(target, 'w', encoding='utf-8') as f:
            nbformat.write(self.nb, f)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get basic statistics about the notebook"""
        stats = {
            'total_cells': len(self.nb.cells),
            'code_cells': 0,
            'markdown_cells': 0,
            'raw_cells': 0,
            'file_size': self.path.stat().st_size,
        }
        
        for cell in self.nb.cells:
            if cell.cell_type == 'code':
                stats['code_cells'] += 1
            elif cell.cell_type == 'markdown':
                stats['markdown_cells'] += 1
            elif cell.cell_type == 'raw':
                stats['raw_cells'] += 1
        
        return stats
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """Get notebook metadata"""
        return self.nb.metadata
    
    @property
    def cells(self):
        """Get notebook cells"""
        return self.nb.cells
    
    def get_imports(self) -> List[str]:
        """Get imports from the notebook"""
        imports = []
        for cell in self.nb.cells:
            if cell.cell_type == 'code':
                for line in cell.source.split('\n'):
                    if line.startswith('import') or line.startswith('from'):
                        imports.append(line)
        return imports
    
    def get_code_metrics(self) -> Dict[str, Any]:
        """Get code metrics from the notebook"""
        metrics = {
            'total_lines': 0,
            'code_cells_count': 0,
            'empty_cells': 0,
            'avg_lines_per_cell': 0.0,
            'largest_cell': {
                'index': None,
                'lines': 0,
            },
            'smallest_cell': {
                'index': None,
                'lines': float('inf'),
            },
        }

        code_cells = [cell for cell in self.nb.cells if cell.cell_type == 'code']
        
        if not code_cells:
            return metrics
        
        for idx, cell in enumerate(code_cells):
            metrics['code_cells_count'] += 1
            
            # Count lines in this cell
            lines = cell.source.split('\n') if cell.source else []
            # Filter out empty lines for accurate count
            non_empty_lines = [line for line in lines if line.strip()]
            line_count = len(non_empty_lines)
            
            # Track total lines
            metrics['total_lines'] += line_count
            
            # Track empty cells
            if line_count == 0 or not cell.source.strip():
                metrics['empty_cells'] += 1
            else:
                # Track largest cell (only non-empty)
                if line_count > metrics['largest_cell']['lines']:
                    metrics['largest_cell']['lines'] = line_count
                    metrics['largest_cell']['index'] = idx
                
                # Track smallest non-empty cell
                if line_count < metrics['smallest_cell']['lines']:
                    metrics['smallest_cell']['lines'] = line_count
                    metrics['smallest_cell']['index'] = idx
        
        # Calculate average
        if metrics['code_cells_count'] > 0:
            metrics['avg_lines_per_cell'] = metrics['total_lines'] / metrics['code_cells_count']
        
        # Clean up smallest_cell if all cells were empty
        if metrics['smallest_cell']['lines'] == float('inf'):
            metrics['smallest_cell'] = {'index': None, 'lines': 0}
        
        return metrics