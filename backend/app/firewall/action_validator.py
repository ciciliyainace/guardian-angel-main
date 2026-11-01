import re
from typing import Dict, Any
from app.firewall.protected_targets import target_validator
from app.core.exceptions import ValidationError

SAFE_RULE_NAME_REGEX = re.compile(r"^SentinelAI_Block_[a-zA-Z0-9_\.\-]+$")


class ActionValidator:
    @staticmethod
    def validate_block_action(target_ip: str, direction: str, duration_min: int, rule_name: str) -> None:
        # 1. Validate IP safety
        target_validator.validate_target(target_ip)

        # 2. Validate direction
        if direction not in ("Inbound", "Outbound"):
            raise ValidationError(f"Invalid direction '{direction}'. Must be 'Inbound' or 'Outbound'.")

        # 3. Validate duration
        if not (5 <= duration_min <= 1440):
            raise ValidationError(f"Invalid duration {duration_min} minutes. Must be between 5 and 1440 (24h).")

        # 4. Validate rule name safety
        if not SAFE_RULE_NAME_REGEX.match(rule_name):
            raise ValidationError(
                f"Invalid managed rule name '{rule_name}'. Must match pattern '^SentinelAI_Block_[a-zA-Z0-9_.-]+$' to ensure isolation."
            )
