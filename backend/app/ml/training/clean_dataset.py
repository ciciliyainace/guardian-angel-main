from typing import Tuple
import pandas as pd
import numpy as np
from app.detection.feature_schema import FEATURE_COLUMNS


def clean_dataset(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Clean dataset, handle NaNs and infinities, extract features and target labels."""
    df_clean = df.copy()

    # Normalize column names: lower case, strip whitespace, replace spaces with underscores
    df_clean.columns = [c.strip().lower().replace(" ", "_") for c in df_clean.columns]

    # Map target label column
    target_col = None
    for cand in ("label", "class", "attack_cat", "category"):
        if cand in df_clean.columns:
            target_col = cand
            break

    if not target_col:
        raise ValueError("Could not find a valid label column in dataset.")

    y = df_clean[target_col].astype(str)

    # Ensure all canonical feature columns are present
    for col in FEATURE_COLUMNS:
        if col not in df_clean.columns:
            df_clean[col] = 0.0

    X = df_clean[FEATURE_COLUMNS]

    # Replace infinities with NaN and fill NaNs with column medians
    X = X.replace([np.inf, -np.inf], np.nan)
    X = X.fillna(X.median())

    return X, y
