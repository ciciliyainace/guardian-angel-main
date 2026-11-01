import io
import csv
from typing import Dict, Any, List
from pymongo.database import Database
from app.repositories.event_repository import EventRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.firewall_repository import FirewallRepository
from app.repositories.audit_repository import AuditRepository


class ReportService:
    def __init__(self, db: Database):
        self.db = db
        self.event_repo = EventRepository(db)
        self.alert_repo = AlertRepository(db)
        self.firewall_repo = FirewallRepository(db)
        self.audit_repo = AuditRepository(db)

    def generate_summary(self) -> Dict[str, Any]:
        total_events = self.event_repo.count_total()
        active_alerts = self.event_repo.count_active()
        critical_threats = self.event_repo.count_critical()
        blocks = self.firewall_repo.list_requests(status="approved")

        return {
            "title": "SentinelAI SOC Executive Security Report",
            "period": "Last 24 Hours",
            "total_events_analyzed": total_events,
            "active_alerts": active_alerts,
            "critical_threats_blocked": len(blocks),
            "threat_distribution": self.event_repo.category_counts(),
            "severity_distribution": self.event_repo.severity_counts(),
            "status": "Healthy — Defense Active",
        }

    def export_events_csv(self, limit: int = 1000) -> str:
        events, _, _, _ = self.event_repo.filter_events(page=1, page_size=limit)
        output = io.StringIO()
        writer = csv.writer(output)

        # Header matching frontend CSV export
        writer.writerow([
            "ID", "Timestamp", "Source IP", "Destination IP", "Src Port",
            "Dst Port", "Protocol", "Category", "Source", "Severity", "Risk Score", "Status"
        ])

        for ev in events:
            writer.writerow([
                ev.id, ev.timestamp, ev.source_ip, ev.dest_ip, ev.src_port or 0,
                ev.dst_port or 0, ev.protocol, ev.category, ev.source, ev.severity,
                ev.risk_score, ev.status
            ])

        return output.getvalue()
