from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ashare_premarket.core.io import read_csv, read_json, write_text

GOAL_ID = "GOAL-06C.6A"

FAILURE_LAYERS = [
    "policy",
    "dependency",
    "network_transport",
    "http_access",
    "anti_bot_access",
    "browser_runtime",
    "provider_contract",
    "parser_implementation",
    "data_quality",
    "pit_calendar_label",
    "storage_bundle",
    "workflow_governance",
    "unknown",
]

POLICY_FAILURES = [
    "NETWORK_DISABLED_BY_POLICY",
    "PROVIDER_DISABLED_BY_POLICY",
    "NON_FINANCE_DOMAIN_BLOCKED",
    "NON_FINANCE_DOMAIN_FLAGGED",
    "SYSTEM_PROXY_NOT_ALLOWED_IN_SCOPE",
    "EXPLICIT_PROXY_REQUIRED_BUT_MISSING",
    "SILENT_PROXY_FALLBACK_BLOCKED",
    "GLOBAL_CONFIG_MUTATION_DETECTED",
]

DEPENDENCY_FAILURES = [
    "DEPENDENCY_MISSING",
    "AKSHARE_IMPORT_FAILED",
    "AKSHARE_VERSION_UNSUPPORTED",
    "TARGET_FUNCTION_MISSING",
    "TARGET_FUNCTION_SIGNATURE_UNSUPPORTED",
    "OPTIONAL_DEPENDENCY_MISSING",
]

NETWORK_TRANSPORT_FAILURES = [
    "EXTERNAL_PROXY_ENVIRONMENT_FAILURE",
    "EXTERNAL_SYSTEM_PROXY_OR_VPN_ROUTE_FAILURE",
    "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED",
    "DNS_RESOLUTION_FAILURE",
    "TLS_SSL_FAILURE",
    "CONNECTION_RESET",
    "CONNECTION_REFUSED",
    "EXTERNAL_NETWORK_TIMEOUT",
    "UNKNOWN_NETWORK_FAILURE",
]

HTTP_ACCESS_FAILURES = [
    "HTTP_403_FORBIDDEN",
    "HTTP_404_NOT_FOUND",
    "HTTP_429_RATE_LIMITED",
    "HTTP_5XX_PROVIDER_ERROR",
    "EXTERNAL_WEBSITE_ACCESS_RESTRICTED",
    "AUTH_OR_CONSENT_REQUIRED",
    "TERMS_OR_ROBOTS_RESTRICTED",
]

ANTI_BOT_FAILURES = [
    "BOT_CHALLENGE_DETECTED",
    "CAPTCHA_OR_VERIFY_PAGE",
    "HTML_RETURNED_INSTEAD_OF_DATA",
    "JS_CHALLENGE_DETECTED",
    "LOGIN_OR_CONSENT_WALL_DETECTED",
]

BROWSER_ASSISTED_FAILURES = [
    "BROWSER_RUNTIME_DEPENDENCY_MISSING",
    "BROWSER_RUNTIME_LAUNCH_FAILED",
    "BROWSER_NAVIGATION_FAILED",
    "BROWSER_NET_EMPTY_RESPONSE",
    "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY",
    "BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED",
    "BROWSER_ASSISTED_ATTEMPTED_NOT_SOLVED",
    "BROWSER_ASSISTED_FORBIDDEN_BY_POLICY",
    "BROWSER_ASSISTED_SCHEMA_MISMATCH",
    "BROWSER_ASSISTED_PARSER_FAILURE",
    "BROWSER_ASSISTED_ACCESS_RESTRICTION_DETECTED",
]

PROVIDER_CONTRACT_FAILURES = [
    "CONTRACT_SCHEMA_MISMATCH",
    "REQUIRED_COLUMN_MISSING",
    "COLUMN_TYPE_MISMATCH",
    "DATE_FORMAT_MISMATCH",
    "SYMBOL_FORMAT_MISMATCH",
    "PROVIDER_FIELD_RENAMED",
    "PROVIDER_RETURN_TYPE_UNSUPPORTED",
    "TENCENT_BJ_UPSTREAM_UNSUPPORTED",
]

PARSER_IMPLEMENTATION_FAILURES = [
    "IMPLEMENTATION_PARSER_FAILURE",
    "NORMALIZATION_FAILURE",
    "CANONICAL_SCHEMA_WRITE_FAILURE",
    "UNHANDLED_EXCEPTION",
    "BUG_IN_PROVIDER_WRAPPER",
]

DATA_QUALITY_FAILURES = [
    "EMPTY_RESPONSE",
    "ZERO_ROWS_RETURNED",
    "INSUFFICIENT_SYMBOL_COVERAGE",
    "INSUFFICIENT_DATE_COVERAGE",
    "INSUFFICIENT_PANEL_ROWS",
    "DUPLICATE_ROWS_DETECTED",
    "MISSING_OHLCV_VALUES",
    "INVALID_PRICE_VALUES",
    "SUSPENSION_OR_STALE_DATA_DETECTED",
    "OUTLIER_OR_BAD_TICK_DETECTED",
]

