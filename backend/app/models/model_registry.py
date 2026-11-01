from datetime import datetime, timezone
from typing import Optional, Dict, Any, List


class ModelRegistry:
    def __init__(
        self,
        name: str = "",
        version: str = "",
        artifact_location: str = "",
        training_dataset: str = "CIC-IDS2017",
        feature_schema_version: str = "v1.0",
        features_count: int = 78,
        classes: Optional[List[str]] = None,
        evaluation_metrics: Optional[Dict[str, float]] = None,
        confusion_matrix: Optional[Dict[str, Any]] = None,
        per_class_metrics: Optional[List[Dict[str, Any]]] = None,
        status: str = "Loaded",
        created_at: Optional[datetime] = None,
        id: Optional[int] = None,
        _id: Optional[Any] = None,
        **kwargs,
    ):
        self.name = name
        self.version = version
        self.artifact_location = artifact_location
        self.training_dataset = training_dataset
        self.feature_schema_version = feature_schema_version
        self.features_count = features_count
        self.classes = classes or []
        self.evaluation_metrics = evaluation_metrics or {}
        self.confusion_matrix = confusion_matrix or {}
        self.per_class_metrics = per_class_metrics or []
        self.status = status
        self.created_at = created_at or datetime.now(timezone.utc)
        self.id = id or 1
        self._id = _id

    def to_doc(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "artifact_location": self.artifact_location,
            "training_dataset": self.training_dataset,
            "feature_schema_version": self.feature_schema_version,
            "features_count": self.features_count,
            "classes": self.classes,
            "evaluation_metrics": self.evaluation_metrics,
            "confusion_matrix": self.confusion_matrix,
            "per_class_metrics": self.per_class_metrics,
            "status": self.status,
            "created_at": self.created_at,
        }

    @classmethod
    def from_doc(cls, doc: Optional[Dict[str, Any]]) -> Optional["ModelRegistry"]:
        if not doc:
            return None
        return cls(
            id=doc.get("id"),
            name=doc.get("name", ""),
            version=doc.get("version", ""),
            artifact_location=doc.get("artifact_location", ""),
            training_dataset=doc.get("training_dataset", "CIC-IDS2017"),
            feature_schema_version=doc.get("feature_schema_version", "v1.0"),
            features_count=doc.get("features_count", 78),
            classes=doc.get("classes") or [],
            evaluation_metrics=doc.get("evaluation_metrics") or {},
            confusion_matrix=doc.get("confusion_matrix") or {},
            per_class_metrics=doc.get("per_class_metrics") or [],
            status=doc.get("status", "Loaded"),
            created_at=doc.get("created_at"),
            _id=doc.get("_id"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "dataset": self.training_dataset,
            "evaluated": self.created_at.strftime("%Y-%m-%d") if self.created_at else "",
            "status": self.status,
            "classes": self.classes or [],
            "features": self.features_count,
            "metrics": self.evaluation_metrics or {},
        }
