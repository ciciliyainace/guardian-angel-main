def test_audit_logs_query(client):
    # Log entries are created during auth and firewall actions
    res = client.get("/api/v1/audit")
    assert res.status_code == 200
    logs = res.json()
    assert isinstance(logs, list)
    if logs:
        first = logs[0]
        assert "actor" in first
        assert "action" in first
        assert "target" in first
        assert "result" in first


def test_audit_secret_sanitization(client):
    # Testing that password fields are never recorded in audit logs
    client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "SamplePassword123!"},
    )

    res = client.get("/api/v1/audit")
    assert res.status_code == 200
    logs = res.json()
    for log in logs:
        log_str = str(log)
        assert "SamplePassword123!" not in log_str
