import pytest
import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from mongomock import MongoClient
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.workspace_repository import WorkspaceRepository


@pytest.fixture
def mock_db():
    client = MongoClient()
    db = client["sentinelai_test"]
    return db


@pytest.fixture
def test_client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def setup_tenants(mock_db):
    user_repo = UserRepository(mock_db)
    ws_repo = WorkspaceRepository(mock_db)

    # Tenant A
    user_a = User(
        id=10,
        username="analyst_alice",
        email="alice@company.internal",
        hashed_password="pw",
        role="analyst",
        is_active=True,
        email_verified=True,
    )
    user_repo.create(user_a)
    ws_a = ws_repo.get_or_create_default_workspace(user_a.id, user_a.username)
    user_a.default_workspace_id = ws_a.id
    user_repo.update(user_a)

    # Tenant B
    user_b = User(
        id=20,
        username="analyst_bob",
        email="bob@company.internal",
        hashed_password="pw",
        role="analyst",
        is_active=True,
        email_verified=True,
    )
    user_repo.create(user_b)
    ws_b = ws_repo.get_or_create_default_workspace(user_b.id, user_b.username)
    user_b.default_workspace_id = ws_b.id
    user_repo.update(user_b)

    token_a = create_access_token(subject=user_a.id, role=user_a.role)
    token_b = create_access_token(subject=user_b.id, role=user_b.role)

    return {
        "user_a": user_a,
        "ws_a": ws_a,
        "token_a": token_a,
        "user_b": user_b,
        "ws_b": ws_b,
        "token_b": token_b,
    }


