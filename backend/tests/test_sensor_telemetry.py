import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import db_manager
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import create_access_token
from app.detection.flow_aggregator import FlowAggregator


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(db_session):
    user_repo = UserRepository(db_session)
    # Ensure admin user exists
    admin = user_repo.get_by_username("test_admin")
    if not admin:
        from app.core.security import hash_password
        admin = User(
            id=999,
            username="test_admin",
            email="admin@sentinelai.test",
            hashed_password=hash_password("Admin123!"),
            role="admin",
            is_active=True,
            email_verified=True,
        )
        user_repo.create(admin)
    return create_access_token(subject="test_admin", role="admin")


def test_sensor_enrollment_and_auth(client: TestClient, admin_token: str):
    # 1. Unauthenticated enrollment fails
    res = client.post("/api/v1/sensors/enroll", json={"sensor_id": "sensor-test-01", "name": "Host Sensor 1"})
    assert res.status_code == 401

    # 2. Admin enrollment succeeds
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = client.post(
        "/api/v1/sensors/enroll",
        json={"sensor_id": "sensor-test-01", "name": "Host Sensor 1", "hostname": "SEC-HOST"},
        headers=headers,
    )
    assert res.status_code == 201
    data = res.json()
    assert data["sensor_id"] == "sensor-test-01"
    assert "api_key" in data
    assert data["api_key"].startswith("sen_live_")
    sensor_key = data["api_key"]

    # 3. Heartbeat without key fails
    res = client.post("/api/v1/sensors/heartbeat", json={"metrics": {}, "collectors": {}})
    assert res.status_code == 401

    # 4. Heartbeat with invalid key fails
    res = client.post("/api/v1/sensors/heartbeat", json={"metrics": {}, "collectors": {}}, headers={"X-Sensor-Key": "invalid_key"})
    assert res.status_code == 401

    # 5. Heartbeat with valid key succeeds
    res = client.post(
        "/api/v1/sensors/heartbeat",
        json={
            "metrics": {"cpu_percent": 12.5, "memory_percent": 45.0},
            "collectors": {"suricata": "operational", "windows_sockets": "operational"},
        },
        headers={"X-Sensor-Key": sensor_key},
    )
    assert res.status_code == 200
    assert res.json()["acknowledged"] is True

    # 6. Check detailed health endpoint reflects live sensor status
    h_res = client.get("/api/v1/health/detailed")
    assert h_res.status_code == 200
    h_data = h_res.json()
    assert h_data["active_sensor_count"] >= 1
    assert "sensor-test-01" in h_data["active_sensors"]
    assert h_data["suricata_operational"] is True
    assert h_data["windows_socket_operational"] is True


def test_flow_aggregator_normalization():
    # A. Suricata EVE Flow Record
    suricata_flow = {
        "event_type": "flow",
        "src_ip": "192.168.1.50",
        "dest_ip": "10.0.0.1",
        "src_port": 54321,
        "dest_port": 443,
        "proto": "TCP",
        "timestamp": "2026-11-02T12:00:00.000000Z",
        "flow": {
            "bytes_toserver": 1500,
            "bytes_toclient": 6500,
            "pkts_toserver": 10,
            "pkts_toclient": 15,
            "age": 2.5,
        },
        "tcp": {"syn": True, "ack": True},
    }
    parsed = FlowAggregator.parse_suricata_eve(suricata_flow, sensor_id="test-sensor")
    assert parsed["src_ip"] == "192.168.1.50"
    assert parsed["dst_ip"] == "10.0.0.1"
    assert parsed["features_valid"] is True
    assert parsed["features_completeness"] == "suricata_flow_level"
    assert parsed["data_origin"] == "live"
    assert parsed["flow_features"]["total_fwd_packets"] == 10
    assert parsed["flow_features"]["total_bwd_packets"] == 15

    # B. Windows Socket Metadata
    winsock_data = {
        "local_address": "127.0.0.1",
        "local_port": 5173,
        "remote_address": "127.0.0.1",
        "remote_port": 8000,
        "protocol": "TCP",
        "status": "ESTABLISHED",
        "pid": 1234,
        "process_name": "node.exe",
    }
    parsed_sock = FlowAggregator.parse_windows_socket(winsock_data, sensor_id="test-sensor")
    assert parsed_sock["src_ip"] == "127.0.0.1"
    assert parsed_sock["dst_port"] == 8000
    assert parsed_sock["features_valid"] is False  # Accurately marked as metadata, not faking flow metrics
    assert parsed_sock["features_completeness"] == "socket_metadata"
    assert parsed_sock["data_origin"] == "live"


def test_live_telemetry_batch_ingest_and_analytics(client: TestClient, admin_token: str):
    # Enroll test sensor
    enroll_res = client.post(
        "/api/v1/sensors/enroll",
        json={"sensor_id": "sensor-telemetry-test", "name": "Telemetry Test Sensor"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    sensor_key = enroll_res.json()["api_key"]

    # Ingest batch of live events
    events_payload = [
        {
            "collector": "windows_sockets",
            "local_address": "10.0.0.5",
            "local_port": 49152,
            "remote_address": "198.51.100.20",
            "remote_port": 443,
            "protocol": "TCP",
            "status": "ESTABLISHED",
            "pid": 5678,
            "process_name": "chrome.exe",
        },
        {
            "collector": "suricata",
            "event_type": "alert",
            "src_ip": "203.0.113.5",
            "dest_ip": "10.0.0.5",
            "src_port": 4444,
            "dest_port": 80,
            "proto": "TCP",
            "alert": {
                "action": "allowed",
                "signature": "ET SCAN Suspicious Inbound Port Scan",
                "category": "Attempted Information Leak",
                "severity": 1,
            },
        },
    ]

    res = client.post(
        "/api/v1/sensors/telemetry",
        json={"events": events_payload},
        headers={"X-Sensor-Key": sensor_key},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["received"] == 2
    assert data["ingested"] >= 1

    # Verify overview summary returns genuine live counts
    sum_res = client.get("/api/v1/analytics/summary?origin=live&range=24h")
    assert sum_res.status_code == 200
    summary = sum_res.json()
    assert summary["totalEvents"] >= 1
