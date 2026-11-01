import re
import math
from typing import Optional, List, Tuple, Dict, Any
from pymongo.database import Database
from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.audit_logs

    def get_by_id(self, log_id: str) -> Optional[AuditLog]:
        doc = self.collection.find_one({"id": log_id})
        return AuditLog.from_doc(doc)

    def create(self, log: AuditLog) -> AuditLog:
        doc = log.to_doc()
        self.collection.update_one({"id": log.id}, {"$set": doc}, upsert=True)
        return log

    def list_logs(
        self,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[AuditLog], int, int, int]:
        q: Dict[str, Any] = {}
        if actor and actor != "all":
            escaped = re.escape(actor.strip())
            q["actor"] = {"$regex": escaped, "$options": "i"}
        if action and action != "all":
            escaped = re.escape(action.strip())
            q["action"] = {"$regex": escaped, "$options": "i"}

        total_count = self.collection.count_documents(q)
        total_pages = max(1, math.ceil(total_count / page_size)) if total_count > 0 else 1
        page = max(1, min(page, total_pages))
        skip = (page - 1) * page_size

        cursor = self.collection.find(q).sort([("timestamp", -1)]).skip(skip).limit(page_size)
        items = [AuditLog.from_doc(doc) for doc in cursor if doc]
        return items, total_count, total_pages, page
