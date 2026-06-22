from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

BROWSER_PROVIDER_CONFIG = "configs/providers/browser_assisted_provider_config.yaml"
SWITCH_CONFIG = "configs/providers/browser_provider_switches.yaml"
TRUE_VALUES = {"1", "true", "TRUE", "yes", "YES"}


@dataclass(frozen=True)
class BrowserProviderPolicy:
    project_default: bool
    explicit_opt_in_env: str
    allowed_domains: tuple[str, ...]
    temporary_cache_cleaned_by_default: bool


def load_browser_provider_policy(root: Path) -> BrowserProviderPolicy:
    payload = json.loads((root / BROWSER_PROVIDER_CONFIG).read_text(encoding="utf-8"))
    runtime = payload.get("runtime", {})
    return BrowserProviderPolicy(
        project_default=bool(payload.get("project_default", False)),
        explicit_opt_in_env=str(payload.get("explicit_opt_in_env", "ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER")),
        allowed_domains=tuple(str(item) for item in payload.get("allowed_finance_domains", [])),
        temporary_cache_cleaned_by_default=bool(runtime.get("temporary_cache_cleaned_by_default", True)),
    )


def browser_assisted_enabled(root: Path, cli_enabled: bool = False) -> bool:
    policy = load_browser_provider_policy(root)
    return bool(cli_enabled and os.environ.get(policy.explicit_opt_in_env, "") in TRUE_VALUES)


def browser_domain_allowed(root: Path, url: str) -> bool:
    policy = load_browser_provider_policy(root)
    domain = urlparse(url).netloc
    return domain in policy.allowed_domains or domain.endswith(".eastmoney.com")


def target_domain(url: str) -> str:
    return urlparse(url).netloc
