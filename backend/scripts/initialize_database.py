import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import db_manager, init_indexes
from app.core.security import hash_password
from app.core.logging_config import setup_logging, logger
from app.utils.time_utils import current_epoch_ms


def seed_database():
    setup_logging()
    logger.info("Initializing MongoDB Atlas collections, indexes, and seed data...")

    # Connect to MongoDB
    connected = db_manager.connect()
    if not connected:
        logger.error(
            f"Cannot connect to MongoDB Atlas at {db_manager.last_error}. "
            "Please verify MONGODB_URI and IP access whitelist in MongoDB Atlas."
        )
        sys.exit(1)

    db = db_manager.get_db()

    # 1. Initialize Collections and Indexes
    init_indexes(db)

    # 2. Seed Default Users (Admin and Analyst)
    initial_admin_pwd = os.environ.get("INITIAL_ADMIN_PASSWORD", "SentinelAdmin2026!")
    initial_analyst_pwd = os.environ.get("INITIAL_ANALYST_PASSWORD", "AnalystPass2026!")

    # Admin User
    admin_user = db.users.find_one({"username": "admin"})
    if not admin_user:
        admin_doc = {
            "id": 1,
            "username": "admin",
            "email": "admin@sentinelai.local",
            "display_name": "Administrator",
            "hashed_password": hash_password(initial_admin_pwd),
            "role": "administrator",
            "is_active": True,
            "created_at": current_epoch_ms(),
            "last_login": None,
        }
        db.users.insert_one(admin_doc)
        logger.info("Created default administrator account: 'admin' (password configured from INITIAL_ADMIN_PASSWORD or initial setup).")
    else:
        logger.info("Administrator 'admin' already exists.")

    # Analyst User
    analyst_user = db.users.find_one({"username": "ciciliya-inace"})
    if not analyst_user:
        analyst_doc = {
            "id": 2,
            "username": "ciciliya-inace",
            "email": "analyst@sentinelai.local",
            "display_name": "Ciciliya Inace",
            "hashed_password": hash_password(initial_analyst_pwd),
            "role": "analyst",
            "is_active": True,
            "created_at": current_epoch_ms(),
            "last_login": None,
        }
        db.users.insert_one(analyst_doc)
        logger.info("Created default analyst account: 'ciciliya-inace' (password configured from INITIAL_ANALYST_PASSWORD or initial setup).")
    else:
        logger.info("Analyst 'ciciliya-inace' already exists.")

    # 3. Seed Default Detection Rules
    default_rules = [
        {
            "id": "R-001",
            "name": "Port scan detection",
            "description": "Distinct destination ports contacted by one source",
            "category": "Port scan detection",
            "severity": "high",
            "enabled": True,
            "threshold": 25,
            "window_sec": 60,
            "last_triggered": current_epoch_ms() - 600000,
            "matches": 142,
            "rule_type": "frequency",
        },
        {
            "id": "R-002",
            "name": "Connection-rate threshold",
            "description": "New connections per source exceed threshold",
            "category": "Connection-rate threshold",
            "severity": "critical",
            "enabled": True,
            "threshold": 300,
            "window_sec": 10,
            "last_triggered": current_epoch_ms() - 3600000,
            "matches": 38,
            "rule_type": "rate",
        },
        {
            "id": "R-003",
            "name": "Repeated auth failures",
            "description": "Failed SSH/RDP logins from same source",
            "category": "Repeated authentication failures",
            "severity": "high",
            "enabled": True,
            "threshold": 8,
            "window_sec": 120,
            "last_triggered": current_epoch_ms() - 900000,
            "matches": 76,
            "rule_type": "threshold",
        },
        {
            "id": "R-004",
            "name": "Suricata ET signatures",
            "description": "Escalate Emerging Threats signature hits",
            "category": "Known signature alerts",
            "severity": "medium",
            "enabled": True,
            "threshold": 1,
            "window_sec": 1,
            "last_triggered": current_epoch_ms() - 200000,
            "matches": 211,
            "rule_type": "signature",
        },
        {
            "id": "R-005",
            "name": "Long low-volume flows",
            "description": "Persistent flows with tiny payloads (beacon-like)",
            "category": "Suspicious flow patterns",
            "severity": "low",
            "enabled": False,
            "threshold": 600,
            "window_sec": 3600,
            "last_triggered": current_epoch_ms() - 86400000,
            "matches": 9,
            "rule_type": "pattern",
        },
    ]

    for rule in default_rules:
        if not db.detection_rules.find_one({"id": rule["id"]}):
            db.detection_rules.insert_one(rule)
            logger.info(f"Seeded detection rule: {rule['id']} ({rule['name']})")

    # 4. Seed System Settings
    settings_seed = [
        ("firewall_mode", "simulation", "firewall", "Firewall operational mode (simulation or windows_firewall)"),
        ("allow_firewall_blocking", False, "firewall", "Master toggle enabling OS-level firewall blocking"),
        ("alert_only_mode", True, "detection", "Default mode where detections create alerts without automated blocks"),
        ("default_block_duration_minutes", 60, "firewall", "Default temporary rule block duration in minutes"),
        ("auto_archive_resolved_alerts_days", 30, "general", "Retention window for resolved security alerts"),
    ]

    for key, val, cat, desc in settings_seed:
        if not db.system_settings.find_one({"key": key}):
            db.system_settings.insert_one({
                "key": key,
                "value": val,
                "category": cat,
                "description": desc,
                "updated_by": "system",
                "updated_at": current_epoch_ms(),
            })
            logger.info(f"Seeded system setting: {key}")

    logger.info("MongoDB database initialization and seeding successfully completed.")


if __name__ == "__main__":
    seed_database()
