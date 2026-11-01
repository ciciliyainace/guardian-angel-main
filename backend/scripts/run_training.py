import sys
import argparse
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.logging_config import setup_logging, logger
from app.ml.training.load_dataset import load_dataset
from app.ml.training.clean_dataset import clean_dataset
from app.ml.training.split_dataset import split_data
from app.ml.training.train_random_forest import train_random_forest
from app.ml.training.train_decision_tree import train_decision_tree
from app.ml.training.train_isolation_forest import train_isolation_forest
from app.ml.training.evaluate_models import evaluate_all
from app.ml.registry import registry
import numpy as np


def run_pipeline(dataset_path: str = "datasets/cicids2017.csv"):
    setup_logging()
    logger.info("=== STARTING SENTINELAI ML TRAINING PIPELINE ===")

    # 1 & 2. Load dataset
    df_raw = load_dataset(dataset_path)
    logger.info(f"Loaded dataset with {len(df_raw)} samples.")

    # 3 & 4 & 5. Clean dataset and select canonical features
    X_clean, y = clean_dataset(df_raw)
    classes = sorted(list(y.unique()))
    logger.info(f"Classes identified: {classes}")

    # 6. Split into Train and Test sets (prevent data leakage)
    X_train, X_test, y_train, y_test = split_data(X_clean, y, test_size=0.2, random_state=42)
    logger.info(f"Training samples: {len(X_train)}, Testing samples: {len(X_test)}")

    # 7. Train Random Forest
    rf_artifact = train_random_forest(
        X_train,
        y_train,
        classes=classes,
        output_path="artifacts/random_forest.joblib",
    )

    # 8. Train Decision Tree Baseline
    dt_artifact = train_decision_tree(
        X_train,
        y_train,
        classes=classes,
        output_path="artifacts/decision_tree.joblib",
    )

    # 9. Train Isolation Forest on Benign/Normal instances
    benign_mask = y_train == "Benign"
    X_benign = X_train[benign_mask] if np.any(benign_mask) else X_train[:500]
    train_isolation_forest(
        X_benign,
        output_path="artifacts/isolation_forest.joblib",
    )

    # 10 & 11. Evaluate on held-out test data
    eval_results = evaluate_all(
        rf_model=rf_artifact["model"],
        dt_model=dt_artifact["model"],
        X_test=X_test,
        y_test=y_test,
        classes=classes,
    )

    # 12. Persist metadata to database ModelRegistry
    try:
        from app.core.database import MongoDBManager
        mongo = MongoDBManager.get_instance()
        if mongo.connect():
            db = mongo.get_db()
            rf_metrics = eval_results["random_forest"]
            db.model_registry.update_one(
                {"name": "Random Forest classifier"},
                {"$set": {
                    "name": "Random Forest classifier",
                    "version": "rf-1.3.0",
                    "artifact_location": "artifacts/random_forest.joblib",
                    "training_dataset": "CIC-IDS2017",
                    "feature_schema_version": "v1.2.0",
                    "features_count": 24,
                    "classes": classes,
                    "evaluation_metrics": {
                        "precision": rf_metrics["precision"],
                        "recall": rf_metrics["recall"],
                        "f1": rf_metrics["f1"],
                        "fpr": rf_metrics["fpr"],
                        "latencyMs": rf_metrics["latencyMs"],
                    },
                    "confusion_matrix": rf_metrics["confusion"],
                    "per_class_metrics": rf_metrics["perClassMetrics"],
                    "status": "Loaded",
                }},
                upsert=True,
            )
            logger.info("Persisted model metadata to MongoDB Atlas")
    except Exception as e:
        logger.warning(f"Could not persist model registry to MongoDB: {e}")

    # Reload active models in registry
    registry.reload_all()
    logger.info("=== ML TRAINING PIPELINE SUCCESSFULLY COMPLETED ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SentinelAI ML Training Pipeline")
    parser.add_argument("--dataset", "-d", default="datasets/cicids2017.csv", help="Path to training dataset CSV")
    args = parser.parse_args()
    run_pipeline(args.dataset)
