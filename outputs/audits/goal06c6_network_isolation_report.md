# GOAL-06C.6 Network Isolation Report

Status: `PASS_WITH_WARNINGS`
Finance ingestion scope: `finance_only`
Selected network mode: `finance_direct_child_env_proxy_cleanup`
System proxy inheritance allowed: `false`
Child proxy env cleanup proven: `true`
Parent environment mutation check: `PASS_RESTORED`
Allowed finance domains: `www.bse.cn;www.akshare.xyz;push2.eastmoney.com;push2his.eastmoney.com;80.push2.eastmoney.com;82.push2.eastmoney.com;quote.eastmoney.com`
Observed domains: `80.push2.eastmoney.com;82.push2.eastmoney.com;www.bse.cn`

No silent fallback to proxy was used.
No global proxy/system/shell/git/npm/pip config was modified.
Default GOAL-06C.6/GOAL-06C.6A provider evidence used no browser automation; explicit CloakBrowser reference probes are separate tag-only diagnostics.
