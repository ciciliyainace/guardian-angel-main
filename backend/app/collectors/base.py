from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class BaseCollector(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = "Disconnected"  # Operational, Degraded, Disconnected, Error
        self.event_count = 0
        self.last_ingestion_time: Optional[datetime] = None
        self.last_error: Optional[str] = None
        self.detail: str = "Initialized"

    @abstractmethod
    def start(self) -> None:
        """Start the collector."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop the collector."""
        pass

    @abstractmethod
    def collect(self) -> list:
        """Fetch newly available events."""
        pass

    def record_success(self, count: int = 1, detail: Optional[str] = None):
        self.status = "Operational"
        self.event_count += count
        self.last_ingestion_time = datetime.now(timezone.utc)
        self.last_error = None
        if detail:
            self.detail = detail

    def record_error(self, error: str, degraded: bool = False):
        self.status = "Degraded" if degraded else "Error"
        self.last_error = error
        self.detail = error

    def get_health_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "eventCount": self.event_count,
            "lastIngestion": self.last_ingestion_time.isoformat() if self.last_ingestion_time else None,
            "error": self.last_error,
        }
