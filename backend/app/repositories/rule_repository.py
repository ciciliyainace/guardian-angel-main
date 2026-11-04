import time
from typing import Optional, List, Dict, Any, Tuple
from pymongo.database import Database
from pymongo import UpdateOne
from app.models.detection_rule import DetectionRule


class RuleRepository:
    _cached_enabled_rules: Optional[List[DetectionRule]] = None
    _cached_enabled_expiry: float = 0.0

    def __init__(self, db: Database):
        self.db = db
        self.collection = db.detection_rules

    def get_by_id(self, rule_id: str) -> Optional[DetectionRule]:
        doc = self.collection.find_one({"id": rule_id})
        return DetectionRule.from_doc(doc)

    def list_all(self) -> List[DetectionRule]:
        cursor = self.collection.find().sort([("id", 1)])
        return [DetectionRule.from_doc(doc) for doc in cursor if doc]

    def list_enabled(self) -> List[DetectionRule]:
        now = time.time()
        if RuleRepository._cached_enabled_rules is not None and now < RuleRepository._cached_enabled_expiry:
            return RuleRepository._cached_enabled_rules

        cursor = self.collection.find({"enabled": True})
        rules = [DetectionRule.from_doc(doc) for doc in cursor if doc]
        RuleRepository._cached_enabled_rules = rules
        RuleRepository._cached_enabled_expiry = now + 30.0  # 30-second TTL
        return rules

    @classmethod
    def invalidate_cache(cls):
        cls._cached_enabled_rules = None
        cls._cached_enabled_expiry = 0.0

    def create(self, rule: DetectionRule) -> DetectionRule:
        RuleRepository.invalidate_cache()
        doc = rule.to_doc()
        self.collection.update_one({"id": rule.id}, {"$set": doc}, upsert=True)
        return rule

    def update(self, rule: DetectionRule) -> DetectionRule:
        RuleRepository.invalidate_cache()
        doc = rule.to_doc()
        self.collection.update_one({"id": rule.id}, {"$set": doc})
        return rule

    def delete(self, rule_id: str) -> bool:
        RuleRepository.invalidate_cache()
        res = self.collection.delete_one({"id": rule_id})
        return res.deleted_count > 0

    def record_match(self, rule_id: str, timestamp_ms: int):
        self.collection.update_one(
            {"id": rule_id},
            {
                "$inc": {"matches": 1},
                "$set": {"last_triggered": timestamp_ms},
            },
        )

    def record_matches_bulk(self, matches_map: Dict[str, Tuple[int, int]]):
        """
        Record multiple rule matches in a single network round-trip.
        matches_map: {rule_id: (match_count, max_timestamp_ms)}
        """
        if not matches_map:
            return
        ops = [
            UpdateOne(
                {"id": r_id},
                {
                    "$inc": {"matches": count},
                    "$set": {"last_triggered": max_ts},
                },
            )
            for r_id, (count, max_ts) in matches_map.items()
        ]
        try:
            self.collection.bulk_write(ops, ordered=False)
        except TypeError:
            for r_id, (count, max_ts) in matches_map.items():
                self.collection.update_one(
                    {"id": r_id},
                    {
                        "$inc": {"matches": count},
                        "$set": {"last_triggered": max_ts},
                    },
                )
