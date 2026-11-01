from typing import Dict, Any, List
import numpy as np
from app.ml.evaluation import evaluate_classifier
from app.core.logging_config import logger


def evaluate_all(
    rf_model: Any,
    dt_model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    classes: List[str],
) -> Dict[str, Any]:
    """Run full evaluation on held-out test data across models."""
    logger.info("Evaluating trained models on held-out test set...")

    rf_eval = evaluate_classifier(rf_model, X_test, y_test, classes)
    dt_eval = evaluate_classifier(dt_model, X_test, y_test, classes)

    logger.info(f"Random Forest — Precision: {rf_eval['precision']}, Recall: {rf_eval['recall']}, F1: {rf_eval['f1']}")
    logger.info(f"Decision Tree — Precision: {dt_eval['precision']}, Recall: {dt_eval['recall']}, F1: {dt_eval['f1']}")

    return {
        "random_forest": rf_eval,
        "decision_tree": dt_eval,
    }
