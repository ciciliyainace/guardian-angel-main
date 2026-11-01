from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def split_data(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Stratified split of features and labels into training and test sets."""
    X_train, X_test, y_train, y_test = train_test_split(
        X.values,
        y.values,
        test_size=test_size,
        random_state=random_state,
        stratify=y.values if len(np.unique(y)) > 1 else None,
    )
    return X_train, X_test, y_train, y_test
