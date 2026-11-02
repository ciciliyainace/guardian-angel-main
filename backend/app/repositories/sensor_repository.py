from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from pymongo.database import Database
from app.models.sensor import Sensor, SensorHeartbeat
from app.core.logging_config import logger


class SensorRepository:
    def __init__(self, db: Database):
        self.db = db
        self.sensors_col = db.sensors
        self.heartbeats_col = db.sensor_heartbeats

    def enroll(self, sensor: Sensor) -> Sensor:
        doc = sensor.to_doc()
        self.sensors_col.update_one(
            {"sensor_id": sensor.sensor_id},
            {"$set": doc},
            upsert=True,
        )
        return sensor

    def get_by_id(self, sensor_id: str) -> Optional[Sensor]:
        doc = self.sensors_col.find_one({"sensor_id": sensor_id})
        return Sensor.from_doc(doc) if doc else None

    def get_by_key_hash(self, key_hash: str) -> Optional[Sensor]:
        doc = self.sensors_col.find_one({"api_key_hash": key_hash, "status": "active"})
        return Sensor.from_doc(doc) if doc else None

    def record_heartbeat(
        self,
        sensor_id: str,
        heartbeat: SensorHeartbeat,
        remote_ip: Optional[str] = None,
    ) -> bool:
        now = datetime.now(timezone.utc)
        update_fields: Dict[str, Any] = {
            "last_heartbeat_at": now,
            "collector_details": heartbeat.collectors,
        }
        if remote_ip:
            update_fields["ip_address"] = remote_ip

        res = self.sensors_col.update_one(
            {"sensor_id": sensor_id, "status": "active"},
            {"$set": update_fields},
        )

        # Store heartbeat record
        self.heartbeats_col.insert_one(heartbeat.to_doc())
        return res.modified_count > 0 or res.matched_count > 0

    def record_telemetry_batch(self, sensor_id: str, count: int) -> None:
        now = datetime.now(timezone.utc)
        self.sensors_col.update_one(
            {"sensor_id": sensor_id},
            {
                "$set": {"last_telemetry_at": now},
                "$inc": {"total_events_ingested": count},
            },
        )

    def revoke(self, sensor_id: str, revoked_by: str) -> bool:
        now = datetime.now(timezone.utc)
        res = self.sensors_col.update_one(
            {"sensor_id": sensor_id},
            {
                "$set": {
                    "status": "revoked",
                    "revoked_at": now,
                    "revoked_by": revoked_by,
                }
            },
        )
        return res.modified_count > 0

    def list_sensors(self) -> List[Sensor]:
        cursor = self.sensors_col.find({}).sort("created_at", -1)
        return [Sensor.from_doc(d) for d in cursor if d]

    def get_active_sensors(self, timeout_sec: int = 60) -> List[Sensor]:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout_sec)
        cursor = self.sensors_col.find({
            "status": "active",
            "last_heartbeat_at": {"$gte": cutoff},
        })
        return [Sensor.from_doc(d) for d in cursor if d]

    def get_monitoring_state(self, timeout_sec: int = 60) -> Dict[str, Any]:
        """
        Calculates the definitive monitoring state based on actual registered sensors and recent telemetry.
        LIVE: Active sensor connected with heartbeat <= timeout_sec AND telemetry received in last 5 minutes.
        STANDBY: Active sensor connected with heartbeat <= timeout_sec, waiting for new telemetry.
        NO_LIVE_SENSOR: No active sensors with recent heartbeat.
        """
        active_sensors = self.get_active_sensors(timeout_sec=timeout_sec)
        if not active_sensors:
            return {
                "overall_status": "NO_LIVE_SENSOR",
                "is_live": False,
                "active_sensor_count": 0,
                "active_sensors": [],
                "suricata_operational": False,
                "windows_socket_operational": False,
                "message": "No live sensor connected — waiting for network telemetry.",
            }

        # Check if telemetry was received recently (within 10 minutes)
        five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        has_recent_telemetry = any(
            s.last_telemetry_at and s.last_telemetry_at.replace(tzinfo=timezone.utc) >= five_min_ago
            for s in active_sensors
        )

        suricata_op = any(
            s.collector_details.get("suricata") == "operational" for s in active_sensors
        )
        windows_op = any(
            s.collector_details.get("windows_sockets") in ("operational", "active")
            for s in active_sensors
        )

        overall = "LIVE" if has_recent_telemetry else "STANDBY"
        message = (
            f"Live network monitoring active across {len(active_sensors)} host sensor(s)."
            if overall == "LIVE"
            else f"{len(active_sensors)} sensor(s) connected in standby — listening for host network flows."
        )

        return {
            "overall_status": overall,
            "is_live": overall == "LIVE",
            "active_sensor_count": len(active_sensors),
            "active_sensors": [s.sensor_id for s in active_sensors],
            "suricata_operational": suricata_op,
            "windows_socket_operational": windows_op,
            "message": message,
        }

