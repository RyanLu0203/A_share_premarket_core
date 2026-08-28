from __future__ import annotations

from ipaddress import ip_address


def require_loopback_host(value: str) -> str:
    """Return a normalized loopback host or fail closed."""

    host = str(value).strip()
    if host.lower() == "localhost":
        return "localhost"
    try:
        address = ip_address(host)
    except ValueError as exc:
        raise ValueError(
            "the research workspace is local-only; --host must be localhost or a loopback IP"
        ) from exc
    if not address.is_loopback:
        raise ValueError(
            "the research workspace is local-only; non-loopback hosts are forbidden"
        )
    return host
