"""
Onehouse CLI - A command-line tool for executing SQL commands against the Onehouse API.
"""

__version__ = "0.1.1"

from .cli import main as cli_main
from .configure import main as configure_main

__all__ = ["cli_main", "configure_main"]
