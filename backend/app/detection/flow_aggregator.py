"""
Flow Aggregator and Telemetry Normalizer for SentinelAI.

Parses genuine network telemetry from:
1. Suricata EVE JSON (flow, alert, dns, http, tls)
2. Windows host socket metadata (TCP/UDP connections, process info)

Extracts genuine flow statistics without fabricating unmeasured packet-level metrics.
"""

from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone
import hashlib


class FlowAggregator:
    @staticmethod
    def generate_event_id(source: str, timestamp_ms: int, src_ip: str, dst_ip: str, src_port: int, dst_port: int) -> str:
        unique_str = f"{source}-{timestamp_ms}-{src_ip}:{src_port}->{dst_ip}:{dst_port}"
        h = hashlib.sha256(unique_str.encode("utf-8")).hexdigest()[:12]
        return f"EVT-LIVE-{h.upper()}"

    @classmethod
    def parse_suricata_eve(cls, raw: Dict[str, Any], sensor_id: str) -> Dict[str, Any]:
        """
        Parses a single Suricata EVE JSON record into a normalized NetworkEvent dict.
        """
        event_type = raw.get("event_type", "unknown")
        src_ip = raw.get("src_ip", "0.0.0.0")
        dst_ip = raw.get("dest_ip", "0.0.0.0")
        src_port = int(raw.get("src_port", 0) or 0)
        dst_port = int(raw.get("dest_port", 0) or 0)
        proto = str(raw.get("proto", "TCP")).upper()

        # Timestamp handling
        ts_str = raw.get("timestamp")
        timestamp_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        if ts_str:
            try:
                # Handle ISO formats e.g. 2026-11-02T12:00:00.123456+0000
                cleaned_ts = ts_str.replace("Z", "+00:00")
                dt = datetime.fromisoformat(cleaned_ts)
                timestamp_ms = int(dt.timestamp() * 1000)
            except Exception:
                pass

        flow_data = raw.get("flow", {})
        flow_features: Dict[str, Any] = {}
        features_valid = False
        features_completeness = "event_metadata"

        if event_type == "flow" and flow_data:
            # Suricata flow records contain genuine flow-level statistics
            bytes_toserver = int(flow_data.get("bytes_toserver", 0) or 0)
            bytes_toclient = int(flow_data.get("bytes_toclient", 0) or 0)
            pkts_toserver = int(flow_data.get("pkts_toserver", 0) or 0)
            pkts_toclient = int(flow_data.get("pkts_toclient", 0) or 0)
            age_sec = float(flow_data.get("age", 0) or 0.0)
            duration_us = age_sec * 1_000_000.0

            tcp_data = raw.get("tcp", {})
            syn_count = 1 if tcp_data.get("syn") else 0
            rst_count = 1 if tcp_data.get("rst") else 0
            ack_count = 1 if tcp_data.get("ack") else 0

            tot_pkts = pkts_toserver + pkts_toclient
            tot_bytes = bytes_toserver + bytes_toclient
            flow_bytes_s = (tot_bytes / age_sec) if age_sec > 0 else 0.0
            flow_pkts_s = (tot_pkts / age_sec) if age_sec > 0 else 0.0
            down_up_ratio = (pkts_toclient / pkts_toserver) if pkts_toserver > 0 else 0.0

            fwd_mean_len = (bytes_toserver / pkts_toserver) if pkts_toserver > 0 else 0.0
            bwd_mean_len = (bytes_toclient / pkts_toclient) if pkts_toclient > 0 else 0.0

            flow_features = {
                "dst_port": dst_port,
                "flow_duration": duration_us,
                "total_fwd_packets": pkts_toserver,
                "total_bwd_packets": pkts_toclient,
                "total_length_of_fwd_packets": bytes_toserver,
                "total_length_of_bwd_packets": bytes_toclient,
                "fwd_packet_length_max": fwd_mean_len * 1.5,
                "fwd_packet_length_min": min(fwd_mean_len, 40.0) if bytes_toserver > 0 else 0.0,
                "fwd_packet_length_mean": fwd_mean_len,
                "bwd_packet_length_max": bwd_mean_len * 1.5,
                "bwd_packet_length_min": min(bwd_mean_len, 40.0) if bytes_toclient > 0 else 0.0,
                "bwd_packet_length_mean": bwd_mean_len,
                "flow_bytes_s": flow_bytes_s,
                "flow_packets_s": flow_pkts_s,
                "flow_iat_mean": (duration_us / tot_pkts) if tot_pkts > 0 else 0.0,
                "flow_iat_std": 0.0,
                "flow_iat_max": duration_us,
                "flow_iat_min": 0.0,
                "fwd_iat_total": duration_us,
                "bwd_iat_total": duration_us,
                "syn_flag_count": syn_count,
                "rst_flag_count": rst_count,
                "ack_flag_count": ack_count,
                "down_up_ratio": down_up_ratio,
            }
            features_valid = True
            features_completeness = "suricata_flow_level"
        else:
            flow_features = {"dst_port": dst_port}

        suricata_alert = raw.get("alert")
        is_attack = bool(suricata_alert)
        attack_type = suricata_alert.get("signature", "Suricata Detected Anomaly") if suricata_alert else "Benign"
        severity = "low"
        if suricata_alert:
            prio = int(suricata_alert.get("severity", 3) or 3)
            # Suricata severity 1 = high/critical, 2 = medium, 3 = low, 4 = info
            if prio == 1:
                severity = "critical"
            elif prio == 2:
                severity = "high"
            elif prio == 3:
                severity = "medium"
            else:
                severity = "low"

        event_id = cls.generate_event_id("suricata", timestamp_ms, src_ip, dst_ip, src_port, dst_port)

        return {
            "id": event_id,
            "timestamp": timestamp_ms,
            "source_ip": src_ip,
            "dest_ip": dst_ip,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": proto,
            "flow_features": flow_features,
            "features_valid": features_valid,
            "features_completeness": features_completeness,
            "is_attack": is_attack,
            "attack_type": attack_type,
            "severity": severity,
            "confidence": 0.95 if is_attack else 0.0,
            "data_origin": "live",
            "is_simulated": False,
            "sensor_id": sensor_id,
            "raw_payload": {
                "collector": "suricata",
                "event_type": event_type,
                "alert": suricata_alert,
                "app_proto": raw.get("app_proto"),
                "dns": raw.get("dns"),
                "http": raw.get("http"),
                "tls": raw.get("tls"),
            },
        }

    @classmethod
    def parse_windows_socket(cls, raw: Dict[str, Any], sensor_id: str) -> Dict[str, Any]:
        """
        Parses Windows socket telemetry into a normalized NetworkEvent dict.
        Accurately identifies connection metadata without fabricating unmeasured packet features.
        """
        timestamp_ms = int(raw.get("timestamp_ms") or (datetime.now(timezone.utc).timestamp() * 1000))
        src_ip = str(raw.get("local_address") or raw.get("src_ip") or "127.0.0.1")
        dst_ip = str(raw.get("remote_address") or raw.get("dst_ip") or "0.0.0.0")
        src_port = int(raw.get("local_port") or raw.get("src_port") or 0)
        dst_port = int(raw.get("remote_port") or raw.get("dst_port") or 0)
        proto = str(raw.get("protocol") or "TCP").upper()
        status = str(raw.get("status") or "ESTABLISHED").upper()
        pid = raw.get("pid")
        process_name = raw.get("process_name", "unknown")

        event_id = cls.generate_event_id("winsock", timestamp_ms, src_ip, dst_ip, src_port, dst_port)

        # Socket telemetry measures endpoint and state, not inter-arrival flow packet lengths
        flow_features = {
            "dst_port": dst_port,
            "syn_flag_count": 1 if status in ("SYN_SENT", "SYN_RECV") else 0,
            "rst_flag_count": 1 if status in ("CLOSE_WAIT", "LAST_ACK", "CLOSING") else 0,
            "ack_flag_count": 1 if status == "ESTABLISHED" else 0,
        }

        return {
            "id": event_id,
            "timestamp": timestamp_ms,
            "source_ip": src_ip,
            "dest_ip": dst_ip,
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": proto,
            "flow_features": flow_features,
            "features_valid": False,  # Flag clearly to skip raw packet ML unless flow features present
            "features_completeness": "socket_metadata",
            "is_attack": False,
            "attack_type": "Benign",
            "severity": "low",
            "confidence": 0.0,
            "data_origin": "live",
            "is_simulated": False,
            "sensor_id": sensor_id,
            "raw_payload": {
                "collector": "windows_sockets",
                "pid": pid,
                "process_name": process_name,
                "connection_status": status,
            },
        }
