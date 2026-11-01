def test_ingest_event_and_retrieve(client):
    payload = {
        "source_ip": "198.51.100.22",
        "dest_ip": "192.168.1.100",
        "src_port": 40123,
        "dst_port": 80,
        "protocol": "TCP",
        "category": "DoS-like traffic",
        "source": "Test Ingestion",
        "severity": "high",
        "risk_score": 75,
    }
    res = client.post("/api/v1/events/ingest", json=payload)
    assert res.status_code == 200
    created = res.json()
    assert created["sourceIp"] == "198.51.100.22"
    assert created["destIp"] == "192.168.1.100"
    assert created["severity"] == "high"
    assert created["riskScore"] == 75

    # Retrieve all events
    res_list = client.get("/api/v1/events")
    assert res_list.status_code == 200
    events = res_list.json()
    assert len(events) >= 1
    assert any(e["sourceIp"] == "198.51.100.22" for e in events)


def test_event_deduplication(client):
    payload = {
        "source_ip": "203.0.113.88",
        "dest_ip": "192.168.1.50",
        "src_port": 50000,
        "dst_port": 22,
        "protocol": "TCP",
    }
    # First ingestion
    res1 = client.post("/api/v1/events/ingest", json=payload)
    assert res1.status_code == 200
    ev1 = res1.json()
    assert ev1["duplicates"] == 0

    # Second identical ingestion within window
    res2 = client.post("/api/v1/events/ingest", json=payload)
    assert res2.status_code == 200
    ev2 = res2.json()
    assert ev2["id"] == ev1["id"]
    assert ev2["duplicates"] == 1


def test_event_filtering(client):
    client.post("/api/v1/events/ingest", json={
        "source_ip": "192.0.2.1",
        "dest_ip": "192.168.1.10",
        "protocol": "TCP",
        "severity": "critical",
        "category": "Port scanning",
    })
    client.post("/api/v1/events/ingest", json={
        "source_ip": "192.0.2.2",
        "dest_ip": "192.168.1.10",
        "protocol": "UDP",
        "severity": "low",
        "category": "Anomalous traffic",
    })

    res = client.get("/api/v1/events?severity=critical")
    assert res.status_code == 200
    data = res.json()
    assert all(e["severity"] == "critical" for e in data)
