import pytest
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException
from app.core.security import hash_password, create_access_token, verify_password, hash_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.token_repository import TokenRepository
from app.services.email_service import EmailService
from app.services.google_auth_service import GoogleAuthService
from app.core.config import settings
from app.api.dependencies import require_authenticated_user, require_admin


# -------------------------------------------------------------
# 1. Registration Tests
# -------------------------------------------------------------
def test_register_new_account_success(client, db_session):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "sarah_connor",
            "email": "sarah@cyberdyne.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "display_name": "Sarah Connor",
            "terms_accepted": True,
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["username"] == "sarah_connor"
    assert data["email"] == "sarah@cyberdyne.com"
    assert data["role"] == "analyst"  # Default role is analyst, never admin
    assert data["email_verified"] is False
    assert "password" not in data
    assert "hashed_password" not in data

    # Verify MongoDB document
    user_doc = db_session.users.find_one({"username": "sarah_connor"})
    assert user_doc is not None
    assert user_doc["password_hash"] != "SecurePassword123!"
    assert verify_password("SecurePassword123!", user_doc["password_hash"])
    assert "password" not in user_doc  # Never stored in plaintext


def test_register_duplicate_username(client):
    # 'admin' already seeded in conftest
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin",
            "email": "different_email@test.com",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"].lower()


def test_register_duplicate_email(client):
    # 'admin@test.local' already seeded in conftest
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "new_unique_admin",
            "email": "admin@test.local",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert res.status_code == 409
    assert "already registered" in res.json()["detail"].lower()


def test_register_password_mismatch(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "mismatch_user",
            "email": "mismatch@test.com",
            "password": "SecurePassword123!",
            "confirm_password": "DifferentPassword123!",
            "terms_accepted": True,
        },
    )
    assert res.status_code == 400
    assert "do not match" in res.json()["detail"].lower()


def test_register_weak_password(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "weak_user",
            "email": "weak@test.com",
            "password": "short",
            "confirm_password": "short",
            "terms_accepted": True,
        },
    )
    assert res.status_code in (400, 422)


def test_register_invalid_email_format(client):
    res = client.post(
        "/api/v1/auth/register",
        json={
            "username": "bad_email_user",
            "email": "not-an-email",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!",
            "terms_accepted": True,
        },
    )
    assert res.status_code == 422


# -------------------------------------------------------------
# 2. Login Tests (Username, Email, Generic Error, Lockout)
# -------------------------------------------------------------
def test_login_with_username(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "TestPassword123!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["username"] == "admin"


def test_login_with_email(client):
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin@test.local", "password": "TestPassword123!"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "admin@test.local"


def test_login_invalid_credentials_generic_error(client):
    # Non-existent user
    res1 = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "non_existent_ghost", "password": "RandomPassword123!"},
    )
    assert res1.status_code == 401
    assert res1.json()["detail"] == "Invalid username/email or password."

    # Existing user, wrong password
    res2 = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "WrongPassword999!"},
    )
    assert res2.status_code == 401
    # Both return the exact same generic message
    assert res2.json()["detail"] == "Invalid username/email or password."


def test_login_inactive_account(client, db_session):
    db_session.users.update_one({"username": "analyst"}, {"$set": {"is_active": False}})
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "analyst", "password": "TestPassword123!"},
    )
    assert res.status_code == 403
    assert "inactive" in res.json()["detail"].lower()


def test_login_rate_limiting_lockout(client, db_session):
    test_user = "lockout_target"
    # Attempt failed logins up to the threshold
    for _ in range(settings.LOGIN_MAX_FAILED_ATTEMPTS):
        client.post(
            "/api/v1/auth/login",
            json={"username_or_email": test_user, "password": "WrongPassword!"},
        )

    # Next attempt should be blocked by rate limiter with 429
    res = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": test_user, "password": "WrongPassword!"},
    )
    assert res.status_code == 429
    assert "temporarily locked" in res.json()["detail"].lower()


# -------------------------------------------------------------
# 3. First-Login Email & Concurrency Idempotency
# -------------------------------------------------------------
def test_first_login_notification_idempotent(db_session):
    repo = UserRepository(db_session)
    user = repo.get_by_username("analyst")
    now = datetime.now(timezone.utc)

    # First claim should succeed
    claimed_first = repo.try_claim_first_login_notification(user.id, now)
    assert claimed_first is True

    # Immediate second claim (concurrent request) should fail and return False
    claimed_second = repo.try_claim_first_login_notification(user.id, now)
    assert claimed_second is False


# -------------------------------------------------------------
# 4. Email Verification Workflow
# -------------------------------------------------------------
def test_email_verification_lifecycle(client, db_session):
    repo = UserRepository(db_session)
    token_repo = TokenRepository(db_session)

    # Create unverified user
    user = User(
        id=99,
        email="verify_me@sentinelai.com",
        username="verify_tester",
        hashed_password=hash_password("Password123!"),
        role="analyst",
        email_verified=False,
    )
    repo.create(user)

    # Generate token
    raw_token = token_repo.create_token(
        user_id=user.id,
        email=user.email,
        token_type="email_verification",
        expires_in_minutes=60,
    )

    # Verify via API
    res = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert res.status_code == 200
    assert "verified" in res.json()["message"].lower()

    # User in database should now be verified
    updated_user = repo.get_by_id(user.id)
    assert updated_user.email_verified is True

    # Reusing the token should fail (single-use)
    res_reuse = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert res_reuse.status_code == 400


