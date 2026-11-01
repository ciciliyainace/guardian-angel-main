def test_event_contract_compatibility(client):
    # Ingest an event and test contract
    client.post("/api/v1/events/ingest", json={
        "source_ip": "198.51.100.10",
        "dest_ip": "192.168.1.1",
        "protocol": "TCP",
        "category": "Port scanning",
        "source": "Rule engine",
        "severity": "high",
        "risk_score": 70,
        "src_port": 12345,
        "dst_port": 80,
    })

    res = client.get("/api/v1/events")
    assert res.status_code == 200
    events = res.json()
    assert len(events) > 0
    e = events[0]

    # Verify all TypeScript SecurityEvent interface fields
    expected_fields = [
        "id", "timestamp", "sourceIp", "destIp", "protocol",
        "category", "source", "severity", "riskScore", "status",
        "srcPort", "dstPort", "duplicates"
    ]
    for field in expected_fields:
        assert field in e, f"Missing TypeScript contract field '{field}' in Event response"


def test_block_request_contract_compatibility(client, analyst_headers):
    client.post("/api/v1/firewall/requests", json={
        "sourceIp": "203.0.113.45",
        "reason": "Contract test block",
        "durationMin": 60,
    }, headers=analyst_headers)

    res = client.get("/api/v1/firewall/requests")
    assert res.status_code == 200
    reqs = res.json()
    assert len(reqs) > 0
    r = reqs[0]

    expected_fields = [
        "id", "sourceIp", "reason", "alertId",
        "requestedBy", "requestedAt", "durationMin",
        "status", "direction"
    ]
    for field in expected_fields:
        assert field in r, f"Missing TypeScript contract field '{field}' in BlockRequest response"


def test_rule_contract_compatibility(client):
    res = client.get("/api/v1/rules")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) > 0
    rule = rules[0]

    expected_fields = [
        "id", "name", "description", "category",
        "severity", "enabled", "threshold", "windowSec",
        "lastTriggered", "matches"
    ]
    for field in expected_fields:
        assert field in rule, f"Missing TypeScript contract field '{field}' in DetectionRule response"


def test_service_health_contract_compatibility(client):
    res = client.get("/health")
    assert res.status_code == 200
    services = res.json()
    assert len(services) > 0
    s = services[0]

    for field in ["name", "status", "detail"]:
        assert field in s, f"Missing TypeScript contract field '{field}' in Health Service response"
    assert s["status"] in ("Operational", "Degraded", "Disconnected", "Error", "Unknown")
