from datetime import datetime, timezone
from typing import Optional, Dict, Any


class FirewallRequest:
    def __init__(
        self,
        id: str = "",
        source_ip: str = "",
        reason: str = "",
        alert_id: str = "",
        requested_by: str = "analyst",
        requested_at: int = 0,
        duration_min: int = 60,
        status: str = "pending",
        direction: str = "Inbound",
        reviewed_by: Optional[str] = None,
        reviewed_at: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.source_ip = source_ip
        self.reason = reason
        self.alert_id = alert_id
        self.requested_by = requested_by
        self.requested_at = requested_at
        self.duration_min = duration_min
        self.status = status
        self.direction = direction
        self.reviewed_by = reviewed_by
        self.reviewed_at = reviewed_at
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_ip": self.source_ip,
            "reason": self.reason,
            "alert_id": self.alert_id,
            "requested_by": self.requested_by,
            "requested_at": self.requested_at,
            "duration_min": self.duration_min,
            "status": self.status,
            "direction": self.direction,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["FirewallRequest"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id", ""),
            source_ip=doc.get("source_ip", ""),
            reason=doc.get("reason", ""),
            alert_id=doc.get("alert_id", ""),
            requested_by=doc.get("requested_by", "analyst"),
            requested_at=doc.get("requested_at", 0),
            duration_min=doc.get("duration_min", 60),
            status=doc.get("status", "pending"),
            direction=doc.get("direction", "Inbound"),
            reviewed_by=doc.get("reviewed_by"),
            reviewed_at=doc.get("reviewed_at"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sourceIp": self.source_ip,
            "reason": self.reason,
            "alertId": self.alert_id or "",
            "requestedBy": self.requested_by,
            "requestedAt": self.requested_at,
            "durationMin": self.duration_min,
            "status": self.status,
            "direction": self.direction,
            "reviewedBy": self.reviewed_by,
            "reviewedAt": self.reviewed_at,
        }
