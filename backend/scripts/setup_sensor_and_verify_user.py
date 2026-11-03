import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

MONGODB_URI = "mongodb+srv://ciciliyainace2210:cici2210@cluster0.kramxzk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

def main():
    client = MongoClient(MONGODB_URI)
    db = client["sentinelai"]
    now = datetime.now(timezone.utc)

    # 1. Verify User 3 (ciciliyainace)
    user_res = db.users.update_one(
        {"id": 3},
        {
            "$set": {
                "email_verified": True,
                "email_verified_at": now,
                "updated_at": now,
            }
        }
    )
    print(f"User 3 email_verified updated (matched={user_res.matched_count}, modified={user_res.modified_count})")

    # Also clean up any pending tokens
    db.auth_tokens.update_many(
        {"user_id": 3, "token_type": "email_verification", "used_at": None},
        {"$set": {"used_at": now}}
    )

    # 2. Setup fresh uncompromised enrollment credential for LAPTOP-BKC801RO-Sensor
    raw_enrollment_key = f"sen_enroll_{secrets.token_hex(16)}"
    key_hash = hashlib.sha256(raw_enrollment_key.encode("utf-8")).hexdigest()
    expires_at = now + timedelta(days=14)

    sensor_res = db.sensors.update_one(
        {"sensor_id": "LAPTOP-BKC801RO-Sensor"},
        {
            "$set": {
                "enrollment_credential_hash": key_hash,
                "api_key_hash": key_hash,
                "enrollment_credential_consumed": False,
                "enrollment_credential_consumed_at": None,
                "enrollment_credential_expires_at": expires_at,
                "status": "pending_enrollment",
                "collector_types": ["windows_sockets", "suricata"],
                "updated_at": now,
            }
        }
    )
    print(f"Sensor LAPTOP-BKC801RO-Sensor updated (matched={sensor_res.matched_count}, modified={sensor_res.modified_count})")
    print(f"FRESH_ENROLLMENT_CREDENTIAL: {raw_enrollment_key}")
    print(f"EXPIRES_AT: {expires_at.isoformat()}")

if __name__ == "__main__":
    main()

