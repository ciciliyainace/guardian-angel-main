from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple
from pymongo.database import Database
from pymongo import ReturnDocument
from app.models.user import User
from app.core.config import settings


class UserRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.users
        self.attempts_collection = db.login_attempts

    @staticmethod
    def normalize_username(username: str) -> str:
        return username.strip() if username else ""

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower() if email else ""

    def get_by_id(self, user_id: int) -> Optional[User]:
        doc = self.collection.find_one({"id": int(user_id)})
        return User.from_doc(doc)

    def get_by_username(self, username: str) -> Optional[User]:
        norm = self.normalize_username(username)
        # Match case-insensitively using regex or direct equality
        doc = self.collection.find_one({"username": {"$regex": f"^{norm}$", "$options": "i"}})
        return User.from_doc(doc)

    def get_by_email(self, email: str) -> Optional[User]:
        norm = self.normalize_email(email)
        doc = self.collection.find_one({"email": norm})
        return User.from_doc(doc)

    def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        clean = identifier.strip()
        doc = self.collection.find_one({
            "$or": [
                {"username": {"$regex": f"^{clean}$", "$options": "i"}},
                {"email": clean.lower()},
            ]
        })
        return User.from_doc(doc)

    def get_by_google_sub(self, google_sub: str) -> Optional[User]:
        if not google_sub:
            return None
        doc = self.collection.find_one({"google_sub": str(google_sub)})
        return User.from_doc(doc)

    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        cursor = self.collection.find().skip(skip).limit(limit)
        return [User.from_doc(doc) for doc in cursor if doc]

    def create(self, user: User) -> User:
        user.username = self.normalize_username(user.username)
        user.email = self.normalize_email(user.email)

        if not user.id or user.id <= 0:
            last = self.collection.find_one(sort=[("id", -1)])
            user.id = (last.get("id", 0) + 1) if last else 1

        doc = user.to_doc()
        self.collection.update_one({"id": user.id}, {"$set": doc}, upsert=True)
        return user

    def update(self, user: User) -> User:
        user.updated_at = datetime.now(timezone.utc)
        doc = user.to_doc()
        self.collection.update_one({"id": user.id}, {"$set": doc})
        return user

    def record_successful_login(self, user_id: int, timestamp: datetime) -> Optional[User]:
        """Update last_login_at and first_login_at (if not previously set)."""
        now = timestamp or datetime.now(timezone.utc)
        existing = self.collection.find_one({"id": int(user_id)})
        first_login_val = existing.get("first_login_at") if existing else None
        if first_login_val is None:
            first_login_val = now

        doc = self.collection.find_one_and_update(
            {"id": int(user_id)},
            {
                "$set": {
                    "last_login_at": now,
                    "first_login_at": first_login_val,
                    "failed_login_attempts": 0,
                    "lockout_until": None,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return User.from_doc(doc)

    def try_claim_first_login_notification(self, user_id: int, timestamp: datetime) -> bool:
        """
        Atomically claim the first-login notification right.
        Ensures concurrent requests cannot trigger duplicate emails.
        Returns True if claimed, False if already sent or claimed.
        """
        now = timestamp or datetime.now(timezone.utc)
        doc = self.collection.find_one_and_update(
            {
                "id": int(user_id),
                "first_login_email_sent_at": None,
            },
            {
                "$set": {
                    "first_login_email_sent_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return doc is not None

    def mark_welcome_email_sent(self, user_id: int, timestamp: datetime) -> None:
        now = timestamp or datetime.now(timezone.utc)
        self.collection.update_one(
            {"id": int(user_id)},
            {"$set": {"welcome_email_sent_at": now}},
        )

    def mark_email_verified(self, user_id: int) -> bool:
        now = datetime.now(timezone.utc)
        res = self.collection.update_one(
            {"id": int(user_id)},
            {"$set": {"email_verified": True, "email_verified_at": now, "updated_at": now}},
        )
        return res.modified_count > 0

    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        now = datetime.now(timezone.utc)
        res = self.collection.update_one(
            {"id": int(user_id)},
            {
                "$set": {
                    "hashed_password": new_password_hash,
                    "password_hash": new_password_hash,
                    "updated_at": now,
                }
            },
        )
        return res.modified_count > 0

    def link_google_account(self, user_id: int, google_sub: str) -> Optional[User]:
        now = datetime.now(timezone.utc)
        doc = self.collection.find_one_and_update(
            {"id": int(user_id)},
            {
                "$set": {
                    "google_sub": str(google_sub),
                    "email_verified": True,
                    "updated_at": now,
                },
                "$addToSet": {"auth_providers": "google"},
            },
            return_document=ReturnDocument.AFTER,
        )
        return User.from_doc(doc)

    # -------------------------------------------------------------
    # Rate Limiting & Account Lockout
    # -------------------------------------------------------------
    def is_locked_out(self, identifier: str) -> Tuple[bool, int]:
        """Check if an identifier (username or email) is locked out. Returns (is_locked, minutes_remaining)."""
        key = identifier.lower().strip()
        now = datetime.now(timezone.utc)

        record = self.attempts_collection.find_one({"key": key})
        if not record:
            return False, 0

        lockout_until = record.get("lockout_until")
        if lockout_until:
            if getattr(lockout_until, "tzinfo", None) is None:
                lockout_until = lockout_until.replace(tzinfo=timezone.utc)
            if lockout_until > now:
                remaining = int((lockout_until - now).total_seconds() / 60) + 1
                return True, remaining

        return False, 0

    def record_failed_attempt(self, identifier: str) -> int:
        """Increment failed login attempts and apply lockout if max reached. Returns current attempt count."""
        key = identifier.lower().strip()
        now = datetime.now(timezone.utc)
        window = timedelta(minutes=settings.LOGIN_LOCKOUT_MINUTES)
        expires_at = now + window

        record = self.attempts_collection.find_one({"key": key})
        count = (record.get("count", 0) + 1) if record else 1

        lockout_until = None
        if count >= settings.LOGIN_MAX_FAILED_ATTEMPTS:
            lockout_until = now + window

        self.attempts_collection.update_one(
            {"key": key},
            {
                "$set": {
                    "count": count,
                    "last_attempt": now,
                    "expires_at": expires_at,
                    "lockout_until": lockout_until,
                }
            },
            upsert=True,
        )
        return count

    def clear_failed_attempts(self, identifier: str) -> None:
        """Clear failed login attempts counter on successful authentication."""
        key = identifier.lower().strip()
        self.attempts_collection.delete_one({"key": key})
