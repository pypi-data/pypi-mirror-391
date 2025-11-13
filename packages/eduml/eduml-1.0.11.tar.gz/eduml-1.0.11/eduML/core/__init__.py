"""
eduML.core
----------

Core utilities for dataset loading, preprocessing, metrics, and visualization.
These modules support the main ML algorithms by providing essential
data handling and evaluation functions.
"""

from .dataset_loader import *
from .preprocessing import *
from .metrics import *
from .visualize import *

__all__ = [
    "dataset_loader",
    "preprocessing",
    "metrics",
    "visualize"
]
