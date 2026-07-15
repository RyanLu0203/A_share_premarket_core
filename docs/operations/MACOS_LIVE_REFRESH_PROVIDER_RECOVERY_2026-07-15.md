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

## Request-level comparison

The 41-row request table is recorded at
`docs/operations/MACOS_LIVE_REFRESH_REQUEST_ATTEMPTS_2026-07-15.csv`.
Shadowrocket recorded exactly 41 direct connections between `11:30:03` and
`11:30:26`, matching the sorted application request sequence. The original
application run did not persist request elapsed time, HTTP status, response
bytes, or terminal exception details. Those historical cells are explicitly
marked `not captured`; none are inferred or fabricated.

- All 41 calls used AKShare `stock_zh_a_hist`, East Money daily kline, `qfq`,
  `klt=101`, `fqt=1`, `beg=end=20260714`, the same fields and public `ut`
  value, and Shenzhen market prefix `secid=0`.
- The application was sequential with a configured 0.2-second minimum interval
  and no application retry. AKShare `requests.get` constructs a new Requests
  session per call, so the canonical burst did not reuse HTTP connections.
- Accepted rows occurred at positions 27, 30, and 32–36, 15–21 seconds after
  the first request. Failures occurred before, inside, and after that window.
- The success cluster is evidence of temporal/intermittent upstream
  availability, but the interleaved failures show that request order alone is
  not a deterministic acceptance rule.
- Symbol, exchange, date, adjustment, endpoint family, query shape, concurrency,
  and configured request headers do not distinguish the accepted and rejected
  groups.

## Controlled four-symbol matrix

The 20-row matrix is recorded at
`docs/operations/MACOS_LIVE_REFRESH_CONTROLLED_MATRIX_2026-07-15.csv`.
It used prior successes `002594.SZ` and `002920.SZ` plus prior failures
`000002.SZ` and `300628.SZ`.

- Isolated fresh process: 0/4 accepted.
- Same isolated requests repeated after a 3-second pause: 0/4 accepted.
- Exact AKShare `requests.get` behavior, sequential with no added pause: 0/4
  accepted.
- One deliberately reused HTTP session, sequential with 5-second pauses: 0/4
  accepted.
- Exact application `load_stock_ohlcv_daily` wrapper in a fresh child process,
  one-second bounded spacing: 0/4 accepted. The wrapper classified all four as
  `BROWSER_NET_EMPTY_RESPONSE` and returned no normalized rows.
- Every result was `BROWSER_NET_EMPTY_RESPONSE`; every terminal exception was
  Requests `ConnectionError` wrapping `RemoteDisconnected` before any HTTP
  status or response body.
- For the initial 16 raw-request probes, total elapsed time ranged from 0.171
  to 0.754 seconds (mean 0.367); send time ranged from 0.161 to 0.301 seconds
  (mean 0.211). For the four exact application-wrapper probes, total wrapper
  elapsed time ranged from 0.383 to 1.504 seconds and transport time from 0.150
  to 1.260 seconds.
- Headers were constant: `python-requests/2.34.2`, `Accept: */*`, and
  `Connection: keep-alive`.

Previously accepted symbols therefore fail when requested alone. The evidence
rejects a symbol-normalization, exchange, concurrency, connection-reuse, or
simple burst-pacing defect. It supports
`INTERMITTENT_STRUCTURAL_PRIMARY_UPSTREAM_REMOTE_CLOSE` as the root-cause
classification. Responsible pauses did not recover the endpoint, so no retry,
backoff, or pacing change is justified from this observation window.

## Inactive upstream-source proposal

Because the primary endpoint remains structurally unreliable, an explicit
proposal is recorded at
`configs/providers/akshare_stock_history_upstream_policy_proposal.yaml`.
The current primary remains AKShare `stock_zh_a_hist` / East Money. AKShare
`stock_zh_a_hist_tx` / Tencent Securities is named only as a candidate
secondary source. It is not callable by the runtime and cannot activate
automatically.

Activation requires explicit user approval, a resolved Tencent volume/amount
schema contract, bounded overlap and adjustment-consistency checks, complete
current T-1 coverage, full provenance, and fail-closed conflict handling.
Source selection must occur before a run; silent mid-run fallback and partial
snapshots remain forbidden.

## Validation

- Focused provider/network/runtime-policy suite: `39 passed`
- Python 3.12.13 compileall: `PASS`
- Full Python suite: `410 passed, 2 failed`; one existing Starlette/httpx
  deprecation warning. Both failures are stale mutable-runtime baseline
  assertions in `tests/test_global_refactor01_architecture.py`: the tests still
  require `latest_refresh_status=SUCCEEDED` and the former
  `/api/experiment` response hash, while the truthful current refresh evidence
  is `BLOCKED` after the 7/41 live result.
- Canonical program profile: `116 / 117 PASS`, overall `BLOCKED`; the sole
  failed command was the same full Python suite. The other 116 canonical
  commands passed.
- Safety, workflow, adapter, destructive-change, PIT, leakage, workspace, and
  macOS prerequisite audits/checks: `PASS`
- Frontend lint: `PASS`
- Frontend typecheck: `PASS`
- Frontend tests: `35 passed` across 12 files
- Frontend production build: `PASS`

No new live acceptance run was made after the matrix because no responsible
request-level implementation fix was supported by the evidence. The existing
7/41 canonical result remains current and blocked. Calendar synchronization
was not repeated because no acceptance refresh was eligible; the last verified
calendar evidence remains the provider-backed result above. No snapshot or
idempotency checksum exists for this blocked run.

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
