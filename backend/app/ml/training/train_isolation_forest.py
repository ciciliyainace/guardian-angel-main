from pathlib import Path
from typing import Dict, Any
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from app.detection.feature_schema import SCHEMA_VERSION, FEATURE_COUNT
from app.core.logging_config import logger


def train_isolation_forest(
    X_benign: np.ndarray,
    output_path: str = "artifacts/isolation_forest.joblib",
    contamination: float = 0.03,
) -> Dict[str, Any]:
    """Train Isolation Forest on benign baseline flows and persist artifact."""
    logger.info("Training Isolation Forest anomaly detector on benign baseline...")
    iso = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    iso.fit(X_benign)

    artifact_dir = Path(output_path).parent
    artifact_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": iso,
        "version": "if-0.9.2",
        "schema_version": SCHEMA_VERSION,
        "features_count": FEATURE_COUNT,
        "threshold": -0.10,
    }
    joblib.dump(artifact, output_path)
    logger.info(f"Isolation Forest model artifact saved to {output_path}")

    return artifact
