import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.collectors.base import BaseCollector
from app.core.logging_config import logger


class JsonFileCollector(BaseCollector):
    def __init__(self, file_path: str = "datasets/sample_events.json"):
        super().__init__(name="JSON File Collector")
        self.file_path = Path(file_path)
        self.checkpoint_line = 0

    def start(self) -> None:
        if self.file_path.exists():
            self.status = "Operational"
            self.detail = f"Monitoring {self.file_path.name}"
        else:
            self.status = "Disconnected"
            self.detail = f"File not found: {self.file_path}"

    def stop(self) -> None:
        self.status = "Disconnected"
        self.detail = "Stopped"

    def collect(self) -> List[Dict[str, Any]]:
        if not self.file_path.exists():
            self.record_error(f"Event file {self.file_path} not found", degraded=True)
            return []

        events = []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            new_lines = lines[self.checkpoint_line :]
            for line in new_lines:
                line_str = line.strip()
                if not line_str:
                    continue
                try:
                    data = json.loads(line_str)
                    events.append(data)
                except json.JSONDecodeError as e:
                    logger.warning(f"Malformed JSON line in {self.file_path}: {e}")

            if events:
                self.checkpoint_line = len(lines)
                self.record_success(count=len(events), detail=f"Processed {len(events)} events from {self.file_path.name}")
        except Exception as e:
            self.record_error(f"Error reading {self.file_path}: {e}")

        return events
