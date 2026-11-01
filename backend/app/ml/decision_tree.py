from pathlib import Path
from typing import Dict, Any, Optional, List
import joblib
import numpy as np
from app.core.exceptions import ModelNotLoadedError
from app.core.logging_config import logger


class DecisionTreeModel:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path) if model_path else None
        self.model = None
        self.version = "dt-1.0.0"
        self.classes: List[str] = ["Benign", "PortScan", "DoS", "BruteForce", "Bot"]
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
                self.classes = artifact.get("classes", self.classes)
            else:
                self.model = artifact
            self.is_loaded = True
            return True
        except Exception as e:
            logger.error(f"Failed to load Decision Tree model artifact: {e}")
            self.is_loaded = False
            return False

    def predict(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None:
            raise ModelNotLoadedError("Decision Tree baseline")

        if len(feature_vector.shape) == 1:
            feature_vector = feature_vector.reshape(1, -1)

        pred = self.model.predict(feature_vector)[0]
        predicted_class = self.classes[pred] if isinstance(pred, (int, np.integer)) and pred < len(self.classes) else str(pred)

        return {
            "predicted_class": predicted_class,
            "version": self.version,
            "is_attack": predicted_class != "Benign",
        }
