import re
from typing import Generator, Optional, Dict, Any
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError, OperationFailure
from app.core.config import settings
from app.core.logging_config import logger


def sanitize_error_message(err_str: str) -> str:
    """Strip passwords and credentials from MongoDB error messages for safe logging and responses."""
    # Replace mongodb+srv://... with masked URI
    sanitized = re.sub(r"://([^:@]+):([^@]+)@", r"://\1:******@", err_str)
    # Strip any explicit password parameter matches
    sanitized = re.sub(r"(password=)[^&,\s]+", r"\1******", sanitized, flags=re.IGNORECASE)
    return sanitized


class MongoDBManager:
    _instance: Optional["MongoDBManager"] = None

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self._db: Optional[Database] = None
        self.is_connected: bool = False
        self.last_error: Optional[str] = None
        self._last_connect_attempt: float = 0.0

    @classmethod
    def get_instance(cls) -> "MongoDBManager":
        if cls._instance is None:
            cls._instance = MongoDBManager()
        return cls._instance

    def connect(self) -> bool:
        """Initialize connection pool to MongoDB Atlas with sensible timeouts."""
        import time
        now = time.time()
        # Cooldown: Don't re-attempt failed connection more than once every 15 seconds
        if not self.is_connected and (now - self._last_connect_attempt < 15.0) and self._db is not None:
            return False
        self._last_connect_attempt = now

        if self.client is not None and self.is_connected:
            return True

        masked_uri = settings.get_masked_mongodb_uri()
        logger.info(f"Connecting to MongoDB Atlas at {masked_uri} (database: {settings.MONGODB_DATABASE})...")

        candidate_uris = [settings.MONGODB_URI]
        # If user included angle brackets in password like :<cici2210>@, also try without brackets :cici2210@
        if ":<" in settings.MONGODB_URI and ">@" in settings.MONGODB_URI:
            candidate_uris.append(re.sub(r":<([^>]+)>@", r":\1@", settings.MONGODB_URI))

        last_err = None
        for uri in candidate_uris:
            try:
                client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=8000,
                    connectTimeoutMS=8000,
                    socketTimeoutMS=8000,
                    maxPoolSize=50,
                    minPoolSize=5,
                    retryWrites=True,
                    appname="SentinelAI",
                )
                # Verify connectivity with ping
                client.admin.command("ping")
                self.client = client
                self._db = self.client[settings.MONGODB_DATABASE]
                self.is_connected = True
                self.last_error = None
                logger.info(f"Successfully connected and verified MongoDB Atlas ({settings.MONGODB_DATABASE}).")
                return True
            except (ServerSelectionTimeoutError, OperationFailure, PyMongoError, Exception) as e:
                last_err = e
                try:
                    client.close()
                except Exception:
                    pass

        safe_err = sanitize_error_message(str(last_err))
        if "tlsv1 alert internal error" in safe_err.lower() or "ssl handshake failed" in safe_err.lower():
            safe_err += " (Atlas dropped TLS handshake — your current IP is likely not whitelisted in MongoDB Atlas Network Access)"
        self.is_connected = False
        self.last_error = safe_err
        logger.error(
            f"Failed to connect to MongoDB Atlas: {safe_err}. "
            "Database is unavailable. Ensure MONGODB_URI credentials are valid and IP access is configured in Atlas."
        )

        # Create offline fallback client so that collection access does not raise AttributeError
        if self._db is None:
            try:
                self.client = MongoClient(
                    settings.MONGODB_URI,
                    serverSelectionTimeoutMS=2000,
                    connectTimeoutMS=2000,
                )
                self._db = self.client[settings.MONGODB_DATABASE]
            except Exception:
                pass

        return False

    def get_db(self) -> Database:
        """Return the active MongoDB database instance."""
        if self._db is None or not self.is_connected:
            self.connect()
        return self._db

    def ping(self) -> bool:
        """Run ping command against MongoDB Atlas admin."""
        if not self.is_connected or self.client is None:
            return self.connect()
        try:
            self.client.admin.command("ping")
            self.is_connected = True
            self.last_error = None
            return True
        except Exception as e:
            self.is_connected = False
            self.last_error = sanitize_error_message(str(e))
            return False

    def close(self):
        """Gracefully close the MongoDB connection pool."""
        if self.client is not None:
            logger.info("Closing MongoDB Atlas connection pool...")
            self.client.close()
            self.client = None
            self._db = None
            self.is_connected = False
            logger.info("MongoDB connection pool closed.")

    def get_health_info(self) -> Dict[str, Any]:
        """Return safe health information without exposing credentials."""
        return {
            "database_type": settings.DATABASE_TYPE,
            "connected": self.is_connected,
            "database_name": settings.MONGODB_DATABASE,
            "cluster_uri": settings.get_masked_mongodb_uri(),
            "error": self.last_error,
        }


db_manager = MongoDBManager.get_instance()


def get_db() -> Generator[Database, None, None]:
    """FastAPI dependency yielding the MongoDB Database instance."""
    db = db_manager.get_db()
    try:
        yield db
    finally:
        pass


def get_database() -> Database:
    """Helper function for workers and scripts to access the database directly."""
    return db_manager.get_db()


