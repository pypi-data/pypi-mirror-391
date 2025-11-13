"""
eduML.interface
---------------

Provides user-facing interfaces for exploring the framework.

Includes:
- cli.py for command-line usage
- app.py for Streamlit-based interactive visualization
"""

from .cli import main as cli_main
from .app import main as launch_app

__all__ = ["cli_main", "launch_app"]
