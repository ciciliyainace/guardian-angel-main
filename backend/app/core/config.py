import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelAI — Network Firewall Attack Detection System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database Configuration
    DATABASE_TYPE: str = "mongodb"
    MONGODB_URI: str = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
    MONGODB_DATABASE: str = "sentinelai"
    DATABASE_URL: str = "sqlite:///./sentinelai.db"
    SQL_ECHO: bool = False

    def get_masked_mongodb_uri(self) -> str:
        """Return MongoDB URI with password masked for safe logging and error messages."""
        uri = self.MONGODB_URI
        if "@" in uri and "://" in uri:
            prefix, rest = uri.split("://", 1)
            credentials, host_part = rest.split("@", 1)
            if ":" in credentials:
                user, _ = credentials.split(":", 1)
                return f"{prefix}://{user}:******@{host_part}"
            return f"{prefix}://******@{host_part}"
        return "mongodb+srv://[masked-uri]"

    
    # Security & Auth
    SECRET_KEY: str = "sentinelai-defense-system-secret-key-production-replace"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REQUIRE_EMAIL_VERIFICATION: bool = False  # Backward-compatible default; enforce when set to True
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    LOGIN_MAX_FAILED_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # Email & SMTP Notifications
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    SMTP_USE_SSL: bool = False
    MAIL_FROM_EMAIL: str = "no-reply@sentinelai.local"
    MAIL_FROM_NAME: str = "SentinelAI Security"
    FRONTEND_BASE_URL: str = "http://localhost:5173"

    # Google OAuth 2.0 / OpenID Connect
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/google/callback"
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Server Binding
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENABLE_BACKGROUND_WORKERS: bool = True

    # Logging
    LOG_LEVEL: str = "INFO"

    # Sensors and Collectors (Portable path, configurable via environment variable)
    SURICATA_EVE_PATH: str = "datasets/eve.json"
    SURICATA_CHECKPOINT_FILE: str = "artifacts/suricata_checkpoint.json"

    # ML & Datasets
    MODEL_ARTIFACT_DIR: str = "artifacts"
    DATASET_DIR: str = "datasets"

    # Firewall Controls
    FIREWALL_MODE: str = "simulation"  # "simulation" | "windows_firewall"
    ALLOW_FIREWALL_BLOCKING: bool = False
    ALERT_ONLY_MODE: bool = True
    DEFAULT_BLOCK_DURATION_MINUTES: int = 60

    # Protected IPs & Networks that can never be blocked
    PROTECTED_IPS: List[str] = [
        "127.0.0.1",
        "::1",
        "192.168.1.1",
        "192.168.0.1",
        "10.0.0.1",
        "8.8.8.8",
        "8.8.4.4",
        "1.1.1.1",
    ]
    PROTECTED_NETWORKS: List[str] = [
        "127.0.0.0/8",
        "::1/128",
        "169.254.0.0/16",
        "224.0.0.0/4",
        "255.255.255.255/32",
    ]

    model_config = SettingsConfigDict(
        env_file=[".env", "backend/.env", "../backend/.env"],
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()
