def test_detection_status(client):
    res = client.get("/api/v1/detection/status")
    assert res.status_code == 200
    data = res.json()
    assert "ruleEngineStatus" in data
    assert "hybridStatus" in data
    assert data["activeRulesCount"] >= 1


def test_analyze_traffic_endpoint(client):
    payload = {
        "source_ip": "198.51.100.77",
        "dest_ip": "192.168.1.50",
        "src_port": 50123,
        "dst_port": 80,
        "protocol": "TCP",
        "flow_features": {
            "flow_duration": 120000,
            "total_fwd_packets": 250,
            "flow_bytes_s": 12000,
        },
    }
    res = client.post("/api/v1/detection/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "eventId" in data
    assert "detectionSources" in data
    assert "riskScore" in data
    assert "recommendedAction" in data
    assert data["severity"] in ("critical", "high", "medium", "low")


def test_port_scan_rule_detection(client):
    # Fire 5 distinct destination port connections from same source (threshold in test seed is 5)
    source = "203.0.113.123"
    for p in [21, 22, 23, 25, 80]:
        client.post("/api/v1/events/ingest", json={
            "source_ip": source,
            "dest_ip": "192.168.1.10",
            "dst_port": p,
            "protocol": "TCP",
        })

    # Trigger detection analyze
    res = client.post("/api/v1/detection/analyze", json={
        "source_ip": source,
        "dest_ip": "192.168.1.10",
        "dst_port": 443,
        "protocol": "TCP",
    })
    assert res.status_code == 200
    data = res.json()
    assert "R-001" in data["ruleIds"]
    assert "Port scanning" == data["predictedCategory"]
