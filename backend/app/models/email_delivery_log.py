from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid


class EmailDeliveryLog:
    """
    Audit log of email notification attempts.
    Tracks delivery state, provider response, and retry attempts.
    Never stores verification tokens in plaintext, passwords, or secrets.
    """
    def __init__(
        self,
        id: Optional[str] = None,
        user_id: Optional[int] = None,
        workspace_id: Optional[str] = None,
        recipient_email: str = "",
        sender: str = "revenreven287@gmail.com",
        subject: Optional[str] = None,
        template_name: Optional[str] = None,
        notification_type: str = "general",  # "email_verification" | "welcome" | "first_login" | "password_reset" | "verification_reminder" | "security_alert" | "support_acknowledgment"
        provider: str = "smtp",
        provider_message_id: Optional[str] = None,
        provider_response_status: Optional[str] = None,
        attempt_count: int = 1,
        status: str = "awaiting_configuration",  # "queued" | "sent_to_provider" | "provider_accepted" | "delivered" | "failed" | "awaiting_configuration"
        error_message: Optional[str] = None,
        attempted_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
    ):
        self.id = id or f"EML-{uuid.uuid4().hex[:12].upper()}"
        self.user_id = user_id
        self.workspace_id = workspace_id or "ws_system"
        self.recipient_email = recipient_email.lower().strip()
        self.sender = sender.lower().strip()
        self.subject = subject
        self.template_name = template_name or notification_type
        self.notification_type = notification_type
        self.provider = provider
        self.provider_message_id = provider_message_id
        self.provider_response_status = provider_response_status
        self.attempt_count = attempt_count
        self.status = status
        self.error_message = error_message
        now = datetime.now(timezone.utc)
        self.attempted_at = attempted_at or now
        self.created_at = created_at or attempted_at or now
        self.updated_at = updated_at or now
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "workspace_id": self.workspace_id,
            "recipient_email": self.recipient_email,
            "recipient": self.recipient_email,
            "sender": self.sender,
            "subject": self.subject,
            "template_name": self.template_name,
            "notification_type": self.notification_type,
            "provider": self.provider,
            "provider_message_id": self.provider_message_id,
            "provider_response_status": self.provider_response_status,
            "attempt_count": self.attempt_count,
            "attempted_at": self.attempted_at,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["EmailDeliveryLog"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id"),
            user_id=doc.get("user_id"),
            workspace_id=doc.get("workspace_id"),
            recipient_email=doc.get("recipient_email") or doc.get("recipient", ""),
            sender=doc.get("sender", "revenreven287@gmail.com"),
            subject=doc.get("subject"),
            template_name=doc.get("template_name") or doc.get("notification_type"),
            notification_type=doc.get("notification_type", "general"),
            provider=doc.get("provider", "smtp"),
            provider_message_id=doc.get("provider_message_id"),
            provider_response_status=doc.get("provider_response_status"),
            attempt_count=doc.get("attempt_count", 1),
            attempted_at=doc.get("attempted_at"),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            status=doc.get("status", "unknown"),
            error_message=doc.get("error_message"),
            _id=doc.get("_id"),
        )
