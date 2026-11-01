from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from pymongo.database import Database
from app.models.system_setting import SystemSetting
from app.models.feedback import Feedback
from app.services.audit_service import AuditService


class SettingsService:
    def __init__(self, db: Database):
        self.db = db
        self.audit_service = AuditService(db)
        self.settings_coll = db.system_settings
        self.feedback_coll = db.feedback

    def list_settings(self) -> List[SystemSetting]:
        cursor = self.settings_coll.find()
        return [SystemSetting.from_doc(doc) for doc in cursor if doc]

    def get_setting(self, key: str) -> Optional[SystemSetting]:
        doc = self.settings_coll.find_one({"key": key})
        return SystemSetting.from_doc(doc)

    def update_setting(self, key: str, value: Any, actor: str = "administrator") -> SystemSetting:
        setting = self.get_setting(key)
        now = datetime.now(timezone.utc)
        if not setting:
            setting = SystemSetting(key=key, value=value, updated_by=actor, updated_at=now)
        else:
            setting.value = value
            setting.updated_by = actor
            setting.updated_at = now

        self.settings_coll.update_one({"key": key}, {"$set": setting.to_doc()}, upsert=True)

        self.audit_service.log(
            actor=actor,
            action="Update setting",
            target=key,
            result="Success",
            reason="Configuration updated via settings interface",
        )
        return setting

    def submit_feedback(
        self,
        category: str,
        message: str,
        user_id: Optional[int] = None,
        user_email: Optional[str] = None,
    ) -> Feedback:
        now = datetime.now(timezone.utc)
        last = self.feedback_coll.find_one(sort=[("id", -1)])
        next_id = (last.get("id", 0) + 1) if last else 1
        fb = Feedback(
            id=next_id,
            user_id=user_id,
            user_email=user_email,
            category=category,
            message=message,
            status="received",
            created_at=now,
        )
        self.feedback_coll.insert_one(fb.to_doc())
        return fb
