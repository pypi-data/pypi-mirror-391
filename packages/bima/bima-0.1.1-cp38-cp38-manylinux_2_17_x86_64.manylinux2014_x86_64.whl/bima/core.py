"""Public Python API wrapping Rust bindings"""

from typing import List
from bima import _bima

def compute(data: List[float]) -> float:
    """
    Compute the sum of a list of numbers using Rust backend.
    
    Args:
        data: List of floating point numbers
        
    Returns:
        The sum of all numbers
        
    Raises:
        ValueError: If the list is empty
    """
    if not data:
        raise ValueError("Cannot compute sum of empty list")
    
    # Call the Rust implementation
    return _bima.compute_internal(data)

class DataProcessor:
    """
    High-level Python wrapper for Rust DataProcessor.
    """
    def __init__(self):
        # Keep the Rust object as a private attribute
        self._processor = _bima.PyDataProcessor()
    
    def process(self, data: List[float]) -> List[float]:
        """Process data through the Rust backend."""
        return self._processor.process(data)