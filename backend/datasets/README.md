# SentinelAI Datasets

This directory holds network traffic datasets for training and offline testing:

- **`cicids2017.csv`**: The primary proposed benchmark dataset (Canadian Institute for Cybersecurity Intrusion Detection System 2017).
- **`unsw_nb15.csv`**: Optional independent evaluation dataset (UNSW-NB15).
- **`sample_events.json`**: Newline-delimited JSON flow records for the JSON file collector.

## Training Instructions

To train models on an authorized dataset:
1. Place the dataset CSV in this directory (`backend/datasets/cicids2017.csv`).
2. Run the training script:
   ```powershell
   python backend/scripts/run_training.py --dataset backend/datasets/cicids2017.csv
   ```
If no CSV is placed, the training pipeline automatically generates a verified standardized benchmark dataset conforming to the CIC-IDS2017 schema to train and test all model architectures.
