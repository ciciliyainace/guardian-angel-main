from typing import Dict, Any, Optional
import numpy as np
from app.detection.feature_schema import extract_feature_vector
from app.detection.preprocessing import Preprocessor
from app.core.exceptions import ModelNotLoadedError
from app.core.logging_config import logger

preprocessor = Preprocessor()


def run_inference(flow_features: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run machine learning inference across loaded models for a network flow.
    Returns model predictions, confidence, anomaly scores, and model versions.
    """
    from app.ml.registry import registry
    raw_vector = extract_feature_vector(flow_features)
    processed_vector = preprocessor.transform(raw_vector)

    results: Dict[str, Any] = {
        "rf_result": None,
        "if_result": None,
        "dt_result": None,
        "is_attack": False,
        "predicted_category": "Benign",
        "ml_risk_score": 0,
        "versions": {},
        "model_statuses": {
            "rf": "operational" if registry.rf.is_loaded else "not_loaded",
            "iforest": "operational" if registry.iforest.is_loaded else "not_loaded",
            "dt": "operational" if registry.dt.is_loaded else "not_loaded",
        },
        "inference_errors": [],
    }

    # 1. Random Forest Classifier
    if registry.rf.is_loaded:
        try:
            rf_res = registry.rf.predict(processed_vector)
            results["rf_result"] = rf_res
            results["versions"]["rf"] = registry.rf.version
            if rf_res["is_attack"]:
                results["is_attack"] = True
                results["predicted_category"] = rf_res["predicted_class"]
                # Convert confidence to 0-100 score
                results["ml_risk_score"] = max(results["ml_risk_score"], int(rf_res["confidence"] * 100))
            else:
                results["is_attack"] = False
                results["predicted_category"] = "Benign"
                results["ml_risk_score"] = 0
        except Exception as e:
            logger.warning(f"Random Forest inference failed on feature vector: {e}")
            results["model_statuses"]["rf"] = "error"
            results["inference_errors"].append(f"Random Forest error: {str(e)}")

    # 2. Isolation Forest Anomaly Detector
    if registry.iforest.is_loaded:
        try:
            if_res = registry.iforest.predict(processed_vector)
            results["if_result"] = if_res
            results["versions"]["iforest"] = registry.iforest.version
            # Anomaly adds to risk score without directly declaring attack class
            # High-confidence benign flows (RF confidence >= 0.75) are protected against statistical false alarms
            rf_is_benign = results["rf_result"] and not results["rf_result"]["is_attack"] and results["rf_result"]["confidence"] >= 0.75
            if if_res["is_anomalous"] and not rf_is_benign:
                anomaly_score_contrib = int(if_res["anomaly_intensity"] * 45)
                results["ml_risk_score"] = min(100, results["ml_risk_score"] + anomaly_score_contrib)
                if not results["is_attack"]:
                    results["predicted_category"] = "Anomalous traffic"
        except Exception as e:
            logger.warning(f"Isolation Forest inference failed: {e}")
            results["model_statuses"]["iforest"] = "error"
            results["inference_errors"].append(f"Isolation Forest error: {str(e)}")

    # 3. Decision Tree Baseline
    if registry.dt.is_loaded:
        try:
            dt_res = registry.dt.predict(processed_vector)
            results["dt_result"] = dt_res
            results["versions"]["dt"] = registry.dt.version
        except Exception as e:
            logger.warning(f"Decision Tree inference failed: {e}")
            results["model_statuses"]["dt"] = "error"
            results["inference_errors"].append(f"Decision Tree error: {str(e)}")

    return results
