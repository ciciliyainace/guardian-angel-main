from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid


class SupportMessage:
    """
    Support inquiry or feedback ticket submitted by an analyst or user.
    Stored in 'support_messages' collection.
    """
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: Optional[int] = None,
        workspace_id: Optional[str] = None,
        email: str = "",
        name: Optional[str] = None,
        subject: str = "",
        category: str = "General",  # "Account", "Verification", "Telemetry", "Sensor", "General"
        message: str = "",
        status: str = "open",  # "open", "in_progress", "resolved", "closed"
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
    ):
        self.id = id or f"SUP-{uuid.uuid4().hex[:8].upper()}"
        self.user_id = user_id
        self.workspace_id = workspace_id or "ws_system"
        self.email = email.lower().strip()
        self.name = name
        self.subject = subject.strip()
        self.category = category
        self.message = message.strip()
        self.status = status
        now = datetime.now(timezone.utc)
        self.created_at = created_at or now
        self.updated_at = updated_at or now
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "email": self.email,
            "name": self.name,
            "subject": self.subject,
            "category": self.category,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["SupportMessage"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id"),
            user_id=doc.get("user_id"),
            workspace_id=doc.get("workspace_id"),
            email=doc.get("email", ""),
            name=doc.get("name"),
            subject=doc.get("subject", ""),
            category=doc.get("category", "General"),
            message=doc.get("message", ""),
            status=doc.get("status", "open"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            _id=doc.get("_id"),
        )
