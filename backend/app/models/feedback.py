from datetime import datetime, timezone
from typing import Optional, Dict, Any


class Feedback:
    def __init__(
        self,
        id: Optional[int] = None,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
        category: str = "general",
        message: str = "",
        status: str = "received",
        created_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.user_id = user_id
        self.user_email = user_email
        self.category = category
        self.message = message
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "category": self.category,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["Feedback"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id"),
            user_id=doc.get("user_id"),
            user_email=doc.get("user_email"),
            category=doc.get("category", "general"),
            message=doc.get("message", ""),
            status=doc.get("status", "received"),
            created_at=doc.get("created_at"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "userEmail": self.user_email,
            "category": self.category,
            "message": self.message,
            "status": self.status,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
