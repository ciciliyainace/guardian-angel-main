from pathlib import Path
from typing import Dict, Any, Optional, List
import joblib
import numpy as np
from app.core.exceptions import ModelNotLoadedError
from app.core.logging_config import logger


class RandomForestModel:
    def __init__(self, model_path: Optional[str] = None):
        self.model_path = Path(model_path) if model_path else None
        self.model = None
        self.version = "rf-1.3.0"
        self.classes: List[str] = ["Benign", "PortScan", "DoS", "BruteForce", "Bot"]
        self.is_loaded = False
        if self.model_path and self.model_path.exists():
            self.load()

    def load(self, path: Optional[str] = None):
        target = Path(path) if path else self.model_path
        if not target or not target.exists():
            logger.info(f"Random Forest model artifact not found at {target}. Model remains in Not Loaded state.")
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
            logger.info(f"Loaded Random Forest model {self.version} from {target}")
            return True
        except Exception as e:
            logger.error(f"Failed to load Random Forest model artifact: {e}")
            self.is_loaded = False
            return False

    def predict(self, feature_vector: np.ndarray) -> Dict[str, Any]:
        if not self.is_loaded or self.model is None:
            raise ModelNotLoadedError("Random Forest classifier")

        if len(feature_vector.shape) == 1:
            feature_vector = feature_vector.reshape(1, -1)

        pred_idx = self.model.predict(feature_vector)[0]
        # Handle string or int label
        if isinstance(pred_idx, (int, np.integer)) and pred_idx < len(self.classes):
            predicted_class = self.classes[pred_idx]
        else:
            predicted_class = str(pred_idx)

        probabilities = {}
        if hasattr(self.model, "predict_proba"):
            probs = self.model.predict_proba(feature_vector)[0]
            for idx, p in enumerate(probs):
                label = self.classes[idx] if idx < len(self.classes) else f"Class_{idx}"
                probabilities[label] = round(float(p), 4)

        confidence = probabilities.get(predicted_class, 1.0)

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "probabilities": probabilities,
            "version": self.version,
            "is_attack": predicted_class != "Benign",
        }
