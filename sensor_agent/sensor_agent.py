#!/usr/bin/env python3
"""
SentinelAI Dedicated Windows Network Sensor Agent.

Captures genuine host network telemetry:
1. Windows Active Sockets (TCP/UDP, PIDs, process names)
2. Suricata EVE JSON (flow, alert, dns, http, tls) with offset tracking and rotation handling
3. Periodic Heartbeat to SentinelAI backend
4. Offline local spooling with backoff retry when backend is unreachable
"""

import os
import sys
import time
import json
import socket
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (SensorAgent) %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("SensorAgent")

# Try to import psutil for high-fidelity socket telemetry
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logger.warning("psutil not installed. Socket telemetry will operate in fallback mode.")


class SensorAgent:
    def __init__(self, config_path: str = "sensor_config.json"):
        self.config_path = config_path
        self.config = self._load_config()

        self.sensor_id = self.config.get("sensor_id", f"win-sensor-{socket.gethostname().lower()}")
        self.sensor_key = self.config.get("sensor_key", "")
        self.backend_url = self.config.get("backend_url", "http://127.0.0.1:8000/api/v1").rstrip("/")
        self.suricata_eve_path = self.config.get("suricata_eve_path", "C:\\Program Files\\Suricata\\log\\eve.json")
        self.poll_interval = float(self.config.get("poll_interval_sec", 5.0))
        self.heartbeat_interval = float(self.config.get("heartbeat_interval_sec", 30.0))
        self.batch_size = int(self.config.get("batch_size", 50))
        self.spool_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".telemetry_spool.jsonl")
        self.offset_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".suricata_offset")

        self.last_heartbeat_time = 0.0
        self.last_offset = self._load_offset()
        self.known_connections: Dict[str, float] = {}

    def _load_config(self) -> Dict[str, Any]:
        cfg = {}
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception as e:
                logger.error(f"Failed to read config file {self.config_path}: {e}")

        # Environment variable overrides
        if os.environ.get("SENTINEL_BACKEND_URL"):
            cfg["backend_url"] = os.environ["SENTINEL_BACKEND_URL"]
        if os.environ.get("SENTINEL_SENSOR_KEY"):
            cfg["sensor_key"] = os.environ["SENTINEL_SENSOR_KEY"]
        if os.environ.get("SENTINEL_SENSOR_ID"):
            cfg["sensor_id"] = os.environ["SENTINEL_SENSOR_ID"]
        if os.environ.get("SURICATA_EVE_PATH"):
            cfg["suricata_eve_path"] = os.environ["SURICATA_EVE_PATH"]

        return cfg

    def _load_offset(self) -> int:
        if os.path.exists(self.offset_path):
            try:
                with open(self.offset_path, "r") as f:
                    return int(f.read().strip() or "0")
            except Exception:
                pass
        return 0

    def _save_offset(self, offset: int) -> None:
        try:
            with open(self.offset_path, "w") as f:
                f.write(str(offset))
        except Exception as e:
            logger.warning(f"Failed to write offset file: {e}")

    def collect_windows_sockets(self) -> List[Dict[str, Any]]:
        """Collects genuine TCP/UDP socket metadata from Windows host."""
        events: List[Dict[str, Any]] = []
        now_ms = int(time.time() * 1000)

        if not HAS_PSUTIL:
            return events

        try:
            connections = psutil.net_connections(kind="inet")
            for conn in connections:
                if not conn.raddr:
                    continue  # Ignore listening sockets with no remote peer

                local_ip, local_port = conn.laddr.ip, conn.laddr.port
                remote_ip, remote_port = conn.raddr.ip, conn.raddr.port
                proto = "TCP" if conn.type == socket.SOCK_STREAM else "UDP"
                status = conn.status if conn.status else "ESTABLISHED"
                pid = conn.pid

                # Throttle duplicate connection states within 30 seconds
                conn_key = f"{proto}:{local_ip}:{local_port}->{remote_ip}:{remote_port}:{status}"
                last_seen = self.known_connections.get(conn_key, 0)
                if (time.time() - last_seen) < 30.0:
                    continue
                self.known_connections[conn_key] = time.time()

                proc_name = "unknown"
                if pid:
                    try:
                        p = psutil.Process(pid)
                        proc_name = p.name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = "protected_or_terminated"

                events.append({
                    "collector": "windows_sockets",
                    "timestamp_ms": now_ms,
                    "local_address": local_ip,
                    "local_port": local_port,
                    "remote_address": remote_ip,
                    "remote_port": remote_port,
                    "protocol": proto,
                    "status": status,
                    "pid": pid,
                    "process_name": proc_name,
                })

            # Clean stale keys
            if len(self.known_connections) > 10000:
                cur_t = time.time()
                self.known_connections = {k: v for k, v in self.known_connections.items() if (cur_t - v) < 60.0}

        except Exception as e:
            logger.warning(f"Error collecting Windows sockets: {e}")

        return events

    def collect_suricata_eve(self) -> List[Dict[str, Any]]:
        """Incrementally reads new events from Suricata EVE JSON log file."""
        events: List[Dict[str, Any]] = []
        if not self.suricata_eve_path or not os.path.exists(self.suricata_eve_path):
            return events

        try:
            current_size = os.path.getsize(self.suricata_eve_path)
            # Detect log rotation or truncation
            if current_size < self.last_offset:
                logger.info("Suricata log file truncated or rotated. Resetting offset to 0.")
                self.last_offset = 0

            with open(self.suricata_eve_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self.last_offset)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        parsed = json.loads(line)
                        parsed["collector"] = "suricata"
                        events.append(parsed)
                    except json.JSONDecodeError:
                        continue
                self.last_offset = f.tell()
                self._save_offset(self.last_offset)

        except Exception as e:
            logger.warning(f"Error reading Suricata eve.json at {self.suricata_eve_path}: {e}")

        return events

    def send_heartbeat(self, client: httpx.Client) -> bool:
        """Sends operational heartbeat and telemetry metrics to SentinelAI backend."""
        url = f"{self.backend_url}/sensors/heartbeat"
        headers = {"X-Sensor-Key": self.sensor_key}
        suricata_op = "operational" if (self.suricata_eve_path and os.path.exists(self.suricata_eve_path)) else "standby"
        sock_op = "operational" if HAS_PSUTIL else "fallback"

        metrics = {
            "hostname": socket.gethostname(),
            "cpu_percent": psutil.cpu_percent() if HAS_PSUTIL else 0.0,
            "memory_percent": psutil.virtual_memory().percent if HAS_PSUTIL else 0.0,
            "tracked_sockets": len(self.known_connections),
        }
        collectors = {
            "suricata": suricata_op,
            "windows_sockets": sock_op,
        }

        payload = {
            "metrics": metrics,
            "collectors": collectors,
            "last_event_time": int(time.time() * 1000),
        }

        try:
            res = client.post(url, json=payload, headers=headers, timeout=8.0)
            if res.status_code == 200:
                logger.info(f"Heartbeat acknowledged by {self.backend_url} (suricata: {suricata_op}, winsock: {sock_op})")
                return True
            else:
                logger.warning(f"Heartbeat rejected: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.warning(f"Heartbeat failed to reach backend: {e}")
            return False

    def spool_events(self, events: List[Dict[str, Any]]) -> None:
        """Appends events to local offline spool file if backend is unreachable."""
        if not events:
            return
        try:
            with open(self.spool_path, "a", encoding="utf-8") as f:
                for ev in events:
                    f.write(json.dumps(ev) + "\n")
            logger.info(f"Spooled {len(events)} events locally to {self.spool_path}")
        except Exception as e:
            logger.error(f"Failed to spool events locally: {e}")

    def read_spooled_events(self, max_count: int = 200) -> List[Dict[str, Any]]:
        """Reads back offline spooled events for re-transmission."""
        if not os.path.exists(self.spool_path):
            return []
        events = []
        remaining = []
        try:
            with open(self.spool_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for i, line in enumerate(lines):
                line = line.strip()
                if not line:
                    continue
                if len(events) < max_count:
                    try:
                        events.append(json.loads(line))
                    except Exception:
                        pass
                else:
                    remaining.append(line)

            # Rewrite spool file with remaining
            if remaining:
                with open(self.spool_path, "w", encoding="utf-8") as f:
                    for l in remaining:
                        f.write(l + "\n")
            else:
                os.remove(self.spool_path)
        except Exception as e:
            logger.warning(f"Failed to read spool file: {e}")

        return events

    def ship_batch(self, client: httpx.Client, events: List[Dict[str, Any]]) -> bool:
        """Ships a batch of telemetry events to SentinelAI backend."""
        if not events:
            return True
        url = f"{self.backend_url}/sensors/telemetry"
        headers = {"X-Sensor-Key": self.sensor_key}
        payload = {"events": events}

        try:
            res = client.post(url, json=payload, headers=headers, timeout=12.0)
            if res.status_code == 200:
                data = res.json()
                logger.info(f"Shipped {len(events)} events: ingested={data.get('ingested')}, duplicates={data.get('duplicates')}, alerts={data.get('alerts_generated')}")
                return True
            else:
                logger.warning(f"Batch ingestion failed: {res.status_code} - {res.text}")
                return False
        except Exception as e:
            logger.warning(f"Batch ingestion connection error: {e}")
            return False

    def run(self) -> None:
        """Main sensor run loop."""
        logger.info(f"Starting SentinelAI Sensor Agent [ID: {self.sensor_id}]")
        logger.info(f"Target Backend: {self.backend_url}")
        logger.info(f"Suricata EVE path: {self.suricata_eve_path} (exists={os.path.exists(self.suricata_eve_path)})")
        logger.info(f"Windows psutil available: {HAS_PSUTIL}")

        if not self.sensor_key:
            logger.error("No sensor_key found in config or environment. Run enroll.py first!")
            sys.exit(1)

        with httpx.Client() as client:
            # Immediate initial heartbeat
            self.send_heartbeat(client)
            self.last_heartbeat_time = time.time()

            while True:
                try:
                    now = time.time()
                    # 1. Periodic Heartbeat
                    if (now - self.last_heartbeat_time) >= self.heartbeat_interval:
                        self.send_heartbeat(client)
                        self.last_heartbeat_time = now

                    # 2. Collect Genuine Telemetry
                    events = []
                    events.extend(self.collect_windows_sockets())
                    events.extend(self.collect_suricata_eve())

                    # 3. Check for previously spooled events
                    spooled = self.read_spooled_events(max_count=self.batch_size)
                    all_events = spooled + events

                    # 4. Ship in chunks
                    if all_events:
                        for i in range(0, len(all_events), self.batch_size):
                            chunk = all_events[i : i + self.batch_size]
                            success = self.ship_batch(client, chunk)
                            if not success:
                                # Spool back remaining chunk and loop
                                self.spool_events(all_events[i:])
                                break

                    time.sleep(self.poll_interval)

                except KeyboardInterrupt:
                    logger.info("Sensor agent stopped by operator.")
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in sensor loop: {e}", exc_info=True)
                    time.sleep(self.poll_interval)


if __name__ == "__main__":
    agent = SensorAgent()
    agent.run()