def test_complete_sensor_enrollment_lifecycle(test_client, setup_tenants, mock_db):
    """
    End-to-end verification of the 2-phase sensor enrollment lifecycle:
      Phase 1: Authenticated user creates sensor record in Web Dashboard (JWT auth).
      Phase 2: Windows Desktop Agent connects using only the enrollment credential (no JWT).
      Phase 3: Sensor sends heartbeat and telemetry batches using Authorization: Bearer <sensor_token>.
      Phase 4: Cross-tenant isolation and security constraints.
    """
    tenants = setup_tenants
    token_a = tenants["token_a"]
    token_b = tenants["token_b"]
    ws_a_id = tenants["ws_a"].id
    ws_b_id = tenants["ws_b"].id

    # -------------------------------------------------------------
    # 1. Web Dashboard: User A generates credential for LAPTOP-SENSOR-01
    # -------------------------------------------------------------
    res = test_client.post(
        "/api/v1/sensors/enroll",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "sensor_id": "LAPTOP-SENSOR-01",
            "name": "Alice Laptop Sensor",
            "collector_types": ["windows_sockets", "suricata"],
        },
    )
    assert res.status_code in (200, 201)
    enroll_data = res.json()
    assert enroll_data["success"] is True
    assert enroll_data["sensor_id"] == "LAPTOP-SENSOR-01"
    assert enroll_data["status"] == "pending_enrollment"
    assert enroll_data["workspace_id"] == ws_a_id
    raw_enrollment_key = enroll_data["enrollment_credential"]
    assert raw_enrollment_key.startswith("sen_enroll_")

    # -------------------------------------------------------------
    # 2. Cross-Tenant Conflict: User B cannot enroll with the same sensor ID
    # -------------------------------------------------------------
    res_b = test_client.post(
        "/api/v1/sensors/enroll",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "sensor_id": "LAPTOP-SENSOR-01",
            "name": "Bob Attempt",
        },
    )
    assert res_b.status_code == 409
    assert "already registered in another workspace" in res_b.json()["detail"]

    # -------------------------------------------------------------
    # 3. Web Dashboard: User A rotates the credential safely
    # -------------------------------------------------------------
    rotate_res = test_client.post(
        "/api/v1/sensors/LAPTOP-SENSOR-01/rotate-key",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    assert rotate_res.status_code == 200
    rotated_data = rotate_res.json()
    new_raw_key = rotated_data["enrollment_credential"]
    assert new_raw_key != raw_enrollment_key
    assert new_raw_key.startswith("sen_enroll_")

    # -------------------------------------------------------------
    # 4. Desktop Setup: Connect & Enroll WITHOUT a user JWT
    # -------------------------------------------------------------
    # The old key should be invalid since it was rotated
    stale_desktop_res = test_client.post(
        "/api/v1/sensors/enroll",
        json={
            "sensor_name": "LAPTOP-SENSOR-01",
            "sensor_description": "Windows 11 Workstation",
            "enrollment_credential": raw_enrollment_key,  # stale key
            "host_info": {
                "machine_name": "ALICE-LAPTOP",
                "os_version": "Microsoft Windows 11 Pro 10.0.22631",
                "suricata_version": "8.0.7",
            },
        },
    )
    assert stale_desktop_res.status_code == 401

    # Connect with the active fresh rotated key
    desktop_res = test_client.post(
        "/api/v1/sensors/enroll",
        json={
            "sensor_name": "LAPTOP-SENSOR-01",
            "sensor_description": "Windows 11 Workstation",
            "enrollment_credential": new_raw_key,
            "host_info": {
                "machine_name": "ALICE-LAPTOP",
                "os_version": "Microsoft Windows 11 Pro 10.0.22631",
                "suricata_version": "8.0.7",
            },
        },
    )
    assert desktop_res.status_code in (200, 201)
    agent_auth = desktop_res.json()
    assert agent_auth["success"] is True
    assert agent_auth["sensor_id"] == "LAPTOP-SENSOR-01"
    assert agent_auth["status"] == "registered"
    assert agent_auth["workspace_id"] == ws_a_id
    sensor_token = agent_auth["sensor_token"]
    assert sensor_token.startswith("sen_live_")

    # -------------------------------------------------------------
    # 5. One-Time Consumption: Reusing the same key fails (HTTP 400)
    # -------------------------------------------------------------
    reuse_res = test_client.post(
        "/api/v1/sensors/enroll",
        json={
            "sensor_name": "LAPTOP-SENSOR-01",
            "enrollment_credential": new_raw_key,
        },
    )
    assert reuse_res.status_code == 401 or reuse_res.status_code == 400

    # -------------------------------------------------------------
    # 6. Sensor Heartbeat: Authorization: Bearer <sensor_token>
    # -------------------------------------------------------------
    hb_res = test_client.post(
        "/api/v1/sensors/heartbeat",
        headers={"Authorization": f"Bearer {sensor_token}"},
        json={
            "sensor_id": "LAPTOP-SENSOR-01",
            "status": "online",
            "suricata_running": True,
            "npcap_running": True,
            "uptime_seconds": 3600,
            "queued_events": 0,
            "transmitted_events": 100,
        },
    )
    assert hb_res.status_code == 200
    assert hb_res.json()["acknowledged"] is True

    # Check that X-Sensor-Key also works as an alias
    hb_alias = test_client.post(
        "/api/v1/sensors/heartbeat",
        headers={"X-Sensor-Key": sensor_token},
        json={"status": "online"},
    )
    assert hb_alias.status_code == 200

    # -------------------------------------------------------------
    # 7. User JWT Rejection on Sensor Endpoints
    # -------------------------------------------------------------
    # Presenting user token_a to /sensors/heartbeat should be rejected
    rejected_hb = test_client.post(
        "/api/v1/sensors/heartbeat",
        headers={"Authorization": f"Bearer {token_a}"},
        json={"status": "online"},
    )
    assert rejected_hb.status_code == 401
    assert "User authentication tokens cannot be used as sensor API tokens" in rejected_hb.json()["detail"]

    # -------------------------------------------------------------
    # 8. Event Batch Ingestion via /api/v1/sensors/events/batch
    # -------------------------------------------------------------
    batch_res = test_client.post(
        "/api/v1/sensors/events/batch",
        headers={"Authorization": f"Bearer {sensor_token}"},
        json={
            "sensor_id": "LAPTOP-SENSOR-01",
            "batch_id": "batch_test_001",
            "events": [
                {
                    "timestamp": "2026-11-03T12:00:00Z",
                    "collector": "windows_sockets",
                    "src_ip": "192.168.1.50",
                    "dst_ip": "93.184.216.34",
                    "src_port": 54321,
                    "dst_port": 443,
                    "protocol": "TCP",
                    "bytes_sent": 1200,
                    "bytes_received": 4500,
                    "process_name": "chrome.exe",
                }
            ],
        },
    )
    assert batch_res.status_code == 200
    assert batch_res.json()["success"] is True
    assert batch_res.json()["processed_count"] == 1

    # Verify event stored with correct workspace binding
    stored_event = mock_db.network_events.find_one({"source_ip": "192.168.1.50"})
    assert stored_event is not None
    assert stored_event["workspace_id"] == ws_a_id

    # -------------------------------------------------------------
    # 9. List Sensors in Dashboard
    # -------------------------------------------------------------
    list_a = test_client.get("/api/v1/sensors", headers={"Authorization": f"Bearer {token_a}"})
    assert list_a.status_code == 200
    items_a = list_a.json()
    assert len(items_a) == 1
    assert items_a[0]["sensor_id"] == "LAPTOP-SENSOR-01"
    assert items_a[0]["connectivity_status"] == "online"
    assert items_a[0]["is_alive"] is True

    # User B should see 0 sensors in their isolated workspace
    list_b = test_client.get("/api/v1/sensors", headers={"Authorization": f"Bearer {token_b}"})
    assert list_b.status_code == 200
    assert len(list_b.json()) == 0
