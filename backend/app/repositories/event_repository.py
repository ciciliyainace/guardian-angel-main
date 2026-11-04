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
        from pymongo import UpdateOne
        ops = [UpdateOne({"id": e.id}, {"$set": e.to_doc()}, upsert=True) for e in events]
        self.collection.bulk_write(ops, ordered=False)
        return events

    def bulk_upsert_events(self, events: List[NetworkEvent]) -> int:
        """
        Durable, idempotent bulk upsert of network events in a single network round-trip.
        Safely handles new inserts, duplicate updates, and retries without duplicate key errors.
        """
        if not events:
            return 0
        from pymongo import UpdateOne
        ops = [UpdateOne({"id": e.id}, {"$set": e.to_doc()}, upsert=True) for e in events]
        try:
            res = self.collection.bulk_write(ops, ordered=False)
            return (res.upserted_count or 0) + (res.modified_count or 0)
        except TypeError:
            count = 0
            for e in events:
                self.create(e)
                count += 1
            return count

    def find_duplicates_batch(
        self,
        candidate_keys: List[Tuple[str, str, Optional[int], Optional[int], str]],
        min_timestamp_ms: int,
    ) -> Dict[Tuple[str, str, Optional[int], Optional[int], str], NetworkEvent]:
        """
        Bulk query to identify existing duplicate flows for an entire batch in a single round-trip.
        Returns a dict mapping (source_ip, dest_ip, src_port, dst_port, protocol) to the latest NetworkEvent.
        """
        if not candidate_keys:
            return {}

        unique_keys = list(set(candidate_keys))
        or_clauses = []
        for s_ip, d_ip, s_p, d_p, proto in unique_keys:
            clause: Dict[str, Any] = {
                "source_ip": s_ip,
                "dest_ip": d_ip,
                "protocol": proto,
            }
            if s_p is not None:
                clause["src_port"] = s_p
            if d_p is not None:
                clause["dst_port"] = d_p
            or_clauses.append(clause)

        if not or_clauses:
            return {}

        query = {
            "$or": or_clauses,
            "timestamp": {"$gte": min_timestamp_ms},
        }

        duplicates_map: Dict[Tuple[str, str, Optional[int], Optional[int], str], NetworkEvent] = {}
        cursor = self.collection.find(query).sort("timestamp", -1)
        for doc in cursor:
            ev = NetworkEvent.from_doc(doc)
            if ev:
                key = (ev.source_ip, ev.dest_ip, ev.src_port, ev.dst_port, ev.protocol)
                if key not in duplicates_map:
                    duplicates_map[key] = ev

        return duplicates_map

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
        origin: Optional[str] = None,
        workspace_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "timestamp",
        sort_dir: str = "desc",
    ) -> Tuple[List[NetworkEvent], int, int, int]:
        q: Dict[str, Any] = {}

        if workspace_id:
            q["workspace_id"] = workspace_id

        if origin and origin != "all":
            if origin == "live":
                q["$or"] = [{"data_origin": "live"}, {"is_simulated": False}]
            elif origin == "simulated":
                q["$or"] = [{"data_origin": "simulated"}, {"is_simulated": True}]

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

    def _build_origin_filter(
        self,
        data_origin: Optional[str] = None,
        since_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        q: Dict[str, Any] = {}
        if workspace_id:
            q["workspace_id"] = workspace_id
        if data_origin and data_origin != "all":
            if data_origin == "live":
                q["$or"] = [{"data_origin": "live"}, {"is_simulated": False}]
            elif data_origin == "simulated":
                q["$or"] = [{"data_origin": "simulated"}, {"is_simulated": True}]
        if since_ms and since_ms > 0:
            q["timestamp"] = {"$gte": since_ms}
        return q

    def count_total(
        self,
        data_origin: Optional[str] = None,
        since_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> int:
        q = self._build_origin_filter(data_origin, since_ms, workspace_id)
        return self.collection.count_documents(q)

    def count_active(
        self,
        data_origin: Optional[str] = None,
        since_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> int:
        q = self._build_origin_filter(data_origin, since_ms, workspace_id)
        q["status"] = {"$ne": "resolved"}
        return self.collection.count_documents(q)

    def count_critical(
        self,
        data_origin: Optional[str] = None,
        since_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> int:
        q = self._build_origin_filter(data_origin, since_ms, workspace_id)
        q["severity"] = "critical"
        return self.collection.count_documents(q)

    def count_suspicious(
        self,
        data_origin: Optional[str] = None,
        since_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> int:
        q = self._build_origin_filter(data_origin, since_ms, workspace_id)
        q["severity"] = {"$in": ["critical", "high", "medium"]}
        return self.collection.count_documents(q)

    def category_counts(
        self,
        data_origin: Optional[str] = None,
        since_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        match_q = self._build_origin_filter(data_origin, since_ms, workspace_id)
        pipeline = []
        if match_q:
            pipeline.append({"$match": match_q})
        pipeline.extend([
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ])
        results = self.collection.aggregate(pipeline)
        return [{"category": r["_id"], "count": r["count"]} for r in results if r.get("_id")]

    def severity_counts(
        self,
        data_origin: Optional[str] = None,
        since_ms: Optional[int] = None,
        workspace_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        match_q = self._build_origin_filter(data_origin, since_ms, workspace_id)
        pipeline = []
        if match_q:
            pipeline.append({"$match": match_q})
        pipeline.extend([
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ])
        results = self.collection.aggregate(pipeline)
        return [{"severity": r["_id"], "count": r["count"]} for r in results if r.get("_id")]

    def update_status(self, event_id: str, new_status: str) -> Optional[NetworkEvent]:
        self.collection.update_one({"id": event_id}, {"$set": {"status": new_status}})
        return self.get_by_id(event_id)
