from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class User:
    def __init__(
        self,
        id: Optional[int] = None,
        email: str = "",
        username: str = "",
        display_name: str = "",
        hashed_password: str = "",
        password_hash: str = "",
        role: str = "analyst",
        is_active: bool = True,
        auth_providers: Optional[List[str]] = None,
        google_sub: Optional[str] = None,
        email_verified: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        first_login_at: Optional[datetime] = None,
        last_login_at: Optional[datetime] = None,
        welcome_email_sent_at: Optional[datetime] = None,
        first_login_email_sent_at: Optional[datetime] = None,
        failed_login_attempts: int = 0,
        lockout_until: Optional[datetime] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id or 1
        self.email = email.lower() if email else ""
        self.username = username
        self.display_name = display_name or username
        # Support both hashed_password and password_hash interchangeably
        self.hashed_password = hashed_password or password_hash or ""
        self.password_hash = self.hashed_password
        self.role = role
        self.is_active = is_active
        self.auth_providers = auth_providers if auth_providers is not None else ["password"]
        self.google_sub = google_sub
        self.email_verified = email_verified
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.first_login_at = first_login_at
        self.last_login_at = last_login_at
        self.welcome_email_sent_at = welcome_email_sent_at
        self.first_login_email_sent_at = first_login_email_sent_at
        self.failed_login_attempts = failed_login_attempts
        self.lockout_until = lockout_until
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        """Serialize user to MongoDB document format."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "display_name": self.display_name,
            "hashed_password": self.hashed_password,
            "password_hash": self.hashed_password,
            "role": self.role,
            "is_active": self.is_active,
            "auth_providers": self.auth_providers,
            "google_sub": self.google_sub,
            "email_verified": self.email_verified,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "first_login_at": self.first_login_at,
            "last_login_at": self.last_login_at,
            "welcome_email_sent_at": self.welcome_email_sent_at,
            "first_login_email_sent_at": self.first_login_email_sent_at,
            "failed_login_attempts": self.failed_login_attempts,
            "lockout_until": self.lockout_until,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["User"]:
        """Deserialize MongoDB document to User model instance."""
        if not doc:
            return None
        # Handle created_at and last_login format whether epoch or datetime
        created = doc.get("created_at")
        if isinstance(created, (int, float)):
            try:
                created = datetime.fromtimestamp(created / 1000.0, tz=timezone.utc)
            except Exception:
                created = datetime.now(timezone.utc)

        first_login = doc.get("first_login_at")
        if isinstance(first_login, (int, float)):
            try:
                first_login = datetime.fromtimestamp(first_login / 1000.0, tz=timezone.utc)
            except Exception:
                first_login = None

        last_login = doc.get("last_login_at") or doc.get("last_login")
        if isinstance(last_login, (int, float)):
            try:
                last_login = datetime.fromtimestamp(last_login / 1000.0, tz=timezone.utc)
            except Exception:
                last_login = None

        # Determine email verification: existing admins/analysts or explicitly verified
        is_verified = doc.get("email_verified", False)
        if doc.get("role") in ("admin", "administrator"):
            is_verified = doc.get("email_verified", True)

        return cls(
            id=doc.get("id"),
            email=doc.get("email", ""),
            username=doc.get("username", ""),
            display_name=doc.get("display_name", "") or doc.get("displayName", ""),
            hashed_password=doc.get("hashed_password") or doc.get("password_hash") or "",
            password_hash=doc.get("password_hash") or doc.get("hashed_password") or "",
            role=doc.get("role", "analyst"),
            is_active=doc.get("is_active", True),
            auth_providers=doc.get("auth_providers", ["password"]),
            google_sub=doc.get("google_sub"),
            email_verified=is_verified,
            created_at=created,
            updated_at=doc.get("updated_at"),
            first_login_at=first_login,
            last_login_at=last_login,
            welcome_email_sent_at=doc.get("welcome_email_sent_at"),
            first_login_email_sent_at=doc.get("first_login_email_sent_at"),
            failed_login_attempts=doc.get("failed_login_attempts", 0),
            lockout_until=doc.get("lockout_until"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Return safe API response dictionary without password hashes or internal secrets."""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "displayName": self.display_name,
            "role": self.role,
            "isActive": self.is_active,
            "emailVerified": self.email_verified,
            "authProviders": self.auth_providers,
            "firstLoginAt": self.first_login_at.isoformat() if self.first_login_at else None,
            "lastLoginAt": self.last_login_at.isoformat() if self.last_login_at else None,
            "createdAt": self.created_at.isoformat() if hasattr(self.created_at, "isoformat") else str(self.created_at),
        }

    def __repr__(self):
        return f"<User {self.username} ({self.role}) provider={self.auth_providers}>"
