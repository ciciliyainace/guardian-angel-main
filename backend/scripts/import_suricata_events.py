import sys
import argparse
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import db_manager, init_indexes
from app.services.event_service import EventService
from app.collectors.suricata_collector import SuricataCollector
from app.core.logging_config import setup_logging, logger


def import_suricata(file_path: str):
    setup_logging()
    path = Path(file_path)
    if not path.exists():
        logger.error(f"Suricata log file not found: {path}")
        return 0

    collector = SuricataCollector(eve_path=str(path))
    records = collector.collect()
    if not records:
        logger.info("No new or valid Suricata records found in file.")
        return 0

    if not db_manager.connect():
        logger.error(f"Failed to connect to MongoDB Atlas: {db_manager.last_error}")
        return 0

    db = db_manager.get_db()
    init_indexes(db)

    imported = 0
    svc = EventService(db)
    for rec in records:
        svc.ingest_event(rec, run_detection=True)
        imported += 1
    logger.info(f"Successfully imported {imported} events from {file_path}")

    return imported


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Suricata Eve JSON log events into SentinelAI")
    parser.add_argument("file", help="Path to eve.json log file")
    args = parser.parse_args()
    import_suricata(args.file)
