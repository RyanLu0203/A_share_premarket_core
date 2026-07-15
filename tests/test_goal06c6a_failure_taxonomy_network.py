from __future__ import annotations

import os

import requests

from ashare_premarket.providers.failure_classification import classify_provider_failure
from ashare_premarket.providers.failure_events import EVENT_FIELDS, build_failure_events
from ashare_premarket.providers.network_isolation import PROXY_ENV_KEYS, scoped_finance_network_env
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
    for key in PROXY_ENV_KEYS:
        monkeypatch.setenv(key, "http://127.0.0.1:8080")
    before = {key: os.environ[key] for key in PROXY_ENV_KEYS}
    discovered = lambda _url, no_proxy=None: {"https": "http://127.0.0.1:1082"}
    monkeypatch.setattr(requests.sessions, "get_environ_proxies", discovered)
    with scoped_finance_network_env("stock_zh_a_hist", network_enabled=True) as evidence:
        assert not any(key in os.environ for key in PROXY_ENV_KEYS)
        assert requests.sessions.get_environ_proxies("https://push2his.eastmoney.com") == {}
        assert evidence["child_proxy_env_present_after_cleanup"] is False
        assert evidence["inherit_system_proxy"] is False
        assert evidence["network_mode"] == "finance_direct_requests_proxy_discovery_disabled"
    assert {key: os.environ[key] for key in PROXY_ENV_KEYS} == before
    assert requests.sessions.get_environ_proxies is discovered


def test_explicit_finance_proxy_authorization_preserves_configured_proxy(monkeypatch) -> None:
    monkeypatch.setenv("HTTPS_PROXY", "http://127.0.0.1:8080")
    monkeypatch.setenv("https_proxy", "http://127.0.0.1:8081")
    monkeypatch.setenv("ASHARE_ALLOW_EXPLICIT_FINANCE_PROXY", "1")
    discovered = lambda _url, no_proxy=None: {"https": "http://127.0.0.1:8080"}
    monkeypatch.setattr(requests.sessions, "get_environ_proxies", discovered)

    with scoped_finance_network_env("stock_zh_a_hist", network_enabled=True) as evidence:
        assert os.environ["HTTPS_PROXY"] == "http://127.0.0.1:8080"
        assert os.environ["https_proxy"] == "http://127.0.0.1:8081"
        assert requests.sessions.get_environ_proxies is discovered
        assert evidence["network_mode"] == "finance_explicit_proxy_authorized"
        assert evidence["inherit_system_proxy"] is True


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
