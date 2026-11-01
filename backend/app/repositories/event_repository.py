import re
import math
from typing import Optional, List, Dict, Any, Tuple
from pymongo.database import Database
from app.models.network_event import NetworkEvent
from app.utils.time_utils import hours_ago_epoch_ms


class EventRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.network_events

    def get_by_id(self, event_id: str) -> Optional[NetworkEvent]:
        doc = self.collection.find_one({"id": event_id})
        return NetworkEvent.from_doc(doc)

    def create(self, event: NetworkEvent) -> NetworkEvent:
        doc = event.to_doc()
        self.collection.update_one({"id": event.id}, {"$set": doc}, upsert=True)
        return event

    def create_batch(self, events: List[NetworkEvent]) -> List[NetworkEvent]:
        if not events:
            return []
        docs = [e.to_doc() for e in events]
        self.collection.insert_many(docs)
        return events

    def find_duplicate(
        self,
        source_ip: str,
        dest_ip: str,
        src_port: Optional[int],
        dst_port: Optional[int],
        protocol: str,
        within_ms: int = 60000,
        current_time_ms: int = 0,
    ) -> Optional[NetworkEvent]:
        window_start = current_time_ms - within_ms
        q: Dict[str, Any] = {
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "protocol": protocol,
            "timestamp": {"$gte": window_start},
        }
        if src_port is not None:
            q["src_port"] = src_port
        if dst_port is not None:
            q["dst_port"] = dst_port

        doc = self.collection.find_one(q, sort=[("timestamp", -1)])
        return NetworkEvent.from_doc(doc)

    def filter_events(
        self,
        query_str: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        range_hours: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "timestamp",
        sort_dir: str = "desc",
    ) -> Tuple[List[NetworkEvent], int, int, int]:
        q: Dict[str, Any] = {}

        if query_str and query_str.strip():
            escaped = re.escape(query_str.strip())
            q["$or"] = [
                {"source_ip": {"$regex": escaped, "$options": "i"}},
                {"dest_ip": {"$regex": escaped, "$options": "i"}},
                {"id": {"$regex": escaped, "$options": "i"}},
                {"category": {"$regex": escaped, "$options": "i"}},
            ]

        if severity and severity != "all":
            q["severity"] = severity.lower()

        if category and category != "all":
            q["category"] = category

        if status and status != "all":
            q["status"] = status.lower()

        if range_hours and range_hours > 0:
            since = hours_ago_epoch_ms(range_hours)
            q["timestamp"] = {"$gte": since}

        total_count = self.collection.count_documents(q)
        total_pages = max(1, math.ceil(total_count / page_size)) if total_count > 0 else 1
        page = max(1, min(page, total_pages))
        skip = (page - 1) * page_size

        # Field mapping for sorting
        sort_key_map = {
            "timestamp": "timestamp",
            "source_ip": "source_ip",
            "sourceIp": "source_ip",
            "dest_ip": "dest_ip",
            "destIp": "dest_ip",
            "risk_score": "risk_score",
            "riskScore": "risk_score",
            "severity": "severity",
            "category": "category",
        }
        mongo_sort_key = sort_key_map.get(sort_by, "timestamp")
        mongo_direction = 1 if sort_dir.lower() == "asc" else -1

        cursor = self.collection.find(q).sort([(mongo_sort_key, mongo_direction)]).skip(skip).limit(page_size)
        items = [NetworkEvent.from_doc(doc) for doc in cursor if doc]
        return items, total_count, total_pages, page

    def count_total(self) -> int:
        return self.collection.count_documents({})

    def count_active(self) -> int:
        return self.collection.count_documents({"status": {"$ne": "resolved"}})

    def count_critical(self) -> int:
        return self.collection.count_documents({"severity": "critical"})

    def count_suspicious(self) -> int:
        return self.collection.count_documents({"severity": {"$in": ["critical", "high", "medium"]}})

    def category_counts(self) -> List[Dict[str, Any]]:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        results = self.collection.aggregate(pipeline)
        return [{"category": r["_id"], "count": r["count"]} for r in results if r.get("_id")]

    def severity_counts(self) -> List[Dict[str, Any]]:
        pipeline = [
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        results = self.collection.aggregate(pipeline)
        return [{"severity": r["_id"], "count": r["count"]} for r in results if r.get("_id")]

    def update_status(self, event_id: str, new_status: str) -> Optional[NetworkEvent]:
        self.collection.update_one({"id": event_id}, {"$set": {"status": new_status}})
        return self.get_by_id(event_id)
