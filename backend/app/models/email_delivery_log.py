from datetime import datetime, timezone
from typing import Optional, Dict, Any


class EmailDeliveryLog:
    """
    Audit log of email notification attempts.
    Never stores verification tokens in plaintext, passwords, or secrets.
    """
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: Optional[int] = None,
        workspace_id: Optional[str] = None,
        recipient_email: str = "",
        notification_type: str = "general",  # "email_verification" | "welcome" | "first_login" | "password_reset"
        provider: str = "smtp",
        provider_message_id: Optional[str] = None,
        attempted_at: Optional[datetime] = None,
        status: str = "awaiting_configuration",  # "delivered" | "failed" | "awaiting_configuration"
        error_message: Optional[str] = None,
        _id: Optional[Any] = None,
    ):
        import uuid
        self.id = id or f"EML-{uuid.uuid4().hex[:12].upper()}"
        self.user_id = user_id
        self.workspace_id = workspace_id or "ws_system"
        self.recipient_email = recipient_email.lower().strip()
        self.notification_type = notification_type
        self.provider = provider
        self.provider_message_id = provider_message_id
        self.attempted_at = attempted_at or datetime.now(timezone.utc)
        self.status = status
        self.error_message = error_message
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "recipient_email": self.recipient_email,
            "notification_type": self.notification_type,
            "provider": self.provider,
            "provider_message_id": self.provider_message_id,
            "attempted_at": self.attempted_at,
            "status": self.status,
            "error_message": self.error_message,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["EmailDeliveryLog"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id"),
            user_id=doc.get("user_id"),
            workspace_id=doc.get("workspace_id"),
            recipient_email=doc.get("recipient_email", ""),
            notification_type=doc.get("notification_type", "general"),
            provider=doc.get("provider", "smtp"),
            provider_message_id=doc.get("provider_message_id"),
            attempted_at=doc.get("attempted_at"),
            status=doc.get("status", "unknown"),
            error_message=doc.get("error_message"),
            _id=doc.get("_id"),
        )

