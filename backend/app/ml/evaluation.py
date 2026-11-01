import time
from typing import Dict, Any, List
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


def evaluate_classifier(
    model: Any,
    X_test: np.ndarray,
    y_test: np.ndarray,
    class_labels: List[str],
) -> Dict[str, Any]:
    """
    Comprehensive model evaluation reporting:
    accuracy, precision, recall, macro-F1, weighted-F1, false positive rate,
    confusion matrix, per-class metrics, and inference latency.
    """
    start_time = time.perf_counter()
    y_pred = model.predict(X_test)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    latency_per_sample_ms = elapsed_ms / max(1, len(X_test))

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, average="weighted", zero_division=0))
    rec = float(recall_score(y_test, y_pred, average="weighted", zero_division=0))
    f1_weighted = float(f1_score(y_test, y_pred, average="weighted", zero_division=0))
    f1_macro = float(f1_score(y_test, y_pred, average="macro", zero_division=0))

    cm = confusion_matrix(y_test, y_pred)
    cm_list = cm.tolist()

    # Calculate False Positive Rate (FPR) assuming index 0 is Benign/Normal
    if len(cm_list) > 1 and cm[0].sum() > 0:
        fp = float(cm[0].sum() - cm[0, 0])
        tn = float(cm[0, 0])
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    else:
        fpr = 0.0

    # Per-class recall
    per_class = []
    report = classification_report(y_test, y_pred, target_names=class_labels, output_dict=True, zero_division=0)
    for cls in class_labels:
        if cls in report:
            per_class.append({
                "cls": cls,
                "precision": round(float(report[cls]["precision"]), 4),
                "recall": round(float(report[cls]["recall"]), 4),
                "f1": round(float(report[cls]["f1-score"]), 4),
                "support": int(report[cls]["support"]),
            })

    return {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1_weighted, 4),
        "macro_f1": round(f1_macro, 4),
        "fpr": round(fpr, 4),
        "latencyMs": round(latency_per_sample_ms, 3),
        "confusion": {
            "labels": class_labels,
            "matrix": cm_list,
        },
        "perClassMetrics": per_class,
    }
