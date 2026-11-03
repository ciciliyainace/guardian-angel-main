import sys
import os
from datetime import datetime, timezone

# Add backend directory to sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import get_database
from app.services.audit_service import AuditService

def run_migration():
    db = get_database()
    users_col = db.users
    tokens_col = db.auth_tokens
    audit = AuditService(db)

    now = datetime.now(timezone.utc)
    print("=" * 60)
    print("SENTINELAI — USER VERIFICATION STATE REPAIR MIGRATION")
    print(f"Timestamp: {now.isoformat()}")
    print("=" * 60)

    users = list(users_col.find({}))
    for u in users:
        uid = u.get("id")
        email = u.get("email")
        username = u.get("username")
        current_verified = u.get("email_verified", False)
        auth_providers = u.get("auth_providers", ["password"])
        google_sub = u.get("google_sub")

        print(f"\nEvaluating User id={uid}, username='{username}', email='{email}'")
        print(f"  Current email_verified: {current_verified}")
        print(f"  Auth providers: {auth_providers}")

        # Check for genuine redeemed tokens
        redeemed_tokens = list(tokens_col.find({
            "user_id": uid,
            "token_type": "email_verification",
            "used_at": {"$ne": None}
        }))

        # If user was verified via authentic Google OAuth with verified claim
        if google_sub and "google" in auth_providers:
            print("  -> User verified via verified Google OAuth claim. Keeping verified.")
            continue

        # If user is password-based and has no authentic token redemption proof:
        # User 3 was artificially set to True in earlier debugging.
        # Check if email is genuine and whether genuine verification occurred.
        if uid == 3 or not redeemed_tokens:
            print(f"  -> Resetting email_verified to False for user {username} ({email}).")
            users_col.update_one(
                {"id": uid},
                {
                    "$set": {
                        "email_verified": False,
                        "email_verified_at": None,
                        "updated_at": now,
                    }
                }
            )
            audit.log(
                actor="system_migration",
                action="ResetEmailVerificationStatus",
                target=f"user:{uid}",
                result="Success",
                reason="Corrected artificial verification status. Real token redemption required.",
            )
            print("  -> Successfully updated.")
        else:
            print(f"  -> User has {len(redeemed_tokens)} redeemed token(s). Verification status preserved.")

    print("\nMigration completed successfully.")

if __name__ == "__main__":
    run_migration()
