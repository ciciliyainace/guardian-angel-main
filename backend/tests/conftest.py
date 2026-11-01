import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
import mongomock

# Set test environment
os.environ["TESTING"] = "true"
os.environ["DATABASE_TYPE"] = "mongodb"
os.environ["MONGODB_DATABASE"] = "sentinelai_test"
os.environ["FIREWALL_MODE"] = "simulation"
os.environ["ALLOW_FIREWALL_BLOCKING"] = "false"

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import db_manager, get_db, init_indexes
from app.main import app
from app.core.security import hash_password, create_access_token
from app.utils.time_utils import current_epoch_ms


@pytest.fixture(scope="session")
def mock_mongo_client():
    """Create a session-scoped in-memory mongomock client."""
    client = mongomock.MongoClient()
    return client


@pytest.fixture(scope="function")
def db_session(mock_mongo_client):
    """
    Isolated per-test MongoDB database using mongomock.
    Cleans collections, seeds baseline test fixtures, and binds to db_manager.
    """
    db = mock_mongo_client["sentinelai_test"]

    # Drop all collections for clean test state
    for col in db.list_collection_names():
        db[col].drop()

    # Re-initialize collection indexes
    init_indexes(db)

    # Attach to global db_manager singleton
    db_manager.client = mock_mongo_client
    db_manager._db = db
    db_manager.is_connected = True
    db_manager.last_error = None

    # Seed baseline admin and analyst for tests
    admin_user = {
        "id": 1,
        "email": "admin@test.local",
        "username": "admin",
        "display_name": "Admin Test",
        "hashed_password": hash_password("TestPassword123!"),
        "role": "administrator",
        "is_active": True,
        "created_at": current_epoch_ms(),
        "last_login": None,
    }
    analyst_user = {
        "id": 2,
        "email": "analyst@test.local",
        "username": "analyst",
        "display_name": "Analyst Test",
        "hashed_password": hash_password("TestPassword123!"),
        "role": "analyst",
        "is_active": True,
        "created_at": current_epoch_ms(),
        "last_login": None,
    }
    db.users.insert_many([admin_user, analyst_user])

    # Seed default rules
    rule = {
        "id": "R-001",
        "name": "Port scan detection",
        "description": "Distinct destination ports",
        "category": "Port scan detection",
        "severity": "high",
        "enabled": True,
        "threshold": 5,
        "window_sec": 60,
        "last_triggered": current_epoch_ms(),
        "matches": 10,
        "rule_type": "frequency",
    }
    db.detection_rules.insert_one(rule)

    # Seed default setting
    setting = {
        "key": "firewall_mode",
        "value": "simulation",
        "category": "firewall",
        "description": "Firewall mode",
        "updated_by": "system",
        "updated_at": current_epoch_ms(),
    }
    db.system_settings.insert_one(setting)

    yield db


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers():
    token = create_access_token(subject="admin", role="administrator")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def analyst_headers():
    token = create_access_token(subject="analyst", role="analyst")
    return {"Authorization": f"Bearer {token}"}
