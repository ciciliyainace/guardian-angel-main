from typing import Dict, Any, List
from pymongo.database import Database
from app.repositories.rule_repository import RuleRepository
from app.detection.rule_engine import RuleEngine
from app.detection.hybrid_engine import HybridDetectionEngine
from app.ml.registry import registry


class DetectionService:
    def __init__(self, db: Database):
        self.db = db
        self.rule_repo = RuleRepository(db)
        active_rules = self.rule_repo.list_enabled()
        self.rule_engine = RuleEngine(active_rules)
        self.hybrid_engine = HybridDetectionEngine(self.rule_engine)

    def analyze_event(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input and run hybrid correlation engine."""
        return self.hybrid_engine.analyze(data)

    def get_status(self) -> Dict[str, Any]:
        active_rules = self.rule_repo.list_enabled()
        loaded_count = sum(
            1 for m in (registry.rf, registry.dt, registry.iforest) if m.is_loaded
        )
        return {
            "rule_engine_status": "Operational" if len(active_rules) > 0 else "Degraded",
            "rf_status": "Operational" if registry.rf.is_loaded else "Not Loaded",
            "if_status": "Operational" if registry.iforest.is_loaded else "Not Loaded",
            "hybrid_status": "Operational",
            "active_rules_count": len(active_rules),
            "loaded_models_count": loaded_count,
        }

    def list_rules(self) -> List[Any]:
        return self.rule_repo.list_all()
