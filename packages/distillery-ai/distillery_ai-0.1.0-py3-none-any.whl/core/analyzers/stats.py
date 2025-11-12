"""
Statistical analysis of RAG logs.

Generates insights about log quality, distribution, and patterns.
"""

from typing import List, Dict
from collections import Counter
from datetime import datetime
from ..models import RAGLog, DatasetStats, FeedbackType


class StatsAnalyzer:
    """Analyze RAG logs and generate statistics"""

    def __init__(self, logs: List[RAGLog]):
        """
        Initialize analyzer with logs.

        Args:
            logs: List of RAG logs to analyze
        """
        self.logs = logs

    def analyze(self, score_threshold: float = 0.8) -> DatasetStats:
        """
        Generate comprehensive statistics.

        Args:
            score_threshold: Minimum score to consider "successful"

        Returns:
            DatasetStats object
        """
        if not self.logs:
            raise ValueError("No logs to analyze")

        # Calculate basic stats
        total_queries = len(self.logs)
        scores = [log.avg_retrieval_score for log in self.logs]
        avg_score = sum(scores) / len(scores)
        successful = sum(1 for s in scores if s >= score_threshold)

        # Date range
        timestamps = [log.timestamp for log in self.logs]
        date_range = (min(timestamps), max(timestamps))

        # Feedback distribution
        feedback_counts = Counter()
        for log in self.logs:
            if log.user_feedback == FeedbackType.THUMBS_UP:
                feedback_counts["thumbs_up"] += 1
            elif log.user_feedback == FeedbackType.THUMBS_DOWN:
                feedback_counts["thumbs_down"] += 1
            else:
                feedback_counts["none"] += 1

        # Score distribution (bucketed)
        score_distribution = self._bucket_scores(scores)

        # Topic distribution (if available in metadata)
        topic_distribution = self._extract_topics()

        return DatasetStats(
            total_queries=total_queries,
            date_range=date_range,
            avg_retrieval_score=avg_score,
            successful_queries=successful,
            feedback_counts=dict(feedback_counts),
            score_distribution=score_distribution,
            topic_distribution=topic_distribution
        )

    def _bucket_scores(self, scores: List[float]) -> Dict[str, int]:
        """Bucket scores into ranges"""
        buckets = {
            "0.9-1.0": 0,
            "0.8-0.9": 0,
            "0.7-0.8": 0,
            "0.6-0.7": 0,
            "< 0.6": 0,
        }

        for score in scores:
            if score >= 0.9:
                buckets["0.9-1.0"] += 1
            elif score >= 0.8:
                buckets["0.8-0.9"] += 1
            elif score >= 0.7:
                buckets["0.7-0.8"] += 1
            elif score >= 0.6:
                buckets["0.6-0.7"] += 1
            else:
                buckets["< 0.6"] += 1

        return buckets

    def _extract_topics(self) -> Dict[str, int]:
        """
        Extract topics from logs.

        Looks for topic in metadata or tries simple keyword extraction.
        """
        topics = Counter()

        for log in self.logs:
            # Check metadata
            if "topic" in log.metadata:
                topics[log.metadata["topic"]] += 1
                continue

            # Simple keyword extraction from query
            query_lower = log.query.lower()
            if "refund" in query_lower or "return" in query_lower:
                topics["refunds_returns"] += 1
            elif "ship" in query_lower:
                topics["shipping"] += 1
            elif "account" in query_lower or "login" in query_lower or "password" in query_lower:
                topics["accounts"] += 1
            elif "bill" in query_lower or "payment" in query_lower or "charge" in query_lower:
                topics["billing"] += 1
            else:
                topics["other"] += 1

        return dict(topics) if topics else None

    def get_top_queries(self, n: int = 10) -> List[tuple[str, float]]:
        """
        Get top N queries by retrieval score.

        Args:
            n: Number of queries to return

        Returns:
            List of (query, score) tuples
        """
        sorted_logs = sorted(
            self.logs,
            key=lambda log: log.avg_retrieval_score,
            reverse=True
        )

        return [(log.query, log.avg_retrieval_score) for log in sorted_logs[:n]]

    def get_bottom_queries(self, n: int = 10) -> List[tuple[str, float]]:
        """
        Get bottom N queries by retrieval score.

        Args:
            n: Number of queries to return

        Returns:
            List of (query, score) tuples
        """
        sorted_logs = sorted(
            self.logs,
            key=lambda log: log.avg_retrieval_score
        )

        return [(log.query, log.avg_retrieval_score) for log in sorted_logs[:n]]

    def get_negative_feedback_queries(self) -> List[RAGLog]:
        """Get all queries with negative feedback"""
        return [log for log in self.logs if log.has_negative_feedback]

    def print_summary(self, score_threshold: float = 0.8):
        """Print a human-readable summary"""
        stats = self.analyze(score_threshold)
        print(stats)

        # Additional insights
        print("\n📊 Score Distribution:")
        for bucket, count in stats.score_distribution.items():
            pct = count / stats.total_queries * 100
            bar = "█" * int(pct / 2)
            print(f"  {bucket}: {count:4d} ({pct:5.1f}%) {bar}")

        if stats.topic_distribution:
            print("\n🏷️  Topics:")
            for topic, count in sorted(
                stats.topic_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                pct = count / stats.total_queries * 100
                print(f"  {topic}: {count} ({pct:.1f}%)")

        # Show some examples
        print("\n✅ Top performing queries:")
        for query, score in self.get_top_queries(3):
            print(f"  {score:.2f} - {query[:70]}...")

        negative = self.get_negative_feedback_queries()
        if negative:
            print(f"\n❌ Queries with negative feedback ({len(negative)}):")
            for log in negative[:3]:
                print(f"  {log.avg_retrieval_score:.2f} - {log.query[:70]}...")


def analyze_logs(logs: List[RAGLog], score_threshold: float = 0.8) -> DatasetStats:
    """
    Convenience function to analyze logs.

    Args:
        logs: List of RAG logs
        score_threshold: Minimum score for "successful" query

    Returns:
        DatasetStats object

    Example:
        >>> stats = analyze_logs(logs)
        >>> print(stats)
    """
    analyzer = StatsAnalyzer(logs)
    return analyzer.analyze(score_threshold)
