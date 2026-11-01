import uuid
from typing import Dict, Any, List, Optional
from app.utils.time_utils import current_epoch_ms


class SampleEventGenerator:
    """
    Generates safe, RFC 5737 documentation-range network events for development,
    automated testing, and demonstrations.
    
    All events are explicitly labeled with `is_simulated: True` and
    `source: 'Simulated Attack Generator (Safe)'`.
    """

    SCENARIOS = {
        "port_scan": {
            "name": "Port Scan Sequence",
            "description": "Sequential probes across common service ports to trigger frequency rules",
            "source_ip": "198.51.100.45",
            "dest_ip": "192.168.1.50",
            "ports": [21, 22, 23, 25, 80, 110, 143, 443, 3306, 3389, 8080],
            "protocol": "TCP",
            "category": "Port scan detection",
            "severity": "high",
            "risk_score": 75,
            "flow_features": {
                "flow_duration": 45000,
                "total_fwd_packets": 28,
                "total_bwd_packets": 0,
                "flow_packets_s": 622.2,
                "syn_flag_count": 28,
                "rst_flag_count": 0,
                "ack_flag_count": 0,
            },
        },
        "dos_syn_flood": {
            "name": "DoS SYN Flood",
            "description": "High-volume connection flood with asymmetrical packet counts",
            "source_ip": "198.51.100.99",
            "dest_ip": "192.168.1.10",
            "ports": [80],
            "protocol": "TCP",
            "category": "DoS-like traffic",
            "severity": "critical",
            "risk_score": 92,
            "flow_features": {
                "flow_duration": 150000,
                "total_fwd_packets": 1200,
                "total_bwd_packets": 5,
                "flow_bytes_s": 850000,
                "flow_packets_s": 8000.0,
                "syn_flag_count": 1200,
                "rst_flag_count": 0,
                "ack_flag_count": 5,
            },
        },
        "brute_force": {
            "name": "Authentication Brute-Force",
            "description": "Rapid repeated connection attempts targeting SSH/RDP",
            "source_ip": "203.0.113.88",
            "dest_ip": "192.168.1.25",
            "ports": [22],
            "protocol": "TCP",
            "category": "Repeated authentication failures",
            "severity": "high",
            "risk_score": 80,
            "flow_features": {
                "flow_duration": 25000,
                "total_fwd_packets": 35,
                "total_bwd_packets": 12,
                "flow_bytes_s": 42000,
                "flow_packets_s": 1400.0,
                "syn_flag_count": 15,
                "rst_flag_count": 8,
                "ack_flag_count": 25,
            },
        },
        "anomalous_beacon": {
            "name": "Anomalous C2-like Beacon",
            "description": "Long, low-volume periodic flow targeting anomaly detection",
            "source_ip": "198.51.100.12",
            "dest_ip": "192.168.1.100",
            "ports": [8443],
            "protocol": "TCP",
            "category": "Anomalous traffic",
            "severity": "medium",
            "risk_score": 60,
            "flow_features": {
                "flow_duration": 900000,
                "total_fwd_packets": 15,
                "total_bwd_packets": 15,
                "flow_bytes_s": 120,
                "flow_packets_s": 0.033,
                "flow_iat_mean": 60000.0,
                "flow_iat_std": 150.0,
                "down_up_ratio": 1.0,
            },
        },
        "benign_web": {
            "name": "Normal HTTPS Browsing",
            "description": "Legitimate balanced web flow to port 443",
            "source_ip": "192.0.2.15",
            "dest_ip": "192.168.1.100",
            "ports": [443],
            "protocol": "TCP",
            "category": "Benign",
            "severity": "low",
            "risk_score": 10,
            "flow_features": {
                "dst_port": 443,
                "flow_duration": 45000,
                "total_fwd_packets": 15,
                "total_bwd_packets": 22,
                "flow_bytes_s": 35000,
                "flow_packets_s": 25.0,
                "syn_flag_count": 1,
                "rst_flag_count": 0,
                "ack_flag_count": 35,
                "down_up_ratio": 1.46,
            },
        },
    }

    @classmethod
    def generate_events(cls, scenario_key: str = "port_scan", count: int = 1) -> List[Dict[str, Any]]:
        scenario = cls.SCENARIOS.get(scenario_key, cls.SCENARIOS["port_scan"])
        now_ms = current_epoch_ms()
        events: List[Dict[str, Any]] = []

        ports = scenario.get("ports", [80])

        for i in range(count):
            dst_port = ports[i % len(ports)]
            src_port = 40000 + (i % 20000)
            event_id = f"SIM-{now_ms}-{uuid.uuid4().hex[:6]}"

            flow_feats = dict(scenario["flow_features"])
            if "dst_port" not in flow_feats:
                flow_feats["dst_port"] = dst_port

            ev = {
                "id": event_id,
                "timestamp": now_ms + (i * 100),
                "source_ip": scenario["source_ip"],
                "dest_ip": scenario["dest_ip"],
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": scenario["protocol"],
                "category": scenario["category"],
                "source": "Simulated Attack Generator (Safe)",
                "severity": scenario["severity"],
                "risk_score": scenario["risk_score"],
                "flow_features": flow_feats,
                "is_simulated": True,
                "event_source": "simulation",
                "metadata": {
                    "scenario": scenario_key,
                    "scenario_name": scenario["name"],
                    "generated_at": now_ms,
                    "safe_test": True,
                },
            }
            events.append(ev)

        return events

    @classmethod
    def list_scenarios(cls) -> List[Dict[str, Any]]:
        return [
            {
                "key": k,
                "name": v["name"],
                "description": v["description"],
                "severity": v["severity"],
                "riskScore": v["risk_score"],
                "sourceIp": v["source_ip"],
                "destIp": v["dest_ip"],
            }
            for k, v in cls.SCENARIOS.items()
        ]
