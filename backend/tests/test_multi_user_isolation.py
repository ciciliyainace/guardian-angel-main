import pytest
from datetime import datetime, timezone


def test_user_registration_and_workspace_provisioning(client):
    """Verify that registering two separate users provisions distinct, isolated workspaces."""
    # Register User A
    res_a = client.post(
        "/api/v1/auth/register",
        json={
            "username": "analyst_alice",
            "email": "alice@security-corp.io",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "display_name": "Alice Analyst",
            "terms_accepted": True,
        },
    )
    assert res_a.status_code == 201, res_a.text
    data_a = res_a.json()
    assert data_a["username"] == "analyst_alice"
    assert data_a["email"] == "alice@security-corp.io"
    assert data_a["email_verified"] is False
    assert data_a["default_workspace_id"] is not None
    assert "analyst_alice" in data_a["workspace_name"].lower() or "alice" in data_a["workspace_name"].lower()

    # Register User B
    res_b = client.post(
        "/api/v1/auth/register",
        json={
            "username": "analyst_bob",
            "email": "bob@security-corp.io",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "display_name": "Bob Analyst",
            "terms_accepted": True,
        },
    )
    assert res_b.status_code == 201, res_b.text
    data_b = res_b.json()
    assert data_b["username"] == "analyst_bob"
    assert data_b["email"] == "bob@security-corp.io"
    assert data_b["email_verified"] is False
    assert data_b["default_workspace_id"] is not None

    # Crucial tenant isolation assertion: distinct workspaces!
    assert data_a["default_workspace_id"] != data_b["default_workspace_id"]


def test_authenticated_profile_identity_and_resolution(client):
    """Verify authenticated user profile returns genuine user data and never hardcoded defaults."""
    # Register Alice
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "analyst_alice",
            "email": "alice@security-corp.io",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "display_name": "Alice Analyst",
            "terms_accepted": True,
        },
    )
    # Register Bob
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "analyst_bob",
            "email": "bob@security-corp.io",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "display_name": "Bob Analyst",
            "terms_accepted": True,
        },
    )

    # Login as User A
    login_a = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "analyst_alice", "password": "SecurePassword123!"},
    )
    assert login_a.status_code == 200
    token_a = login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # Login as User B
    login_b = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "analyst_bob", "password": "SecurePassword123!"},
    )
    assert login_b.status_code == 200
    token_b = login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Request profile as Alice
    prof_a = client.get("/api/v1/profile", headers=headers_a)
    assert prof_a.status_code == 200
    pdata_a = prof_a.json()
    assert pdata_a["username"] == "analyst_alice"
    assert pdata_a["email"] == "alice@security-corp.io"
    assert (pdata_a.get("displayName") or pdata_a.get("display_name")) == "Alice Analyst"
    assert (pdata_a.get("emailVerified") if "emailVerified" in pdata_a else pdata_a.get("email_verified")) is False
    assert pdata_a["username"] != "ciciliya-inace"
    assert pdata_a["email"] != "analyst@sentinelai.local"

    # Request profile as Bob
    prof_b = client.get("/api/v1/profile", headers=headers_b)
    assert prof_b.status_code == 200
    pdata_b = prof_b.json()
    assert pdata_b["username"] == "analyst_bob"
    assert pdata_b["email"] == "bob@security-corp.io"
    assert (pdata_b.get("displayName") or pdata_b.get("display_name")) == "Bob Analyst"
    assert (pdata_b.get("emailVerified") if "emailVerified" in pdata_b else pdata_b.get("email_verified")) is False
    ws_a = pdata_a.get("defaultWorkspaceId") or pdata_a.get("default_workspace_id")
    ws_b = pdata_b.get("defaultWorkspaceId") or pdata_b.get("default_workspace_id")
    assert ws_a != ws_b


