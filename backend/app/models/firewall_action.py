from datetime import datetime, timezone
from typing import Optional, Dict, Any


class FirewallAction:
    def __init__(
        self,
        id: str = "",
        managed_rule_name: str = "",
        request_id: Optional[str] = None,
        target_ip: str = "",
        direction: str = "Inbound",
        action_type: str = "block",
        status: str = "created",
        duration_min: int = 60,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        verification_status: str = "simulated",
        rollback_status: Optional[str] = None,
        failure_details: Optional[str] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.managed_rule_name = managed_rule_name
        self.request_id = request_id
        self.target_ip = target_ip
        self.direction = direction
        self.action_type = action_type
        self.status = status
        self.duration_min = duration_min
        self.created_at = created_at or datetime.now(timezone.utc)
        self.expires_at = expires_at
        self.verification_status = verification_status
        self.rollback_status = rollback_status
        self.failure_details = failure_details
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "managed_rule_name": self.managed_rule_name,
            "request_id": self.request_id,
            "target_ip": self.target_ip,
            "direction": self.direction,
            "action_type": self.action_type,
            "status": self.status,
            "duration_min": self.duration_min,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "verification_status": self.verification_status,
            "rollback_status": self.rollback_status,
            "failure_details": self.failure_details,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["FirewallAction"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id", ""),
            managed_rule_name=doc.get("managed_rule_name", ""),
            request_id=doc.get("request_id"),
            target_ip=doc.get("target_ip", ""),
            direction=doc.get("direction", "Inbound"),
            action_type=doc.get("action_type", "block"),
            status=doc.get("status", "created"),
            duration_min=doc.get("duration_min", 60),
            created_at=doc.get("created_at"),
            expires_at=doc.get("expires_at"),
            verification_status=doc.get("verification_status", "simulated"),
            rollback_status=doc.get("rollback_status"),
            failure_details=doc.get("failure_details"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "managedRuleName": self.managed_rule_name,
            "requestId": self.request_id,
            "targetIp": self.target_ip,
            "direction": self.direction,
            "actionType": self.action_type,
            "status": self.status,
            "durationMin": self.duration_min,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "expiresAt": self.expires_at.isoformat() if self.expires_at else None,
            "verificationStatus": self.verification_status,
            "rollbackStatus": self.rollback_status,
            "failureDetails": self.failure_details,
        }