PIT_CALENDAR_LABEL_FAILURES = [
    "TRADING_CALENDAR_INSUFFICIENT",
    "TRADING_DAY_ALIGNMENT_FAILURE",
    "PIT_CUTOFF_VIOLATION",
    "LABEL_LOOKAHEAD_ALIGNMENT_FAILURE",
    "LABEL_READY_ROWS_INSUFFICIENT",
    "LABEL_LEAKAGE_RISK",
    "FEATURE_LABEL_JOIN_FAILURE",
]

STORAGE_BUNDLE_FAILURES = [
    "LOCAL_DATA_ROOT_MISSING",
    "LOCAL_DATA_ROOT_NOT_WRITABLE",
    "BUNDLE_MANIFEST_WRITE_FAILURE",
    "LOCAL_BUNDLE_WRITE_FAILURE",
    "CHECKSUM_FAILURE",
    "HEAVY_DATA_STAGED_FOR_GIT",
    "GITHUB_STORAGE_POLICY_VIOLATION",
]

WORKFLOW_GOVERNANCE_FAILURES = [
    "WORKFLOW_STATUS_INCONSISTENT",
    "WORKFLOW_CLEANLINESS_FAILURE",
    "DUPLICATE_ACTIVE_CANONICAL_PATH",
    "GOAL06D_UNBLOCKED_WITHOUT_ENGINEERING_PILOT",
    "DOWNSTREAM_LOCK_VIOLATION",
]

FAILURE_CLASSES = [
    "PROVIDER_OK",
    *POLICY_FAILURES,
    *DEPENDENCY_FAILURES,
    *NETWORK_TRANSPORT_FAILURES,
    *HTTP_ACCESS_FAILURES,
    *ANTI_BOT_FAILURES,
    *BROWSER_ASSISTED_FAILURES,
    *PROVIDER_CONTRACT_FAILURES,
    *PARSER_IMPLEMENTATION_FAILURES,
    *DATA_QUALITY_FAILURES,
    *PIT_CALENDAR_LABEL_FAILURES,
    *STORAGE_BUNDLE_FAILURES,
    *WORKFLOW_GOVERNANCE_FAILURES,
    "UNKNOWN_PROVIDER_FAILURE",
]

FAILURE_CLASS_TO_LAYER: dict[str, str] = {
    **{failure_class: "policy" for failure_class in POLICY_FAILURES},
    **{failure_class: "dependency" for failure_class in DEPENDENCY_FAILURES},
    **{failure_class: "network_transport" for failure_class in NETWORK_TRANSPORT_FAILURES},
    **{failure_class: "http_access" for failure_class in HTTP_ACCESS_FAILURES},
    **{failure_class: "anti_bot_access" for failure_class in ANTI_BOT_FAILURES},
    **{
        "BROWSER_RUNTIME_DEPENDENCY_MISSING": "dependency",
        "BROWSER_RUNTIME_LAUNCH_FAILED": "browser_runtime",
        "BROWSER_NAVIGATION_FAILED": "browser_runtime",
        "BROWSER_NET_EMPTY_RESPONSE": "network_transport",
        "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY": "browser_runtime",
        "BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED": "unknown",
        "BROWSER_ASSISTED_ATTEMPTED_NOT_SOLVED": "browser_runtime",
        "BROWSER_ASSISTED_FORBIDDEN_BY_POLICY": "policy",
        "BROWSER_ASSISTED_SCHEMA_MISMATCH": "provider_contract",
        "BROWSER_ASSISTED_PARSER_FAILURE": "parser_implementation",
        "BROWSER_ASSISTED_ACCESS_RESTRICTION_DETECTED": "anti_bot_access",
    },
    **{failure_class: "provider_contract" for failure_class in PROVIDER_CONTRACT_FAILURES},
    **{failure_class: "parser_implementation" for failure_class in PARSER_IMPLEMENTATION_FAILURES},
    **{failure_class: "data_quality" for failure_class in DATA_QUALITY_FAILURES},
    **{failure_class: "pit_calendar_label" for failure_class in PIT_CALENDAR_LABEL_FAILURES},
    **{failure_class: "storage_bundle" for failure_class in STORAGE_BUNDLE_FAILURES},
    **{failure_class: "workflow_governance" for failure_class in WORKFLOW_GOVERNANCE_FAILURES},
    "PROVIDER_OK": "unknown",
    "UNKNOWN_PROVIDER_FAILURE": "unknown",
}


@dataclass(frozen=True)
class FailureDecision:
    owner: str
    action: str
    retry_allowed: bool = False
    fallback_allowed: bool = False
    requires_user_action: bool = False
    requires_provider_replacement: bool = False
    requires_schema_update: bool = False
    requires_code_fix: bool = False
    requires_network_fix: bool = False
    goal06d_allowed_after_failure: bool = False


