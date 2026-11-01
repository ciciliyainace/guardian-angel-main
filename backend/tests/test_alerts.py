def test_alert_created_from_critical_event_and_updated(client, admin_headers):
    # Ingest critical event which auto-creates an alert
    res_ev = client.post("/api/v1/events/ingest", json={
        "source_ip": "198.51.100.99",
        "dest_ip": "192.168.1.1",
        "protocol": "TCP",
        "category": "DoS-like traffic",
        "severity": "critical",
        "risk_score": 92,
    })
    assert res_ev.status_code == 200
    ev = res_ev.json()

    # Verify alert exists
    res_alerts = client.get("/api/v1/alerts")
    assert res_alerts.status_code == 200
    alerts = res_alerts.json()
    assert len(alerts) >= 1

    alert = alerts[0]
    alert_id = alert["id"]
    assert alert["status"] == "new"

    # Update alert status to investigating
    res_update = client.patch(
        f"/api/v1/alerts/{alert_id}",
        json={"status": "investigating", "notes": "Under review by SOC lead"},
        headers=admin_headers,
    )
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["status"] == "investigating"
    assert updated["notes"] == "Under review by SOC lead"

    # Check alert summary
    res_summary = client.get("/api/v1/alerts/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["total_alerts"] >= 1
