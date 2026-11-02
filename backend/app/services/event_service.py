from typing import Optional, List, Dict, Any, Tuple
from pymongo.database import Database
from app.models.network_event import NetworkEvent
from app.models.alert import Alert
from app.repositories.event_repository import EventRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.rule_repository import RuleRepository
from app.detection.rule_engine import RuleEngine
from app.detection.hybrid_engine import HybridDetectionEngine
from app.utils.time_utils import current_epoch_ms


class EventService:
    def __init__(self, db: Database):
        self.db = db
        self.event_repo = EventRepository(db)
        self.alert_repo = AlertRepository(db)
        self.rule_repo = RuleRepository(db)

        # Initialize detection engine with enabled database rules
        active_rules = self.rule_repo.list_enabled()
        self.rule_engine = RuleEngine(active_rules)
        self.hybrid_engine = HybridDetectionEngine(self.rule_engine)

    def ingest_event(
        self,
        event_dict: Dict[str, Any],
        run_detection: bool = True,
        actor: str = "ingestion",
    ) -> NetworkEvent:
        now_ms = event_dict.get("timestamp") or current_epoch_ms()
        source_ip = event_dict.get("source_ip") or event_dict.get("sourceIp", "")
        dest_ip = event_dict.get("dest_ip") or event_dict.get("destIp", "")
        src_port = event_dict.get("src_port") or event_dict.get("srcPort", 0)
        dst_port = event_dict.get("dst_port") or event_dict.get("dstPort", 0)
        protocol = event_dict.get("protocol", "TCP")

        # 1. Deduplication check within 60s
        existing_dup = self.event_repo.find_duplicate(
            source_ip=source_ip,
            dest_ip=dest_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            within_ms=60000,
            current_time_ms=now_ms,
        )
        if existing_dup:
            existing_dup.duplicates += 1
            existing_dup.timestamp = now_ms
            self.event_repo.create(existing_dup)
            return existing_dup

        # 2. Run Hybrid Detection Engine if requested
        category = event_dict.get("category", "Anomalous traffic")
        source = event_dict.get("source", "Live ingestion")
        severity = event_dict.get("severity", "low")
        risk_score = event_dict.get("risk_score") or event_dict.get("riskScore", 0)
        detection_result = None

        if run_detection:
            has_explicit_flow = bool(event_dict.get("flow_features") or event_dict.get("flowFeatures"))
            flow_feats = dict(event_dict.get("flow_features") or event_dict.get("flowFeatures", {}) or {})
            if "dst_port" not in flow_feats and dst_port and has_explicit_flow:
                flow_feats["dst_port"] = dst_port

            detection_result = self.hybrid_engine.analyze({
                "source_ip": source_ip,
                "dest_ip": dest_ip,
                "src_port": src_port,
                "dst_port": dst_port,
                "protocol": protocol,
                "timestamp": now_ms,
                "flow_features": flow_feats,
                "metadata": event_dict.get("metadata", {}),
            })
            det_score = detection_result["risk_score"]
            if risk_score > 0 and not has_explicit_flow:
                # Direct event ingestion with explicit risk score provided — keep caller values
                pass
            elif risk_score > det_score:
                # Keep explicitly provided severity and risk score
                pass
            elif det_score > 0:
                category = detection_result["predicted_category"]
                severity = detection_result["severity"]
                risk_score = det_score
                source = detection_result["detection_sources"][0] if detection_result["detection_sources"] else source

            # Record rule matches
            for r_id in detection_result.get("rule_ids", []):
                self.rule_repo.record_match(r_id, now_ms)

        # 3. Create Network Event
        import uuid
        event_id = event_dict.get("id") or f"EVT-{now_ms}-{uuid.uuid4().hex[:6]}"
        is_simulated = bool(event_dict.get("is_simulated") or event_dict.get("isSimulated") or ("SIM-" in str(event_id)))
        sensor_id = event_dict.get("sensor_id")
        data_origin = event_dict.get("data_origin")
        if not data_origin:
            data_origin = "simulated" if is_simulated else "live"

        event = NetworkEvent(
            id=event_id,
            timestamp=now_ms,
            source_ip=source_ip,
            dest_ip=dest_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            category=category,
            source=source,
            severity=severity,
            risk_score=risk_score,
            status=event_dict.get("status", "new"),
            duplicates=event_dict.get("duplicates", 0),
            event_source=event_dict.get("event_source", "collector"),
            flow_features=event_dict.get("flow_features") or event_dict.get("flowFeatures"),
            collector_metadata=event_dict.get("metadata") or event_dict.get("raw_payload"),
            ingestion_status="processed",
            is_simulated=is_simulated,
            sensor_id=sensor_id,
            data_origin=data_origin,
        )
        saved_event = self.event_repo.create(event)

        # 4. Generate Alert if high risk, risk_score >= 60, or verified anomaly (never for Benign)
        is_anomaly = bool(detection_result.get("is_anomaly")) if detection_result else False
        if (severity in ("critical", "high") or risk_score >= 60 or is_anomaly) and category != "Benign":
            recommendation = (detection_result.get("recommendation") if detection_result else None) or "Monitor and investigate host connections."
            alert = Alert(
                id=f"ALT-{saved_event.id.replace('EVT-', '')}",
                related_event_id=saved_event.id,
                timestamp=now_ms,
                category=category,
                severity=severity,
                risk_score=risk_score,
                detection_sources=detection_result["detection_sources"] if detection_result else [source],
                evidence=detection_result["evidence"] if detection_result else {},
                status="new",
                model_versions=detection_result["model_versions"] if detection_result else {},
                rule_ids=detection_result["rule_ids"] if detection_result else [],
                sensor_id=sensor_id,
                data_origin=data_origin,
                recommendation=recommendation,
            )
            self.alert_repo.create(alert)

        return saved_event

    def ingest_batch(self, events: List[Dict[str, Any]]) -> int:
        count = 0
        for ev in events:
            try:
                self.ingest_event(ev, run_detection=False)
                count += 1
            except Exception:
                continue
        return count

    def get_event(self, event_id: str) -> Optional[NetworkEvent]:
        return self.event_repo.get_by_id(event_id)

    def filter_events(
        self,
        query: Optional[str] = None,
        severity: Optional[str] = None,
        category: Optional[str] = None,
        status: Optional[str] = None,
        range_hours: Optional[int] = None,
        origin: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_by: str = "timestamp",
        sort_dir: str = "desc",
    ) -> Tuple[List[NetworkEvent], int, int, int]:
        return self.event_repo.filter_events(
            query_str=query,
            severity=severity,
            category=category,
            status=status,
            range_hours=range_hours,
            origin=origin,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

    def update_event_status(self, event_id: str, new_status: str) -> Optional[NetworkEvent]:
        return self.event_repo.update_status(event_id, new_status)
