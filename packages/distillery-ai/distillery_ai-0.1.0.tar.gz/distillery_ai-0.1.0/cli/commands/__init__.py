"""
CLI commands for Distillery.

Each command implements a specific workflow:
- analyze: Analyze RAG logs and show ROI
- generate: Generate training dataset
- train: Upload and start fine-tuning
"""

from .analyze import analyze
from .generate import generate
from .train import train

__all__ = [
    "analyze",
    "generate",
    "train",
]
