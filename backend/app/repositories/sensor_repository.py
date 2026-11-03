from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from pymongo.database import Database
from pymongo import ReturnDocument
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
        doc = self.sensors_col.find_one({"sensor_id": str(sensor_id)})
        return Sensor.from_doc(doc) if doc else None

    def get_by_key_hash(self, key_hash: str) -> Optional[Sensor]:
        """Lookup active or registered sensor by its persistent sensor API token or key hash."""
        doc = self.sensors_col.find_one({
            "$or": [
                {"sensor_token_hash": key_hash},
                {"api_key_hash": key_hash},
            ],
            "status": {"$ne": "revoked"},
        })
        return Sensor.from_doc(doc) if doc else None

    def get_by_enrollment_credential_hash(self, credential_hash: str) -> Optional[Sensor]:
        """Lookup sensor with a matching pending or active enrollment credential."""
        doc = self.sensors_col.find_one({
            "$or": [
                {"enrollment_credential_hash": credential_hash},
                {"api_key_hash": credential_hash},
            ],
            "status": {"$ne": "revoked"},
        })
        return Sensor.from_doc(doc) if doc else None

    def consume_enrollment_and_activate(
        self,
        sensor_id: str,
        sensor_token_hash: str,
        host_info: Optional[Dict[str, Any]] = None,
        remote_ip: Optional[str] = None,
    ) -> Optional[Sensor]:
        """
        Atomically consumes the one-time enrollment credential, records the long-lived
        sensor token hash, activates the sensor to 'registered', and stores host details.
        """
        now = datetime.now(timezone.utc)
        host_info = host_info or {}

        update_set: Dict[str, Any] = {
            "status": "registered",
            "api_key_hash": sensor_token_hash,
            "sensor_token_hash": sensor_token_hash,
            "enrollment_credential_consumed": True,
            "enrollment_credential_consumed_at": now,
            "enrollment_credential_hash": None,
            "enrolled_at": now,
            "updated_at": now,
            "collector_details": host_info,
        }

        if host_info.get("machine_name"):
            update_set["hostname"] = host_info.get("machine_name")
        if remote_ip:
            update_set["ip_address"] = remote_ip
        if host_info.get("agent_version"):
            update_set["agent_version"] = host_info.get("agent_version")

        doc = self.sensors_col.find_one_and_update(
            {"sensor_id": str(sensor_id)},
            {"$set": update_set},
            return_document=ReturnDocument.AFTER,
        )
        return Sensor.from_doc(doc) if doc else None

    def rotate_enrollment_credential(
        self,
        sensor_id: str,
        new_credential_hash: str,
        expires_at: datetime,
    ) -> Optional[Sensor]:
        """Regenerate a one-time enrollment credential for an existing sensor identity."""
        now = datetime.now(timezone.utc)
        doc = self.sensors_col.find_one_and_update(
            {"sensor_id": str(sensor_id)},
            {
                "$set": {
                    "enrollment_credential_hash": new_credential_hash,
                    "api_key_hash": new_credential_hash,
                    "enrollment_credential_expires_at": expires_at,
                    "enrollment_credential_consumed": False,
                    "enrollment_credential_consumed_at": None,
                    "status": "pending_enrollment",
                    "updated_at": now,
                }
            },
            return_document=ReturnDocument.AFTER,
        )
        return Sensor.from_doc(doc) if doc else None

    def record_heartbeat(
        self,
        sensor_id: str,
        heartbeat: SensorHeartbeat,
        remote_ip: Optional[str] = None,
    ) -> bool:
        """Record periodic heartbeat from an authenticated sensor agent."""
        now = datetime.now(timezone.utc)
        update_fields: Dict[str, Any] = {
            "last_heartbeat_at": now,
            "status": "online",
        }
        if remote_ip:
            update_fields["ip_address"] = remote_ip
        if heartbeat.collectors:
            update_fields["collector_details"] = heartbeat.collectors
        if heartbeat.suricata_running is not None:
            update_fields["suricata_running"] = heartbeat.suricata_running
        if heartbeat.npcap_running is not None:
            update_fields["npcap_running"] = heartbeat.npcap_running
        if heartbeat.uptime_seconds:
            update_fields["uptime_seconds"] = heartbeat.uptime_seconds
        if heartbeat.agent_version:
            update_fields["agent_version"] = heartbeat.agent_version

        res = self.sensors_col.update_one(
            {"sensor_id": sensor_id, "status": {"$ne": "revoked"}},
            {"$set": update_fields},
        )

        # Store heartbeat log beacon
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
                    "api_key_hash": None,
                    "sensor_token_hash": None,
                    "enrollment_credential_hash": None,
                }
            },
        )
        return res.modified_count > 0

    def list_sensors(self) -> List[Sensor]:
        cursor = self.sensors_col.find({}).sort("created_at", -1)
        return [Sensor.from_doc(d) for d in cursor if d]

    def list_by_workspace(self, workspace_id: str) -> List[Sensor]:
        cursor = self.sensors_col.find({"workspace_id": str(workspace_id)}).sort("created_at", -1)
        return [Sensor.from_doc(d) for d in cursor if d]

    def get_active_sensors(self, timeout_sec: int = 90) -> List[Sensor]:
        cutoff = datetime.now(timezone.utc) - timedelta(seconds=timeout_sec)
        cursor = self.sensors_col.find({
            "status": {"$in": ["active", "registered", "online"]},
            "last_heartbeat_at": {"$gte": cutoff},
        })
        return [Sensor.from_doc(d) for d in cursor if d]

    def get_monitoring_state(self, timeout_sec: int = 90) -> Dict[str, Any]:
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

        five_min_ago = datetime.now(timezone.utc) - timedelta(minutes=10)
        has_recent_telemetry = any(
            s.last_telemetry_at and (
                s.last_telemetry_at.replace(tzinfo=timezone.utc) if getattr(s.last_telemetry_at, "tzinfo", None) is None else s.last_telemetry_at
            ) >= five_min_ago
            for s in active_sensors
        )

        suricata_op = any(
            s.suricata_running or s.collector_details.get("suricata") == "operational" for s in active_sensors
        )
        windows_op = any(
            s.npcap_running or s.collector_details.get("windows_sockets") in ("operational", "active")
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
