import sys
import argparse
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import db_manager, init_indexes
from app.core.security import hash_password
from app.utils.time_utils import current_epoch_ms


def create_admin_user(username: str, email: str, password: str, display_name: str = "Administrator"):
    connected = db_manager.connect()
    if not connected:
        print(f"Error: Failed to connect to MongoDB Atlas ({db_manager.last_error})")
        return False

    db = db_manager.get_db()
    init_indexes(db)

    try:
        existing = db.users.find_one({"$or": [{"username": username}, {"email": email}]})
        if existing:
            print(f"Error: User with username '{username}' or email '{email}' already exists.")
            return False

        # Get next auto-increment id
        last_user = db.users.find_one(sort=[("id", -1)])
        next_id = (last_user["id"] + 1) if (last_user and "id" in last_user and isinstance(last_user["id"], int)) else 1

        user_doc = {
            "id": next_id,
            "username": username,
            "email": email,
            "display_name": display_name,
            "hashed_password": hash_password(password),
            "role": "administrator",
            "is_active": True,
            "created_at": current_epoch_ms(),
            "last_login": None,
        }
        db.users.insert_one(user_doc)
        print(f"Success: Administrator account '{username}' ({email}) created successfully.")
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False


if __name__ == "__main__":
    import os
    import getpass

    parser = argparse.ArgumentParser(description="Create a SentinelAI Administrator Account")
    parser.add_argument("--username", "-u", default="admin", help="Admin username")
    parser.add_argument("--email", "-e", default="admin@sentinelai.local", help="Admin email")
    parser.add_argument("--password", "-p", default=None, help="Admin password (or prompts if omitted)")
    parser.add_argument("--display-name", "-n", default="Administrator", help="Display name")

    args = parser.parse_args()
    pwd = args.password or os.environ.get("SENTINEL_ADMIN_PASSWORD")
    if not pwd:
        if sys.stdin.isatty():
            pwd = getpass.getpass("Enter Admin Password: ")
        else:
            pwd = os.environ.get("INITIAL_ADMIN_PASSWORD", "SentinelAdmin2026!")

    create_admin_user(args.username, args.email, pwd, args.display_name)
