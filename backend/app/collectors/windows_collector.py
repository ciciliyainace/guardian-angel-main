import subprocess
import sys
from typing import List, Dict, Any
from app.collectors.base import BaseCollector
from app.core.logging_config import logger


class WindowsCollector(BaseCollector):
    """
    Windows network telemetry collector.
    Collects active TCP/UDP endpoints and connection metadata from Windows network stack.
    Note: Does not perform full packet capture; captures socket metadata and active connection states.
    """
    def __init__(self):
        super().__init__(name="Windows network collector")
        self.is_windows = sys.platform == "win32"

    def start(self) -> None:
        if self.is_windows:
            self.status = "Operational"
            self.detail = "Windows socket telemetry active (connection states, not packet capture)"
        else:
            self.status = "Degraded"
            self.detail = "Non-Windows OS: Windows collector inactive"

    def stop(self) -> None:
        self.status = "Disconnected"
        self.detail = "Stopped"

    def collect(self) -> List[Dict[str, Any]]:
        if not self.is_windows:
            return []

        events = []
        try:
            # Query active TCP connections using netstat safely
            res = subprocess.run(
                ["netstat", "-n", "-o"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if res.returncode == 0:
                lines = res.stdout.splitlines()
                loopbacks = ("127.0.0.1", "::1", "0.0.0.0", "*", "[::]", "localhost")
                for line in lines[4:25]:
                    parts = line.split()
                    if len(parts) >= 4 and parts[0].upper() in ("TCP", "UDP"):
                        proto = parts[0].upper()
                        local = parts[1]
                        foreign = parts[2]
                        if ":" in local and ":" in foreign:
                            local_ip, local_port = local.rsplit(":", 1)
                            foreign_ip, foreign_port = foreign.rsplit(":", 1)
                            # Exclude local/loopback internal IPC connections
                            if foreign_ip not in loopbacks and local_ip not in loopbacks:
                                events.append({
                                    "source_ip": foreign_ip,
                                    "dest_ip": local_ip,
                                    "src_port": int(foreign_port) if foreign_port.isdigit() else 0,
                                    "dst_port": int(local_port) if local_port.isdigit() else 0,
                                    "protocol": proto,
                                    "category": "Active network connection",
                                    "source": "Windows socket telemetry",
                                    "severity": "low",
                                    "risk_score": 15,
                                    "is_simulated": False,
                                    "event_source": "windows_socket",
                                    "metadata": {
                                        "state": parts[3] if len(parts) > 3 else "ESTABLISHED",
                                        "telemetry_type": "socket_metadata",
                                    },
                                })

            if events:
                self.record_success(count=len(events), detail=f"Polled {len(events)} external socket connections")
            else:
                self.status = "Operational"
                self.detail = "No active external anomalous socket connections"
        except Exception as e:
            self.record_error(f"Windows telemetry collection error: {e}", degraded=True)

        return events