DEFAULT_DECISIONS_BY_LAYER: dict[str, FailureDecision] = {
    "policy": FailureDecision("project policy", "fix the scoped workflow policy violation", requires_code_fix=True),
    "dependency": FailureDecision("local dependency", "install or pin the required optional dependency", requires_user_action=True),
    "network_transport": FailureDecision(
        "local environment / external network",
        "classify network path; do not modify global proxy or VPN settings",
        retry_allowed=True,
        fallback_allowed=True,
        requires_user_action=True,
        requires_network_fix=True,
    ),
    "http_access": FailureDecision(
        "provider access policy",
        "do not bypass; use a compliant provider or local import",
        fallback_allowed=True,
        requires_user_action=True,
        requires_provider_replacement=True,
    ),
    "anti_bot_access": FailureDecision(
        "provider access restriction",
        "do not bypass challenge pages; disable provider or use a compliant source",
        fallback_allowed=True,
        requires_user_action=True,
        requires_provider_replacement=True,
    ),
    "browser_runtime": FailureDecision(
        "optional browser-assisted provider",
        "treat browser access as explicit opt-in only; count only schema-valid finance rows",
        fallback_allowed=True,
        requires_user_action=True,
    ),
    "provider_contract": FailureDecision(
        "provider contract",
        "update schema normalization and tests",
        requires_schema_update=True,
        requires_code_fix=True,
    ),
    "parser_implementation": FailureDecision("project code", "fix parser, normalization, or write path", requires_code_fix=True),
    "data_quality": FailureDecision(
        "data coverage",
        "expand universe, date range, provider, or local import; keep GOAL-06D blocked",
        fallback_allowed=True,
        requires_user_action=True,
    ),
    "pit_calendar_label": FailureDecision("project PIT/label logic", "block panel and fix PIT/calendar/label builder", requires_code_fix=True),
    "storage_bundle": FailureDecision(
        "storage policy",
        "fix local bundle path or remove forbidden staged artifacts",
        requires_user_action=True,
        requires_code_fix=True,
    ),
    "workflow_governance": FailureDecision("workflow governance", "fix workflow status and locked-boundary evidence", requires_code_fix=True),
    "unknown": FailureDecision("triage", "capture safe metadata and add a specific classifier", requires_code_fix=True),
}

