"""
Distillery CLI

Beautiful command-line interface for converting RAG logs to fine-tuning datasets.
"""

__version__ = "0.1.0"

from .main import cli, main

__all__ = ["cli", "main"]
