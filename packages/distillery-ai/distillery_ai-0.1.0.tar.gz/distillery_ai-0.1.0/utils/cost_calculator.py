"""
Cost calculator for RAG vs fine-tuned models.

Calculates and compares costs to help users make informed decisions.
"""

from typing import List, Optional
from core.models import RAGLog, TrainingExample, CostComparison


# ==============================================================================
# OpenAI Pricing (as of 2024)
# ==============================================================================

OPENAI_PRICING = {
    "gpt-4o": {
        "input": 0.0025,  # per 1K tokens
        "output": 0.010,
        "fine_tune_training": 0.025,
        "fine_tuned_input": 0.00375,
        "fine_tuned_output": 0.015,
    },
    "gpt-4o-mini": {
        "input": 0.00015,  # per 1K tokens
        "output": 0.0006,
        "fine_tune_training": 0.003,
        "fine_tuned_input": 0.0003,
        "fine_tuned_output": 0.0012,
    },
    "text-embedding-3-small": {
        "input": 0.00002,  # per 1K tokens
    },
    "text-embedding-3-large": {
        "input": 0.00013,  # per 1K tokens
    }
}

# Vector DB costs (Pinecone standard)
VECTOR_DB_COSTS = {
    "pinecone": {
        "query": 0.00000095,  # per query
        "storage_gb_month": 0.095,  # per GB/month
    }
}


