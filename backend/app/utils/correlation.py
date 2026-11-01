import uuid
import hashlib


def generate_correlation_id() -> str:
    """Generate a unique correlation ID for tracing operations across components."""
    return f"corr-{uuid.uuid4().hex[:12]}"


def compute_event_fingerprint(source_ip: str, dest_ip: str, src_port: int, dst_port: int, protocol: str) -> str:
    """Compute an MD5 hash fingerprint of flow 5-tuple for fast deduplication lookup."""
    raw = f"{source_ip}:{src_port}->{dest_ip}:{dst_port}|{protocol.upper()}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()
