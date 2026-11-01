def test_rules_crud(client, admin_headers):
    # 1. Get rules
    res = client.get("/api/v1/rules")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 1
    initial_count = len(rules)

    # 2. Create rule
    new_rule = {
        "id": "R-TEST-99",
        "name": "Custom SSH brute-force rule",
        "description": "Trigger when repeated SSH auth fails",
        "category": "Brute-force",
        "severity": "high",
        "enabled": True,
        "threshold": 5,
        "windowSec": 60,
        "ruleType": "threshold",
    }
    res_create = client.post("/api/v1/rules", json=new_rule, headers=admin_headers)
    assert res_create.status_code == 201
    created = res_create.json()
    assert created["id"] == "R-TEST-99"

    # 3. Update rule
    res_update = client.patch(
        "/api/v1/rules/R-TEST-99",
        json={"enabled": False, "threshold": 10},
        headers=admin_headers,
    )
    assert res_update.status_code == 200
    updated = res_update.json()
    assert updated["enabled"] is False
    assert updated["threshold"] == 10

    # 4. Delete rule
    res_del = client.delete("/api/v1/rules/R-TEST-99", headers=admin_headers)
    assert res_del.status_code == 200

    # Verify count is back to initial
    res_after = client.get("/api/v1/rules")
    assert len(res_after.json()) == initial_count
