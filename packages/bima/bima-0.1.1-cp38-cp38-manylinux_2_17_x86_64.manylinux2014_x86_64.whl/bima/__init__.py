"""My Project - A Python library with Rust performance backend"""

__version__ = "0.1.0"

# Import the private Rust module
from bima import _bima

# Re-export only what you want public
from bima.core import compute, DataProcessor

# (Optional) Clean up namespace
__all__ = ["compute", "DataProcessor", "__version__"]