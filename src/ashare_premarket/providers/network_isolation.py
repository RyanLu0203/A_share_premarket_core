from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

EXPLICIT_FINANCE_PROXY_ENV = "ASHARE_ALLOW_EXPLICIT_FINANCE_PROXY"
_PROXY_SCOPE_LOCK = threading.RLock()

PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "NO_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "no_proxy",
)

ALLOWED_FINANCE_DOMAINS = [
    "www.bse.cn",
    "www.akshare.xyz",
    "push2.eastmoney.com",
    "push2his.eastmoney.com",
    "80.push2.eastmoney.com",
    "82.push2.eastmoney.com",
    "quote.eastmoney.com",
    "finance.sina.com.cn",
]

FUNCTION_TARGET_DOMAINS = {
    "stock_info_a_code_name": "www.bse.cn",
    "stock_zh_a_spot_em": "82.push2.eastmoney.com",
    "stock_zh_a_hist": "push2his.eastmoney.com",
    "index_zh_a_hist": "80.push2.eastmoney.com",
    "tool_trade_date_hist_sina": "finance.sina.com.cn",
    "run_goal06c6_source_backed_engineering_pilot_bundle": "akshare_finance_domains",
    "import akshare": "local_dependency_import",
}


@dataclass
class NetworkIsolationEvidence:
    network_scope: str
    network_mode: str
    inherit_system_proxy: bool
    parent_proxy_env_present: bool
    child_proxy_env_present_after_cleanup: bool
    target_domain: str
    domain_allowed: bool
    parent_environment_restored: bool
    proxy_keys_removed_for_scope: str
    safe_notes: str

    def to_dict(self) -> dict[str, object]:
        return {
            "network_scope": self.network_scope,
            "network_mode": self.network_mode,
            "inherit_system_proxy": self.inherit_system_proxy,
            "parent_proxy_env_present": self.parent_proxy_env_present,
            "child_proxy_env_present_after_cleanup": self.child_proxy_env_present_after_cleanup,
            "target_domain": self.target_domain,
            "domain_allowed": self.domain_allowed,
            "parent_environment_restored": self.parent_environment_restored,
            "proxy_keys_removed_for_scope": self.proxy_keys_removed_for_scope,
            "safe_notes": self.safe_notes,
        }


def target_domain_for_function(function_name: str) -> str:
    return FUNCTION_TARGET_DOMAINS.get(function_name, "unknown_finance_provider_domain")


def domain_allowed(domain: str) -> bool:
    if domain in {"", "local_dependency_import", "akshare_finance_domains"}:
        return True
    return domain in ALLOWED_FINANCE_DOMAINS or domain.endswith(".eastmoney.com")


def parent_proxy_env_present(env: dict[str, str] | None = None) -> bool:
    env = env or dict(os.environ)
    return any(key in env and bool(env[key]) for key in PROXY_ENV_KEYS)


def cleaned_child_env(env: dict[str, str] | None = None) -> dict[str, str]:
    child = dict(env or os.environ)
    for key in PROXY_ENV_KEYS:
        child.pop(key, None)
    return child


def child_proxy_env_present_after_cleanup(env: dict[str, str] | None = None) -> bool:
    child = cleaned_child_env(env)
    return parent_proxy_env_present(child)


def explicit_finance_proxy_authorized(env: dict[str, str] | None = None) -> bool:
    environment = env or os.environ
    return str(environment.get(EXPLICIT_FINANCE_PROXY_ENV, "")).strip().lower() in {"1", "true", "yes"}


def isolation_evidence(function_name: str, network_enabled: bool, target_domain: str | None = None) -> NetworkIsolationEvidence:
    domain = target_domain or target_domain_for_function(function_name)
    parent_has_proxy = parent_proxy_env_present()
    explicit_proxy = network_enabled and explicit_finance_proxy_authorized()
    child_has_proxy = parent_has_proxy if explicit_proxy else child_proxy_env_present_after_cleanup()
    mode = (
        "network_disabled_by_policy"
        if not network_enabled
        else "finance_explicit_proxy_authorized"
        if explicit_proxy
        else "finance_direct_requests_proxy_discovery_disabled"
    )
    return NetworkIsolationEvidence(
        network_scope="finance_only",
        network_mode=mode,
        inherit_system_proxy=explicit_proxy,
        parent_proxy_env_present=parent_has_proxy,
        child_proxy_env_present_after_cleanup=child_has_proxy,
        target_domain=domain,
        domain_allowed=domain_allowed(domain),
        parent_environment_restored=True,
        proxy_keys_removed_for_scope="" if explicit_proxy else ";".join(PROXY_ENV_KEYS),
        safe_notes=(
            "finance-only proxy use explicitly authorized; configured proxy discovery preserved"
            if explicit_proxy
            else "finance-only direct mode removes proxy variables and disables Requests environment/system proxy discovery"
        ),
    )


@contextmanager
def scoped_finance_network_env(function_name: str, network_enabled: bool) -> Iterator[dict[str, object]]:
    """Apply one synchronous finance-provider proxy policy and restore process state."""
    with _PROXY_SCOPE_LOCK:
        original = {key: os.environ.get(key) for key in PROXY_ENV_KEYS}
        target_domain = target_domain_for_function(function_name)
        evidence = isolation_evidence(function_name, network_enabled, target_domain).to_dict()
        explicit_proxy = network_enabled and explicit_finance_proxy_authorized()
        requests_sessions = None
        original_get_environ_proxies = None
        if network_enabled and not explicit_proxy:
            for key in PROXY_ENV_KEYS:
                os.environ.pop(key, None)
            evidence["child_proxy_env_present_after_cleanup"] = parent_proxy_env_present()
            evidence["inherit_system_proxy"] = False
            try:
                from requests import sessions as requests_sessions_module

                requests_sessions = requests_sessions_module
                original_get_environ_proxies = requests_sessions.get_environ_proxies
                requests_sessions.get_environ_proxies = lambda _url, no_proxy=None: {}
            except ImportError:
                requests_sessions = None
        try:
            yield evidence
        finally:
            if requests_sessions is not None and original_get_environ_proxies is not None:
                requests_sessions.get_environ_proxies = original_get_environ_proxies
            for key, value in original.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
            restored = all(os.environ.get(key) == value for key, value in original.items())
            evidence["parent_environment_restored"] = restored
