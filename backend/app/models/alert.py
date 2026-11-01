from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class Alert:
    def __init__(
        self,
        id: str = "",
        related_event_id: Optional[str] = None,
        timestamp: int = 0,
        category: str = "",
        severity: str = "medium",
        risk_score: int = 50,
        detection_sources: Optional[List[str]] = None,
        evidence: Optional[Dict[str, Any]] = None,
        status: str = "new",
        notes: Optional[str] = None,
        model_versions: Optional[Dict[str, str]] = None,
        rule_ids: Optional[List[str]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.id = id
        self.related_event_id = related_event_id
        self.timestamp = timestamp
        self.category = category
        self.severity = severity
        self.risk_score = risk_score
        self.detection_sources = detection_sources or []
        self.evidence = evidence or {}
        self.status = status
        self.notes = notes
        self.model_versions = model_versions or {}
        self.rule_ids = rule_ids or []
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "related_event_id": self.related_event_id,
            "timestamp": self.timestamp,
            "category": self.category,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "detection_sources": self.detection_sources,
            "evidence": self.evidence,
            "status": self.status,
            "notes": self.notes,
            "model_versions": self.model_versions,
            "rule_ids": self.rule_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["Alert"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id", ""),
            related_event_id=doc.get("related_event_id"),
            timestamp=doc.get("timestamp", 0),
            category=doc.get("category", ""),
            severity=doc.get("severity", "medium"),
            risk_score=doc.get("risk_score", 50),
            detection_sources=doc.get("detection_sources") or [],
            evidence=doc.get("evidence") or {},
            status=doc.get("status", "new"),
            notes=doc.get("notes"),
            model_versions=doc.get("model_versions") or {},
            rule_ids=doc.get("rule_ids") or [],
            created_at=doc.get("created_at"),
            updated_at=doc.get("updated_at"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "relatedEventId": self.related_event_id,
            "timestamp": self.timestamp,
            "category": self.category,
            "severity": self.severity,
            "riskScore": self.risk_score,
            "detectionSources": self.detection_sources or [],
            "evidence": self.evidence or {},
            "status": self.status,
            "notes": self.notes or "",
            "modelVersions": self.model_versions or {},
            "ruleIds": self.rule_ids or [],
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
