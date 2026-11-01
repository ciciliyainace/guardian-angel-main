import pytest
from app.core.config import Settings
from app.core.database import sanitize_error_message, MongoDBManager


def test_sanitize_error_message_masks_password():
    raw_error = "ServerSelectionTimeoutError: connection to mongodb+srv://ciciliyainace2210:MySecretPass123!@cluster0.kramxzk.mongodb.net failed"
    sanitized = sanitize_error_message(raw_error)
    assert "MySecretPass123!" not in sanitized
    assert "******" in sanitized
    assert "ciciliyainace2210" in sanitized


def test_masked_mongodb_uri_in_settings():
    s = Settings(
        MONGODB_URI="mongodb+srv://admin_user:SuperSecretPassword99@cluster0.mongodb.net/testdb?retryWrites=true",
        DATABASE_TYPE="mongodb",
        MONGODB_DATABASE="testdb",
    )
    masked = s.get_masked_mongodb_uri()
    assert "SuperSecretPassword99" not in masked
    assert "admin_user:******@cluster0.mongodb.net" in masked


def test_mongodb_manager_health_info(db_session):
    mgr = MongoDBManager.get_instance()
    info = mgr.get_health_info()
    assert info["database_type"] == "mongodb"
    assert info["connected"] is True
    assert "cluster_uri" in info
    assert "password" not in str(info).lower() or "******" in str(info)


def test_health_ready_endpoint(client):
    res = client.get("/health/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert "cluster" in data
    # Guarantee password is never leaked in health ready payload
    assert "password" not in str(data).lower()
