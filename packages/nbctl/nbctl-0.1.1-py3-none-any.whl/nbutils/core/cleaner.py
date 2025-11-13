"""
Notebook cleaning functionality
Removes outputs, execution counts, and metadata
"""
from typing import Dict, Any
from nbformat.notebooknode import NotebookNode


class NotebookCleaner:
    """Clean notebook outputs and metadata"""
    
    def __init__(self, notebook: NotebookNode):
        self.nb = notebook
        self.stats = {
            'cells_cleaned': 0,
            'outputs_removed': 0,
            'execution_counts_reset': 0,
            'metadata_cleaned': False,
        }
    
    def clean(self, 
              remove_outputs: bool = True,
              reset_execution_count: bool = True,
              clean_metadata: bool = True) -> Dict[str, Any]:
        """
        Clean the notebook
        
        Args:
            remove_outputs: Remove all cell outputs
            reset_execution_count: Reset execution counts to None
            clean_metadata: Remove unnecessary metadata
        
        Returns:
            Dictionary with cleaning statistics
        """
        for cell in self.nb.cells:
            if cell.cell_type == 'code':
                self._clean_code_cell(
                    cell, 
                    remove_outputs=remove_outputs,
                    reset_execution_count=reset_execution_count
                )
        
        if clean_metadata:
            self._clean_metadata()
        
        return self.stats
    
    def _clean_code_cell(self, cell, remove_outputs: bool, reset_execution_count: bool):
        """Clean a single code cell"""
        cleaned = False
        
        # Remove outputs
        if remove_outputs and cell.outputs:
            output_count = len(cell.outputs)
            cell.outputs = []
            self.stats['outputs_removed'] += output_count
            cleaned = True
        
        # Reset execution count
        if reset_execution_count and cell.execution_count is not None:
            cell.execution_count = None
            self.stats['execution_counts_reset'] += 1
            cleaned = True
        
        if cleaned:
            self.stats['cells_cleaned'] += 1
    
    def _clean_metadata(self):
        """Remove unnecessary notebook metadata"""
        # Keep essential metadata, remove the rest
        essential_keys = {'kernelspec', 'language_info'}
        
        # Clean notebook-level metadata
        if hasattr(self.nb, 'metadata'):
            keys_to_remove = [
                k for k in self.nb.metadata.keys() 
                if k not in essential_keys
            ]
            for key in keys_to_remove:
                del self.nb.metadata[key]
            
            if keys_to_remove:
                self.stats['metadata_cleaned'] = True
        
        # Clean cell-level metadata
        for cell in self.nb.cells:
            if hasattr(cell, 'metadata') and cell.metadata:
                # Remove all cell metadata except collapsed
                keys_to_remove = [
                    k for k in list(cell.metadata.keys())
                    if k != 'collapsed'
                ]
                for key in keys_to_remove:
                    del cell.metadata[key]