FAILURE_DECISION_OVERRIDES: dict[str, FailureDecision] = {
    "PROVIDER_OK": FailureDecision("provider", "no failure observed"),
    "NETWORK_DISABLED_BY_POLICY": FailureDecision("project policy", "explicitly enable finance ingestion only when intended"),
    "PROVIDER_DISABLED_BY_POLICY": FailureDecision("project policy", "provider is intentionally disabled"),
    "NON_FINANCE_DOMAIN_BLOCKED": FailureDecision("project policy", "block non-finance domain access", requires_code_fix=True),
    "SYSTEM_PROXY_NOT_ALLOWED_IN_SCOPE": FailureDecision(
        "project policy",
        "run finance-scoped direct environment; do not inherit system proxy silently",
        requires_network_fix=True,
    ),
    "SILENT_PROXY_FALLBACK_BLOCKED": FailureDecision(
        "project policy",
        "fail closed instead of silently falling back to proxy settings",
        requires_code_fix=True,
    ),
    "GLOBAL_CONFIG_MUTATION_DETECTED": FailureDecision(
        "project policy",
        "restore global config and remove mutation path",
        requires_code_fix=True,
        requires_user_action=True,
    ),
    "DEPENDENCY_MISSING": FailureDecision("local dependency", "install optional data dependency", requires_user_action=True),
    "AKSHARE_IMPORT_FAILED": FailureDecision("local dependency", "install or repair AKShare", requires_user_action=True),
    "TARGET_FUNCTION_MISSING": FailureDecision("provider contract", "replace provider function or pin provider version", requires_provider_replacement=True, requires_schema_update=True),
    "TARGET_FUNCTION_SIGNATURE_UNSUPPORTED": FailureDecision(
        "provider contract",
        "update wrapper signature filtering and tests",
        requires_schema_update=True,
        requires_code_fix=True,
    ),
    "EXTERNAL_PROXY_ENVIRONMENT_FAILURE": FailureDecision(
        "local environment / scoped network config",
        "run finance direct child env; keep global VPN/proxy unchanged",
        fallback_allowed=True,
        requires_user_action=True,
        requires_network_fix=True,
    ),
    "EXTERNAL_SYSTEM_PROXY_OR_VPN_ROUTE_FAILURE": FailureDecision(
        "system route / VPN mode",
        "classify only; do not modify global settings; user may adjust external VPN manually if desired",
        fallback_allowed=True,
        requires_user_action=True,
        requires_network_fix=True,
    ),
    "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED": FailureDecision(
        "external network path",
        "child proxy env was cleaned but provider path still failed; use compliant fallback or local import",
        fallback_allowed=True,
        requires_user_action=True,
        requires_network_fix=True,
    ),
    "EXTERNAL_NETWORK_TIMEOUT": FailureDecision(
        "external network",
        "retry later within rate limits; keep GOAL-06D blocked until data coverage exists",
        retry_allowed=True,
        fallback_allowed=True,
        requires_network_fix=True,
    ),
    "HTTP_403_FORBIDDEN": FailureDecision(
        "provider access policy / website restriction",
        "do not bypass; use fallback provider or local import",
        fallback_allowed=True,
        requires_user_action=True,
        requires_provider_replacement=True,
    ),
    "HTTP_429_RATE_LIMITED": FailureDecision(
        "provider rate limit",
        "wait or reduce request rate; do not bypass",
        retry_allowed=True,
        requires_user_action=True,
    ),
    "HTTP_5XX_PROVIDER_ERROR": FailureDecision(
        "provider availability",
        "retry later or use fallback provider",
        retry_allowed=True,
        fallback_allowed=True,
        requires_provider_replacement=True,
    ),
    "BOT_CHALLENGE_DETECTED": FailureDecision(
        "provider access restriction",
        "do not bypass; disable provider or use compliant source",
        fallback_allowed=True,
        requires_user_action=True,
        requires_provider_replacement=True,
    ),
    "CAPTCHA_OR_VERIFY_PAGE": FailureDecision(
        "provider access restriction",
        "do not solve captcha; use compliant source or manual local import",
        fallback_allowed=True,
        requires_user_action=True,
        requires_provider_replacement=True,
    ),
    "BROWSER_RUNTIME_DEPENDENCY_MISSING": FailureDecision(
        "local optional dependency",
        "install CloakBrowser/Playwright only in an explicit temporary runtime if browser-assisted ingestion is intended",
        fallback_allowed=True,
        requires_user_action=True,
    ),
    "BROWSER_RUNTIME_LAUNCH_FAILED": FailureDecision(
        "optional browser runtime",
        "fix the temporary browser runtime or use direct/local provider fallback",
        retry_allowed=True,
        fallback_allowed=True,
        requires_user_action=True,
    ),
    "BROWSER_NAVIGATION_FAILED": FailureDecision(
        "optional browser runtime",
        "retry within rate limits or use a compliant provider fallback",
        retry_allowed=True,
        fallback_allowed=True,
        requires_user_action=True,
    ),
    "BROWSER_NET_EMPTY_RESPONSE": FailureDecision(
        "external finance website network",
        "classify separately from generic network failures; retry later or use local import",
        retry_allowed=True,
        fallback_allowed=True,
        requires_network_fix=True,
    ),
    "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY": FailureDecision(
        "optional browser-assisted provider",
        "domain access alone is not ingestion success; parser/schema-valid rows are still required",
        fallback_allowed=True,
        requires_code_fix=True,
    ),
    "BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED": FailureDecision(
        "optional browser-assisted provider",
        "structured schema-valid finance rows were obtained by explicit browser-assisted provider",
    ),
    "BROWSER_ASSISTED_ATTEMPTED_NOT_SOLVED": FailureDecision(
        "optional browser-assisted provider",
        "browser was attempted but did not return schema-valid rows",
        fallback_allowed=True,
        requires_user_action=True,
    ),
    "BROWSER_ASSISTED_FORBIDDEN_BY_POLICY": FailureDecision(
        "project policy",
        "do not use browser-assisted provider outside explicit finance-domain opt-in policy",
        requires_code_fix=True,
    ),
    "BROWSER_ASSISTED_SCHEMA_MISMATCH": FailureDecision(
        "provider contract",
        "update schema normalization or mark this provider attempt unsolved",
        fallback_allowed=True,
        requires_schema_update=True,
        requires_code_fix=True,
    ),
    "BROWSER_ASSISTED_PARSER_FAILURE": FailureDecision(
        "project code",
        "fix browser-assisted parser; do not store raw browser payloads in GitHub",
        requires_code_fix=True,
    ),
    "BROWSER_ASSISTED_ACCESS_RESTRICTION_DETECTED": FailureDecision(
        "provider access restriction",
        "do not bypass challenge/login/captcha; use fallback provider or local import",
        fallback_allowed=True,
        requires_user_action=True,
        requires_provider_replacement=True,
    ),
    "CONTRACT_SCHEMA_MISMATCH": FailureDecision("provider contract", "update schema normalization and tests", requires_schema_update=True, requires_code_fix=True),
    "REQUIRED_COLUMN_MISSING": FailureDecision("provider contract", "update schema normalization or provider contract", requires_schema_update=True, requires_code_fix=True),
    "COLUMN_TYPE_MISMATCH": FailureDecision("provider contract", "update type normalization and tests", requires_schema_update=True, requires_code_fix=True),
    "IMPLEMENTATION_PARSER_FAILURE": FailureDecision("project code", "fix parser / normalization", requires_code_fix=True),
    "INSUFFICIENT_PANEL_ROWS": FailureDecision(
        "data coverage",
        "expand universe/date/provider; keep GOAL-06D blocked",
        fallback_allowed=True,
        requires_user_action=True,
    ),
    "PIT_CUTOFF_VIOLATION": FailureDecision("project logic", "block panel; fix PIT builder", requires_code_fix=True),
    "LABEL_LEAKAGE_RISK": FailureDecision("project logic", "block panel; fix label alignment", requires_code_fix=True),
    "HEAVY_DATA_STAGED_FOR_GIT": FailureDecision(
        "storage policy",
        "unstage/remove heavy data; keep only samples/audits",
        requires_user_action=True,
        requires_code_fix=True,
    ),
    "GOAL06D_UNBLOCKED_WITHOUT_ENGINEERING_PILOT": FailureDecision(
        "workflow governance",
        "re-lock GOAL-06D until engineering_pilot exists",
        requires_code_fix=True,
    ),
}


