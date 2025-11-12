"""
JSONL (JSON Lines) connector for custom RAG logs.

Supports reading RAG logs from .jsonl files where each line is a JSON object.

Expected format:
{
  "query": "What's the refund policy?",
  "response": "Our refund policy...",
  "retrieved_chunks": [
    {
      "text": "...",
      "score": 0.89,
      "doc_id": "doc_123",
      "metadata": {}
    }
  ],
  "timestamp": "2024-01-15T10:23:45.123Z",
  "user_feedback": "thumbs_up",  // optional
  "session_id": "user_abc123",   // optional
  "model": "gpt-4o-mini",         // optional
  "tokens": {"prompt": 456, "completion": 52}  // optional
}
"""

import json
import glob
from pathlib import Path
from typing import Iterator, Optional, List
from datetime import datetime
from .base import BaseConnector
from ..models import RAGLog, RetrievedChunk, FeedbackType


class JSONLConnector(BaseConnector):
    """Connector for JSONL log files"""

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize JSONL connector.

        Args:
            config: Configuration dict with:
                - file_path: Path to JSONL file or glob pattern (e.g., "logs/*.jsonl")
        """
        super().__init__(config)
        self.file_path = self.config.get("file_path")

        if not self.file_path:
            raise ValueError("file_path is required in config")

    def connect(self) -> bool:
        """Test that files exist"""
        files = self._get_files()
        if not files:
            raise ConnectionError(f"No files found matching: {self.file_path}")
        return True

    def _get_files(self) -> List[Path]:
        """Get list of files matching pattern"""
        path = Path(self.file_path)

        # If exact file
        if path.is_file():
            return [path]

        # If glob pattern
        if "*" in str(path):
            files = [Path(p) for p in glob.glob(str(path))]
            return sorted(files)

        # If directory, get all .jsonl files
        if path.is_dir():
            files = list(path.glob("*.jsonl"))
            return sorted(files)

        return []

    def fetch_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Iterator[RAGLog]:
        """
        Fetch logs from JSONL files.

        Yields RAGLog objects in chronological order.
        """
        files = self._get_files()
        count = 0

        for file_path in files:
            with open(file_path, "r") as f:
                for line_num, line in enumerate(f, 1):
                    # Check limit
                    if limit and count >= limit:
                        return

                    # Parse JSON
                    try:
                        data = json.loads(line.strip())
                    except json.JSONDecodeError as e:
                        print(f"⚠️  Skipping invalid JSON at {file_path}:{line_num}: {e}")
                        continue

                    # Convert to RAGLog
                    try:
                        log = self._parse_log(data)
                    except Exception as e:
                        print(f"⚠️  Skipping invalid log at {file_path}:{line_num}: {e}")
                        continue

                    # Filter by date
                    if start_date and log.timestamp < start_date:
                        continue
                    if end_date and log.timestamp > end_date:
                        continue

                    # Validate
                    if not self.validate_log(log):
                        print(f"⚠️  Skipping invalid log at {file_path}:{line_num}")
                        continue

                    yield log
                    count += 1

    def count_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """Count total logs"""
        count = 0
        for _ in self.fetch_logs(start_date, end_date):
            count += 1
        return count

    def _parse_log(self, data: dict) -> RAGLog:
        """Parse JSON data into RAGLog"""
        # Parse timestamp
        timestamp_str = data.get("timestamp")
        if isinstance(timestamp_str, str):
            # Try ISO format
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.now()
        else:
            timestamp = datetime.now()

        # Parse retrieved chunks
        chunks_data = data.get("retrieved_chunks", [])
        chunks = []
        for chunk_data in chunks_data:
            chunk = RetrievedChunk(
                text=chunk_data.get("text", ""),
                score=float(chunk_data.get("score", 0.0)),
                doc_id=chunk_data.get("doc_id", "unknown"),
                metadata=chunk_data.get("metadata", {})
            )
            chunks.append(chunk)

        # Parse user feedback
        feedback_str = data.get("user_feedback")
        user_feedback = None
        if feedback_str == "thumbs_up":
            user_feedback = FeedbackType.THUMBS_UP
        elif feedback_str == "thumbs_down":
            user_feedback = FeedbackType.THUMBS_DOWN

        # Create RAGLog
        return RAGLog(
            query=data.get("query", ""),
            response=data.get("response", ""),
            retrieved_chunks=chunks,
            timestamp=timestamp,
            user_feedback=user_feedback,
            session_id=data.get("session_id"),
            model=data.get("model"),
            tokens=data.get("tokens"),
            metadata=data.get("metadata", {})
        )


def create_jsonl_connector(file_path: str) -> JSONLConnector:
    """
    Convenience function to create JSONL connector.

    Args:
        file_path: Path to JSONL file(s)

    Returns:
        JSONLConnector instance

    Example:
        >>> connector = create_jsonl_connector("logs/*.jsonl")
        >>> logs = list(connector.fetch_logs(limit=10))
    """
    return JSONLConnector(config={"file_path": file_path})