def test_resend_verification_cooldown(client, db_session):
    repo = UserRepository(db_session)
    user = User(
        id=100,
        email="resend_test@example.com",
        username="resend_tester",
        hashed_password=hash_password("Password123!"),
        email_verified=False,
    )
    repo.create(user)

    # First request
    res1 = client.post("/api/v1/auth/resend-verification", json={"email": user.email})
    assert res1.status_code == 200

    # Immediate second request triggers cooldown (HTTP 429)
    res2 = client.post("/api/v1/auth/resend-verification", json={"email": user.email})
    assert res2.status_code == 429


# -------------------------------------------------------------
# 5. Forgot Password & Password Reset Workflow
# -------------------------------------------------------------
def test_forgot_and_reset_password_lifecycle(client, db_session):
    repo = UserRepository(db_session)
    token_repo = TokenRepository(db_session)

    # 1. Forgot password request (returns generic confirmation)
    res_forgot = client.post("/api/v1/auth/forgot-password", json={"email": "admin@test.local"})
    assert res_forgot.status_code == 200
    assert "dispatched" in res_forgot.json()["message"].lower()

    # 2. Check token in DB
    user = repo.get_by_email("admin@test.local")
    token_doc = db_session.auth_tokens.find_one({"user_id": user.id, "token_type": "password_reset"})
    assert token_doc is not None
    assert "token_hash" in token_doc

    # Generate a fresh token for reset test
    raw_reset_token = token_repo.create_token(
        user_id=user.id,
        email=user.email,
        token_type="password_reset",
        expires_in_minutes=30,
    )

    # 3. Reset password
    res_reset = client.post(
        "/api/v1/auth/reset-password",
        json={
            "token": raw_reset_token,
            "password": "NewBrandSecurePassword999!",
            "confirm_password": "NewBrandSecurePassword999!",
        },
    )
    assert res_reset.status_code == 200
    assert "successfully updated" in res_reset.json()["message"].lower()

    # 4. Verify login with new password
    res_login_new = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "NewBrandSecurePassword999!"},
    )
    assert res_login_new.status_code == 200

    # 5. Old password no longer works
    res_login_old = client.post(
        "/api/v1/auth/login",
        json={"username_or_email": "admin", "password": "TestPassword123!"},
    )
    assert res_login_old.status_code == 401


# -------------------------------------------------------------
# 6. Google OAuth Status & Token Verification
# -------------------------------------------------------------
def test_google_auth_url_endpoint(client):
    res = client.get("/api/v1/auth/google/url")
    assert res.status_code == 200
    data = res.json()
    assert "configured" in data


def test_google_auth_unconfigured_error(client):
    # When GOOGLE_CLIENT_ID is not configured, calling /api/v1/auth/google returns bad request
    res = client.post(
        "/api/v1/auth/google",
        json={"id_token": "mock.google.id.token"},
    )
    assert res.status_code == 400
    assert "google sign-in is unavailable" in res.json()["detail"].lower()


def test_google_user_creation_and_linking(db_session):
    service = GoogleAuthService()
    # Mock verified google payload
    verified_payload = {
        "google_sub": "google-uid-123456789",
        "email": "alex.analyst@sentinelai.com",
        "name": "Alex Analyst",
        "email_verified": True,
    }

    # First time: provisions new user
    user, is_new, is_first = service.process_google_login(db_session, verified_payload)
    assert is_new is True
    assert is_first is True
    assert user.google_sub == "google-uid-123456789"
    assert user.email == "alex.analyst@sentinelai.com"
    assert user.email_verified is True
    assert "google" in user.auth_providers

    # Second time: existing user found by google_sub
    user2, is_new2, is_first2 = service.process_google_login(db_session, verified_payload)
    assert is_new2 is False
    assert user2.id == user.id


def test_google_prevents_unauthorized_account_takeover(db_session):
    service = GoogleAuthService()
    repo = UserRepository(db_session)

    # An existing password-only user
    existing = User(
        id=200,
        email="victim@sentinelai.com",
        username="victim_user",
        hashed_password=hash_password("Password123!"),
        auth_providers=["password"],
        google_sub=None,
    )
    repo.create(existing)

    # Attacker tries to log in with a Google account claiming the same email
    fake_google_payload = {
        "google_sub": "attacker-google-sub-999",
        "email": "victim@sentinelai.com",
        "name": "Attacker",
        "email_verified": True,
    }

    with pytest.raises(ValueError) as excinfo:
        service.process_google_login(db_session, fake_google_payload)
    assert "sign in with your password first to link" in str(excinfo.value).lower()


# -------------------------------------------------------------
# 7. Role Restrictions & Protected Route Tests
# -------------------------------------------------------------
def test_require_authenticated_user_unauthorized():
    with pytest.raises(HTTPException) as excinfo:
        require_authenticated_user(current_user=None)
    assert excinfo.value.status_code == 401
    assert "Authentication required" in excinfo.value.detail


def test_admin_only_route_analyst_forbidden(client, analyst_headers):
    # Approve firewall block request requires administrator
    res = client.post("/api/v1/firewall/requests/REQ-001/approve", headers=analyst_headers, json={})
    assert res.status_code == 403


def test_admin_only_route_admin_allowed(client, admin_headers):
    # Administrator can access firewall endpoint
    res = client.post("/api/v1/firewall/requests/REQ-001/approve", headers=admin_headers, json={})
    # Returns 404 (REQ-001 not found) or success, but NOT 401 or 403
    assert res.status_code not in (401, 403)
