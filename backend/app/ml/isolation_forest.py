from pathlib import Path
from typing import Dict, Any, Optional
import joblib
import numpy as np
from app.core.exceptions import ModelNotLoadedError
from app.detection.thresholds import DEFAULT_THRESHOLDS
from app.core.logging_config import logger


class IsolationForestModel:
    """
    Isolation Forest Anomaly Detector.
    
    Score direction semantics:
    - Scikit-learn `decision_function(X)` outputs lower (negative) values for outliers/anomalies,
      and higher (positive) values for normal inliers.
    - An observation is flagged anomalous if `anomaly_score < threshold`.
    - Anomalies represent statistical deviation, NOT confirmed malicious attacks.
    """
    def __init__(self, model_path: Optional[str] = None, threshold: Optional[float] = None):
        self.model_path = Path(model_path) if model_path else None
        self.model = None
        self.version = "if-0.9.2"
        self.threshold = threshold if threshold is not None else DEFAULT_THRESHOLDS["isolation_forest_anomaly_threshold"]
        self.is_loaded = False
        if self.model_path and self.model_path.exists():
            self.load()

    def load(self, path: Optional[str] = None):
        target = Path(path) if path else self.model_path
        if not target or not target.exists():
            self.is_loaded = False
            return False

        try:
            artifact = joblib.load(target)
            if isinstance(artifact, dict) and "model" in artifact:
                self.model = artifact["model"]
                self.version = artifact.get("version", self.version)
                self.threshold = artifact.get("threshold", self.threshold)
            else:
                self.model = artifact
            self.is_loaded = True
            logger.info(f"Loaded Isolation Forest model {self.version} from {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Isolation Forest model artifact: {e}")
            self.is_loaded = False
            return False

    def predict(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None:
            raise ModelNotLoadedError("Isolation Forest anomaly detector")

        if len(feature_vector.shape) == 1:
            feature_vector = feature_vector.reshape(1, -1)

        # decision_function gives signed anomaly score: negative = outlier, positive = inlier
        raw_score = float(self.model.decision_function(feature_vector)[0])
        is_anomalous = raw_score < self.threshold

        # Compute normalized anomaly intensity 0.0 - 1.0 (higher = more anomalous)
        # Typical range is [-0.5, 0.5]
        normalized_intensity = min(1.0, max(0.0, (0.2 - raw_score) / 0.7))

        return {
            "raw_score": round(raw_score, 4),
            "threshold": self.threshold,
            "is_anomalous": is_anomalous,
            "anomaly_intensity": round(normalized_intensity, 4),
            "version": self.version,
        }
