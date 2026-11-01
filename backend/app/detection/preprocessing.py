from typing import Tuple, Dict, Any, Optional
import numpy as np
from app.detection.feature_schema import FEATURE_COLUMNS, FEATURE_COUNT, extract_feature_vector


class Preprocessor:
    def __init__(self, means: Optional[np.ndarray] = None, scales: Optional[np.ndarray] = None):
        self.means = means if means is not None else np.zeros(FEATURE_COUNT, dtype=np.float32)
        self.scales = scales if scales is not None else np.ones(FEATURE_COUNT, dtype=np.float32)

    def fit(self, X: np.ndarray):
        """Fit means and scales on training data only to prevent data leakage."""
        self.means = np.nanmean(X, axis=0)
        self.scales = np.nanstd(X, axis=0)
        self.scales[self.scales == 0.0] = 1.0  # Prevent division by zero

    def transform(self, vector: np.ndarray) -> np.ndarray:
        """Apply standardization and sanitize infinities/NaNs."""
        sanitized = np.nan_to_num(vector, nan=0.0, posinf=1e6, neginf=-1e6)
        if len(sanitized.shape) == 1:
            sanitized = sanitized.reshape(1, -1)
        # Only apply standardization and z-score clipping when actual means and scales are fitted
        if np.any(self.means != 0.0) or np.any(self.scales != 1.0):
            normalized = (sanitized - self.means) / self.scales
            return np.clip(normalized, -10.0, 10.0)
        return sanitized

    def prepare_single_flow(self, flow_features: Dict[str, Any]) -> np.ndarray:
        raw_vec = extract_feature_vector(flow_features)
        return self.transform(raw_vec)
