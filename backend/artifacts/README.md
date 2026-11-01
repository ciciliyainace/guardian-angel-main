# SentinelAI Model Artifacts

This directory holds trusted, versioned model artifacts saved by Joblib:

- **`random_forest.joblib`**: Trained Random Forest multiclass classifier (`rf-1.3.0`).
- **`decision_tree.joblib`**: Trained Decision Tree baseline model (`dt-1.0.0`).
- **`isolation_forest.joblib`**: Trained Isolation Forest anomaly detector (`if-0.9.2`).
- **`suricata_checkpoint.json`**: Bookmark offset for reliable Eve JSON tailing across restarts.

These artifacts are created and evaluated by `backend/scripts/run_training.py`.
