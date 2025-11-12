"""
OpenAI fine-tuning format converter.

Converts RAG logs to OpenAI's chat completion fine-tuning format.

Format:
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."}
  ]
}

Docs: https://platform.openai.com/docs/guides/fine-tuning
"""

from typing import List, Optional
from ..models import RAGLog, TrainingExample


class OpenAIConverter:
    """Convert RAG logs to OpenAI format"""

    def __init__(self, system_prompt: Optional[str] = None, include_context: bool = False):
        """
        Initialize OpenAI converter.

        Args:
            system_prompt: Optional system prompt to prepend
            include_context: If True, includes retrieved chunks in system prompt
        """
        self.system_prompt = system_prompt
        self.include_context = include_context

    def convert(self, logs: List[RAGLog]) -> List[TrainingExample]:
        """
        Convert RAG logs to OpenAI training examples.

        Args:
            logs: List of RAG logs

        Returns:
            List of TrainingExample objects
        """
        examples = []

        for log in logs:
            example = self._convert_log(log)
            examples.append(example)

        return examples

    def _convert_log(self, log: RAGLog) -> TrainingExample:
        """Convert single log to training example"""
        messages = []

        # Add system prompt if configured
        if self.system_prompt or self.include_context:
            system_content = self._build_system_prompt(log)
            messages.append({
                "role": "system",
                "content": system_content
            })

        # Add user query
        messages.append({
            "role": "user",
            "content": log.query
        })

        # Add assistant response
        messages.append({
            "role": "assistant",
            "content": log.response
        })

        return TrainingExample(
            messages=messages,
            source_query=log.query,
            source_timestamp=log.timestamp,
            metadata={
                "avg_retrieval_score": log.avg_retrieval_score,
                "feedback": log.user_feedback.value if log.user_feedback else None
            }
        )

    def _build_system_prompt(self, log: RAGLog) -> str:
        """Build system prompt, optionally including context"""
        parts = []

        # Base system prompt
        if self.system_prompt:
            parts.append(self.system_prompt)

        # Include retrieved context
        if self.include_context:
            context = "\n\n".join([
                chunk.text for chunk in log.retrieved_chunks
            ])
            parts.append(f"Use the following context to answer:\n\n{context}")

        return "\n\n".join(parts)


def convert_to_openai(
    logs: List[RAGLog],
    system_prompt: Optional[str] = None,
    include_context: bool = False
) -> List[TrainingExample]:
    """
    Convert RAG logs to OpenAI format.

    Args:
        logs: List of RAG logs
        system_prompt: Optional system prompt
        include_context: If True, includes retrieved chunks

    Returns:
        List of training examples

    Example:
        >>> examples = convert_to_openai(logs)
        >>> # Simple format (no system prompt)

        >>> examples = convert_to_openai(
        ...     logs,
        ...     system_prompt="You are a helpful customer support agent."
        ... )

        >>> examples = convert_to_openai(
        ...     logs,
        ...     include_context=True  # Bakes knowledge into system prompt
        ... )
    """
    converter = OpenAIConverter(system_prompt, include_context)
    return converter.convert(logs)


# Preset configurations

def convert_simple(logs: List[RAGLog]) -> List[TrainingExample]:
    """
    Simple conversion: just query → response.

    This "bakes" the knowledge directly into the model.
    No system prompt, no context.

    Args:
        logs: List of RAG logs

    Returns:
        List of training examples
    """
    return convert_to_openai(logs, system_prompt=None, include_context=False)


def convert_with_system_prompt(logs: List[RAGLog], system_prompt: str) -> List[TrainingExample]:
    """
    Conversion with system prompt.

    Useful for setting role/personality.

    Args:
        logs: List of RAG logs
        system_prompt: System prompt to use

    Returns:
        List of training examples
    """
    return convert_to_openai(logs, system_prompt=system_prompt, include_context=False)


def convert_with_context(logs: List[RAGLog]) -> List[TrainingExample]:
    """
    Conversion including retrieved context.

    Each example includes the retrieved chunks in the system prompt.
    This teaches the model to use context.

    Args:
        logs: List of RAG logs

    Returns:
        List of training examples
    """
    return convert_to_openai(logs, system_prompt=None, include_context=True)