@dataclass(frozen=True)
class FailureClassification:
    failure_class: str
    retry_allowed: bool
    notes: str
    failure_layer: str = "unknown"
    secondary_failure_class: str = ""
    fallback_allowed: bool = False
    requires_user_action: bool = False
    requires_provider_replacement: bool = False
    requires_schema_update: bool = False
    requires_code_fix: bool = False
    requires_network_fix: bool = False
    goal06d_allowed_after_failure: bool = False
    owner: str = "triage"
    action: str = "capture safe metadata and add a specific classifier"


def classify_provider_failure(
    exc: BaseException | None = None,
    response_text: str | None = None,
    status_code: int | None = None,
    context: dict[str, object] | None = None,
) -> FailureClassification:
    context = context or {}
    text = (response_text or "").lower()
    exc_type = type(exc).__name__ if exc else ""
    message = f"{exc_type}: {exc}".lower() if exc else ""
    combined = f"{text} {message}"

    if status_code == 403:
        return _classification("HTTP_403_FORBIDDEN", "provider returned HTTP 403")
    if status_code == 404:
        return _classification("HTTP_404_NOT_FOUND", "provider returned HTTP 404")
    if status_code == 429:
        return _classification("HTTP_429_RATE_LIMITED", "provider returned HTTP 429")
    if status_code is not None and 500 <= status_code <= 599:
        return _classification("HTTP_5XX_PROVIDER_ERROR", f"provider returned HTTP {status_code}")

    dependency = _classify_dependency(combined, exc_type)
    if dependency:
        return dependency

    network = _classify_network(combined, context)
    if network:
        return network

    challenge = _classify_challenge(combined)
    if challenge:
        return challenge

    contract = _classify_contract(combined)
    if contract:
        return contract

    if "parse" in combined or "parser" in combined:
        return _classification("IMPLEMENTATION_PARSER_FAILURE", "provider parser failed")
    if "normalization" in combined or "normalize" in combined:
        return _classification("NORMALIZATION_FAILURE", "provider normalization failed")
    if "write" in combined and "schema" in combined:
        return _classification("CANONICAL_SCHEMA_WRITE_FAILURE", "canonical schema write failed")
    if exc is not None:
        return _classification("UNHANDLED_EXCEPTION", f"provider error: {exc_type}")
    return _classification("UNKNOWN_PROVIDER_FAILURE", "unknown provider failure")


def classify_provider_success(rows_returned: int, schema_valid: bool) -> FailureClassification:
    if rows_returned <= 0:
        return _classification("ZERO_ROWS_RETURNED", "provider returned zero rows")
    if not schema_valid:
        return _classification("CONTRACT_SCHEMA_MISMATCH", "provider returned rows but schema normalization failed")
    return _classification("PROVIDER_OK", "provider returned normalized rows")


def classify_schema_contract(
    required_columns: set[str] | None = None,
    observed_columns: set[str] | None = None,
    type_errors: dict[str, str] | None = None,
    date_format_error: bool = False,
    symbol_format_error: bool = False,
    return_type_supported: bool = True,
) -> FailureClassification:
    required_columns = required_columns or set()
    observed_columns = observed_columns or set()
    missing = sorted(required_columns - observed_columns)
    if missing:
        return _classification("REQUIRED_COLUMN_MISSING", f"missing required columns: {','.join(missing)}")
    if type_errors:
        return _classification("COLUMN_TYPE_MISMATCH", f"column type mismatch: {','.join(sorted(type_errors))}")
    if date_format_error:
        return _classification("DATE_FORMAT_MISMATCH", "provider date format mismatch")
    if symbol_format_error:
        return _classification("SYMBOL_FORMAT_MISMATCH", "provider symbol format mismatch")
    if not return_type_supported:
        return _classification("PROVIDER_RETURN_TYPE_UNSUPPORTED", "provider return type is unsupported")
    return _classification("PROVIDER_OK", "provider contract matches")


def classify_parser_exception(exc: BaseException) -> FailureClassification:
    return _classification("IMPLEMENTATION_PARSER_FAILURE", f"parser exception: {type(exc).__name__}")