def test_multi_user_sensor_and_telemetry_isolation(client):
    """
    Verify complete tenant telemetry isolation:
    - User A enrolls a sensor in Workspace A.
    - User B cannot see User A's sensor.
    - Sensor ingests live attack telemetry -> stamped with Workspace A.
    - User A sees events and alerts.
    - User B sees 0 events and 0 alerts in Workspace B.
    """
    # Register Alice & Bob
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "analyst_alice",
            "email": "alice@security-corp.io",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "display_name": "Alice Analyst",
            "terms_accepted": True,
        },
    )
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "analyst_bob",
            "email": "bob@security-corp.io",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "display_name": "Bob Analyst",
            "terms_accepted": True,
        },
    )

    # 1. Login Alice & Bob
    tok_a = client.post("/api/v1/auth/login", json={"username_or_email": "analyst_alice", "password": "SecurePassword123!"}).json()["access_token"]
    tok_b = client.post("/api/v1/auth/login", json={"username_or_email": "analyst_bob", "password": "SecurePassword123!"}).json()["access_token"]
    head_a = {"Authorization": f"Bearer {tok_a}"}
    head_b = {"Authorization": f"Bearer {tok_b}"}

    # 2. Alice enrolls sensor
    enroll_res = client.post(
        "/api/v1/sensors/enroll",
        headers=head_a,
        json={
            "sensor_id": "sensor-alice-win-01",
            "name": "Alice Office Sensor",
            "hostname": "ALICE-DESKTOP",
            "collector_types": ["windows_sockets", "suricata"],
        },
    )
    assert enroll_res.status_code == 201, enroll_res.text
    sensor_key = enroll_res.json()["api_key"]

    # 3. Verify sensor listing visibility
    sensors_a = client.get("/api/v1/sensors", headers=head_a).json()
    alice_sensor_ids = [s["sensor_id"] for s in sensors_a]
    assert "sensor-alice-win-01" in alice_sensor_ids

    sensors_b = client.get("/api/v1/sensors", headers=head_b).json()
    bob_sensor_ids = [s["sensor_id"] for s in sensors_b]
    assert "sensor-alice-win-01" not in bob_sensor_ids  # Bob cannot see Alice's sensor!

    # 4. Sensor streams telemetry batch
    telemetry_payload = {
        "sensor_id": "sensor-alice-win-01",
        "events": [
            {
                "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
                "source_ip": "198.51.100.44",
                "dest_ip": "10.0.0.15",
                "src_port": 54321,
                "dst_port": 22,
                "protocol": "TCP",
                "flow_features": {
                    "dst_port": 22,
                    "flow_duration_ms": 250,
                    "syn_flag_count": 1,
                    "fin_flag_count": 0,
                    "packet_count": 3,
                    "byte_count": 180,
                },
                "collector": "windows_sockets",
            }
        ],
    }
    ingest_res = client.post(
        "/api/v1/sensors/telemetry",
        headers={"X-Sensor-Key": sensor_key},
        json=telemetry_payload,
    )
    assert ingest_res.status_code == 200, ingest_res.text
    assert ingest_res.json()["ingested"] >= 1

    # 5. Query events: Alice MUST see the event
    events_a = client.get("/api/v1/events?origin=live", headers=head_a).json()
    assert len(events_a) >= 1
    assert any(e["sourceIp"] == "198.51.100.44" for e in events_a)

    # 6. Query events: Bob MUST NOT see Alice's events!
    events_b = client.get("/api/v1/events?origin=live", headers=head_b).json()
    assert not any(e["sourceIp"] == "198.51.100.44" for e in events_b)

    # 7. Query analytics summary: Alice sees her event count, Bob sees 0
    summary_a = client.get("/api/v1/analytics/summary?origin=live", headers=head_a).json()
    summary_b = client.get("/api/v1/analytics/summary?origin=live", headers=head_b).json()
    assert summary_a["totalEvents"] >= 1
    assert summary_b["totalEvents"] == 0
