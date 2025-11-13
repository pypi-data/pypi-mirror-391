"""
Core notebook diff functionality
"""
from pathlib import Path
from typing import List, Dict, Any, Tuple
import difflib
import nbformat
from nbformat.notebooknode import NotebookNode


class CellDiff:
    """Represents a difference in a cell"""
    
    def __init__(self, cell_type: str, index: int, status: str, old_content: str = None, new_content: str = None):
        self.cell_type = cell_type
        self.index = index
        self.status = status  # 'added', 'deleted', 'modified', 'unchanged'
        self.old_content = old_content
        self.new_content = new_content
        self.changes = []
        
        if status == 'modified' and old_content and new_content:
            self._compute_changes()
    
    def _compute_changes(self):
        """Compute line-by-line changes"""
        old_lines = self.old_content.split('\n')
        new_lines = self.new_content.split('\n')
        
        diff = difflib.unified_diff(old_lines, new_lines, lineterm='')
        self.changes = list(diff)


class NotebookDiffer:
    """Handles comparison of two notebooks"""
    
    def __init__(self, old_path: Path, new_path: Path):
        self.old_path = old_path
        self.new_path = new_path
        self.old_nb = self._load_notebook(old_path)
        self.new_nb = self._load_notebook(new_path)
        self.diffs: List[CellDiff] = []
        self.ignore_outputs = True
        self.ignore_metadata = True
    
    def _load_notebook(self, path: Path) -> NotebookNode:
        """Load a notebook from file"""
        with open(path, 'r', encoding='utf-8') as f:
            return nbformat.read(f, as_version=4)
    
    def _normalize_cell(self, cell) -> str:
        """Normalize cell content for comparison (ignore execution counts, etc.)"""
        return cell.source.strip()
    
    def _cells_equal(self, cell1, cell2) -> bool:
        """Check if two cells are equal"""
        if cell1.cell_type != cell2.cell_type:
            return False
        
        # Compare source content
        if self._normalize_cell(cell1) != self._normalize_cell(cell2):
            return False
        
        # Compare outputs if not ignoring
        if not self.ignore_outputs and cell1.cell_type == 'code':
            outputs1 = getattr(cell1, 'outputs', [])
            outputs2 = getattr(cell2, 'outputs', [])
            
            # Simple comparison: check if output counts differ
            if len(outputs1) != len(outputs2):
                return False
            
            # Compare output content
            for out1, out2 in zip(outputs1, outputs2):
                if out1.get('output_type') != out2.get('output_type'):
                    return False
                # Compare text/data content (simplified)
                if str(out1) != str(out2):
                    return False
        
        # Compare metadata if not ignoring
        if not self.ignore_metadata:
            meta1 = getattr(cell1, 'metadata', {})
            meta2 = getattr(cell2, 'metadata', {})
            if meta1 != meta2:
                return False
        
        return True
    
    def compare(self, ignore_outputs: bool = True, ignore_metadata: bool = True) -> List[CellDiff]:
        """
        Compare two notebooks and return list of differences
        
        Args:
            ignore_outputs: If True, ignore cell outputs in comparison
            ignore_metadata: If True, ignore metadata changes
        """
        # Store comparison settings
        self.ignore_outputs = ignore_outputs
        self.ignore_metadata = ignore_metadata
        
        old_cells = self.old_nb.cells
        new_cells = self.new_nb.cells
        
        # Simple approach: compare cell by cell using LCS-based matching
        self.diffs = self._compute_cell_diffs(old_cells, new_cells)
        
        return self.diffs
    
    def _get_cell_key(self, cell) -> str:
        """Get a comparison key for a cell that respects ignore flags"""
        key_parts = [cell.cell_type, self._normalize_cell(cell)]
        
        # Add outputs to key if not ignoring
        if not self.ignore_outputs and cell.cell_type == 'code':
            outputs = getattr(cell, 'outputs', [])
            key_parts.append(f"outputs_count:{len(outputs)}")
            for i, out in enumerate(outputs):
                key_parts.append(f"out{i}_type:{out.get('output_type', '')}")
                # Include output content
                if 'text' in out:
                    key_parts.append(f"out{i}_text:{out['text']}")
                if 'data' in out:
                    key_parts.append(f"out{i}_data:{str(out['data'])}")
        
        # Add metadata to key if not ignoring
        if not self.ignore_metadata:
            meta = getattr(cell, 'metadata', {})
            key_parts.append(f"metadata:{str(meta)}")
        
        return '|'.join(str(p) for p in key_parts)
    
    def _compute_cell_diffs(self, old_cells, new_cells) -> List[CellDiff]:
        """Compute cell-level differences using sequence matching"""
        diffs = []
        
        # Use difflib to match sequences with keys that respect ignore flags
        matcher = difflib.SequenceMatcher(None, 
                                         [self._get_cell_key(c) for c in old_cells],
                                         [self._get_cell_key(c) for c in new_cells])
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Unchanged cells
                for i in range(i1, i2):
                    diffs.append(CellDiff(
                        cell_type=old_cells[i].cell_type,
                        index=i,
                        status='unchanged',
                        old_content=old_cells[i].source,
                        new_content=new_cells[j1 + (i - i1)].source
                    ))
            
            elif tag == 'delete':
                # Deleted cells
                for i in range(i1, i2):
                    diffs.append(CellDiff(
                        cell_type=old_cells[i].cell_type,
                        index=i,
                        status='deleted',
                        old_content=old_cells[i].source
                    ))
            
            elif tag == 'insert':
                # Added cells
                for j in range(j1, j2):
                    diffs.append(CellDiff(
                        cell_type=new_cells[j].cell_type,
                        index=j,
                        status='added',
                        new_content=new_cells[j].source
                    ))
            
            elif tag == 'replace':
                # Modified cells
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    diffs.append(CellDiff(
                        cell_type=old_cells[i].cell_type,
                        index=i,
                        status='modified',
                        old_content=old_cells[i].source,
                        new_content=new_cells[j].source
                    ))
                
                # Handle unequal replacement lengths
                if i2 - i1 > j2 - j1:
                    # More old cells than new cells
                    for i in range(i1 + (j2 - j1), i2):
                        diffs.append(CellDiff(
                            cell_type=old_cells[i].cell_type,
                            index=i,
                            status='deleted',
                            old_content=old_cells[i].source
                        ))
                elif j2 - j1 > i2 - i1:
                    # More new cells than old cells
                    for j in range(j1 + (i2 - i1), j2):
                        diffs.append(CellDiff(
                            cell_type=new_cells[j].cell_type,
                            index=j,
                            status='added',
                            new_content=new_cells[j].source
                        ))
        
        return diffs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the differences"""
        stats = {
            'total_changes': 0,
            'cells_added': 0,
            'cells_deleted': 0,
            'cells_modified': 0,
            'cells_unchanged': 0,
        }
        
        for diff in self.diffs:
            if diff.status == 'added':
                stats['cells_added'] += 1
                stats['total_changes'] += 1
            elif diff.status == 'deleted':
                stats['cells_deleted'] += 1
                stats['total_changes'] += 1
            elif diff.status == 'modified':
                stats['cells_modified'] += 1
                stats['total_changes'] += 1
            elif diff.status == 'unchanged':
                stats['cells_unchanged'] += 1
        
        return stats
    
    def has_changes(self) -> bool:
        """Check if there are any changes"""
        return any(diff.status != 'unchanged' for diff in self.diffs)

