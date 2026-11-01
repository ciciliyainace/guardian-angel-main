from typing import List, Dict, Any
import numpy as np

# Canonical feature columns matching CIC-IDS2017 standard flow features
FEATURE_COLUMNS: List[str] = [
    "dst_port",
    "flow_duration",
    "total_fwd_packets",
    "total_bwd_packets",
    "total_length_of_fwd_packets",
    "total_length_of_bwd_packets",
    "fwd_packet_length_max",
    "fwd_packet_length_min",
    "fwd_packet_length_mean",
    "bwd_packet_length_max",
    "bwd_packet_length_min",
    "bwd_packet_length_mean",
    "flow_bytes_s",
    "flow_packets_s",
    "flow_iat_mean",
    "flow_iat_std",
    "flow_iat_max",
    "flow_iat_min",
    "fwd_iat_total",
    "bwd_iat_total",
    "syn_flag_count",
    "rst_flag_count",
    "ack_flag_count",
    "down_up_ratio",
]

SCHEMA_VERSION = "v1.2.0"
FEATURE_COUNT = len(FEATURE_COLUMNS)

DEFAULT_FEATURE_VALUES: Dict[str, float] = {col: 0.0 for col in FEATURE_COLUMNS}


def extract_feature_vector(raw_features: Dict[str, Any]) -> np.ndarray:
    """
    Extract a normalized numeric numpy feature vector conforming to FEATURE_COLUMNS.
    Fills absent features with validated defaults and handles NaN/infinite values.
    """
    values = []
    for col in FEATURE_COLUMNS:
        val = raw_features.get(col, DEFAULT_FEATURE_VALUES[col])
        try:
            num = float(val)
            if np.isnan(num) or np.isinf(num):
                num = 0.0
        except (ValueError, TypeError):
            num = 0.0
        values.append(num)

    return np.array(values, dtype=np.float32)
