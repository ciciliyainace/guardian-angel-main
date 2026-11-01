from app.firewall.base import BaseFirewallAdapter
from app.firewall.simulation_adapter import SimulationFirewallAdapter
from app.firewall.windows_firewall_adapter import WindowsFirewallAdapter
from app.firewall.action_validator import ActionValidator
from app.firewall.protected_targets import ProtectedTargetValidator, target_validator
from app.firewall.rollback_manager import RollbackManager
from app.core.config import settings


def get_firewall_adapter() -> BaseFirewallAdapter:
    """Factory providing the configured firewall adapter (defaults to simulation)."""
    if settings.FIREWALL_MODE == "windows_firewall" and settings.ALLOW_FIREWALL_BLOCKING:
        return WindowsFirewallAdapter()
    return SimulationFirewallAdapter()


__all__ = [
    "BaseFirewallAdapter",
    "SimulationFirewallAdapter",
    "WindowsFirewallAdapter",
    "ActionValidator",
    "ProtectedTargetValidator",
    "target_validator",
    "RollbackManager",
    "get_firewall_adapter",
]
