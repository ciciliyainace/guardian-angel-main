from typing import List
from fastapi import Depends
from app.core.exceptions import PermissionDeniedError


def check_role(user_role: str, allowed_roles: List[str]) -> bool:
    """Check if the user's role matches any of the allowed roles."""
    normalized_role = user_role.lower()
    normalized_allowed = [r.lower() for r in allowed_roles]
    # Treat "admin" and "administrator" as equivalent
    if "admin" in normalized_allowed and normalized_role in ("admin", "administrator"):
        return True
    if "administrator" in normalized_allowed and normalized_role in ("admin", "administrator"):
        return True
    return normalized_role in normalized_allowed


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: dict):
        role = current_user.get("role", "analyst")
        if not check_role(role, self.allowed_roles):
            raise PermissionDeniedError(
                f"Action requires one of the following roles: {', '.join(self.allowed_roles)}"
            )
        return True


require_admin_role = RoleChecker(["admin", "administrator"])
require_analyst_or_admin = RoleChecker(["analyst", "admin", "administrator"])
