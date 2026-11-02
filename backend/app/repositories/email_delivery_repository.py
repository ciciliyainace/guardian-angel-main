from typing import Optional, List, Dict, Any
from pymongo.database import Database
from app.models.email_delivery_log import EmailDeliveryLog


class EmailDeliveryRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.email_delivery_logs

    def record_attempt(self, log: EmailDeliveryLog) -> EmailDeliveryLog:
        doc = log.to_doc()
        self.collection.insert_one(doc)
        return log

    record_delivery = record_attempt

    def list_by_workspace(
        self,
        workspace_id: str,
        limit: int = 50,
        skip: int = 0,
    ) -> List[EmailDeliveryLog]:
        cursor = self.collection.find({"workspace_id": str(workspace_id)}).sort("attempted_at", -1).skip(skip).limit(limit)
        return [EmailDeliveryLog.from_doc(doc) for doc in cursor if doc]

    def list_by_user(
        self,
        user_id: int,
        limit: int = 50,
    ) -> List[EmailDeliveryLog]:
        cursor = self.collection.find({"user_id": int(user_id)}).sort("attempted_at", -1).limit(limit)
        return [EmailDeliveryLog.from_doc(doc) for doc in cursor if doc]
