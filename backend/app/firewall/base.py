from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseFirewallAdapter(ABC):
    @abstractmethod
    def block_ip(
        self,
        target_ip: str,
        rule_name: str,
        direction: str = "Inbound",
        duration_min: int = 60,
    ) -> Dict[str, Any]:
        """
        Block an IP address.
        Returns result dictionary: {success: bool, rule_name: str, verification_status: str, detail: str}
        """
        pass

    @abstractmethod
    def remove_rule(self, rule_name: str) -> Dict[str, Any]:
        """
        Remove/rollback a previously created firewall rule.
        Returns result dictionary: {success: bool, rule_name: str, detail: str}
        """
        pass

    @abstractmethod
    def verify_rule(self, rule_name: str) -> bool:
        """Verify whether a firewall rule currently exists on the system."""
        pass
