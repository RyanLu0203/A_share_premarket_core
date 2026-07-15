# macOS live refresh and provider recovery report — 2026-07-15

## Outcome

Repository repair and validation passed, but deployment is
`BLOCKED_EXTERNAL_RUNTIME`. The approved live calendar succeeded; the bounded
market-data refresh returned no accepted T-1 rows through the host's active
VPN/TUN route. The gate correctly wrote no current snapshot. launchd, backend,
frontend, API acceptance, and browser acceptance were therefore not started.

## Source and branch

- Authoritative remote branch: `origin/project-current`
- Authoritative merge commit:
  `d3563eab97f4e422d3da9a6e32430510d4043867`
- Included PR #32 fix commit:
  `7f54f24f1e62f3509f4297162e21c2ef27ffb322`
- Recovery branch: `codex/macos-live-refresh-and-provider-recovery`
- Deployment checkout: `/Users/luxinyu/Desktop/A_share_premarket_core_current`
- The forbidden `codex/runtime-calendar-source-authority-fix` branch was not
  used for deployment.

## Repairs

- `run_macos_daily_refresh.py` passes `replay_date=None` explicitly. A focused
  regression demonstrated that the old call omitted the argument and failed
  before the repair.
- Finance direct mode removes upper/lowercase HTTP, HTTPS, ALL, and NO proxy
  variables and disables Requests environment/system proxy discovery for the
  scoped synchronous call. Process state is restored under a lock.
- Configured proxy use remains possible only with explicit
  `ASHARE_ALLOW_EXPLICIT_FINANCE_PROXY=1` authorization.
- AKShare calls receive a 30-second timeout. TLS verification remains enabled.
  Provider errors remain failures; there is no replay, local-data, proxy, or
  deterministic fallback.

## Live calendar evidence

- Provider/function: `akshare_sina` / `tool_trade_date_hist_sina`
- Status: `VERIFIED`
- Coverage: `1990-12-19` through `2026-12-31`
- Rows: `8797`
- SHA-256:
  `db13387fd42cb1ef98bbde07a12d2f8c64c438eeea940926d4ec49b2a5263d14`
- `2026-06-19`: closed; absent from provider-returned sessions
- PIT: `exchange_schedule_evidence_only_no_market_observation_or_future_return`
- Runtime target: `2026-07-15`
- Expected T-1: `2026-07-14`

The runtime CSV and metadata were written atomically under ignored
`outputs/local/runtime/` paths. Source, coverage, checksum, row count,
committed-fixture conflict provenance, and PIT validation passed.

## Bounded live refresh evidence

- Execution mode: `daily_operational`
- Evidence mode: `live_bounded_fetch`
- Required symbols / attempts: `41 / 41`
- Accepted T-1 rows: `0`
- Result distribution: `41 BROWSER_NET_EMPTY_RESPONSE`
- Last available committed data date: `2026-06-30`
- Validation blockers: `INVALID_PROVIDER_STATE`,
  `MISSING_REQUIRED_EVIDENCE`, `STALE_SOURCE_DATA`
- OPM executed: `false`
- Current snapshot path/checksum: none
- Second live/idempotency run: not permitted because the first run produced no
  verified snapshot

## Reproducible network evidence

- Proxy environment variables were absent.
- macOS system proxy state exposed HTTP/HTTPS `127.0.0.1:1082`; the listener
  was active, but the exact Eastmoney HTTPS request failed through it.
- Requests default mode reproduced a `ProxyError`.
- Scoped direct mode did not rediscover that proxy, but the provider returned
  an empty response.
- Finance DNS names resolved to synthetic `198.18.0.x` addresses.
- Both a synthetic provider address and the real public provider address
  `14.103.188.89` routed through `utun4`; a `curl --resolve --noproxy '*'
  probe` still returned `Empty reply from server`.

This proves that host VPN/TUN interception remains outside the repository's
Requests proxy policy. The concrete unblock is to correct or disable that
local VPN/TUN finance-domain route, verify direct/provider access, and rerun
the canonical live command.

## Validation

- Python 3.12.13 compileall: `PASS`
- Python suite: `410 passed`; one existing Starlette/httpx deprecation warning
- Canonical program profile: `117 / 117 PASS`
- Safety, workflow, adapter, destructive-change, PIT, leakage, workspace, and
  macOS prerequisite audits/checks: `PASS`
- Frontend lint: `PASS`
- Frontend typecheck: `PASS`
- Frontend tests: `35 passed` across 12 files
- Frontend production build: `PASS`

## Deferred deployment acceptance

- Existing plist files still reference rollback directories, but neither
  `com.ashare.premarket.workspace` nor
  `com.ashare.premarket.daily-refresh` is loaded.
- Backend PID / URL: none / `http://127.0.0.1:8000` not started
- Frontend PID / URL: none / `http://127.0.0.1:3000` not started
- Canonical 22-route GET probe and zero-write-route runtime confirmation:
  deferred
- Browser pages, chart ranges, volume, crosshair/tooltip, provider markers,
  console, network, and screenshots: deferred

Old deployment directories remain intact as rollback copies. No old launchd
job or port 8000/3000 process is active. Recommendation, trading, broker,
production, factor-mining, and DQN/RL capabilities remain locked.
