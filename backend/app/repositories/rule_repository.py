from typing import Optional, List
from pymongo.database import Database
from app.models.detection_rule import DetectionRule


class RuleRepository:
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
        cursor = self.collection.find({"enabled": True})
        return [DetectionRule.from_doc(doc) for doc in cursor if doc]

    def create(self, rule: DetectionRule) -> DetectionRule:
        doc = rule.to_doc()
        self.collection.update_one({"id": rule.id}, {"$set": doc}, upsert=True)
        return rule

    def update(self, rule: DetectionRule) -> DetectionRule:
        doc = rule.to_doc()
        self.collection.update_one({"id": rule.id}, {"$set": doc})
        return rule

    def delete(self, rule_id: str) -> bool:
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
