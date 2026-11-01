import ipaddress
from typing import List, Tuple
from app.core.config import settings


def parse_ip_address(ip_str: str) -> Tuple[bool, ipaddress.IPv4Address | ipaddress.IPv6Address | None, str]:
    """Parse and validate an IP address string. Returns (is_valid, ip_obj, error_message)."""
    if not ip_str or not isinstance(ip_str, str):
        return False, None, "Target IP address is required."
    
    clean_ip = ip_str.strip()
    try:
        ip_obj = ipaddress.ip_address(clean_ip)
        return True, ip_obj, ""
    except ValueError as e:
        return False, None, f"Invalid IP address format: {clean_ip} ({e})"


def is_protected_ip(ip_str: str, custom_protected_ips: List[str] = None, custom_protected_nets: List[str] = None) -> Tuple[bool, str]:
    """
    Check if an IP address belongs to protected/forbidden ranges.
    Returns (is_protected, reason).
    """
    is_valid, ip_obj, error = parse_ip_address(ip_str)
    if not is_valid:
        return True, f"Invalid IP: {error}"

    # Check loopback
    if ip_obj.is_loopback:
        return True, f"Address {ip_str} is a loopback address and cannot be blocked."

    # Check multicast
    if ip_obj.is_multicast:
        return True, f"Address {ip_str} is a multicast address and cannot be blocked."

    # Check link-local
    if ip_obj.is_link_local:
        return True, f"Address {ip_str} is a link-local address and cannot be blocked."

    # Check unspecified (0.0.0.0 or ::)
    if ip_obj.is_unspecified:
        return True, f"Address {ip_str} is an unspecified address and cannot be blocked."

    # Check configured protected IPs
    protected_ips = custom_protected_ips if custom_protected_ips is not None else settings.PROTECTED_IPS
    for p_ip in protected_ips:
        try:
            if ip_obj == ipaddress.ip_address(p_ip.strip()):
                return True, f"Address {ip_str} is listed in system PROTECTED_IPS."
        except ValueError:
            continue

    # Check configured protected subnets
    protected_nets = custom_protected_nets if custom_protected_nets is not None else settings.PROTECTED_NETWORKS
    for net in protected_nets:
        try:
            net_obj = ipaddress.ip_network(net.strip(), strict=False)
            if ip_obj in net_obj:
                return True, f"Address {ip_str} belongs to protected network {net}."
        except ValueError:
            continue

    return False, ""
