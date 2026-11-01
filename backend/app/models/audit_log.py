from datetime import datetime, timezone
from typing import Optional, Dict, Any


class AuditLog:
    def __init__(
        self,
        id: str = "",
        timestamp: int = 0,
        actor: str = "",
        action: str = "",
        target: str = "",
        result: str = "Success",
        reason: str = "—",
        related: str = "—",
        correlation_id: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.timestamp = timestamp
        self.actor = actor
        self.action = action
        self.target = target
        self.result = result
        self.reason = reason
        self.related = related
        self.correlation_id = correlation_id
        self.extra_metadata = extra_metadata or {}
        self.created_at = created_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "target": self.target,
            "result": self.result,
            "reason": self.reason,
            "related": self.related,
            "correlation_id": self.correlation_id,
            "extra_metadata": self.extra_metadata,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["AuditLog"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id", ""),
            timestamp=doc.get("timestamp", 0),
            actor=doc.get("actor", ""),
            action=doc.get("action", ""),
            target=doc.get("target", ""),
            result=doc.get("result", "Success"),
            reason=doc.get("reason", "—"),
            related=doc.get("related", "—"),
            correlation_id=doc.get("correlation_id"),
            extra_metadata=doc.get("extra_metadata"),
            created_at=doc.get("created_at"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "actor": self.actor,
            "action": self.action,
            "target": self.target,
            "result": self.result,
            "reason": self.reason,
            "related": self.related,
        }
