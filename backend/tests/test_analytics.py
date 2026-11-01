def test_analytics_summary(client):
    res = client.get("/api/v1/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert "totalEvents" in data
    assert "activeAlerts" in data
    assert "criticalThreats" in data
    assert "suspiciousConnections" in data
    assert "managedBlocks" in data


def test_analytics_categories(client):
    res = client.get("/api/v1/analytics/categories")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert any("category" in item for item in data)


def test_analytics_severity(client):
    res = client.get("/api/v1/analytics/severity")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4
    sevs = [d["severity"] for d in data]
    assert set(sevs) == {"critical", "high", "medium", "low"}


def test_traffic_series(client):
    res = client.get("/api/v1/analytics/traffic-series")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 24
    assert data[0]["time"] == "00:00"
    assert "benign" in data[0]
    assert "total" in data[0]


def test_model_metrics(client):
    res = client.get("/api/v1/analytics/model-metrics")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "perClassRecall" in data
    assert "confusion" in data
    assert "models" in data
