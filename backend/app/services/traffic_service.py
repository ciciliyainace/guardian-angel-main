from typing import List, Dict, Any
from pymongo.database import Database
from app.utils.time_utils import hours_ago_epoch_ms, epoch_ms_to_datetime


class TrafficService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.network_events

    def get_timeseries_24h(self) -> List[Dict[str, Any]]:
        """
        Aggregate events from the last 24 hours into 24 hourly buckets
        formatted as: [{ time: "HH:00", benign: int, suspicious: int, total: int }, ...]
        """
        since_ms = hours_ago_epoch_ms(24)
        cursor = self.collection.find(
            {"timestamp": {"$gte": since_ms}},
            {"timestamp": 1, "severity": 1, "_id": 0},
        )

        buckets: Dict[int, Dict[str, int]] = {
            h: {"benign": 0, "suspicious": 0} for h in range(24)
        }

        for doc in cursor:
            ts = doc.get("timestamp", 0)
            sev = doc.get("severity", "low")
            dt = epoch_ms_to_datetime(ts)
            hour = dt.hour
            if sev in ("critical", "high", "medium"):
                buckets[hour]["suspicious"] += 1
            else:
                buckets[hour]["benign"] += 1

        series = []
        for h in range(24):
            benign = buckets[h]["benign"]
            suspicious = buckets[h]["suspicious"]
            series.append({
                "time": f"{h:02d}:00",
                "benign": benign,
                "suspicious": suspicious,
                "total": benign + suspicious,
            })

        return series

    def get_summary(self) -> Dict[str, Any]:
        series = self.get_timeseries_24h()
        total = sum(p["total"] for p in series)
        benign = sum(p["benign"] for p in series)
        suspicious = total - benign
        return {
            "total_flow_count": total,
            "benign_flow_count": benign,
            "suspicious_flow_count": suspicious,
            "series": series,
        }
