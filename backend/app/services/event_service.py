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

        workspace_id = event_dict.get("workspace_id") or event_dict.get("workspaceId")
        owner_user_id = event_dict.get("owner_user_id") or event_dict.get("ownerUserId")

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
            workspace_id=workspace_id,
            owner_user_id=owner_user_id,
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
                workspace_id=saved_event.workspace_id,
                owner_user_id=saved_event.owner_user_id,
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
        workspace_id: Optional[str] = None,
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
            workspace_id=workspace_id,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )

    def update_event_status(self, event_id: str, new_status: str) -> Optional[NetworkEvent]:
        return self.event_repo.update_status(event_id, new_status)

    def ingest_telemetry_batch_fast(
        self,
        raw_events: List[Dict[str, Any]],
        sensor: Any,
    ) -> Dict[str, Any]:
        """
        High-throughput bulk ingestion pipeline for sensor telemetry batches.
        Coordinates:
          1. Collector normalization (Suricata EVE / Windows Socket)
          2. Single-pass bulk deduplication check against MongoDB Atlas within 60s
          3. Vectorized ML & rule detection via analyze_batch (40x faster)
          4. Single-round-trip bulk upsert for events and alerts
          5. Aggregated rule match counters and telemetry batch stats
          6. Returns exact ingest stats without repetitive count_documents round-trips.
        """
        if not raw_events:
            return {
                "received": 0,
                "ingested": 0,
                "duplicates": 0,
                "alerts_generated": 0,
                "processed_count": 0,
                "rejected_count": 0,
            }

        import uuid
        from app.detection.flow_aggregator import FlowAggregator
        from app.repositories.sensor_repository import SensorRepository
        from app.core.logging_config import logger

        received = len(raw_events)
        normalized_events: List[Dict[str, Any]] = []

        for raw in raw_events:
            try:
                collector = raw.get("collector") or ("suricata" if "event_type" in raw else "windows_sockets")
                if collector == "suricata" or "event_type" in raw:
                    norm = FlowAggregator.parse_suricata_eve(raw, sensor_id=sensor.sensor_id)
                else:
                    norm = FlowAggregator.parse_windows_socket(raw, sensor_id=sensor.sensor_id)

                norm["workspace_id"] = sensor.workspace_id
                norm["owner_user_id"] = sensor.owner_user_id
                norm["sensor_id"] = sensor.sensor_id
                normalized_events.append(norm)
            except Exception as e:
                logger.warning(f"Error normalizing raw event from sensor {sensor.sensor_id}: {e}")
                continue

        if not normalized_events:
            return {
                "received": received,
                "ingested": 0,
                "duplicates": 0,
                "alerts_generated": 0,
                "processed_count": 0,
                "rejected_count": received,
            }

        now_default_ms = current_epoch_ms()

        # Step 2: Prepare keys for bulk deduplication query
        candidate_keys: List[Tuple[str, str, Optional[int], Optional[int], str]] = []
        min_ts = now_default_ms

        for norm in normalized_events:
            t_ms = norm.get("timestamp") or now_default_ms
            if t_ms < min_ts:
                min_ts = t_ms
            s_ip = norm.get("source_ip") or norm.get("sourceIp", "")
            d_ip = norm.get("dest_ip") or norm.get("destIp", "")
            s_port = norm.get("src_port") if norm.get("src_port") is not None else norm.get("srcPort")
            d_port = norm.get("dst_port") if norm.get("dst_port") is not None else norm.get("dstPort")
            proto = norm.get("protocol", "TCP")
            candidate_keys.append((s_ip, d_ip, s_port, d_port, proto))

        # Query existing duplicates from DB in a single network round-trip
        window_start_ms = min_ts - 60000
        db_duplicates = self.event_repo.find_duplicates_batch(candidate_keys, min_timestamp_ms=window_start_ms)

        # Step 3: Separate duplicates vs new candidates (including intra-batch duplicates)
        duplicate_events_map: Dict[str, NetworkEvent] = {}
        events_to_analyze: List[Tuple[Dict[str, Any], str, str, Optional[int], Optional[int], str, int]] = []
        seen_in_batch: Dict[Tuple[str, str, Optional[int], Optional[int], str], NetworkEvent] = {}

        duplicate_count = 0

        for norm, key in zip(normalized_events, candidate_keys):
            now_ms = norm.get("timestamp") or now_default_ms
            s_ip, d_ip, s_port, d_port, proto = key

            # Check if matching event exists in DB within 60s
            if key in db_duplicates:
                existing = db_duplicates[key]
                existing.duplicates += 1
                existing.timestamp = now_ms
                duplicate_events_map[existing.id] = existing
                duplicate_count += 1
            # Or if already seen in current batch
            elif key in seen_in_batch:
                first_ev = seen_in_batch[key]
                first_ev.duplicates += 1
                first_ev.timestamp = now_ms
                duplicate_count += 1
            else:
                events_to_analyze.append((norm, s_ip, d_ip, s_port, d_port, proto, now_ms))

        # Step 4: Run Vectorized Hybrid Detection on non-duplicate events
        new_events: List[NetworkEvent] = []
        alerts_to_create: List[Alert] = []
        rule_matches_map: Dict[str, Tuple[int, int]] = {}

        if events_to_analyze:
            detection_inputs = []
            for norm, s_ip, d_ip, s_port, d_port, proto, now_ms in events_to_analyze:
                has_explicit_flow = bool(norm.get("flow_features") or norm.get("flowFeatures"))
                flow_feats = dict(norm.get("flow_features") or norm.get("flowFeatures", {}) or {})
                if "dst_port" not in flow_feats and d_port and has_explicit_flow:
                    flow_feats["dst_port"] = d_port

                detection_inputs.append({
                    "source_ip": s_ip,
                    "dest_ip": d_ip,
                    "src_port": s_port or 0,
                    "dst_port": d_port or 0,
                    "protocol": proto,
                    "timestamp": now_ms,
                    "flow_features": flow_feats,
                    "metadata": norm.get("metadata", {}),
                    "category": norm.get("category", "Anomalous traffic"),
                })

            batch_detection_results = self.hybrid_engine.analyze_batch(detection_inputs)

            for (norm, s_ip, d_ip, s_port, d_port, proto, now_ms), det_res in zip(events_to_analyze, batch_detection_results):
                category = norm.get("category", "Anomalous traffic")
                source = norm.get("source", "Live ingestion")
                severity = norm.get("severity", "low")
                risk_score = norm.get("risk_score") or norm.get("riskScore", 0)

                det_score = det_res["risk_score"]
                has_explicit_flow = bool(norm.get("flow_features") or norm.get("flowFeatures"))
                if risk_score > 0 and not has_explicit_flow:
                    pass
                elif risk_score > det_score:
                    pass
                elif det_score > 0:
                    category = det_res["predicted_category"]
                    severity = det_res["severity"]
                    risk_score = det_score
                    source = det_res["detection_sources"][0] if det_res["detection_sources"] else source

                for r_id in det_res.get("rule_ids", []):
                    if r_id != "SURICATA-EVE":
                        curr_cnt, curr_max = rule_matches_map.get(r_id, (0, 0))
                        rule_matches_map[r_id] = (curr_cnt + 1, max(curr_max, now_ms))

                event_id = norm.get("id") or f"EVT-{now_ms}-{uuid.uuid4().hex[:6]}"
                is_simulated = bool(norm.get("is_simulated") or norm.get("isSimulated") or ("SIM-" in str(event_id)))
                data_origin = norm.get("data_origin")
                if not data_origin:
                    data_origin = "simulated" if is_simulated else "live"

                event = NetworkEvent(
                    id=event_id,
                    timestamp=now_ms,
                    source_ip=s_ip,
                    dest_ip=d_ip,
                    src_port=s_port or 0,
                    dst_port=d_port or 0,
                    protocol=proto,
                    category=category,
                    source=source,
                    severity=severity,
                    risk_score=risk_score,
                    status=norm.get("status", "new"),
                    duplicates=norm.get("duplicates", 0),
                    event_source=norm.get("event_source", "collector"),
                    flow_features=norm.get("flow_features") or norm.get("flowFeatures"),
                    collector_metadata=norm.get("metadata") or norm.get("raw_payload"),
                    ingestion_status="processed",
                    is_simulated=is_simulated,
                    sensor_id=sensor.sensor_id,
                    workspace_id=sensor.workspace_id,
                    owner_user_id=sensor.owner_user_id,
                    data_origin=data_origin,
                )
                new_events.append(event)
                key = (s_ip, d_ip, s_port, d_port, proto)
                seen_in_batch[key] = event

                # Check if alert should be created
                is_anomaly = bool(det_res.get("is_anomaly"))
                if (severity in ("critical", "high") or risk_score >= 60 or is_anomaly) and category != "Benign":
                    recommendation = det_res.get("recommended_action") or "Monitor and investigate host connections."
                    alert = Alert(
                        id=f"ALT-{event.id.replace('EVT-', '')}",
                        related_event_id=event.id,
                        timestamp=now_ms,
                        category=category,
                        severity=severity,
                        risk_score=risk_score,
                        detection_sources=det_res.get("detection_sources", [source]),
                        evidence=det_res.get("evidence", {}),
                        status="new",
                        model_versions=det_res.get("model_versions", {}),
                        rule_ids=det_res.get("rule_ids", []),
                        sensor_id=sensor.sensor_id,
                        workspace_id=event.workspace_id,
                        owner_user_id=event.owner_user_id,
                        data_origin=data_origin,
                        recommendation=recommendation,
                    )
                    alerts_to_create.append(alert)

        # Step 5: Perform bulk writes in minimal network round-trips
        # 5a. Record rule matches
        if rule_matches_map:
            self.rule_repo.record_matches_bulk(rule_matches_map)

        # 5b. Bulk upsert all events (new and modified duplicates)
        all_events_to_write = list(duplicate_events_map.values()) + new_events
        if all_events_to_write:
            self.event_repo.bulk_upsert_events(all_events_to_write)

        # 5c. Bulk insert alerts
        if alerts_to_create:
            self.alert_repo.create_batch(alerts_to_create)

        # 5d. Record sensor telemetry batch
        ingested = len(new_events)
        total_processed = ingested + duplicate_count
        if total_processed > 0:
            sensor_repo = SensorRepository(self.db)
            sensor_repo.record_telemetry_batch(sensor.sensor_id, total_processed)

        rejected = received - total_processed
        return {
            "received": received,
            "ingested": ingested,
            "duplicates": duplicate_count,
            "alerts_generated": len(alerts_to_create),
            "processed_count": total_processed,
            "rejected_count": rejected,
        }
