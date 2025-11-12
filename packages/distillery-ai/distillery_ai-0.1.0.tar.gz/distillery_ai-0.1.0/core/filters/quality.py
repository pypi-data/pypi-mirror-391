"""
Quality filtering for RAG logs.

Filters out low-quality examples that shouldn't become training data.
"""

from typing import List, Callable, Optional
from ..models import RAGLog, FeedbackType


class QualityFilter:
    """Filter RAG logs based on quality criteria"""

    def __init__(self):
        """Initialize quality filter"""
        self.filters: List[Callable[[RAGLog], bool]] = []

    def add_filter(self, filter_fn: Callable[[RAGLog], bool]):
        """
        Add a custom filter function.

        Args:
            filter_fn: Function that takes RAGLog and returns True if should keep
        """
        self.filters.append(filter_fn)

    def filter(self, logs: List[RAGLog]) -> List[RAGLog]:
        """
        Apply all filters to logs.

        Args:
            logs: List of RAG logs

        Returns:
            Filtered list of logs
        """
        filtered = logs

        for filter_fn in self.filters:
            filtered = [log for log in filtered if filter_fn(log)]

        return filtered

    def filter_with_stats(self, logs: List[RAGLog]) -> tuple[List[RAGLog], dict]:
        """
        Filter logs and return statistics.

        Returns:
            (filtered_logs, stats_dict)
        """
        stats = {
            "original_count": len(logs),
            "filtered_count": 0,
            "filters_applied": []
        }

        filtered = logs

        for filter_fn in self.filters:
            before = len(filtered)
            filtered = [log for log in filtered if filter_fn(log)]
            after = len(filtered)

            stats["filters_applied"].append({
                "filter": filter_fn.__name__,
                "removed": before - after
            })

        stats["filtered_count"] = len(filtered)
        stats["success_rate"] = len(filtered) / len(logs) if logs else 0

        return filtered, stats


# ==============================================================================
# Pre-built filter functions
# ==============================================================================

def min_retrieval_score(threshold: float = 0.8) -> Callable[[RAGLog], bool]:
    """
    Filter by minimum average retrieval score.

    Args:
        threshold: Minimum score (0.0 - 1.0)

    Returns:
        Filter function

    Example:
        >>> filter = QualityFilter()
        >>> filter.add_filter(min_retrieval_score(0.8))
    """
    def filter_fn(log: RAGLog) -> bool:
        return log.avg_retrieval_score >= threshold

    filter_fn.__name__ = f"min_retrieval_score({threshold})"
    return filter_fn


def no_negative_feedback() -> Callable[[RAGLog], bool]:
    """
    Filter out queries with negative feedback.

    Returns:
        Filter function
    """
    def filter_fn(log: RAGLog) -> bool:
        return not log.has_negative_feedback

    filter_fn.__name__ = "no_negative_feedback"
    return filter_fn


def only_positive_feedback() -> Callable[[RAGLog], bool]:
    """
    Keep only queries with positive feedback.

    Note: This will remove queries with no feedback.

    Returns:
        Filter function
    """
    def filter_fn(log: RAGLog) -> bool:
        return log.has_positive_feedback

    filter_fn.__name__ = "only_positive_feedback"
    return filter_fn


def min_response_length(min_chars: int = 20) -> Callable[[RAGLog], bool]:
    """
    Filter by minimum response length.

    Args:
        min_chars: Minimum characters in response

    Returns:
        Filter function
    """
    def filter_fn(log: RAGLog) -> bool:
        return len(log.response) >= min_chars

    filter_fn.__name__ = f"min_response_length({min_chars})"
    return filter_fn


def no_uncertain_responses() -> Callable[[RAGLog], bool]:
    """
    Filter out uncertain/unclear responses.

    Removes responses containing:
    - "I don't know"
    - "I'm not sure"
    - "contact support"
    - "I cannot"

    Returns:
        Filter function
    """
    uncertain_phrases = [
        "i don't know",
        "i don't have",
        "i'm not sure",
        "i cannot",
        "i can't",
        "contact support",
        "please contact",
        "not sure",
        "unclear",
    ]

    def filter_fn(log: RAGLog) -> bool:
        response_lower = log.response.lower()
        return not any(phrase in response_lower for phrase in uncertain_phrases)

    filter_fn.__name__ = "no_uncertain_responses"
    return filter_fn


