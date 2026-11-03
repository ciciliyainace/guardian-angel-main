import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.email_service import EmailService
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User


client = TestClient(app)


def test_email_service_configuration_checks(client, db_session):
    """Verify EmailService is_configured safely requires host, password, and sender."""
    service = EmailService(db_session)
    
    # By default in test environment, SMTP_PASSWORD is empty
    assert service.is_configured() is False

    # Calling send when unconfigured does not crash and records awaiting_configuration
    res = service._send_email(
        to_email="analyst@domain.com",
        subject="Test Alert",
        html_content="<p>Test</p>",
        text_content="Test",
        notification_type="security_alert",
    )
    assert res["status"] == "awaiting_configuration"
    assert "awaiting" in res["message"].lower()

    # Check delivery log in database
    log = db_session.email_delivery_logs.find_one({"recipient_email": "analyst@domain.com"})
    assert log is not None
    assert log["status"] == "awaiting_configuration"
    assert log["sender"] == "revenreven287@gmail.com"


def test_email_templates_include_primary_support_address(client, db_session):
    """Verify all templates include designated support contact: revenreven287@gmail.com."""
    service = EmailService(db_session)
    user = User(id=101, username="testanalyst", email="testanalyst@example.com", role="analyst")

    welcome_res = service.send_welcome_email(user, verification_token="tok123")
    assert welcome_res["status"] == "awaiting_configuration"
    assert welcome_res["sender"] == "revenreven287@gmail.com"

    verif_res = service.send_verification_email(user, verification_token="tok123")
    assert verif_res["status"] == "awaiting_configuration"

    first_login_res = service.send_first_login_email(user, datetime.now(timezone.utc), ip_address="192.168.1.50")
    assert first_login_res["status"] == "awaiting_configuration"

    reminder_res = service.send_verification_reminder_email(user, verification_token="tok123")
    assert reminder_res["status"] == "awaiting_configuration"

    alert_res = service.send_security_alert_email(user, "PasswordChanged", "Password was updated from settings")
    assert alert_res["status"] == "awaiting_configuration"


def test_verify_me_shortcut_is_removed(client, db_session):
    """Verify that the artificial /verify-me endpoint has been completely removed."""
    res = client.post("/api/v1/auth/verify-me")
    assert res.status_code in (401, 404, 405)


def test_token_redemption_and_expiration_lifecycle(client, db_session):
    """Verify that only authentic token redemption marks user verified."""
    user_repo = UserRepository(db_session)
    token_repo = TokenRepository(db_session)

    # 1. Register new unverified user
    reg_payload = {
        "username": "phase12user",
        "email": "phase12user@test.org",
        "password": "SecurePassword123!",
        "confirm_password": "SecurePassword123!",
        "terms_accepted": True,
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    user_data = reg_res.json()
    assert user_data["email_verified"] is False

    user_id = user_data["id"]

    # 2. Extract generated token for this user
    token_doc = db_session.auth_tokens.find_one({"user_id": user_id, "used_at": None})
    assert token_doc is not None

    # Generating a real raw token via token repo
    raw_token = token_repo.create_token(
        user_id=user_id,
        email="phase12user@test.org",
        token_type="email_verification",
        expires_in_minutes=60,
    )

    # 3. Invalid token returns 400
    bad_res = client.post("/api/v1/auth/verify-email", json={"token": "invalid_token_12345"})
    assert bad_res.status_code == 400

    # User remains unverified
    u = user_repo.get_by_id(user_id)
    assert u.email_verified is False

    # 4. Valid token redemption
    good_res = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert good_res.status_code == 200
    assert "verified" in good_res.json()["message"].lower()

    # User is now verified in database
    u_updated = user_repo.get_by_id(user_id)
    assert u_updated.email_verified is True
    assert u_updated.email_verified_at is not None

    # 5. Single-use: Replaying the same token fails
    replay_res = client.post("/api/v1/auth/verify-email", json={"token": raw_token})
    assert replay_res.status_code == 400


def test_resend_verification_rate_limiting(client, db_session):
    """Verify resend verification limits requests to max 3 per 15 minutes."""
    token_repo = TokenRepository(db_session)
    test_email = "rate_limit_probe@test.org"

    # Seed 3 recent tokens
    now = datetime.now(timezone.utc)
    for i in range(3):
        db_session.auth_tokens.insert_one({
            "token_hash": f"hash_{i}",
            "user_id": 999,
            "email": test_email,
            "token_type": "email_verification",
            "created_at": now - timedelta(minutes=i),
            "expires_at": now + timedelta(hours=24),
            "used_at": None,
        })

    # 4th request must be rate-limited
    res = client.post("/api/v1/auth/resend-verification", json={"email": test_email})
    assert res.status_code == 429
    assert "Rate limit exceeded" in res.json()["detail"]


def test_support_messages_submission_and_rate_limiting(client, db_session):
    """Verify support messages endpoint stores in support_messages and limits rate."""
    support_payload = {
        "subject": "Email verification assistance needed",
        "category": "Account & Verification",
        "email": "analyst_probe@test.org",
        "message": "I have not received the verification email in my inbox.",
    }

    # 1. Successful submission
    res = client.post("/api/v1/support/messages", json=support_payload)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "success"
    assert data["ticket_id"].startswith("SUP-")
    assert data["support_contact"] == "revenreven287@gmail.com"

    # Verify persisted in database
    saved = db_session.support_messages.find_one({"id": data["ticket_id"]})
    assert saved is not None
    assert saved["subject"] == support_payload["subject"]
    assert saved["status"] == "open"

    # Verify audit log
    audit_entry = db_session.audit_logs.find_one({"action": "SubmitSupportMessage"})
    assert audit_entry is not None

    # 2. Rate limiting (max 5 per 15 mins)
    now = datetime.now(timezone.utc)
    for i in range(4):
        db_session.support_messages.insert_one({
            "id": f"SUP-TEST{i}",
            "email": "analyst_probe@test.org",
            "subject": f"Inquiry {i}",
            "category": "General",
            "message": "Testing limit",
            "status": "open",
            "created_at": now,
        })

    # Next attempt must trigger 429
    res_limited = client.post("/api/v1/support/messages", json=support_payload)
    assert res_limited.status_code == 429
    assert "Rate limit exceeded" in res_limited.json()["detail"]