class CostCalculator:
    """Calculate RAG and fine-tuning costs"""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        embedding_model: str = "text-embedding-3-small",
        vector_db: str = "pinecone",
    ):
        """
        Initialize cost calculator.

        Args:
            model: LLM model name
            embedding_model: Embedding model name
            vector_db: Vector database service
        """
        self.model = model
        self.embedding_model = embedding_model
        self.vector_db = vector_db

        # Get pricing
        if model not in OPENAI_PRICING:
            raise ValueError(f"Unknown model: {model}")
        if embedding_model not in OPENAI_PRICING:
            raise ValueError(f"Unknown embedding model: {embedding_model}")

        self.llm_pricing = OPENAI_PRICING[model]
        self.embedding_pricing = OPENAI_PRICING[embedding_model]
        self.vector_db_pricing = VECTOR_DB_COSTS.get(vector_db, {})

    def calculate_rag_cost_per_query(
        self,
        avg_query_tokens: int = 20,
        avg_context_tokens: int = 600,
        avg_response_tokens: int = 50,
    ) -> dict:
        """
        Calculate cost per RAG query.

        Args:
            avg_query_tokens: Average tokens in user query
            avg_context_tokens: Average tokens in retrieved context
            avg_response_tokens: Average tokens in response

        Returns:
            Dict with cost breakdown
        """
        # Embedding cost
        embedding_cost = (avg_query_tokens / 1000) * self.embedding_pricing["input"]

        # Vector DB query cost
        vector_db_cost = self.vector_db_pricing.get("query", 0)

        # LLM cost (context + query in, response out)
        llm_input_tokens = avg_context_tokens + avg_query_tokens
        llm_input_cost = (llm_input_tokens / 1000) * self.llm_pricing["input"]
        llm_output_cost = (avg_response_tokens / 1000) * self.llm_pricing["output"]

        total_cost = embedding_cost + vector_db_cost + llm_input_cost + llm_output_cost

        return {
            "embedding": embedding_cost,
            "vector_db": vector_db_cost,
            "llm_input": llm_input_cost,
            "llm_output": llm_output_cost,
            "total": total_cost,
            "breakdown": {
                "embedding_tokens": avg_query_tokens,
                "llm_input_tokens": llm_input_tokens,
                "llm_output_tokens": avg_response_tokens,
            }
        }

    def calculate_finetuned_cost_per_query(
        self,
        avg_query_tokens: int = 20,
        avg_response_tokens: int = 50,
    ) -> dict:
        """
        Calculate cost per query for fine-tuned model.

        Args:
            avg_query_tokens: Average tokens in user query
            avg_response_tokens: Average tokens in response

        Returns:
            Dict with cost breakdown
        """
        # No embedding or vector DB costs
        # Just LLM inference (fine-tuned rates)
        llm_input_cost = (avg_query_tokens / 1000) * self.llm_pricing["fine_tuned_input"]
        llm_output_cost = (avg_response_tokens / 1000) * self.llm_pricing["fine_tuned_output"]

        total_cost = llm_input_cost + llm_output_cost

        return {
            "llm_input": llm_input_cost,
            "llm_output": llm_output_cost,
            "total": total_cost,
            "breakdown": {
                "llm_input_tokens": avg_query_tokens,
                "llm_output_tokens": avg_response_tokens,
            }
        }

    def calculate_training_cost(self, training_examples: List[TrainingExample]) -> dict:
        """
        Calculate one-time fine-tuning cost.

        Args:
            training_examples: List of training examples

        Returns:
            Dict with cost breakdown
        """
        total_tokens = sum(ex.estimate_tokens() for ex in training_examples)

        training_cost = (total_tokens / 1000) * self.llm_pricing["fine_tune_training"]

        return {
            "total_tokens": total_tokens,
            "cost": training_cost,
            "examples": len(training_examples),
            "avg_tokens_per_example": total_tokens / len(training_examples) if training_examples else 0,
        }

    def calculate_from_logs(
        self,
        logs: List[RAGLog],
        training_examples: List[TrainingExample],
        monthly_queries: int,
    ) -> CostComparison:
        """
        Calculate cost comparison from actual logs.

        Args:
            logs: RAG logs (to estimate token usage)
            training_examples: Training examples
            monthly_queries: Projected monthly query volume

        Returns:
            CostComparison object
        """
        # Estimate average tokens from logs
        if logs:
            avg_query_tokens = sum(len(log.query) // 4 for log in logs) // len(logs)
            avg_response_tokens = sum(len(log.response) // 4 for log in logs) // len(logs)
            avg_context_tokens = sum(
                sum(len(chunk.text) for chunk in log.retrieved_chunks) // 4
                for log in logs
            ) // len(logs)
        else:
            # Defaults
            avg_query_tokens = 20
            avg_response_tokens = 50
            avg_context_tokens = 600

        # Calculate RAG costs
        rag_costs = self.calculate_rag_cost_per_query(
            avg_query_tokens,
            avg_context_tokens,
            avg_response_tokens
        )

        # Calculate fine-tuned costs
        finetuned_costs = self.calculate_finetuned_cost_per_query(
            avg_query_tokens,
            avg_response_tokens
        )

        # Calculate training cost
        training_info = self.calculate_training_cost(training_examples)

        return CostComparison(
            rag_embedding_cost=rag_costs["embedding"],
            rag_retrieval_cost=rag_costs["vector_db"],
            rag_llm_cost=rag_costs["llm_input"] + rag_costs["llm_output"],
            rag_total_per_query=rag_costs["total"],
            training_cost=training_info["cost"],
            finetuned_llm_cost_per_query=finetuned_costs["total"],
            monthly_queries=monthly_queries,
        )


def estimate_savings(
    logs: List[RAGLog],
    training_examples: List[TrainingExample],
    monthly_queries: int,
    model: str = "gpt-4o-mini",
) -> CostComparison:
    """
    Estimate cost savings from fine-tuning.

    Args:
        logs: RAG logs
        training_examples: Generated training examples
        monthly_queries: Monthly query volume
        model: LLM model to use

    Returns:
        CostComparison with full breakdown

    Example:
        >>> comparison = estimate_savings(logs, examples, monthly_queries=50000)
        >>> print(comparison)
    """
    calculator = CostCalculator(model=model)
    return calculator.calculate_from_logs(logs, training_examples, monthly_queries)


def print_cost_comparison(comparison: CostComparison):
    """
    Print a nice cost comparison.

    Args:
        comparison: CostComparison object
    """
    print(comparison)

    # Add recommendation
    if comparison.monthly_savings > 0:
        print(f"\n💡 Recommendation: Fine-tune!")
        print(f"   You'll save ${comparison.monthly_savings:.2f}/month")
        print(f"   Break-even in {comparison.breakeven_months:.1f} months")
        print(f"   Annual ROI: {(comparison.annual_savings / comparison.training_cost * 100):.0f}%")
    else:
        print(f"\n💡 Recommendation: Stick with RAG for now")
        print(f"   Fine-tuning doesn't provide cost savings at your current volume")
        print(f"   Consider fine-tuning when you reach {int(comparison.training_cost / comparison.rag_total_per_query):,} queries/month")
