"""Base telemetry reader interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class TelemetryReader(ABC):
    """Abstract base class for telemetry readers"""

    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to telemetry source

        Returns:
            True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from telemetry source"""
        pass

    @abstractmethod
    def read(self) -> Optional[Dict[str, Any]]:
        """
        Read current telemetry data

        Returns:
            Dictionary with telemetry data or None if unavailable
        """
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to telemetry source

        Returns:
            True if connected, False otherwise
        """
        pass

