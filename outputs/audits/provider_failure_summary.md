# Provider Failure Summary

GOAL-06C.6A Network Isolation and Failure Taxonomy Readiness: PASS_WITH_WARNINGS
Source bundle health status: `BLOCKED`
AKShare import status: `available`
AKShare version: `1.18.64`
Explicit ingestion attempted: `true`
Selected network mode: `finance_direct_child_env_proxy_cleanup`
System proxy inheritance allowed: `false`
Child proxy env cleanup proven: `true`
Parent environment mutation check: `PASS_RESTORED`
Failure classes: `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED`
GOAL-06D allowed to proceed: `false`

No fake data was used.
No silent fallback to proxy was used.
No global proxy/system/shell/git/npm/pip config was modified.
No cloakbrowser, stealth browser, captcha solving, or proxy-rotation bypass was used.
No heavy local data was committed.

## Layer Distribution
- `network_transport`: `3`

## Raw Failure Mapping
- `index_zh_a_hist`: `ProxyError persisted after finance-scoped proxy env cleanup` -> `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED` (network_transport)
- `stock_info_a_code_name`: `ProxyError persisted after finance-scoped proxy env cleanup` -> `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED` (network_transport)
- `stock_zh_a_spot_em`: `ProxyError persisted after finance-scoped proxy env cleanup` -> `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED` (network_transport)

## Action Buckets
- Code-fixable: ``
- Provider/source issues: ``
- Local network/system issues: `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED`
- Requires user action: `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED`

Recommended next action: Keep GOAL-06D blocked; user may adjust external network/VPN manually or use compliant local import/provider replacement.
