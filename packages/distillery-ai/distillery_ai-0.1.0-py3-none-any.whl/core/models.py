"""
Core data models for Distillery.

These models represent RAG logs, training examples, and quality metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class FeedbackType(Enum):
    """User feedback types"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    NONE = None


@dataclass
class RetrievedChunk:
    """A single retrieved document chunk from RAG"""
    text: str
    score: float
    doc_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate chunk data"""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError(f"Score must be between 0 and 1, got {self.score}")
        if not self.text:
            raise ValueError("Chunk text cannot be empty")


@dataclass
class RAGLog:
    """A single RAG query log entry"""
    query: str
    response: str
    retrieved_chunks: List[RetrievedChunk]
    timestamp: datetime

    # Optional fields
    user_feedback: Optional[FeedbackType] = None
    session_id: Optional[str] = None
    model: Optional[str] = None
    tokens: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def avg_retrieval_score(self) -> float:
        """Calculate average retrieval score"""
        if not self.retrieved_chunks:
            return 0.0
        return sum(c.score for c in self.retrieved_chunks) / len(self.retrieved_chunks)

    @property
    def max_retrieval_score(self) -> float:
        """Get maximum retrieval score"""
        if not self.retrieved_chunks:
            return 0.0
        return max(c.score for c in self.retrieved_chunks)

    @property
    def has_positive_feedback(self) -> bool:
        """Check if user gave positive feedback"""
        return self.user_feedback == FeedbackType.THUMBS_UP

    @property
    def has_negative_feedback(self) -> bool:
        """Check if user gave negative feedback"""
        return self.user_feedback == FeedbackType.THUMBS_DOWN

    def __post_init__(self):
        """Validate log data"""
        if not self.query:
            raise ValueError("Query cannot be empty")
        if not self.response:
            raise ValueError("Response cannot be empty")
        if not self.retrieved_chunks:
            raise ValueError("Must have at least one retrieved chunk")


@dataclass
class TrainingExample:
    """A training example for fine-tuning"""
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Source tracking
    source_query: Optional[str] = None
    source_timestamp: Optional[datetime] = None

    @property
    def is_valid_openai_format(self) -> bool:
        """Check if example is valid OpenAI format"""
        if not self.messages:
            return False

        for msg in self.messages:
            if "role" not in msg or "content" not in msg:
                return False
            if msg["role"] not in ["system", "user", "assistant"]:
                return False
            if not msg["content"]:
                return False

        return True

    def estimate_tokens(self) -> int:
        """Estimate token count (rough: 1 token ≈ 4 chars)"""
        total_chars = sum(len(msg["content"]) for msg in self.messages)
        return total_chars // 4


@dataclass
class QualityMetrics:
    """Quality metrics for a dataset"""
    total_examples: int
    avg_retrieval_score: float
    diversity_score: float
    quality_score: float
    estimated_tokens: int
    estimated_cost: float

    # Breakdown
    score_distribution: Dict[str, int] = field(default_factory=dict)
    feedback_distribution: Dict[str, int] = field(default_factory=dict)
    topic_distribution: Dict[str, int] = field(default_factory=dict)

    def __str__(self) -> str:
        """Pretty print metrics"""
        return f"""
Quality Metrics:
  Total Examples: {self.total_examples}
  Avg Retrieval Score: {self.avg_retrieval_score:.2f}
  Diversity Score: {self.diversity_score:.2f}/1.0
  Quality Score: {self.quality_score:.2f}/1.0
  Estimated Tokens: {self.estimated_tokens:,}
  Estimated Cost: ${self.estimated_cost:.2f}
"""


@dataclass
class DatasetStats:
    """Statistics about a RAG log dataset"""
    total_queries: int
    date_range: tuple[datetime, datetime]
    avg_retrieval_score: float
    successful_queries: int  # score > threshold

    # Distributions
    feedback_counts: Dict[str, int]
    score_distribution: Dict[str, int]

    # Topics (if available)
    topic_distribution: Optional[Dict[str, int]] = None

    def __str__(self) -> str:
        """Pretty print stats"""
        start, end = self.date_range
        return f"""
Dataset Statistics:
  Total Queries: {self.total_queries}
  Date Range: {start.date()} to {end.date()}
  Avg Retrieval Score: {self.avg_retrieval_score:.2f}
  Successful Queries: {self.successful_queries} ({self.successful_queries/self.total_queries*100:.1f}%)
  Feedback: {self.feedback_counts}
"""


@dataclass
class CostComparison:
    """Cost comparison between RAG and fine-tuned approaches"""
    # RAG costs (per query)
    rag_embedding_cost: float
    rag_retrieval_cost: float
    rag_llm_cost: float
    rag_total_per_query: float

    # Fine-tuned costs
    training_cost: float  # one-time
    finetuned_llm_cost_per_query: float

    # Usage projection
    monthly_queries: int

    @property
    def monthly_rag_cost(self) -> float:
        """Monthly RAG cost"""
        return self.rag_total_per_query * self.monthly_queries

    @property
    def monthly_finetuned_cost(self) -> float:
        """Monthly fine-tuned cost"""
        return self.finetuned_llm_cost_per_query * self.monthly_queries

    @property
    def monthly_savings(self) -> float:
        """Monthly savings"""
        return self.monthly_rag_cost - self.monthly_finetuned_cost

    @property
    def annual_savings(self) -> float:
        """Annual savings"""
        return self.monthly_savings * 12

    @property
    def breakeven_months(self) -> float:
        """Months to break even"""
        if self.monthly_savings <= 0:
            return float('inf')
        return self.training_cost / self.monthly_savings

    def __str__(self) -> str:
        """Pretty print comparison"""
        return f"""
Cost Comparison ({self.monthly_queries:,} queries/month):

Current RAG System:
  Embedding: ${self.rag_embedding_cost * self.monthly_queries:.2f}/mo
  Retrieval: ${self.rag_retrieval_cost * self.monthly_queries:.2f}/mo
  LLM: ${self.rag_llm_cost * self.monthly_queries:.2f}/mo
  Total: ${self.monthly_rag_cost:.2f}/mo

Fine-Tuned Model:
  Training (one-time): ${self.training_cost:.2f}
  LLM only: ${self.monthly_finetuned_cost:.2f}/mo

Savings:
  Monthly: ${self.monthly_savings:.2f}
  Annual: ${self.annual_savings:.2f}
  Break-even: {self.breakeven_months:.1f} months

ROI: {(self.annual_savings / self.training_cost * 100):.0f}% annual return
"""
