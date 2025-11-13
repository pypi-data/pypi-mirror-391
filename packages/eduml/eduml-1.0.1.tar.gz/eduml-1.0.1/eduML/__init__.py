"""
eduML - Educational Machine Learning Framework

eduML is a lightweight, modular library designed for learning and
teaching core machine learning algorithms. It emphasizes transparency,
traceability, and readability over performance, helping students
understand what happens inside popular ML algorithms.

Author: Varnit Patel
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Varnit Patel"

# Expose top-level imports for convenience
from . import core
from . import supervised
from . import unsupervised
from . import explainers
from . import interface
from . import metrics
