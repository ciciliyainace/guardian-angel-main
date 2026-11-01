import json
import os
import sys
import tempfile
from pathlib import Path
import pytest
from app.collectors.suricata_collector import SuricataCollector
from app.collectors.windows_collector import WindowsCollector


def test_suricata_collector_not_configured():
    collector = SuricataCollector(eve_path="", checkpoint_path=tempfile.mktemp())
    collector.start()
    assert collector.status == "Not Configured"
    assert collector.collect() == []


def test_suricata_collector_disconnected():
    non_existent = Path(tempfile.gettempdir()) / "non_existent_suricata_eve.json"
    if non_existent.exists():
        non_existent.unlink()
    collector = SuricataCollector(eve_path=str(non_existent), checkpoint_path=tempfile.mktemp())
    collector.start()
    assert collector.status == "Disconnected"
    assert collector.collect() == []


def test_suricata_collector_live_tailing_and_rotation(tmp_path):
    eve_file = tmp_path / "eve.json"
    chk_file = tmp_path / "suricata_chk.json"

    # 1. Create file with 2 initial events
    alert_event = {
        "timestamp": "2026-10-27T12:00:00.123456+0000",
        "event_type": "alert",
        "src_ip": "198.51.100.10",
        "src_port": 54321,
        "dest_ip": "192.168.1.50",
        "dest_port": 80,
        "proto": "TCP",
        "alert": {
            "signature": "ET SCAN Potential SSH Scan",
            "signature_id": 2001219,
            "severity": 2,
            "category": "Attempted Information Leak",
        },
    }
    flow_event = {
        "timestamp": "2026-10-27T12:01:00.654321+0000",
        "event_type": "flow",
        "src_ip": "198.51.100.20",
        "src_port": 443,
        "dest_ip": "192.168.1.50",
        "dest_port": 51234,
        "proto": "TCP",
        "flow": {
            "pkts_toserver": 10,
            "pkts_toclient": 12,
            "bytes_toserver": 1200,
            "bytes_toclient": 2400,
        },
    }

    with open(eve_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(alert_event) + "\n")
        f.write(json.dumps(flow_event) + "\n")

    collector = SuricataCollector(eve_path=str(eve_file), checkpoint_path=str(chk_file))
    collector.start()
    assert collector.status == "Operational"

    # Collect first batch
    events = collector.collect()
    assert len(events) == 2
    assert events[0]["source_ip"] == "198.51.100.10"
    assert events[0]["severity"] == "high"
    assert events[0]["is_simulated"] is False
    assert events[0]["event_source"] == "suricata_eve"
    assert events[1]["category"] == "Network flow"
    assert events[1]["is_simulated"] is False

    # Second collect without new data: returns 0 new events
    events_empty = collector.collect()
    assert len(events_empty) == 0

    # Append 1 new event
    new_alert = {
        "timestamp": "2026-10-27T12:02:00.000000+0000",
        "event_type": "alert",
        "src_ip": "203.0.113.99",
        "src_port": 12345,
        "dest_ip": "192.168.1.50",
        "dest_port": 22,
        "proto": "TCP",
        "alert": {
            "signature": "ET EXPLOIT Attempted Remote Code Execution",
            "severity": 1,
            "category": "Attempted Administrator Privilege Gain",
        },
    }
    with open(eve_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(new_alert) + "\n")

    events_new = collector.collect()
    assert len(events_new) == 1
    assert events_new[0]["source_ip"] == "203.0.113.99"
    assert events_new[0]["severity"] == "critical"

    # Test file truncation / rotation
    rotated_event = {
        "timestamp": "2026-10-27T12:05:00.000000+0000",
        "event_type": "alert",
        "src_ip": "198.51.100.77",
        "dest_ip": "192.168.1.50",
        "proto": "TCP",
        "alert": {"signature": "Post-rotation test alert", "severity": 2},
    }
    # Overwrite file with smaller length to simulate logrotate
    with open(eve_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(rotated_event) + "\n")

    events_rotated = collector.collect()
    assert len(events_rotated) == 1
    assert events_rotated[0]["source_ip"] == "198.51.100.77"


def test_windows_collector():
    collector = WindowsCollector()
    collector.start()
    if sys.platform == "win32":
        assert collector.status == "Operational"
        events = collector.collect()
        assert isinstance(events, list)
        for ev in events:
            assert ev["is_simulated"] is False
            assert ev["event_source"] == "windows_socket"
            assert ev["source_ip"] not in ("127.0.0.1", "::1", "0.0.0.0")
    else:
        assert collector.status == "Degraded"
        assert collector.collect() == []
    collector.stop()
    assert collector.status == "Disconnected"
