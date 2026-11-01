from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from app.detection.feature_schema import SCHEMA_VERSION, FEATURE_COUNT
from app.core.logging_config import logger


def train_random_forest(
    X_train: np.ndarray,
    y_train: np.ndarray,
    classes: List[str],
    output_path: str = "artifacts/random_forest.joblib",
    n_estimators: int = 100,
) -> Dict[str, Any]:
    """Train Random Forest classifier and persist versioned artifact."""
    logger.info("Training Random Forest classifier...")
    clf = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=16,
        random_state=42,
        class_weight="balanced",
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    artifact_dir = Path(output_path).parent
    artifact_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": clf,
        "version": "rf-1.3.0",
        "schema_version": SCHEMA_VERSION,
        "features_count": FEATURE_COUNT,
        "classes": classes,
    }
    joblib.dump(artifact, output_path)
    logger.info(f"Random Forest model artifact saved to {output_path}")

    return artifact
