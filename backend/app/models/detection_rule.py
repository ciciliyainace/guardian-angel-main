from datetime import datetime, timezone
from typing import Optional, Dict, Any


class DetectionRule:
    def __init__(
        self,
        id: str = "",
        name: str = "",
        description: str = "",
        category: str = "",
        severity: str = "medium",
        enabled: bool = True,
        threshold: int = 10,
        window_sec: int = 60,
        last_triggered: int = 0,
        matches: int = 0,
        rule_type: str = "threshold",
        config: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.category = category
        self.severity = severity
        self.enabled = enabled
        self.threshold = threshold
        self.window_sec = window_sec
        self.last_triggered = last_triggered
        self.matches = matches
        self.rule_type = rule_type
        self.config = config or {}
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "enabled": self.enabled,
            "threshold": self.threshold,
            "window_sec": self.window_sec,
            "last_triggered": self.last_triggered,
            "matches": self.matches,
            "rule_type": self.rule_type,
            "config": self.config,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["DetectionRule"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id", ""),
            name=doc.get("name", ""),
            description=doc.get("description", ""),
            category=doc.get("category", ""),
            severity=doc.get("severity", "medium"),
            enabled=doc.get("enabled", True),
            threshold=doc.get("threshold", 10),
            window_sec=doc.get("window_sec", 60),
            last_triggered=doc.get("last_triggered", 0),
            matches=doc.get("matches", 0),
            rule_type=doc.get("rule_type", "threshold"),
            config=doc.get("config") or {},
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "severity": self.severity,
            "enabled": self.enabled,
            "threshold": self.threshold,
            "windowSec": self.window_sec,
            "lastTriggered": self.last_triggered,
            "matches": self.matches,
            "ruleType": self.rule_type,
            "config": self.config or {},
        }
