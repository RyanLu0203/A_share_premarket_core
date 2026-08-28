from __future__ import annotations

import pytest

from ashare_premarket.interfaces.api.network import require_loopback_host


@pytest.mark.parametrize("host", ["127.0.0.1", "::1", "localhost"])
def test_loopback_hosts_are_allowed(host: str) -> None:
    assert require_loopback_host(host) == host


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.1.20", "example.com", ""])
def test_non_loopback_hosts_are_rejected(host: str) -> None:
    with pytest.raises(ValueError, match="local-only|loopback"):
        require_loopback_host(host)
