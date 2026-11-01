import sys
import subprocess
from typing import Dict, Any
from app.firewall.base import BaseFirewallAdapter
from app.firewall.action_validator import ActionValidator
from app.core.config import settings
from app.core.exceptions import FirewallExecutionError, PermissionDeniedError
from app.core.logging_config import logger


class WindowsFirewallAdapter(BaseFirewallAdapter):
    """
    Windows Defender Firewall Adapter.
    Executes parameterized netsh commands without arbitrary shell string evaluation.
    Only active when ALLOW_FIREWALL_BLOCKING=true and running on Windows.
    """
    def __init__(self):
        self.is_windows = sys.platform == "win32"

    def block_ip(
        self,
        target_ip: str,
        rule_name: str,
        direction: str = "Inbound",
        duration_min: int = 60,
    ) -> Dict[str, Any]:
        # Enforce application setting safety barrier
        if not settings.ALLOW_FIREWALL_BLOCKING:
            raise PermissionDeniedError(
                "Real firewall blocking is disabled by default in system configuration (ALLOW_FIREWALL_BLOCKING=False). Use simulation mode or enable in .env after administrator verification."
            )

        if not self.is_windows:
            raise FirewallExecutionError("Windows Defender Firewall adapter requires a Windows host.")

        # Strict validation of IP, direction, duration, rule name
        ActionValidator.validate_block_action(target_ip, direction, duration_min, rule_name)

        netsh_dir = "in" if direction.lower() == "inbound" else "out"

        # Parameterized command argument list — never pass unescaped shell strings
        cmd = [
            "netsh",
            "advfirewall",
            "firewall",
            "add",
            "rule",
            f"name={rule_name}",
            f"dir={netsh_dir}",
            "action=block",
            f"remoteip={target_ip}",
            "enable=yes",
            f"description=Managed by SentinelAI Security Center. Duration: {duration_min}m.",
        ]

        logger.info(f"Executing Windows firewall block: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)
            if res.returncode != 0:
                err_msg = res.stderr.strip() or res.stdout.strip()
                logger.error(f"Failed to create Windows firewall rule: {err_msg}")
                raise FirewallExecutionError(f"Windows Defender Firewall error: {err_msg}")

            # Verify rule creation
            verified = self.verify_rule(rule_name)
            if not verified:
                raise FirewallExecutionError("Firewall rule creation succeeded but rule verification check failed.")

            logger.info(f"Successfully created and verified rule '{rule_name}'")
            return {
                "success": True,
                "rule_name": rule_name,
                "verification_status": "verified",
                "detail": f"Windows Defender Firewall rule '{rule_name}' active for {target_ip}.",
            }
        except subprocess.TimeoutExpired:
            raise FirewallExecutionError("Timeout waiting for netsh advfirewall execution.")
        except Exception as e:
            if isinstance(e, (FirewallExecutionError, PermissionDeniedError)):
                raise
            raise FirewallExecutionError(f"Unexpected error executing firewall block: {e}")

    def remove_rule(self, rule_name: str) -> Dict[str, Any]:
        if not self.is_windows:
            return {"success": True, "rule_name": rule_name, "detail": "Non-windows host"}

        # Validate that the rule belongs to SentinelAI before deletion
        if not rule_name.startswith("SentinelAI_Block_"):
            raise FirewallExecutionError(f"Refusing to delete unmanaged firewall rule: {rule_name}")

        cmd = [
            "netsh",
            "advfirewall",
            "firewall",
            "delete",
            "rule",
            f"name={rule_name}",
        ]

        logger.info(f"Executing Windows firewall rule rollback: {' '.join(cmd)}")
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)
            if res.returncode != 0:
                logger.warning(f"Rule removal returned code {res.returncode}: {res.stderr or res.stdout}")
            return {
                "success": True,
                "rule_name": rule_name,
                "detail": f"Firewall rule '{rule_name}' removed.",
            }
        except Exception as e:
            logger.error(f"Failed to remove Windows firewall rule '{rule_name}': {e}")
            raise FirewallExecutionError(f"Error rolling back firewall rule: {e}")

    def verify_rule(self, rule_name: str) -> bool:
        if not self.is_windows:
            return False

        cmd = [
            "netsh",
            "advfirewall",
            "firewall",
            "show",
            "rule",
            f"name={rule_name}",
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=5)
            return res.returncode == 0 and rule_name in res.stdout
        except Exception:
            return False