class SessionLocalProxy:
    """
    Callable proxy returning the MongoDB Database instance.
    Enables background workers to call `db = SessionLocal()` without breaking compatibility.
    """
    def __call__(self) -> Database:
        return db_manager.get_db()

    def close(self):
        pass


# Provide no-op methods on PyMongo Database class to guarantee compatibility with any legacy session calls
if not hasattr(Database, "close"):
    setattr(Database, "close", lambda self: None)
if not hasattr(Database, "commit"):
    setattr(Database, "commit", lambda self: None)
if not hasattr(Database, "rollback"):
    setattr(Database, "rollback", lambda self: None)

SessionLocal = SessionLocalProxy()


def init_indexes(db: Database):
    """Create all required collections and indexes idempotently."""
    try:
        # 1. users
        db.users.create_index("username", unique=True)
        db.users.create_index("email", unique=True)
        db.users.create_index("id", unique=True)
        db.users.create_index("google_sub", sparse=True)
        db.users.create_index("default_workspace_id")

        # 1a. workspaces (Multi-tenant SaaS isolation)
        db.workspaces.create_index("id", unique=True)
        db.workspaces.create_index("owner_user_id")
        db.workspaces.create_index("members.user_id")

        # 1b. auth_tokens (Single-use hashed tokens with TTL expiry)
        db.auth_tokens.create_index("token_hash", unique=True)
        db.auth_tokens.create_index([("expires_at", 1)], expireAfterSeconds=0)
        db.auth_tokens.create_index([("user_id", 1), ("token_type", 1)])

        # 1c. login_attempts (Rate limiting and lockout)
        db.login_attempts.create_index("key", unique=True)
        db.login_attempts.create_index([("expires_at", 1)], expireAfterSeconds=0)

        # 1d. email_delivery_logs (Email delivery audit trail)
        db.email_delivery_logs.create_index([("workspace_id", 1), ("attempted_at", -1)])
        db.email_delivery_logs.create_index([("user_id", 1), ("attempted_at", -1)])

        # 2. network_events
        db.network_events.create_index("id", unique=True)
        db.network_events.create_index([("timestamp", -1)])
        db.network_events.create_index([("workspace_id", 1), ("timestamp", -1)])
        db.network_events.create_index([("workspace_id", 1), ("severity", 1), ("timestamp", -1)])
        db.network_events.create_index("category")
        db.network_events.create_index([("severity", 1), ("timestamp", -1)])
        db.network_events.create_index([("source_ip", 1), ("dest_ip", 1)])
        db.network_events.create_index([("source_ip", 1), ("dest_ip", 1), ("protocol", 1), ("timestamp", -1)])
        db.network_events.create_index("data_origin")
        db.network_events.create_index("sensor_id")
        db.network_events.create_index([("sensor_id", 1), ("timestamp", -1)])
        db.network_events.create_index("is_simulated")
        db.network_events.create_index([("sensor_id", 1), ("id", 1)])

        # 3. alerts
        db.alerts.create_index("id", unique=True)
        db.alerts.create_index([("timestamp", -1)])
        db.alerts.create_index([("workspace_id", 1), ("timestamp", -1)])
        db.alerts.create_index([("workspace_id", 1), ("status", 1)])
        db.alerts.create_index([("status", 1), ("severity", 1)])
        db.alerts.create_index("related_event_id")
        db.alerts.create_index("data_origin")
        db.alerts.create_index("sensor_id")

        # 3b. sensors & sensor_heartbeats (Live network telemetry architecture)
        db.sensors.create_index("sensor_id", unique=True)
        db.sensors.create_index("api_key_hash", unique=True)
        db.sensors.create_index("sensor_token_hash", sparse=True)
        db.sensors.create_index("status")
        db.sensors.create_index([("workspace_id", 1), ("sensor_id", 1)])
        db.sensors.create_index("owner_user_id")
        db.sensor_heartbeats.create_index([("sensor_id", 1), ("timestamp", -1)])

        # 4. detection_rules
        db.detection_rules.create_index("id", unique=True)
        db.detection_rules.create_index("enabled")

        # 5. firewall_requests
        db.firewall_requests.create_index("id", unique=True)
        db.firewall_requests.create_index([("status", 1), ("requested_at", -1)])
        db.firewall_requests.create_index("source_ip")

        # 6. firewall_actions
        db.firewall_actions.create_index("id", unique=True)
        db.firewall_actions.create_index("managed_rule_name", unique=True)
        db.firewall_actions.create_index([("status", 1), ("expires_at", 1)])

        # 7. model_registry
        db.model_registry.create_index("version", unique=True)

        # 8. audit_logs
        db.audit_logs.create_index("id", unique=True)
        db.audit_logs.create_index([("timestamp", -1)])
        db.audit_logs.create_index([("actor", 1), ("timestamp", -1)])

        # 9. system_settings
        db.system_settings.create_index("key", unique=True)

        # 10. feedback
        db.feedback.create_index([("created_at", -1)])

        logger.info("MongoDB Atlas indexes verified and initialized.")
    except Exception as e:
        safe_err = sanitize_error_message(str(e))
        logger.warning(f"Note on MongoDB index initialization: {safe_err}")
