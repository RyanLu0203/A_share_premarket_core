# Provider Failure Classification Audit

Status: `PASS`
Goal: `GOAL-06C.6A`
Failure classes: `78`
Failure layers: `12`
ProxyError, timeout, DNS, TLS, HTTP access, anti-bot, schema, parser, data quality, PIT/label, storage, and workflow failures are specifically classified.
No raw HTML challenge pages are stored in GitHub.
Default provider classification uses no browser automation; explicit CloakBrowser reference probes are separate tag-only diagnostics.

## Layer Coverage
- `policy`: `8`
- `dependency`: `6`
- `network_transport`: `9`
- `http_access`: `7`
- `anti_bot_access`: `5`
- `provider_contract`: `7`
- `parser_implementation`: `5`
- `data_quality`: `10`
- `pit_calendar_label`: `7`
- `storage_bundle`: `7`
- `workflow_governance`: `5`
- `unknown`: `2`

## Decision Matrix
- `PROVIDER_OK` -> owner: provider; action: no failure observed
- `NETWORK_DISABLED_BY_POLICY` -> owner: project policy; action: explicitly enable finance ingestion only when intended
- `PROVIDER_DISABLED_BY_POLICY` -> owner: project policy; action: provider is intentionally disabled
- `NON_FINANCE_DOMAIN_BLOCKED` -> owner: project policy; action: block non-finance domain access
- `NON_FINANCE_DOMAIN_FLAGGED` -> owner: project policy; action: fix the scoped workflow policy violation
- `SYSTEM_PROXY_NOT_ALLOWED_IN_SCOPE` -> owner: project policy; action: run finance-scoped direct environment; do not inherit system proxy silently
- `EXPLICIT_PROXY_REQUIRED_BUT_MISSING` -> owner: project policy; action: fix the scoped workflow policy violation
- `SILENT_PROXY_FALLBACK_BLOCKED` -> owner: project policy; action: fail closed instead of silently falling back to proxy settings
- `GLOBAL_CONFIG_MUTATION_DETECTED` -> owner: project policy; action: restore global config and remove mutation path
- `DEPENDENCY_MISSING` -> owner: local dependency; action: install optional data dependency
- `AKSHARE_IMPORT_FAILED` -> owner: local dependency; action: install or repair AKShare
- `AKSHARE_VERSION_UNSUPPORTED` -> owner: local dependency; action: install or pin the required optional dependency
- `TARGET_FUNCTION_MISSING` -> owner: provider contract; action: replace provider function or pin provider version
- `TARGET_FUNCTION_SIGNATURE_UNSUPPORTED` -> owner: provider contract; action: update wrapper signature filtering and tests
- `OPTIONAL_DEPENDENCY_MISSING` -> owner: local dependency; action: install or pin the required optional dependency
- `EXTERNAL_PROXY_ENVIRONMENT_FAILURE` -> owner: local environment / scoped network config; action: run finance direct child env; keep global VPN/proxy unchanged
- `EXTERNAL_SYSTEM_PROXY_OR_VPN_ROUTE_FAILURE` -> owner: system route / VPN mode; action: classify only; do not modify global settings; user may adjust external VPN manually if desired
- `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED` -> owner: external network path; action: child proxy env was cleaned but provider path still failed; use compliant fallback or local import
- `DNS_RESOLUTION_FAILURE` -> owner: local environment / external network; action: classify network path; do not modify global proxy or VPN settings
- `TLS_SSL_FAILURE` -> owner: local environment / external network; action: classify network path; do not modify global proxy or VPN settings
- `CONNECTION_RESET` -> owner: local environment / external network; action: classify network path; do not modify global proxy or VPN settings
- `CONNECTION_REFUSED` -> owner: local environment / external network; action: classify network path; do not modify global proxy or VPN settings
- `EXTERNAL_NETWORK_TIMEOUT` -> owner: external network; action: retry later within rate limits; keep GOAL-06D blocked until data coverage exists
- `UNKNOWN_NETWORK_FAILURE` -> owner: local environment / external network; action: classify network path; do not modify global proxy or VPN settings
- `HTTP_403_FORBIDDEN` -> owner: provider access policy / website restriction; action: do not bypass; use fallback provider or local import
- `HTTP_404_NOT_FOUND` -> owner: provider access policy; action: do not bypass; use a compliant provider or local import
- `HTTP_429_RATE_LIMITED` -> owner: provider rate limit; action: wait or reduce request rate; do not bypass
- `HTTP_5XX_PROVIDER_ERROR` -> owner: provider availability; action: retry later or use fallback provider
- `EXTERNAL_WEBSITE_ACCESS_RESTRICTED` -> owner: provider access policy; action: do not bypass; use a compliant provider or local import
- `AUTH_OR_CONSENT_REQUIRED` -> owner: provider access policy; action: do not bypass; use a compliant provider or local import
- `TERMS_OR_ROBOTS_RESTRICTED` -> owner: provider access policy; action: do not bypass; use a compliant provider or local import
- `BOT_CHALLENGE_DETECTED` -> owner: provider access restriction; action: do not bypass; disable provider or use compliant source
- `CAPTCHA_OR_VERIFY_PAGE` -> owner: provider access restriction; action: do not solve captcha; use compliant source or manual local import
- `HTML_RETURNED_INSTEAD_OF_DATA` -> owner: provider access restriction; action: do not bypass challenge pages; disable provider or use a compliant source
- `JS_CHALLENGE_DETECTED` -> owner: provider access restriction; action: do not bypass challenge pages; disable provider or use a compliant source
- `LOGIN_OR_CONSENT_WALL_DETECTED` -> owner: provider access restriction; action: do not bypass challenge pages; disable provider or use a compliant source
- `CONTRACT_SCHEMA_MISMATCH` -> owner: provider contract; action: update schema normalization and tests
- `REQUIRED_COLUMN_MISSING` -> owner: provider contract; action: update schema normalization or provider contract
- `COLUMN_TYPE_MISMATCH` -> owner: provider contract; action: update type normalization and tests
- `DATE_FORMAT_MISMATCH` -> owner: provider contract; action: update schema normalization and tests
- `SYMBOL_FORMAT_MISMATCH` -> owner: provider contract; action: update schema normalization and tests
- `PROVIDER_FIELD_RENAMED` -> owner: provider contract; action: update schema normalization and tests
- `PROVIDER_RETURN_TYPE_UNSUPPORTED` -> owner: provider contract; action: update schema normalization and tests
- `IMPLEMENTATION_PARSER_FAILURE` -> owner: project code; action: fix parser / normalization
- `NORMALIZATION_FAILURE` -> owner: project code; action: fix parser, normalization, or write path
- `CANONICAL_SCHEMA_WRITE_FAILURE` -> owner: project code; action: fix parser, normalization, or write path
- `UNHANDLED_EXCEPTION` -> owner: project code; action: fix parser, normalization, or write path
- `BUG_IN_PROVIDER_WRAPPER` -> owner: project code; action: fix parser, normalization, or write path
- `EMPTY_RESPONSE` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `ZERO_ROWS_RETURNED` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `INSUFFICIENT_SYMBOL_COVERAGE` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `INSUFFICIENT_DATE_COVERAGE` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `INSUFFICIENT_PANEL_ROWS` -> owner: data coverage; action: expand universe/date/provider; keep GOAL-06D blocked
- `DUPLICATE_ROWS_DETECTED` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `MISSING_OHLCV_VALUES` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `INVALID_PRICE_VALUES` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `SUSPENSION_OR_STALE_DATA_DETECTED` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `OUTLIER_OR_BAD_TICK_DETECTED` -> owner: data coverage; action: expand universe, date range, provider, or local import; keep GOAL-06D blocked
- `TRADING_CALENDAR_INSUFFICIENT` -> owner: project PIT/label logic; action: block panel and fix PIT/calendar/label builder
- `TRADING_DAY_ALIGNMENT_FAILURE` -> owner: project PIT/label logic; action: block panel and fix PIT/calendar/label builder
- `PIT_CUTOFF_VIOLATION` -> owner: project logic; action: block panel; fix PIT builder
- `LABEL_LOOKAHEAD_ALIGNMENT_FAILURE` -> owner: project PIT/label logic; action: block panel and fix PIT/calendar/label builder
- `LABEL_READY_ROWS_INSUFFICIENT` -> owner: project PIT/label logic; action: block panel and fix PIT/calendar/label builder
- `LABEL_LEAKAGE_RISK` -> owner: project logic; action: block panel; fix label alignment
- `FEATURE_LABEL_JOIN_FAILURE` -> owner: project PIT/label logic; action: block panel and fix PIT/calendar/label builder
- `LOCAL_DATA_ROOT_MISSING` -> owner: storage policy; action: fix local bundle path or remove forbidden staged artifacts
- `LOCAL_DATA_ROOT_NOT_WRITABLE` -> owner: storage policy; action: fix local bundle path or remove forbidden staged artifacts
- `BUNDLE_MANIFEST_WRITE_FAILURE` -> owner: storage policy; action: fix local bundle path or remove forbidden staged artifacts
- `LOCAL_BUNDLE_WRITE_FAILURE` -> owner: storage policy; action: fix local bundle path or remove forbidden staged artifacts
- `CHECKSUM_FAILURE` -> owner: storage policy; action: fix local bundle path or remove forbidden staged artifacts
- `HEAVY_DATA_STAGED_FOR_GIT` -> owner: storage policy; action: unstage/remove heavy data; keep only samples/audits
- `GITHUB_STORAGE_POLICY_VIOLATION` -> owner: storage policy; action: fix local bundle path or remove forbidden staged artifacts
- `WORKFLOW_STATUS_INCONSISTENT` -> owner: workflow governance; action: fix workflow status and locked-boundary evidence
- `WORKFLOW_CLEANLINESS_FAILURE` -> owner: workflow governance; action: fix workflow status and locked-boundary evidence
- `DUPLICATE_ACTIVE_CANONICAL_PATH` -> owner: workflow governance; action: fix workflow status and locked-boundary evidence
- `GOAL06D_UNBLOCKED_WITHOUT_ENGINEERING_PILOT` -> owner: workflow governance; action: re-lock GOAL-06D until engineering_pilot exists
- `DOWNSTREAM_LOCK_VIOLATION` -> owner: workflow governance; action: fix workflow status and locked-boundary evidence
- `UNKNOWN_PROVIDER_FAILURE` -> owner: triage; action: capture safe metadata and add a specific classifier

## Failures
