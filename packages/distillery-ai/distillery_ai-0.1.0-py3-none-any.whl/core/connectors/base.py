"""
Base connector interface.

All log connectors must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import List, Iterator, Optional
from datetime import datetime
from ..models import RAGLog


class BaseConnector(ABC):
    """Base class for RAG log connectors"""

    def __init__(self, config: Optional[dict] = None):
        """
        Initialize connector with configuration.

        Args:
            config: Connector-specific configuration
        """
        self.config = config or {}

    @abstractmethod
    def connect(self) -> bool:
        """
        Test connection to log source.

        Returns:
            True if connection successful

        Raises:
            ConnectionError: If cannot connect
        """
        pass

    @abstractmethod
    def fetch_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> Iterator[RAGLog]:
        """
        Fetch RAG logs from source.

        Args:
            start_date: Filter logs after this date
            end_date: Filter logs before this date
            limit: Maximum number of logs to fetch

        Yields:
            RAGLog objects

        Raises:
            ValueError: If invalid date range
            RuntimeError: If fetch fails
        """
        pass

    @abstractmethod
    def count_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> int:
        """
        Count total logs in source.

        Args:
            start_date: Filter logs after this date
            end_date: Filter logs before this date

        Returns:
            Total log count
        """
        pass

    def validate_log(self, log: RAGLog) -> bool:
        """
        Validate a RAG log entry.

        Args:
            log: RAG log to validate

        Returns:
            True if valid
        """
        try:
            # Check required fields
            if not log.query or not log.response:
                return False

            if not log.retrieved_chunks:
                return False

            # Check retrieval scores
            for chunk in log.retrieved_chunks:
                if not 0.0 <= chunk.score <= 1.0:
                    return False

            return True

        except Exception:
            return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"