def min_chunks_retrieved(min_count: int = 1) -> Callable[[RAGLog], bool]:
    """
    Filter by minimum number of chunks retrieved.

    Args:
        min_count: Minimum number of chunks

    Returns:
        Filter function
    """
    def filter_fn(log: RAGLog) -> bool:
        return len(log.retrieved_chunks) >= min_count

    filter_fn.__name__ = f"min_chunks_retrieved({min_count})"
    return filter_fn


def max_chunks_retrieved(max_count: int = 10) -> Callable[[RAGLog], bool]:
    """
    Filter by maximum number of chunks retrieved.

    Too many chunks might indicate poor retrieval.

    Args:
        max_count: Maximum number of chunks

    Returns:
        Filter function
    """
    def filter_fn(log: RAGLog) -> bool:
        return len(log.retrieved_chunks) <= max_count

    filter_fn.__name__ = f"max_chunks_retrieved({max_count})"
    return filter_fn


def top_chunk_min_score(threshold: float = 0.7) -> Callable[[RAGLog], bool]:
    """
    Filter by top chunk score.

    The best-matching chunk should have a good score.

    Args:
        threshold: Minimum score for top chunk

    Returns:
        Filter function
    """
    def filter_fn(log: RAGLog) -> bool:
        return log.max_retrieval_score >= threshold

    filter_fn.__name__ = f"top_chunk_min_score({threshold})"
    return filter_fn


# ==============================================================================
# Preset filter configurations
# ==============================================================================

def create_default_filter(
    min_score: float = 0.8,
    allow_neutral_feedback: bool = True
) -> QualityFilter:
    """
    Create filter with sensible defaults.

    Args:
        min_score: Minimum retrieval score
        allow_neutral_feedback: If True, keeps logs without feedback

    Returns:
        Configured QualityFilter
    """
    filter = QualityFilter()

    # Core filters
    filter.add_filter(min_retrieval_score(min_score))
    filter.add_filter(no_uncertain_responses())
    filter.add_filter(min_response_length(20))

    # Feedback filter
    if allow_neutral_feedback:
        filter.add_filter(no_negative_feedback())
    else:
        filter.add_filter(only_positive_feedback())

    # Chunk filters
    filter.add_filter(min_chunks_retrieved(1))
    filter.add_filter(max_chunks_retrieved(10))

    return filter


def create_strict_filter() -> QualityFilter:
    """
    Create strict filter for high-quality data.

    Only keeps:
    - Excellent retrieval (> 0.9)
    - Positive feedback required
    - No uncertain responses

    Returns:
        Strict QualityFilter
    """
    filter = QualityFilter()

    filter.add_filter(min_retrieval_score(0.9))
    filter.add_filter(only_positive_feedback())
    filter.add_filter(no_uncertain_responses())
    filter.add_filter(min_response_length(30))
    filter.add_filter(top_chunk_min_score(0.85))

    return filter


def create_permissive_filter() -> QualityFilter:
    """
    Create permissive filter for more data.

    Keeps most data except obviously bad examples.

    Returns:
        Permissive QualityFilter
    """
    filter = QualityFilter()

    filter.add_filter(min_retrieval_score(0.6))
    filter.add_filter(no_negative_feedback())
    filter.add_filter(min_response_length(10))

    return filter


# ==============================================================================
# Convenience function
# ==============================================================================

def filter_logs(
    logs: List[RAGLog],
    min_score: float = 0.8,
    allow_neutral_feedback: bool = True,
    show_stats: bool = False
) -> List[RAGLog]:
    """
    Filter logs with default settings.

    Args:
        logs: List of RAG logs
        min_score: Minimum retrieval score
        allow_neutral_feedback: If True, keeps logs without feedback
        show_stats: If True, prints filtering statistics

    Returns:
        Filtered list of logs

    Example:
        >>> filtered = filter_logs(logs, min_score=0.85)
        >>> print(f"Kept {len(filtered)} of {len(logs)} examples")
    """
    filter = create_default_filter(min_score, allow_neutral_feedback)

    if show_stats:
        filtered, stats = filter.filter_with_stats(logs)
        print(f"\n🔍 Quality Filtering:")
        print(f"  Original: {stats['original_count']}")
        print(f"  Kept: {stats['filtered_count']} ({stats['success_rate']*100:.1f}%)")
        print(f"  Removed: {stats['original_count'] - stats['filtered_count']}")
        print(f"\n  Filters applied:")
        for f in stats['filters_applied']:
            print(f"    - {f['filter']}: removed {f['removed']}")
        return filtered
    else:
        return filter.filter(logs)
