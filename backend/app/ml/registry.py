from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.config import settings
from app.ml.random_forest import RandomForestModel
from app.ml.decision_tree import DecisionTreeModel
from app.ml.isolation_forest import IsolationForestModel
from app.detection.feature_schema import FEATURE_COUNT


class ModelRegistryManager:
    def __init__(self, artifact_dir: Optional[str] = None):
        self.artifact_dir = Path(artifact_dir or settings.MODEL_ARTIFACT_DIR)
        self.rf = RandomForestModel(self.artifact_dir / "random_forest.joblib")
        self.dt = DecisionTreeModel(self.artifact_dir / "decision_tree.joblib")
        self.iforest = IsolationForestModel(self.artifact_dir / "isolation_forest.joblib")

    def reload_all(self):
        self.rf.load(self.artifact_dir / "random_forest.joblib")
        self.dt.load(self.artifact_dir / "decision_tree.joblib")
        self.iforest.load(self.artifact_dir / "isolation_forest.joblib")

    def get_models_metadata(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "Random Forest classifier",
                "version": self.rf.version,
                "dataset": "CIC-IDS2017 (sample split)",
                "evaluated": "2026-10-02",
                "status": "Loaded" if self.rf.is_loaded else "Not Loaded",
                "classes": self.rf.classes,
                "features": FEATURE_COUNT,
            },
            {
                "name": "Isolation Forest anomaly detector",
                "version": self.iforest.version,
                "dataset": "Benign baseline (local)",
                "evaluated": "2026-10-01",
                "status": "Loaded" if self.iforest.is_loaded else "Not Loaded",
                "classes": ["Normal", "Anomalous"],
                "features": FEATURE_COUNT,
            },
            {
                "name": "Decision Tree baseline",
                "version": self.dt.version,
                "dataset": "CIC-IDS2017",
                "evaluated": "2026-10-01",
                "status": "Loaded" if self.dt.is_loaded else "Not Loaded",
                "classes": self.dt.classes,
                "features": FEATURE_COUNT,
            },
            {
                "name": "Hybrid risk engine",
                "version": "hre-1.0.0",
                "dataset": "Rules + RF + IF outputs",
                "evaluated": "2026-10-03",
                "status": "Active",
                "classes": ["Risk score 0–100"],
                "features": 6,
            },
        ]


registry = ModelRegistryManager()
