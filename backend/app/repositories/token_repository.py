from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from pymongo.database import Database
from pymongo import ReturnDocument
from app.core.security import generate_secure_token, hash_token


class TokenRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.auth_tokens

    def create_token(
        self,
        user_id: int,
        email: str,
        token_type: str,
        expires_in_minutes: int = 30,
    ) -> str:
        """
        Generate a cryptographically secure random token, store ONLY its SHA-256 hash in MongoDB,
        and return the raw token string to be sent via email.
        """
        raw_token = generate_secure_token(32)
        token_hash = hash_token(raw_token)
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(minutes=expires_in_minutes)

        # Invalidate any previous unconsumed tokens of this type for this user
        self.collection.update_many(
            {"user_id": int(user_id), "token_type": token_type, "used_at": None},
            {"$set": {"used_at": now}},
        )

        doc = {
            "token_hash": token_hash,
            "user_id": int(user_id),
            "email": email.lower().strip(),
            "token_type": token_type,  # "email_verification" | "password_reset"
            "created_at": now,
            "expires_at": expires_at,
            "used_at": None,
        }
        self.collection.insert_one(doc)
        return raw_token

    def verify_and_consume_token(
        self,
        raw_token: str,
        token_type: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Atomically verify that the token exists, matches type, has not expired,
        and has not been consumed. If valid, marks `used_at` to prevent reuse.
        """
        if not raw_token:
            return None

        token_hash = hash_token(raw_token.strip())
        now = datetime.now(timezone.utc)

        # First verify token exists and is unused
        doc = self.collection.find_one({
            "token_hash": token_hash,
            "token_type": token_type,
            "used_at": None,
        })
        if not doc:
            return None

        # Check expiration safely handling naive or aware datetimes
        expires_at = doc.get("expires_at")
        if expires_at:
            if getattr(expires_at, "tzinfo", None) is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at <= now:
                return None

        # Consume token atomically
        updated = self.collection.find_one_and_update(
            {
                "token_hash": token_hash,
                "token_type": token_type,
                "used_at": None,
            },
            {"$set": {"used_at": now}},
            return_document=ReturnDocument.AFTER,
        )
        return updated

    def check_resend_cooldown(self, email: str, token_type: str, cooldown_seconds: int = 60) -> bool:
        """
        Check whether a token of this type was generated for this email recently.
        Returns True if cooldown is still active (cannot resend), False if allowed.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=cooldown_seconds)
        cursor = self.collection.find({
            "email": email.lower().strip(),
            "token_type": token_type,
        })
        for item in cursor:
            created = item.get("created_at")
            if created:
                if getattr(created, "tzinfo", None) is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created > cutoff:
                    return True
        return False

    def is_rate_limited(self, email: str, token_type: str, max_requests: int = 3, window_minutes: int = 15) -> bool:
        """
        Check if more than `max_requests` tokens of this type have been created
        for this email address in the last `window_minutes`.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=window_minutes)
        cursor = self.collection.find({
            "email": email.lower().strip(),
            "token_type": token_type,
        })
        count = 0
        for item in cursor:
            created = item.get("created_at")
            if created:
                if getattr(created, "tzinfo", None) is None:
                    created = created.replace(tzinfo=timezone.utc)
                if created > cutoff:
                    count += 1
        return count >= max_requests
