from pathlib import Path
from typing import Dict, Any, List
import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from app.detection.feature_schema import SCHEMA_VERSION, FEATURE_COUNT
from app.core.logging_config import logger


def train_decision_tree(
    X_train: np.ndarray,
    y_train: np.ndarray,
    classes: List[str],
    output_path: str = "artifacts/decision_tree.joblib",
    max_depth: int = 12,
) -> Dict[str, Any]:
    """Train Decision Tree baseline classifier and persist versioned artifact."""
    logger.info("Training Decision Tree baseline...")
    clf = DecisionTreeClassifier(
        max_depth=max_depth,
        random_state=42,
        class_weight="balanced",
    )
    clf.fit(X_train, y_train)

    artifact_dir = Path(output_path).parent
    artifact_dir.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": clf,
        "version": "dt-1.0.0",
        "schema_version": SCHEMA_VERSION,
        "features_count": FEATURE_COUNT,
        "classes": classes,
    }
    joblib.dump(artifact, output_path)
    logger.info(f"Decision Tree model artifact saved to {output_path}")

    return artifact
