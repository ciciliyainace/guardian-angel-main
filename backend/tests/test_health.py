def test_health_ping(client):
    res = client.get("/health/ping")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "pong"
    assert "version" in data


def test_health_ready(client):
    res = client.get("/health/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_services_list(client):
    res = client.get("/health")
    assert res.status_code == 200
    services = res.json()
    assert isinstance(services, list)
    assert len(services) >= 6
    names = [s["name"] for s in services]
    assert "Backend API (FastAPI)" in names
    assert any("MongoDB" in n or "Database" in n for n in names)
