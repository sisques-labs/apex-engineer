"""Base AI module interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AIModule(ABC):
    """Abstract base class for AI modules"""

    @abstractmethod
    def generate_response(
        self, user_query: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate AI response to user query

        Args:
            user_query: User's question or command
            context: Optional telemetry context

        Returns:
            AI-generated response string
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if AI module is available and ready

        Returns:
            True if available, False otherwise
        """
        pass

