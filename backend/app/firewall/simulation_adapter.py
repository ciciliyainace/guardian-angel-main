from typing import Dict, Any, Set
from app.firewall.base import BaseFirewallAdapter
from app.firewall.action_validator import ActionValidator
from app.core.logging_config import logger


class SimulationFirewallAdapter(BaseFirewallAdapter):
    """
    Simulation firewall adapter.
    Performs full input and safety validation, records simulated firewall rules in memory,
    and guarantees zero modification to the host operating system's firewall.
    """
    def __init__(self):
        self.active_simulated_rules: Set[str] = set()

    def block_ip(
        self,
        target_ip: str,
        rule_name: str,
        direction: str = "Inbound",
        duration_min: int = 60,
    ) -> Dict[str, Any]:
        # Perform exact same safety validation as real adapter
        ActionValidator.validate_block_action(target_ip, direction, duration_min, rule_name)

        self.active_simulated_rules.add(rule_name)
        logger.info(
            f"[FIREWALL SIMULATION] Simulated block created for {target_ip} ({direction}) named '{rule_name}' for {duration_min}m"
        )

        return {
            "success": True,
            "rule_name": rule_name,
            "verification_status": "simulated",
            "detail": f"Simulated rule '{rule_name}' created in memory. Real host firewall remained untouched.",
        }

    def remove_rule(self, rule_name: str) -> Dict[str, Any]:
        if rule_name in self.active_simulated_rules:
            self.active_simulated_rules.remove(rule_name)
            logger.info(f"[FIREWALL SIMULATION] Simulated rule '{rule_name}' removed.")
            return {
                "success": True,
                "rule_name": rule_name,
                "detail": f"Simulated rule '{rule_name}' rolled back successfully.",
            }
        return {
            "success": True,
            "rule_name": rule_name,
            "detail": f"Simulated rule '{rule_name}' was not active.",
        }

    def verify_rule(self, rule_name: str) -> bool:
        return rule_name in self.active_simulated_rules
