import pytest


def test_protected_target_rejection_loopback(client):
    # Attempting to request a block on 127.0.0.1 must be rejected
    res = client.post("/api/v1/firewall/requests", json={
        "sourceIp": "127.0.0.1",
        "reason": "Test block",
        "durationMin": 60,
    })
    assert res.status_code == 400
    assert "protected" in res.json()["message"].lower() or "loopback" in res.json()["message"].lower()


def test_protected_target_rejection_dns(client):
    # Attempting to request a block on 8.8.8.8 (configured protected DNS) must be rejected
    res = client.post("/api/v1/firewall/requests", json={
        "sourceIp": "8.8.8.8",
        "reason": "Malicious DNS test",
        "durationMin": 60,
    })
    assert res.status_code == 400
    assert "protected" in res.json()["message"].lower()


def test_invalid_ip_format_rejected(client):
    res = client.post("/api/v1/firewall/requests", json={
        "sourceIp": "999.999.999.999",
        "reason": "Malformed test",
        "durationMin": 60,
    })
    assert res.status_code == 422


def test_duration_boundary_validation(client):
    # Duration < 5 min must fail validation
    res_low = client.post("/api/v1/firewall/requests", json={
        "sourceIp": "198.51.100.12",
        "reason": "Duration test",
        "durationMin": 2,
    })
    assert res_low.status_code == 422

    # Duration > 1440 min (24h) must fail validation
    res_high = client.post("/api/v1/firewall/requests", json={
        "sourceIp": "198.51.100.12",
        "reason": "Duration test",
        "durationMin": 2000,
    })
    assert res_high.status_code == 422


def test_approval_workflow_and_rollback(client, admin_headers, analyst_headers):
    # 1. Analyst creates a valid block request
    res_req = client.post(
        "/api/v1/firewall/requests",
        json={"sourceIp": "198.51.100.55", "reason": "Confirmed port scan", "durationMin": 30},
        headers=analyst_headers,
    )
    assert res_req.status_code == 201
    req = res_req.json()
    req_id = req["id"]
    assert req["status"] == "pending"

    # 2. Analyst tries to approve their own request -> Must be rejected (PermissionDenied)
    res_self_appr = client.post(
        f"/api/v1/firewall/requests/{req_id}/approve",
        headers=analyst_headers,
    )
    assert res_self_appr.status_code in (400, 403)

    # 3. Admin approves request -> Succeeds in simulation mode
    res_admin_appr = client.post(
        f"/api/v1/firewall/requests/{req_id}/approve",
        headers=admin_headers,
    )
    assert res_admin_appr.status_code == 200
    appr_data = res_admin_appr.json()
    assert appr_data["request"]["status"] == "approved"
    assert appr_data["action"]["verificationStatus"] == "simulated"
    action_id = appr_data["action"]["id"]

    # 4. Rollback the active firewall action
    res_rollback = client.post(
        f"/api/v1/firewall/actions/{action_id}/rollback",
        headers=admin_headers,
    )
    assert res_rollback.status_code == 200
    assert res_rollback.json()["success"] is True
