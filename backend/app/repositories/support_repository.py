from typing import Optional, List, Dict, Any
from pymongo.database import Database
from app.models.support_message import SupportMessage


class SupportRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.support_messages

    def create(self, msg: SupportMessage) -> SupportMessage:
        doc = msg.to_doc()
        self.collection.insert_one(doc)
        return msg

    def get_by_id(self, message_id: str) -> Optional[SupportMessage]:
        doc = self.collection.find_one({"id": str(message_id)})
        return SupportMessage.from_doc(doc) if doc else None

    def list_by_workspace(
        self,
        workspace_id: str,
        limit: int = 50,
        skip: int = 0,
    ) -> List[SupportMessage]:
        cursor = (
            self.collection.find({"workspace_id": str(workspace_id)})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        return [SupportMessage.from_doc(doc) for doc in cursor if doc]

    def list_by_email(self, email: str, limit: int = 20) -> List[SupportMessage]:
        cursor = (
            self.collection.find({"email": email.lower().strip()})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [SupportMessage.from_doc(doc) for doc in cursor if doc]
