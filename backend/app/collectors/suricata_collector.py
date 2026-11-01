import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.collectors.base import BaseCollector
from app.core.config import settings
from app.core.logging_config import logger
from app.utils.time_utils import iso_to_epoch_ms, current_epoch_ms


class SuricataCollector(BaseCollector):
    """
    Production-ready Suricata EVE JSON log tailing collector.
    Monitors Suricata's eve.json output incrementally using byte-offset checkpoints,
    detecting log rotation, parsing alert and flow events, and normalizing them for detection.

    States:
    - 'Not Configured': SURICATA_EVE_PATH is empty or unconfigured.
    - 'Disconnected': Path is configured, but eve.json does not exist (Suricata offline).
    - 'Connected' / 'Operational': File exists, is readable, and is actively being monitored.
    - 'Error': Permission or file access exception encountered.
    """

    def __init__(self, eve_path: Optional[str] = None, checkpoint_path: Optional[str] = None):
        super().__init__(name="Suricata IDS integration")
        raw_path = eve_path if eve_path is not None else settings.SURICATA_EVE_PATH
        self.eve_path_raw = raw_path
        self.eve_path = Path(raw_path) if raw_path and raw_path.strip().lower() not in ("", "none") else None
        self.checkpoint_path = Path(checkpoint_path or settings.SURICATA_CHECKPOINT_FILE)
        self.last_byte_offset = 0
        self.last_file_mtime: Optional[float] = None
        self.last_event_time: Optional[datetime] = None
        self._load_checkpoint()

    def _load_checkpoint(self):
        """Load the saved byte offset from the checkpoint file to avoid re-reading old logs."""
        try:
            if self.checkpoint_path.exists():
                with open(self.checkpoint_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.last_byte_offset = data.get("offset", 0)
                    self.last_file_mtime = data.get("mtime")
        except Exception as e:
            logger.warning(f"Could not load Suricata checkpoint from {self.checkpoint_path}: {e}")
            self.last_byte_offset = 0

    def _save_checkpoint(self, offset: int, mtime: Optional[float] = None):
        """Save the current byte offset and file timestamp safely."""
        try:
            self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.checkpoint_path, "w", encoding="utf-8") as f:
                json.dump({
                    "offset": offset,
                    "mtime": mtime or self.last_file_mtime,
                    "file": str(self.eve_path) if self.eve_path else "",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                }, f, indent=2)
            self.last_byte_offset = offset
            if mtime:
                self.last_file_mtime = mtime
        except Exception as e:
            logger.warning(f"Could not save Suricata checkpoint: {e}")

    def update_state(self):
        """Evaluate current configuration and filesystem state."""
        if not self.eve_path:
            self.status = "Not Configured"
            self.detail = "SURICATA_EVE_PATH is not configured in backend/.env. Specify path to Suricata's eve.json log."
            return

        if not self.eve_path.exists():
            self.status = "Disconnected"
            self.detail = f"Suricata eve.json not found at '{self.eve_path}'. Sensor offline or Suricata service stopped."
            return

        if not os.access(self.eve_path, os.R_OK):
            self.status = "Error"
            self.detail = f"Permission denied reading '{self.eve_path}'. Ensure the backend has file read permissions."
            return

        self.status = "Operational"
        self.detail = f"Actively monitoring '{self.eve_path.name}'"

    def start(self) -> None:
        self.update_state()
        logger.info(f"SuricataCollector started in status: {self.status} ({self.detail})")

    def stop(self) -> None:
        self.status = "Disconnected"
        self.detail = "Sensor tailing stopped"
        logger.info("SuricataCollector stopped.")

    def collect(self) -> List[Dict[str, Any]]:
        """
        Incrementally read new JSON lines from eve.json starting from last_byte_offset.
        Handles file rotation, truncation, and malformed lines.
        """
        if not self.eve_path:
            self.status = "Not Configured"
            self.detail = "SURICATA_EVE_PATH is not configured."
            return []

        if not self.eve_path.exists():
            self.status = "Disconnected"
            self.detail = f"Suricata eve.json not found at '{self.eve_path}'. Sensor offline."
            return []

        if not os.access(self.eve_path, os.R_OK):
            self.record_error(f"Permission denied: cannot read '{self.eve_path}'")
            return []

        parsed_events = []
        try:
            stat_info = self.eve_path.stat()
            file_size = stat_info.st_size
            current_mtime = stat_info.st_mtime

            # Log rotation or truncation detection:
            # 1. If file size shrunk, or
            # 2. If mtime changed and file size is smaller than offset
            if file_size < self.last_byte_offset:
                logger.info(
                    f"Suricata log truncation/rotation detected: size ({file_size}B) < offset ({self.last_byte_offset}B). Resetting to 0."
                )
                self.last_byte_offset = 0

            with open(self.eve_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self.last_byte_offset)
                for line in f:
                    line_str = line.strip()
                    if not line_str:
                        continue
                    try:
                        record = json.loads(line_str)
                        normalized = self._normalize_record(record)
                        if normalized:
                            parsed_events.append(normalized)
                    except json.JSONDecodeError as err:
                        logger.warning(f"Malformed JSON line skipped in Suricata log: {err}")
                        continue
                current_offset = f.tell()

            if parsed_events:
                self._save_checkpoint(current_offset, current_mtime)
                self.last_event_time = datetime.now(timezone.utc)
                self.record_success(
                    count=len(parsed_events),
                    detail=f"Ingested {len(parsed_events)} live Suricata events (offset: {current_offset}B)",
                )
            else:
                self.status = "Operational"
                self.detail = f"Monitoring '{self.eve_path.name}' — log tail up to date ({current_offset}B)"

        except PermissionError as pe:
            self.record_error(f"Permission error accessing '{self.eve_path}': {pe}")
        except Exception as e:
            self.record_error(f"Unexpected error reading Suricata log '{self.eve_path}': {e}")

        return parsed_events

    def _normalize_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize a raw Suricata EVE record into the canonical SentinelAI event schema.
        Preserves original UTC timestamps, protocol numbers, ports, and marks event as non-simulated real data.
        """
        event_type = record.get("event_type")
        src_ip = record.get("src_ip")
        dest_ip = record.get("dest_ip")

        if not src_ip or not dest_ip:
            return None

        # Parse Suricata ISO-8601 UTC timestamp if available
        raw_ts = record.get("timestamp")
        timestamp_ms = iso_to_epoch_ms(raw_ts) if raw_ts else current_epoch_ms()

        # Handle Alert events
        if event_type == "alert":
            alert_data = record.get("alert", {})
            signature = alert_data.get("signature", "Suricata signature alert")
            signature_id = alert_data.get("signature_id")
            severity_num = alert_data.get("severity", 3)
            sev_map = {1: "critical", 2: "high", 3: "medium", 4: "low"}
            severity = sev_map.get(severity_num, "medium")

            # Risk score calculation calibrated to Suricata severity
            risk_score = 90 if severity == "critical" else 75 if severity == "high" else 50 if severity == "medium" else 30

            return {
                "timestamp": timestamp_ms,
                "source_ip": src_ip,
                "dest_ip": dest_ip,
                "src_port": record.get("src_port", 0),
                "dst_port": record.get("dest_port", 0),
                "protocol": record.get("proto", "TCP").upper(),
                "category": alert_data.get("category", "Signature match"),
                "source": "Suricata IDS",
                "severity": severity,
                "risk_score": risk_score,
                "is_simulated": False,  # REAL collected network event
                "event_source": "suricata_eve",
                "metadata": {
                    "suricata_event_type": "alert",
                    "signature": signature,
                    "signature_id": signature_id,
                    "action": alert_data.get("action", "allowed"),
                    "rev": alert_data.get("rev"),
                    "category": alert_data.get("category"),
                },
            }

        # Handle Flow summary events
        elif event_type == "flow":
            flow_data = record.get("flow", {})
            bytes_toserver = flow_data.get("bytes_toserver", 0)
            bytes_toclient = flow_data.get("bytes_toclient", 0)
            pkts_toserver = flow_data.get("pkts_toserver", 0)
            pkts_toclient = flow_data.get("pkts_toclient", 0)
            total_bytes = bytes_toserver + bytes_toclient

            # Basic heuristic for flow risk
            is_suspicious_flow = (pkts_toserver > 500 and pkts_toclient < 5) or total_bytes > 50000000
            severity = "medium" if is_suspicious_flow else "low"
            risk_score = 45 if is_suspicious_flow else 15

            return {
                "timestamp": timestamp_ms,
                "source_ip": src_ip,
                "dest_ip": dest_ip,
                "src_port": record.get("src_port", 0),
                "dst_port": record.get("dest_port", 0),
                "protocol": record.get("proto", "TCP").upper(),
                "category": "Suspicious flow" if is_suspicious_flow else "Network flow",
                "source": "Suricata IDS",
                "severity": severity,
                "risk_score": risk_score,
                "is_simulated": False,  # REAL collected network event
                "event_source": "suricata_eve",
                "flow_features": {
                    "total_fwd_packets": pkts_toserver,
                    "total_bwd_packets": pkts_toclient,
                    "flow_bytes_s": total_bytes,
                },
                "metadata": {
                    "suricata_event_type": "flow",
                    "reason": flow_data.get("reason"),
                    "age": flow_data.get("age"),
                },
            }

        return None
