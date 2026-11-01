def test_login_success(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "TestPassword123!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "administrator"


def test_login_failure(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "WrongPassword!"},
    )
    assert res.status_code == 401


def test_get_current_user_authenticated(client, admin_headers):
    res = client.get("/api/v1/auth/me", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "admin"
    assert data["role"] == "administrator"


def test_get_current_user_unauthenticated(client):
    res = client.get("/api/v1/auth/me")
    assert res.status_code == 200
    data = res.json()
    # Returns default demo profile
    assert data["username"] == "ciciliya-inace"
