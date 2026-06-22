from __future__ import annotations

import os

from ashare_premarket.providers.failure_classification import classify_provider_failure
from ashare_premarket.providers.failure_events import EVENT_FIELDS, build_failure_events
from ashare_premarket.providers.network_isolation import scoped_finance_network_env
from ashare_premarket.providers.provider_attempt_log import make_attempt


def test_proxy_error_maps_to_specific_proxy_class() -> None:
    result = classify_provider_failure(exc=RuntimeError("ProxyError: Cannot connect to proxy"))
    assert result.failure_class == "EXTERNAL_PROXY_ENVIRONMENT_FAILURE"
    assert result.failure_layer == "network_transport"
    assert result.requires_network_fix is True


def test_proxy_error_after_cleanup_maps_to_child_env_class() -> None:
    result = classify_provider_failure(
        exc=RuntimeError("ProxyError: Cannot connect to proxy"),
        context={"child_proxy_env_present_after_cleanup": False},
    )
    assert result.failure_class == "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED"
    assert result.secondary_failure_class == "EXTERNAL_PROXY_ENVIRONMENT_FAILURE"


def test_network_transport_subclasses_are_specific() -> None:
    assert classify_provider_failure(exc=TimeoutError("request timed out")).failure_class == "EXTERNAL_NETWORK_TIMEOUT"
    assert classify_provider_failure(exc=OSError("NameResolutionError getaddrinfo failed")).failure_class == "DNS_RESOLUTION_FAILURE"
    assert classify_provider_failure(exc=OSError("SSLError certificate verify failed")).failure_class == "TLS_SSL_FAILURE"
    assert classify_provider_failure(exc=OSError("connection reset by peer")).failure_class == "CONNECTION_RESET"
    assert classify_provider_failure(exc=OSError("connection refused")).failure_class == "CONNECTION_REFUSED"


def test_scoped_finance_env_removes_proxy_vars_and_restores_parent(monkeypatch) -> None:
    monkeypatch.setenv("HTTP_PROXY", "http://127.0.0.1:8080")
    before = os.environ["HTTP_PROXY"]
    with scoped_finance_network_env("stock_zh_a_hist", network_enabled=True) as evidence:
        assert "HTTP_PROXY" not in os.environ
        assert evidence["child_proxy_env_present_after_cleanup"] is False
        assert evidence["inherit_system_proxy"] is False
    assert os.environ["HTTP_PROXY"] == before


def test_failure_event_schema_contains_required_network_columns() -> None:
    attempt = make_attempt(
        "akshare",
        "stock_zh_a_hist",
        symbol="600036.SH",
        network_enabled=True,
        status="FAIL",
        failure_class="EXTERNAL_PROXY_ENVIRONMENT_FAILURE",
        notes="provider error: ProxyError",
    )
    event = build_failure_events([attempt], network_enabled=True)[0]
    assert set(EVENT_FIELDS) <= set(event)
    assert event["target_domain"] == "push2his.eastmoney.com"
    assert event["domain_allowed"] is True
    assert event["inherit_system_proxy"] is False
    assert event["primary_failure_class"] == "EXTERNAL_PROXY_ENVIRONMENT_FAILURE"
