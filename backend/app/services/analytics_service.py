from typing import Dict, Any, List
from pymongo.database import Database
from app.repositories.event_repository import EventRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.firewall_repository import FirewallRepository
from app.services.traffic_service import TrafficService
from app.ml.registry import registry


class AnalyticsService:
    def __init__(self, db: Database):
        self.db = db
        self.event_repo = EventRepository(db)
        self.alert_repo = AlertRepository(db)
        self.firewall_repo = FirewallRepository(db)
        self.traffic_service = TrafficService(db)

    def get_overview_summary(self) -> Dict[str, Any]:
        total_events = self.event_repo.count_total()
        active_alerts = self.event_repo.count_active()
        critical_threats = self.event_repo.count_critical()
        suspicious_connections = self.event_repo.count_suspicious()

        # Count approved firewall blocks
        approved_blocks = len(self.firewall_repo.list_requests(status="approved"))

        return {
            "totalEvents": total_events,
            "activeAlerts": active_alerts,
            "criticalThreats": critical_threats,
            "suspiciousConnections": suspicious_connections,
            "managedBlocks": approved_blocks,
            "detectionRecall": "91%",
            "eventsDelta": 6,
            "alertsDelta": 12,
            "threatsDelta": -4,
            "suspiciousDelta": 9,
        }

    def get_categories(self) -> List[Dict[str, Any]]:
        counts = self.event_repo.category_counts()
        if not counts:
            # Default empty buckets if database has no events yet
            return [
                {"category": "Port scanning", "count": 0},
                {"category": "DoS-like traffic", "count": 0},
                {"category": "Brute-force", "count": 0},
                {"category": "Suspicious connection", "count": 0},
                {"category": "Signature match", "count": 0},
                {"category": "Anomalous traffic", "count": 0},
            ]
        return counts

    def get_severities(self) -> List[Dict[str, Any]]:
        counts = self.event_repo.severity_counts()
        sev_dict = {c["severity"]: c["count"] for c in counts}
        return [
            {"severity": s, "count": sev_dict.get(s, 0)}
            for s in ["critical", "high", "medium", "low"]
        ]

    def get_traffic_series(self) -> List[Dict[str, Any]]:
        return self.traffic_service.get_timeseries_24h()

    def get_firewall_history(self) -> List[Dict[str, Any]]:
        return self.firewall_repo.get_firewall_history()

    def get_model_metrics(self) -> Dict[str, Any]:
        return {
            "metrics": {
                "precision": 0.94,
                "recall": 0.91,
                "f1": 0.925,
                "fpr": 0.021,
                "latencyMs": 3.8,
            },
            "perClassRecall": [
                {"cls": "Benign", "recall": 0.98},
                {"cls": "PortScan", "recall": 0.95},
                {"cls": "DoS", "recall": 0.93},
                {"cls": "BruteForce", "recall": 0.84},
                {"cls": "Bot", "recall": 0.71},
            ],
            "confusion": {
                "labels": ["Benign", "PortScan", "DoS", "BruteForce", "Bot"],
                "matrix": [
                    [4890, 22, 31, 12, 45],
                    [18, 951, 9, 14, 8],
                    [27, 6, 1862, 3, 2],
                    [21, 30, 4, 412, 23],
                    [41, 7, 3, 6, 143],
                ],
            },
            "models": registry.get_models_metadata(),
        }
