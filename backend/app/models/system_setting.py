from datetime import datetime, timezone
from typing import Optional, Dict, Any


class SystemSetting:
    def __init__(
        self,
        key: str = "",
        value: Any = None,
        category: str = "general",
        description: Optional[str] = None,
        updated_at: Optional[datetime] = None,
        updated_by: str = "system",
        id: Optional[int] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.key = key
        self.value = value
        self.category = category
        self.description = description
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self.updated_by = updated_by
        self.id = id
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "description": self.description,
            "updated_at": self.updated_at,
            "updated_by": self.updated_by,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["SystemSetting"]:
        if not doc:
            return None
        return cls(
            key=doc.get("key", ""),
            value=doc.get("value"),
            category=doc.get("category", "general"),
            description=doc.get("description"),
            updated_at=doc.get("updated_at"),
            updated_by=doc.get("updated_by", "system"),
            id=doc.get("id"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "key": self.key,
            "value": self.value,
            "category": self.category,
            "description": self.description,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
            "updatedBy": self.updated_by,
        }
