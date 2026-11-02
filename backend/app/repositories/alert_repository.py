import math
from typing import Optional, List, Tuple, Dict, Any
from pymongo.database import Database
from app.models.alert import Alert


class AlertRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.alerts

    def get_by_id(self, alert_id: str) -> Optional[Alert]:
        doc = self.collection.find_one({"$or": [{"id": alert_id}, {"related_event_id": alert_id}]})
        return Alert.from_doc(doc)

    def create(self, alert: Alert) -> Alert:
        doc = alert.to_doc()
        self.collection.update_one({"id": alert.id}, {"$set": doc}, upsert=True)
        return alert

    def filter_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        origin: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Alert], int, int, int]:
        q: Dict[str, Any] = {}

        if status and status != "all":
            q["status"] = status.lower()

        if severity and severity != "all":
            q["severity"] = severity.lower()

        if category and category != "all":
            q["category"] = category

        if origin and origin != "all":
            if origin == "live":
                q["$or"] = [{"data_origin": "live"}, {"is_simulated": False}]
            elif origin == "simulated":
                q["$or"] = [{"data_origin": "simulated"}, {"is_simulated": True}]

        total_count = self.collection.count_documents(q)
        total_pages = max(1, math.ceil(total_count / page_size)) if total_count > 0 else 1
        page = max(1, min(page, total_pages))
        skip = (page - 1) * page_size

        cursor = self.collection.find(q).sort([("timestamp", -1)]).skip(skip).limit(page_size)
        items = [Alert.from_doc(doc) for doc in cursor if doc]
        return items, total_count, total_pages, page

    def count_by_status(self) -> dict:
        total = self.collection.count_documents({})
        active = self.collection.count_documents({"status": {"$ne": "resolved"}})
        critical = self.collection.count_documents({"severity": "critical"})
        high = self.collection.count_documents({"severity": "high"})
        resolved = self.collection.count_documents({"status": "resolved"})
        return {
            "total_alerts": total,
            "active_alerts": active,
            "critical_alerts": critical,
            "high_alerts": high,
            "resolved_alerts": resolved,
        }

    def update_status(self, alert_id: str, new_status: str, notes: Optional[str] = None) -> Optional[Alert]:
        update_doc: Dict[str, Any] = {"status": new_status}
        if notes is not None:
            update_doc["notes"] = notes
        self.collection.update_one({"$or": [{"id": alert_id}, {"related_event_id": alert_id}]}, {"$set": update_doc})
        return self.get_by_id(alert_id)
