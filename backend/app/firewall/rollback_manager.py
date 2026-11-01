from typing import Dict, Any
from app.firewall.base import BaseFirewallAdapter
from app.core.logging_config import logger


class RollbackManager:
    def __init__(self, adapter: BaseFirewallAdapter):
        self.adapter = adapter

    def rollback_rule(self, rule_name: str) -> Dict[str, Any]:
        """
        Safely rollback and clean up a managed firewall rule.
        Verifies existence and records outcome.
        """
        logger.info(f"Initiating rollback for managed rule: {rule_name}")
        try:
            # Check existence first if adapter supports verification
            exists = self.adapter.verify_rule(rule_name)
            result = self.adapter.remove_rule(rule_name)
            return {
                "success": result.get("success", True),
                "rule_name": rule_name,
                "was_active": exists,
                "detail": result.get("detail", "Rollback executed."),
            }
        except Exception as e:
            logger.error(f"Rollback failed for rule {rule_name}: {e}")
            return {
                "success": False,
                "rule_name": rule_name,
                "error": str(e),
                "detail": f"Failed to remove rule: {e}",
            }
