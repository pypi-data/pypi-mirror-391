"""
Converters for training data formats.

Convert RAG logs to OpenAI fine-tuning format.
"""

from .openai import (
    convert_simple,
    convert_with_system_prompt,
    convert_with_context
)

__all__ = [
    "convert_simple",
    "convert_with_system_prompt",
    "convert_with_context",
]
