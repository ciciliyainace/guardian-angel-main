import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pymongo.database import Database
from app.models.workspace import Workspace
from app.core.logging_config import logger


class WorkspaceRepository:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db.workspaces

    def create(self, workspace: Workspace) -> Workspace:
        doc = workspace.to_doc()
        self.collection.update_one({"id": workspace.id}, {"$set": doc}, upsert=True)
        return workspace

    def get_by_id(self, workspace_id: str) -> Optional[Workspace]:
        if not workspace_id:
            return None
        doc = self.collection.find_one({"id": str(workspace_id)})
        return Workspace.from_doc(doc) if doc else None

    def get_by_owner_id(self, user_id: int) -> Optional[Workspace]:
        doc = self.collection.find_one({"owner_user_id": int(user_id)})
        return Workspace.from_doc(doc) if doc else None

    def get_or_create_default_workspace(self, user_id: int, username: str) -> Workspace:
        """
        Idempotently fetch or create the default workspace for a user.
        Ensures every user has an isolated workspace upon registration or initial lookup.
        """
        existing = self.get_by_owner_id(user_id)
        if existing:
            return existing

        ws_id = f"ws_usr_{user_id}_{uuid.uuid4().hex[:6]}"
        clean_name = f"{username.capitalize()}'s Workspace"
        now = datetime.now(timezone.utc)

        workspace = Workspace(
            id=ws_id,
            name=clean_name,
            owner_user_id=user_id,
            description=f"Default private security operations workspace for {username}.",
            created_at=now,
            updated_at=now,
            is_active=True,
            members=[{"user_id": int(user_id), "role": "owner", "added_at": now.isoformat()}],
        )
        self.create(workspace)
        logger.info(f"[WorkspaceRepository] Created default workspace '{workspace.id}' for user_id={user_id}")
        return workspace

    def list_for_user(self, user_id: int) -> List[Workspace]:
        """List all workspaces owned by or shared with this user."""
        cursor = self.collection.find({
            "$or": [
                {"owner_user_id": int(user_id)},
                {"members.user_id": int(user_id)},
            ]
        }).sort("created_at", -1)
        return [Workspace.from_doc(doc) for doc in cursor if doc]

