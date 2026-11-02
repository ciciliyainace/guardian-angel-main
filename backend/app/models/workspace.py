from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class Workspace:
    """
    Tenant Workspace domain model.
    Every user owns an isolated workspace where their sensors, telemetry,
    alerts, and firewall configurations reside.
    """
    def __init__(
        self,
        id: str,
        name: str,
        owner_user_id: int,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        is_active: bool = True,
        members: Optional[List[Dict[str, Any]]] = None,
        settings: Optional[Dict[str, Any]] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.owner_user_id = int(owner_user_id)
        self.description = description or ""
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.is_active = is_active
        # Default members list contains the owner with 'owner' role
        self.members = members if members is not None else [
            {"user_id": int(owner_user_id), "role": "owner", "added_at": self.created_at.isoformat()}
        ]
        self.settings = settings or {
            "retention_days": 90,
            "alert_email_notifications": True,
            "max_sensors": 10,
        }
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "owner_user_id": self.owner_user_id,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active,
            "members": self.members,
            "settings": self.settings,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["Workspace"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id", ""),
            name=doc.get("name", ""),
            owner_user_id=doc.get("owner_user_id", 0),
            description=doc.get("description", ""),
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            is_active=doc.get("is_active", True),
            members=doc.get("members", []),
            settings=doc.get("settings", {}),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "ownerUserId": self.owner_user_id,
            "description": self.description,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "isActive": self.is_active,
            "memberCount": len(self.members),
            "settings": self.settings,
        }