def classify_data_quality(
    symbol_count: int,
    trading_date_count: int,
    row_count: int,
    min_symbols: int = 50,
    min_trading_dates: int = 120,
    min_rows: int = 6000,
    duplicate_rows: bool = False,
    missing_ohlcv: bool = False,
    invalid_prices: bool = False,
) -> FailureClassification:
    if row_count <= 0:
        return _classification("ZERO_ROWS_RETURNED", "panel returned zero rows")
    if symbol_count < min_symbols:
        return _classification("INSUFFICIENT_SYMBOL_COVERAGE", "symbol coverage is below engineering_pilot target")
    if trading_date_count < min_trading_dates:
        return _classification("INSUFFICIENT_DATE_COVERAGE", "date coverage is below engineering_pilot target")
    if row_count < min_rows:
        return _classification("INSUFFICIENT_PANEL_ROWS", "panel rows are below engineering_pilot target")
    if duplicate_rows:
        return _classification("DUPLICATE_ROWS_DETECTED", "duplicate panel rows detected")
    if missing_ohlcv:
        return _classification("MISSING_OHLCV_VALUES", "required OHLCV values are missing")
    if invalid_prices:
        return _classification("INVALID_PRICE_VALUES", "invalid price values detected")
    return _classification("PROVIDER_OK", "data quality thresholds pass")


def classification_for_class(
    failure_class: str,
    notes: str = "",
    secondary_failure_class: str = "",
) -> FailureClassification:
    if not secondary_failure_class and failure_class == "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED":
        secondary_failure_class = "EXTERNAL_PROXY_ENVIRONMENT_FAILURE"
    return _classification(failure_class, notes or failure_class, secondary_failure_class=secondary_failure_class)


def failure_layer_for(failure_class: str) -> str:
    return FAILURE_CLASS_TO_LAYER.get(failure_class, "unknown")


def decision_for_class(failure_class: str) -> FailureDecision:
    layer = failure_layer_for(failure_class)
    return FAILURE_DECISION_OVERRIDES.get(failure_class, DEFAULT_DECISIONS_BY_LAYER.get(layer, DEFAULT_DECISIONS_BY_LAYER["unknown"]))


def retry_allowed(failure_class: str) -> bool:
    return decision_for_class(failure_class).retry_allowed


