from typing import List, Optional
from app.utils.ip_utils import is_protected_ip
from app.core.exceptions import ProtectedTargetError
from app.core.logging_config import logger


class ProtectedTargetValidator:
    def __init__(self, protected_ips: Optional[List[str]] = None, protected_nets: Optional[List[str]] = None):
        self.protected_ips = protected_ips
        self.protected_nets = protected_nets

    def validate_target(self, target_ip: str) -> None:
        """
        Validate that the target IP is safe to block.
        Raises ProtectedTargetError if the address is protected, reserved, or malformed.
        """
        is_protected, reason = is_protected_ip(
            target_ip,
            custom_protected_ips=self.protected_ips,
            custom_protected_nets=self.protected_nets,
        )
        if is_protected:
            logger.warning(f"Firewall block attempt blocked by safety policy: {target_ip} ({reason})")
            raise ProtectedTargetError(target=target_ip, message=reason)


target_validator = ProtectedTargetValidator()
