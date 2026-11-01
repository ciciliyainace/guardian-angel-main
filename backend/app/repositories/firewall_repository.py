from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pymongo.database import Database
from app.models.firewall_request import FirewallRequest
from app.models.firewall_action import FirewallAction


class FirewallRepository:
    def __init__(self, db: Database):
        self.db = db
        self.requests_coll = db.firewall_requests
        self.actions_coll = db.firewall_actions

    def get_request_by_id(self, request_id: str) -> Optional[FirewallRequest]:
        doc = self.requests_coll.find_one({"id": request_id})
        return FirewallRequest.from_doc(doc)

    def list_requests(self, status: Optional[str] = None) -> List[FirewallRequest]:
        q: Dict[str, Any] = {}
        if status and status != "all":
            q["status"] = status.lower()
        cursor = self.requests_coll.find(q).sort([("requested_at", -1)])
        return [FirewallRequest.from_doc(doc) for doc in cursor if doc]

    def create_request(self, req: FirewallRequest) -> FirewallRequest:
        doc = req.to_doc()
        self.requests_coll.update_one({"id": req.id}, {"$set": doc}, upsert=True)
        return req

    def update_request(self, req: FirewallRequest) -> FirewallRequest:
        doc = req.to_doc()
        self.requests_coll.update_one({"id": req.id}, {"$set": doc})
        return req

    def get_action_by_id(self, action_id: str) -> Optional[FirewallAction]:
        doc = self.actions_coll.find_one({"id": action_id})
        return FirewallAction.from_doc(doc)

    def get_action_by_rule_name(self, rule_name: str) -> Optional[FirewallAction]:
        doc = self.actions_coll.find_one({"managed_rule_name": rule_name})
        return FirewallAction.from_doc(doc)

    def list_actions(self, status: Optional[str] = None) -> List[FirewallAction]:
        q: Dict[str, Any] = {}
        if status and status != "all":
            q["status"] = status.lower()
        cursor = self.actions_coll.find(q).sort([("created_at", -1)])
        return [FirewallAction.from_doc(doc) for doc in cursor if doc]

    def list_active_actions(self) -> List[FirewallAction]:
        cursor = self.actions_coll.find({"status": {"$in": ["created", "verified"]}})
        return [FirewallAction.from_doc(doc) for doc in cursor if doc]

    def list_expired_actions(self) -> List[FirewallAction]:
        now = datetime.now(timezone.utc)
        cursor = self.actions_coll.find({
            "status": {"$in": ["created", "verified"]},
            "expires_at": {"$lte": now},
        })
        return [FirewallAction.from_doc(doc) for doc in cursor if doc]

    def create_action(self, action: FirewallAction) -> FirewallAction:
        doc = action.to_doc()
        self.actions_coll.update_one({"id": action.id}, {"$set": doc}, upsert=True)
        return action

    def update_action(self, action: FirewallAction) -> FirewallAction:
        doc = action.to_doc()
        self.actions_coll.update_one({"id": action.id}, {"$set": doc})
        return action

    def get_firewall_history(self) -> List[Dict[str, Any]]:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        approved = self.requests_coll.count_documents({"status": "approved"})
        rejected = self.requests_coll.count_documents({"status": "rejected"})
        expired = self.requests_coll.count_documents({"status": "expired"})

        history = []
        for i, day in enumerate(days):
            history.append({
                "day": day,
                "approved": max(0, int(approved * ((i + 1) / 7.0))),
                "rejected": max(0, int(rejected * ((7 - i) / 7.0))),
                "expired": max(0, int(expired * (0.5 if i % 2 == 0 else 0.8))),
            })
        return history