def audit_provider_failure_classification(root: Path) -> bool:
    failures: list[str] = []
    expected = set(FAILURE_CLASSES)
    if len(expected) != len(FAILURE_CLASSES):
        failures.append("duplicate provider failure class")
    for layer in FAILURE_LAYERS:
        if layer != "unknown" and layer not in set(FAILURE_CLASS_TO_LAYER.values()):
            failures.append(f"missing failure layer coverage: {layer}")
    for required in [
        "NETWORK_DISABLED_BY_POLICY",
        "EXTERNAL_PROXY_ENVIRONMENT_FAILURE",
        "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED",
        "EXTERNAL_NETWORK_TIMEOUT",
        "DNS_RESOLUTION_FAILURE",
        "TLS_SSL_FAILURE",
        "HTTP_403_FORBIDDEN",
        "HTTP_429_RATE_LIMITED",
        "HTTP_5XX_PROVIDER_ERROR",
        "BOT_CHALLENGE_DETECTED",
        "CAPTCHA_OR_VERIFY_PAGE",
        "HTML_RETURNED_INSTEAD_OF_DATA",
        "BROWSER_RUNTIME_DEPENDENCY_MISSING",
        "BROWSER_RUNTIME_LAUNCH_FAILED",
        "BROWSER_NAVIGATION_FAILED",
        "BROWSER_NET_EMPTY_RESPONSE",
        "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY",
        "BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED",
        "BROWSER_ASSISTED_ATTEMPTED_NOT_SOLVED",
        "BROWSER_ASSISTED_FORBIDDEN_BY_POLICY",
        "BROWSER_ASSISTED_SCHEMA_MISMATCH",
        "BROWSER_ASSISTED_PARSER_FAILURE",
        "BROWSER_ASSISTED_ACCESS_RESTRICTION_DETECTED",
        "TARGET_FUNCTION_MISSING",
        "TARGET_FUNCTION_SIGNATURE_UNSUPPORTED",
        "REQUIRED_COLUMN_MISSING",
        "COLUMN_TYPE_MISMATCH",
        "IMPLEMENTATION_PARSER_FAILURE",
        "INSUFFICIENT_PANEL_ROWS",
        "PIT_CUTOFF_VIOLATION",
        "HEAVY_DATA_STAGED_FOR_GIT",
        "GOAL06D_UNBLOCKED_WITHOUT_ENGINEERING_PILOT",
    ]:
        if required not in expected:
            failures.append(f"missing failure class: {required}")

    mapping_checks = {
        "proxy": classify_provider_failure(exc=RuntimeError("ProxyError: cannot connect to proxy")).failure_class,
        "timeout": classify_provider_failure(exc=TimeoutError("request timed out")).failure_class,
        "dns": classify_provider_failure(exc=OSError("NameResolutionError: getaddrinfo failed")).failure_class,
        "ssl": classify_provider_failure(exc=OSError("SSLError certificate verify failed")).failure_class,
        "browser-empty": classify_provider_failure(exc=RuntimeError("ERR_EMPTY_RESPONSE from browser navigation")).failure_class,
        "browser-dep": classification_for_class("BROWSER_RUNTIME_DEPENDENCY_MISSING").failure_class,
        "403": classify_provider_failure(status_code=403).failure_class,
        "429": classify_provider_failure(status_code=429).failure_class,
        "captcha": classify_provider_failure(response_text="<html>captcha verify</html>").failure_class,
    }
    expected_mappings = {
        "proxy": {"EXTERNAL_PROXY_ENVIRONMENT_FAILURE"},
        "timeout": {"EXTERNAL_NETWORK_TIMEOUT"},
        "dns": {"DNS_RESOLUTION_FAILURE"},
        "ssl": {"TLS_SSL_FAILURE"},
        "browser-empty": {"BROWSER_NET_EMPTY_RESPONSE"},
        "browser-dep": {"BROWSER_RUNTIME_DEPENDENCY_MISSING"},
        "403": {"HTTP_403_FORBIDDEN"},
        "429": {"HTTP_429_RATE_LIMITED"},
        "captcha": {"CAPTCHA_OR_VERIFY_PAGE"},
    }
    for name, actual in mapping_checks.items():
        if actual not in expected_mappings[name]:
            failures.append(f"{name} mapped to {actual}")
    if any(cls in {"NETWORK_ERROR", "TIMEOUT", "SCHEMA_CHANGED"} for cls in FAILURE_CLASSES):
        failures.append("legacy generic failure class remains in active taxonomy")

    try:
        from ashare_premarket.providers.failure_events import write_goal06c6a_failure_evidence
        from ashare_premarket.providers.provider_attempt_log import make_attempt

        attempt_path = root / "outputs/audits/akshare_provider_attempt_summary.csv"
        attempts = read_csv(attempt_path) if attempt_path.exists() else []
        if not attempts:
            attempts = [
                make_attempt(
                    "akshare",
                    "audit_provider_failure_classification",
                    network_enabled=False,
                    status="FAIL",
                    failure_class="NETWORK_DISABLED_BY_POLICY",
                    retry_allowed=False,
                    notes="network_disabled_by_policy",
                )
            ]
        manifest_path = root / "outputs/audits/source_backed_bundle_manifest_summary.json"
        manifest = read_json(manifest_path) if manifest_path.exists() else {}
        write_goal06c6a_failure_evidence(
            root,
            attempts,
            network_enabled=any(row.get("network_enabled") in {True, "true"} for row in attempts),
            manifest=manifest,
        )
    except Exception as exc:  # pragma: no cover - defensive audit path
        failures.append(f"failed to write GOAL-06C.6A failure evidence: {type(exc).__name__}: {exc}")

    status = "PASS" if not failures else "BLOCKED"
    layer_counts = {layer: sum(1 for cls in FAILURE_CLASSES if failure_layer_for(cls) == layer) for layer in FAILURE_LAYERS}
    matrix_lines = []
    for failure_class in FAILURE_CLASSES:
        decision = decision_for_class(failure_class)
        matrix_lines.append(f"- `{failure_class}` -> owner: {decision.owner}; action: {decision.action}")
    write_text(
        root / "outputs/audits/provider_failure_classification_audit.md",
        "\n".join(
            [
                "# Provider Failure Classification Audit",
                "",
                f"Status: `{status}`",
                f"Goal: `{GOAL_ID}`",
                f"Failure classes: `{len(FAILURE_CLASSES)}`",
                f"Failure layers: `{len(FAILURE_LAYERS)}`",
                "ProxyError, timeout, DNS, TLS, HTTP access, anti-bot, browser-assisted optional runtime, schema, parser, data quality, PIT/label, storage, and workflow failures are specifically classified.",
                "No raw HTML challenge pages are stored in GitHub.",
                "Default provider classification uses no browser automation; explicit browser-assisted ingestion is opt-in and counted only when schema-valid rows are produced.",
                "",
                "## Layer Coverage",
                *[f"- `{layer}`: `{count}`" for layer, count in layer_counts.items()],
                "",
                "## Decision Matrix",
                *matrix_lines,
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return not failures


def _classify_challenge(combined: str) -> FailureClassification | None:
    if "terms" in combined or "robots" in combined or "robot.txt" in combined:
        return _classification("TERMS_OR_ROBOTS_RESTRICTED", "terms or robots restriction detected")
    if "captcha" in combined or "验证码" in combined:
        return _classification("CAPTCHA_OR_VERIFY_PAGE", "captcha or verification page detected")
    if ("verify" in combined and "certificate verify" not in combined) or "验证" in combined or "安全检查" in combined:
        return _classification("CAPTCHA_OR_VERIFY_PAGE", "verification challenge detected")
    if "javascript" in combined or "js challenge" in combined or "enable js" in combined:
        return _classification("JS_CHALLENGE_DETECTED", "javascript challenge detected")
    if "bot" in combined or "robot" in combined or "爬虫" in combined:
        return _classification("BOT_CHALLENGE_DETECTED", "bot challenge detected")
    if "login" in combined or "consent wall" in combined or "auth" in combined or "授权" in combined:
        return _classification("LOGIN_OR_CONSENT_WALL_DETECTED", "login or consent wall detected")
    if "<html" in combined or "<!doctype html" in combined:
        return _classification("HTML_RETURNED_INSTEAD_OF_DATA", "HTML returned instead of structured finance data")
    return None


def _classify_dependency(combined: str, exc_type: str) -> FailureClassification | None:
    if "modulenotfounderror" in combined or "no module named" in combined or exc_type == "ModuleNotFoundError":
        if "akshare" in combined:
            return _classification("AKSHARE_IMPORT_FAILED", "AKShare import failed")
        return _classification("DEPENDENCY_MISSING", "optional data dependency is missing")
    if "akshare" in combined and "version" in combined and ("unsupported" in combined or "incompatible" in combined):
        return _classification("AKSHARE_VERSION_UNSUPPORTED", "AKShare version is unsupported")
    if "has no attribute" in combined or "missing target function" in combined or "function missing" in combined:
        return _classification("TARGET_FUNCTION_MISSING", "target provider function is missing")
    if "unexpected keyword" in combined or "missing required positional" in combined or "signature" in combined:
        return _classification("TARGET_FUNCTION_SIGNATURE_UNSUPPORTED", "target provider function signature is unsupported")
    return None


def _classify_network(combined: str, context: dict[str, object]) -> FailureClassification | None:
    child_cleaned = bool(context.get("child_proxy_env_cleaned") or context.get("child_proxy_env_present_after_cleanup") is False)
    if "proxyerror" in combined or "cannot connect to proxy" in combined or "proxy error" in combined:
        if child_cleaned:
            return _classification(
                "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED",
                "ProxyError persisted after finance-scoped proxy env cleanup",
                secondary_failure_class="EXTERNAL_PROXY_ENVIRONMENT_FAILURE",
            )
        if "vpn" in combined or "tun" in combined or "route" in combined:
            return _classification("EXTERNAL_SYSTEM_PROXY_OR_VPN_ROUTE_FAILURE", "external system proxy or VPN route failure")
        return _classification("EXTERNAL_PROXY_ENVIRONMENT_FAILURE", "external proxy environment failure")
    if "err_empty_response" in combined or "remote end closed connection" in combined:
        return _classification("BROWSER_NET_EMPTY_RESPONSE", "browser or finance endpoint returned an empty response")
    if "timed out" in combined or "timeout" in combined or "read timed out" in combined:
        return _classification("EXTERNAL_NETWORK_TIMEOUT", "provider request timed out")
    if "getaddrinfo" in combined or "nameresolutionerror" in combined or "temporary failure in name resolution" in combined:
        return _classification("DNS_RESOLUTION_FAILURE", "DNS resolution failed")
    if "ssl" in combined or "certificate" in combined or "tls" in combined:
        return _classification("TLS_SSL_FAILURE", "TLS or certificate validation failed")
    if "connection reset" in combined or "connection aborted" in combined:
        return _classification("CONNECTION_RESET", "connection reset by peer")
    if "connection refused" in combined or "failed to establish a new connection" in combined:
        return _classification("CONNECTION_REFUSED", "connection refused")
    if "network" in combined or "connection" in combined or "requestexception" in combined:
        return _classification("UNKNOWN_NETWORK_FAILURE", "network failure could not be made more specific")
    return None


def _classify_contract(combined: str) -> FailureClassification | None:
    if "required column" in combined or "missing column" in combined:
        return _classification("REQUIRED_COLUMN_MISSING", "required provider column is missing")
    if "type mismatch" in combined or "could not convert" in combined or "dtype" in combined:
        return _classification("COLUMN_TYPE_MISMATCH", "provider column type mismatch")
    if "date format" in combined:
        return _classification("DATE_FORMAT_MISMATCH", "provider date format mismatch")
    if "symbol format" in combined:
        return _classification("SYMBOL_FORMAT_MISMATCH", "provider symbol format mismatch")
    if "schema" in combined or "columns" in combined:
        return _classification("CONTRACT_SCHEMA_MISMATCH", "provider schema did not match expected contract")
    return None


def _classification(
    failure_class: str,
    notes: str,
    secondary_failure_class: str = "",
) -> FailureClassification:
    decision = decision_for_class(failure_class)
    layer = failure_layer_for(failure_class)
    return FailureClassification(
        failure_class=failure_class,
        failure_layer=layer,
        secondary_failure_class=secondary_failure_class,
        retry_allowed=decision.retry_allowed,
        fallback_allowed=decision.fallback_allowed,
        requires_user_action=decision.requires_user_action,
        requires_provider_replacement=decision.requires_provider_replacement,
        requires_schema_update=decision.requires_schema_update,
        requires_code_fix=decision.requires_code_fix,
        requires_network_fix=decision.requires_network_fix,
        goal06d_allowed_after_failure=decision.goal06d_allowed_after_failure,
        owner=decision.owner,
        action=decision.action,
        notes=_safe_note(notes),
    )


def _safe_note(value: Any) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ")
    if len(text) > 240:
        return text[:237] + "..."
    return text
