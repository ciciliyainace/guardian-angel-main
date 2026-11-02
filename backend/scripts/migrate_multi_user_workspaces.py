#!/usr/bin/env python3
"""
SentinelAI Multi-User Workspace Migration Script
Idempotently migrates existing single-user / legacy records to multi-tenant workspace architecture.
Supports --dry-run mode.
"""
import sys
import os
import argparse
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pymongo.database import Database
from app.core.database import get_db, db_manager
from app.core.logging_config import logger
from app.repositories.workspace_repository import WorkspaceRepository


def run_migration(db: Database, dry_run: bool = False):
    print(f"=== SentinelAI Workspace Migration (Dry-run: {dry_run}) ===")
    ws_repo = WorkspaceRepository(db)

    # 1. Migrate Users to have valid default_workspace_id
    users_cursor = db.users.find({})
    users_total = 0
    users_migrated = 0

    for u in users_cursor:
        users_total += 1
        user_id = u.get("id")
        username = u.get("username", f"user_{user_id}")
        existing_ws_id = u.get("default_workspace_id")

        needs_ws = False
        if not existing_ws_id:
            needs_ws = True
        else:
            ws_check = db.workspaces.find_one({"id": existing_ws_id})
            if not ws_check:
                needs_ws = True

        if needs_ws:
            print(f"  [User] User id={user_id} ({username}) missing workspace.")
            if not dry_run:
                ws = ws_repo.get_or_create_default_workspace(user_id, username)
                db.users.update_one({"id": user_id}, {"$set": {"default_workspace_id": ws.id}})
                print(f"  -> Created/assigned workspace {ws.id} ({ws.name})")
            users_migrated += 1

    # 2. Ensure legacy fallback workspace exists
    legacy_ws_id = "ws_system_legacy"
    if not db.workspaces.find_one({"id": legacy_ws_id}):
        print(f"  [Workspace] Creating {legacy_ws_id} for unassigned system events...")
        if not dry_run:
            db.workspaces.insert_one({
                "id": legacy_ws_id,
                "name": "System Legacy Workspace",
                "owner_user_id": 1,
                "members": [{"user_id": 1, "username": "admin", "role": "owner", "added_at": datetime.now(timezone.utc)}],
                "settings": {"allow_guest_sensors": False},
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            })

    # 3. Migrate Sensors
    sensors_cursor = db.sensors.find({"$or": [{"workspace_id": None}, {"workspace_id": {"$exists": False}}]})
    sensors_migrated = 0
    for s in sensors_cursor:
        sensor_id = s.get("sensor_id")
        enrolled_by = s.get("enrolled_by")
        owner_user = db.users.find_one({"username": enrolled_by}) if enrolled_by else None
        target_ws_id = owner_user.get("default_workspace_id") if (owner_user and owner_user.get("default_workspace_id")) else legacy_ws_id
        owner_user_id = owner_user.get("id") if owner_user else 1

        print(f"  [Sensor] Binding sensor '{sensor_id}' to workspace {target_ws_id} (owner_id: {owner_user_id})")
        if not dry_run:
            db.sensors.update_one(
                {"sensor_id": sensor_id},
                {"$set": {"workspace_id": target_ws_id, "owner_user_id": owner_user_id}},
            )
        sensors_migrated += 1

    # 4. Migrate Events without workspace_id
    events_unscoped = db.network_events.count_documents({"$or": [{"workspace_id": None}, {"workspace_id": {"$exists": False}}]})
    print(f"  [NetworkEvents] Unscoped events found: {events_unscoped}")
    if events_unscoped > 0 and not dry_run:
        # Match by sensor_id if known
        for s in db.sensors.find({"workspace_id": {"$ne": None}}):
            db.network_events.update_many(
                {"sensor_id": s["sensor_id"], "$or": [{"workspace_id": None}, {"workspace_id": {"$exists": False}}]},
                {"$set": {"workspace_id": s["workspace_id"], "owner_user_id": s.get("owner_user_id", 1)}},
            )
        # Remaining unscoped get assigned to legacy workspace
        db.network_events.update_many(
            {"$or": [{"workspace_id": None}, {"workspace_id": {"$exists": False}}]},
            {"$set": {"workspace_id": legacy_ws_id, "owner_user_id": 1}},
        )
        print(f"  -> Successfully migrated {events_unscoped} network events.")

    # 5. Migrate Alerts without workspace_id
    alerts_unscoped = db.alerts.count_documents({"$or": [{"workspace_id": None}, {"workspace_id": {"$exists": False}}]})
    print(f"  [Alerts] Unscoped alerts found: {alerts_unscoped}")
    if alerts_unscoped > 0 and not dry_run:
        for s in db.sensors.find({"workspace_id": {"$ne": None}}):
            db.alerts.update_many(
                {"sensor_id": s["sensor_id"], "$or": [{"workspace_id": None}, {"workspace_id": {"$exists": False}}]},
                {"$set": {"workspace_id": s["workspace_id"], "owner_user_id": s.get("owner_user_id", 1)}},
            )
        db.alerts.update_many(
            {"$or": [{"workspace_id": None}, {"workspace_id": {"$exists": False}}]},
            {"$set": {"workspace_id": legacy_ws_id, "owner_user_id": 1}},
        )
        print(f"  -> Successfully migrated {alerts_unscoped} alerts.")

    print(f"\nMigration complete. Summary: Users inspected: {users_total}, Users updated: {users_migrated}, Sensors updated: {sensors_migrated}, Events updated: {events_unscoped}, Alerts updated: {alerts_unscoped}")


def main():
    parser = argparse.ArgumentParser(description="Migrate SentinelAI database to multi-user workspace architecture.")
    parser.add_argument("--dry-run", action="store_true", help="Inspect and simulate migration without committing changes.")
    args = parser.parse_args()

    db = next(get_db())
    run_migration(db, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
