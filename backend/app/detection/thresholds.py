from typing import Literal

SeverityLevel = Literal["critical", "high", "medium", "low"]


def score_to_severity(score: int) -> SeverityLevel:
    """Map a 0-100 risk score to severity tier matching SOC standard."""
    if score >= 85:
        return "critical"
    elif score >= 65:
        return "high"
    elif score >= 40:
        return "medium"
    return "low"


DEFAULT_THRESHOLDS = {
    "port_scan_distinct_ports": 25,
    "port_scan_window_sec": 60,
    "connection_rate_limit": 300,
    "connection_rate_window_sec": 10,
    "auth_failure_threshold": 8,
    "auth_failure_window_sec": 120,
    "beacon_interval_tolerance": 0.15,
    "isolation_forest_anomaly_threshold": -0.10,
}
