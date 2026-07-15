# macOS live refresh and provider recovery report — 2026-07-15

## Outcome

Repository repair and validation passed, but deployment remains blocked. After
Shadowrocket split routing was verified for `push2his.eastmoney.com`, the
application child-process provider path no longer attempted
`127.0.0.1:1082`; it connected directly to the synthetic finance route. The
bounded market-data refresh improved from 0 accepted rows to 7 accepted T-1
rows, but 34 required rows were still missing/failed. The gate correctly wrote
no current snapshot. launchd, backend, frontend, API acceptance, and browser
acceptance were therefore not started.

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
- Accepted T-1 rows: `7`
- Rejected/missing required T-1 rows: `34`
- Accepted symbols: `002594.SZ`, `002736.SZ`, `002821.SZ`, `002841.SZ`,
  `002916.SZ`, `002920.SZ`, `300015.SZ`
- Missing symbols: `000002.SZ`, `000063.SZ`, `000100.SZ`, `000157.SZ`,
  `000166.SZ`, `000333.SZ`, `000338.SZ`, `000425.SZ`, `000568.SZ`,
  `000596.SZ`, `000651.SZ`, `000725.SZ`, `000786.SZ`, `000895.SZ`,
  `000938.SZ`, `000963.SZ`, `001979.SZ`, `002236.SZ`, `002241.SZ`,
  `002311.SZ`, `002352.SZ`, `002371.SZ`, `002415.SZ`, `002460.SZ`,
  `002466.SZ`, `002493.SZ`, `002601.SZ`, `002714.SZ`, `002812.SZ`,
  `300033.SZ`, `300059.SZ`, `300122.SZ`, `300502.SZ`, `300628.SZ`
- Latest available data date: `2026-07-14`
- Validation blockers: `INVALID_PROVIDER_STATE`, `MISSING_REQUIRED_EVIDENCE`
- OPM executed: `false`
- Current snapshot path/checksum: none
- Second live/idempotency run: not permitted because the first run produced no
  verified snapshot
- Refresh manifest checksum:
  `21fcf987e52110cd709fc274ee43efd28e72b4cfe6eeaccc0a6324f84012f064`
- Canonical candidate checksum:
  `e9c5e1aa94c0b9eec16d62d3e02f7ec085a5ee3a6cc442632798f536c4e4a39c`
- Incremental live-source checksum:
  `1453a6b9514c6244936d002ba2588fdf3d88cbe7479fcdfcc87750214419167d`

## Reproducible network evidence

- Shadowrocket request log confirmed
  `push2his.eastmoney.com:443`, `DOMAIN,push2his.eastmoney.com,DIRECT`,
  `HTTPS`.
- macOS system proxy state still exposes HTTP/HTTPS `127.0.0.1:1082`.
- The exact unwrapped AKShare call under Python 3.12.13 still used Requests
  default `trust_env=True`, attempted `127.0.0.1:1082`, and failed with
  `ProxyError`.
- The exact application child-process provider invocation for
  `stock_zh_a_hist` did not attempt `127.0.0.1:1082`; socket evidence showed
  zero localhost:1082 connects and one direct connect to `198.18.0.39:443`.
- Direct Python and `curl --noproxy '*'` probes of the exact East Money kline
  endpoint path
  `/api/qt/stock/kline/get?fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61%2Cf116&ut=7eea3edcaed734bea9cbfc24409ed989&klt=101&fqt=1&secid=0.000002&beg=20260714&end=20260714`
  connected to `198.18.0.39:443` and failed as an empty response /
  remote-close-without-HTTP-status.
- Date, adjustment, and browser-like header variants produced the same empty
  response classification for the probed endpoint, which points away from a
  simple AKShare request-shape or date-only issue and toward intermittent
  provider endpoint availability, route-level behavior, or anti-bot handling on
  the exact kline API path.

The repository's scoped Requests policy is still working for the application
path, but PR #33 is not ready to merge because the canonical live refresh has
not produced a complete accepted T-1 snapshot.

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
