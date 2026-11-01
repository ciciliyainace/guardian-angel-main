import sys
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, Any, List

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import db_manager, init_indexes
from app.core.logging_config import setup_logging, logger


TABLE_TO_COLLECTION = {
    "users": "users",
    "network_events": "network_events",
    "alerts": "alerts",
    "detection_rules": "detection_rules",
    "firewall_requests": "firewall_requests",
    "firewall_actions": "firewall_actions",
    "audit_logs": "audit_logs",
    "system_settings": "system_settings",
    "feedback": "feedback",
    "model_registry": "model_registry",
}


def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}


def migrate_data(sqlite_path: str, dry_run: bool = False):
    setup_logging()
    db_file = Path(sqlite_path)
    if not db_file.exists():
        logger.warning(f"SQLite database file not found at '{sqlite_path}'. Nothing to migrate.")
        return

    logger.info(f"Connecting to SQLite source: {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = dict_factory
    cursor = conn.cursor()

    # Discover existing tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row["name"] for row in cursor.fetchall()]
    logger.info(f"Discovered SQLite tables: {existing_tables}")

    if not dry_run:
        if not db_manager.connect():
            logger.error(f"Cannot connect to MongoDB Atlas: {db_manager.last_error}")
            return
        mongo_db = db_manager.get_db()
        init_indexes(mongo_db)
    else:
        logger.info("[DRY-RUN MODE] No data will be written to MongoDB.")

    total_migrated = 0

    for table, collection_name in TABLE_TO_COLLECTION.items():
        if table not in existing_tables:
            logger.debug(f"Table '{table}' does not exist in SQLite source. Skipping.")
            continue

        cursor.execute(f"SELECT * FROM {table}")
        rows: List[Dict[str, Any]] = cursor.fetchall()
        count = len(rows)

        logger.info(f"Table '{table}': found {count} records for collection '{collection_name}'")

        if dry_run:
            if count > 0:
                logger.info(f"  [DRY RUN] Sample row: {rows[0]}")
            continue

        if count == 0:
            continue

        inserted = 0
        skipped = 0
        col = mongo_db[collection_name]

        for row in rows:
            # Check unique constraints if primary key exists
            unique_query = None
            if "id" in row and row["id"] is not None:
                unique_query = {"id": row["id"]}
            elif "username" in row and row["username"] is not None:
                unique_query = {"username": row["username"]}
            elif "key" in row and row["key"] is not None:
                unique_query = {"key": row["key"]}

            if unique_query and col.find_one(unique_query):
                skipped += 1
                continue

            col.insert_one(row)
            inserted += 1

        total_migrated += inserted
        logger.info(f"  Collection '{collection_name}': {inserted} inserted, {skipped} skipped (already present)")

    conn.close()
    if dry_run:
        logger.info("[DRY-RUN COMPLETE] Migration simulated successfully.")
    else:
        logger.info(f"[MIGRATION COMPLETE] Successfully migrated {total_migrated} records to MongoDB Atlas.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate SentinelAI data from SQLite to MongoDB Atlas")
    parser.add_argument("--sqlite-path", default="sentinelai.db", help="Path to SQLite database file")
    parser.add_argument("--dry-run", action="store_true", help="Simulate migration without modifying MongoDB")
    args = parser.parse_args()

    migrate_data(sqlite_path=args.sqlite_path, dry_run=args.dry_run)
