"""
LangSmith connector for retrieving RAG logs.

LangSmith is the official logging/observability platform for LangChain.
This connector fetches run data from LangSmith projects.

Requires:
    pip install langsmith

Usage:
    connector = LangSmithConnector(config={
        "api_key": "your_api_key",
        "project_name": "my-rag-project"
    })
    logs = list(connector.fetch_logs(limit=100))
"""

import os
from typing import Iterator, Optional, List
from datetime import datetime

try:
    from langsmith import Client
    LANGSMITH_AVAILABLE = True
except ImportError:
    LANGSMITH_AVAILABLE = False

from .base import BaseConnector
from ..models import RAGLog, RetrievedChunk, FeedbackType


class LangSmithConnector(BaseConnector):
    """Connector for LangSmith"""

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize LangSmith connector.

        Args:
            config: Configuration dict with:
                - api_key: LangSmith API key (or set LANGSMITH_API_KEY env var)
                - project_name: LangSmith project name
                - endpoint: Optional custom endpoint

        Raises:
            ImportError: If langsmith package not installed
        """
        if not LANGSMITH_AVAILABLE:
            raise ImportError(
                "langsmith package is required. Install with: pip install langsmith"
            )

        super().__init__(config)

        # Get API key
        self.api_key = self.config.get("api_key") or os.getenv("LANGSMITH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "LangSmith API key required. Set in config or LANGSMITH_API_KEY env var"
            )

        # Get project name
        self.project_name = self.config.get("project_name")
        if not self.project_name:
            raise ValueError("project_name is required in config")

        # Create client
        endpoint = self.config.get("endpoint", "https://api.smith.langchain.com")
        self.client = Client(api_key=self.api_key, api_url=endpoint)

    def connect(self) -> bool:
        """Test LangSmith connection"""
        try:
            # Try to list projects to verify connection
            list(self.client.list_projects(limit=1))
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to LangSmith: {e}")

    def fetch_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Iterator[RAGLog]:
        """
        Fetch RAG logs from LangSmith.

        LangSmith stores "runs" which represent LLM/chain executions.
        We filter for runs that look like RAG queries.

        Yields:
            RAGLog objects
        """
        # Fetch runs from LangSmith
        runs = self.client.list_runs(
            project_name=self.project_name,
            start_time=start_date,
            end_time=end_date,
            is_root=True,  # Only root runs (not intermediate steps)
            limit=limit,
        )

        for run in runs:
            try:
                log = self._parse_run(run)
                if log and self.validate_log(log):
                    yield log
            except Exception as e:
                # Skip runs that can't be parsed
                print(f"⚠️  Skipping run {run.id}: {e}")
                continue

    def count_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Count total logs in LangSmith project"""
        count = 0
        for _ in self.fetch_logs(start_date, end_date):
            count += 1
        return count

    def _parse_run(self, run) -> Optional[RAGLog]:
        """
        Parse a LangSmith run into RAGLog.

        LangSmith runs have:
        - inputs: {"input": "user query"} or {"question": "user query"}
        - outputs: {"output": "response"} or {"answer": "response"}
        - events: Contains retrieval information
        - feedback: User feedback (thumbs up/down)
        """
        # Extract query
        query = self._extract_query(run)
        if not query:
            return None

        # Extract response
        response = self._extract_response(run)
        if not response:
            return None

        # Extract retrieved chunks
        chunks = self._extract_retrieved_chunks(run)
        if not chunks:
            # Not a RAG query (no retrieval step)
            return None

        # Extract feedback
        feedback = self._extract_feedback(run)

        # Create RAGLog
        return RAGLog(
            query=query,
            response=response,
            retrieved_chunks=chunks,
            timestamp=run.start_time or datetime.now(),
            user_feedback=feedback,
            session_id=run.session_id,
            model=self._extract_model(run),
            tokens=self._extract_tokens(run),
            metadata={
                "run_id": str(run.id),
                "run_type": run.run_type,
                "langsmith_url": run.url if hasattr(run, 'url') else None,
            }
        )

    def _extract_query(self, run) -> Optional[str]:
        """Extract user query from run inputs"""
        if not run.inputs:
            return None

        # Try common input keys
        for key in ["input", "question", "query", "prompt"]:
            if key in run.inputs:
                return str(run.inputs[key])

        # If only one input, use that
        if len(run.inputs) == 1:
            return str(next(iter(run.inputs.values())))

        return None

    def _extract_response(self, run) -> Optional[str]:
        """Extract model response from run outputs"""
        if not run.outputs:
            return None

        # Try common output keys
        for key in ["output", "answer", "response", "result"]:
            if key in run.outputs:
                value = run.outputs[key]
                # Handle nested responses
                if isinstance(value, dict) and "text" in value:
                    return str(value["text"])
                return str(value)

        # If only one output, use that
        if len(run.outputs) == 1:
            value = next(iter(run.outputs.values()))
            if isinstance(value, dict) and "text" in value:
                return str(value["text"])
            return str(value)

        return None

    def _extract_retrieved_chunks(self, run) -> List[RetrievedChunk]:
        """
        Extract retrieved document chunks from run.

        LangSmith stores retrieval in child runs or events.
        """
        chunks = []

        # Check if run has child runs (retrieval step)
        if hasattr(run, 'child_runs'):
            for child in run.child_runs:
                if child.run_type == "retriever":
                    # Parse retriever output
                    if child.outputs and "documents" in child.outputs:
                        docs = child.outputs["documents"]
                        for i, doc in enumerate(docs):
                            chunk = self._parse_document(doc, i)
                            if chunk:
                                chunks.append(chunk)

        # Check outputs for documents (some chains return them directly)
        if run.outputs and "source_documents" in run.outputs:
            docs = run.outputs["source_documents"]
            for i, doc in enumerate(docs):
                chunk = self._parse_document(doc, i)
                if chunk:
                    chunks.append(chunk)

        return chunks

    def _parse_document(self, doc, index: int) -> Optional[RetrievedChunk]:
        """Parse a LangChain document into RetrievedChunk"""
        try:
            # LangChain documents have page_content and metadata
            if isinstance(doc, dict):
                text = doc.get("page_content", "")
                metadata = doc.get("metadata", {})
                # Score might be in metadata
                score = metadata.get("score", 0.9 - (index * 0.1))  # Estimate if not present
            else:
                # Object format
                text = getattr(doc, "page_content", str(doc))
                metadata = getattr(doc, "metadata", {})
                score = metadata.get("score", 0.9 - (index * 0.1))

            # Get doc ID
            doc_id = metadata.get("source", metadata.get("id", f"doc_{index}"))

            return RetrievedChunk(
                text=text,
                score=float(score),
                doc_id=str(doc_id),
                metadata=metadata
            )

        except Exception:
            return None

    def _extract_feedback(self, run) -> Optional[FeedbackType]:
        """Extract user feedback from run"""
        # LangSmith stores feedback separately
        try:
            feedbacks = list(self.client.list_feedback(run_ids=[run.id]))
            for feedback in feedbacks:
                # Check for thumbs up/down
                if feedback.score == 1:
                    return FeedbackType.THUMBS_UP
                elif feedback.score == 0:
                    return FeedbackType.THUMBS_DOWN
        except Exception:
            pass

        return None

    def _extract_model(self, run) -> Optional[str]:
        """Extract model name from run"""
        # Try to get model from extra fields
        if hasattr(run, 'extra') and run.extra:
            if "invocation_params" in run.extra:
                params = run.extra["invocation_params"]
                if "model_name" in params:
                    return params["model_name"]
                if "model" in params:
                    return params["model"]

        # Try serialized data
        if hasattr(run, 'serialized') and run.serialized:
            if "id" in run.serialized:
                return run.serialized["id"][-1]  # Last part is usually model name

        return None

    def _extract_tokens(self, run) -> Optional[dict]:
        """Extract token usage from run"""
        # LangSmith stores token usage in extra
        if hasattr(run, 'extra') and run.extra:
            if "usage" in run.extra:
                usage = run.extra["usage"]
                return {
                    "prompt": usage.get("prompt_tokens", 0),
                    "completion": usage.get("completion_tokens", 0),
                    "total": usage.get("total_tokens", 0)
                }

        return None


def create_langsmith_connector(project_name: str, api_key: Optional[str] = None) -> LangSmithConnector:
    """
    Convenience function to create LangSmith connector.

    Args:
        project_name: LangSmith project name
        api_key: Optional API key (defaults to LANGSMITH_API_KEY env var)

    Returns:
        LangSmithConnector instance

    Example:
        >>> connector = create_langsmith_connector("my-rag-project")
        >>> logs = list(connector.fetch_logs(limit=100))
    """
    config = {"project_name": project_name}
    if api_key:
        config["api_key"] = api_key

    return LangSmithConnector(config=config)
