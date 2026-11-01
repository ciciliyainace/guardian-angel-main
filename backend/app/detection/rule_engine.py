import time
from collections import defaultdict
from typing import Dict, Any, List, Optional
from app.detection.base import BaseDetector
from app.models.detection_rule import DetectionRule


class RuleEngine(BaseDetector):
    # Shared in-memory tracking windows across requests:
    _port_history: Dict[str, List[tuple]] = defaultdict(list)
    _conn_history: Dict[str, List[int]] = defaultdict(list)
    _auth_history: Dict[str, List[tuple]] = defaultdict(list)

    def __init__(self, rules: Optional[List[DetectionRule]] = None):
        self.port_history = RuleEngine._port_history
        self.conn_history = RuleEngine._conn_history
        self.auth_history = RuleEngine._auth_history
        
        self.rules: Dict[str, DetectionRule] = {}
        if rules:
            self.load_rules(rules)

    def load_rules(self, rules: List[DetectionRule]):
        self.rules = {r.id: r for r in rules}

    def evaluate(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate an event against all active rules.
        Returns triggered rules, matched evidence, and category suggestion.
        """
        source_ip = event_data.get("source_ip", "")
        dest_ip = event_data.get("dest_ip", "")
        dst_port = event_data.get("dst_port", 0)
        now_ms = event_data.get("timestamp", int(time.time() * 1000))
        metadata = event_data.get("metadata", {}) or {}

        triggered_rule_ids = []
        evidence = {}
        highest_severity = "low"
        suggested_category = "Anomalous traffic"

        sev_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}

        def update_sev(rule_sev: str):
            nonlocal highest_severity
            if sev_rank.get(rule_sev, 1) > sev_rank.get(highest_severity, 1):
                highest_severity = rule_sev

        # R-001: Port scan detection
        r1 = self.rules.get("R-001")
        if r1 and r1.enabled and source_ip:
            window_ms = r1.window_sec * 1000
            self.port_history[source_ip].append((now_ms, dst_port))
            # Clean expired
            cutoff = now_ms - window_ms
            self.port_history[source_ip] = [
                (t, p) for t, p in self.port_history[source_ip] if t >= cutoff
            ]
            distinct_ports = {p for _, p in self.port_history[source_ip]}
            if len(distinct_ports) >= r1.threshold:
                triggered_rule_ids.append(r1.id)
                evidence["port_scan"] = {
                    "distinct_ports_contacted": len(distinct_ports),
                    "threshold": r1.threshold,
                    "window_sec": r1.window_sec,
                }
                update_sev(r1.severity)
                suggested_category = "Port scanning"

        # R-002: Connection-rate threshold
        r2 = self.rules.get("R-002")
        if r2 and r2.enabled and source_ip:
            window_ms = r2.window_sec * 1000
            self.conn_history[source_ip].append(now_ms)
            cutoff = now_ms - window_ms
            self.conn_history[source_ip] = [
                t for t in self.conn_history[source_ip] if t >= cutoff
            ]
            rate = len(self.conn_history[source_ip])
            if rate >= r2.threshold:
                triggered_rule_ids.append(r2.id)
                evidence["connection_rate"] = {
                    "connections_in_window": rate,
                    "threshold": r2.threshold,
                    "window_sec": r2.window_sec,
                }
                update_sev(r2.severity)
                suggested_category = "DoS-like traffic"

        # R-003: Repeated auth failures (port 22 SSH or 3389 RDP or 445 SMB)
        r3 = self.rules.get("R-003")
        if r3 and r3.enabled and source_ip and dst_port in (22, 3389, 445):
            window_ms = r3.window_sec * 1000
            self.auth_history[source_ip].append((now_ms, dst_port))
            cutoff = now_ms - window_ms
            self.auth_history[source_ip] = [
                (t, p) for t, p in self.auth_history[source_ip] if t >= cutoff
            ]
            attempts = len(self.auth_history[source_ip])
            if attempts >= r3.threshold:
                triggered_rule_ids.append(r3.id)
                evidence["auth_failures"] = {
                    "attempts": attempts,
                    "target_port": dst_port,
                    "threshold": r3.threshold,
                    "window_sec": r3.window_sec,
                }
                update_sev(r3.severity)
                suggested_category = "Brute-force"

        # R-004: Suricata signature matches
        r4 = self.rules.get("R-004")
        if r4 and r4.enabled and metadata.get("signature"):
            triggered_rule_ids.append(r4.id)
            evidence["signature"] = {
                "name": metadata.get("signature"),
                "category": metadata.get("category", "Signature alert"),
            }
            update_sev(r4.severity)
            suggested_category = "Signature match"

        # R-005: Low-volume beaconing patterns
        r5 = self.rules.get("R-005")
        if r5 and r5.enabled:
            flow_feats = event_data.get("flow_features", {}) or {}
            bytes_total = flow_feats.get("flow_bytes_s", 0)
            duration = flow_feats.get("flow_duration", 0)
            if duration > r5.window_sec and bytes_total < r5.threshold:
                triggered_rule_ids.append(r5.id)
                evidence["beacon_pattern"] = {
                    "duration": duration,
                    "bytes": bytes_total,
                }
                update_sev(r5.severity)
                suggested_category = "Suspicious connection"

        is_match = len(triggered_rule_ids) > 0
        return {
            "matched": is_match,
            "rule_ids": triggered_rule_ids,
            "severity": highest_severity if is_match else "low",
            "category": suggested_category if is_match else "Benign",
            "evidence": evidence,
        }
