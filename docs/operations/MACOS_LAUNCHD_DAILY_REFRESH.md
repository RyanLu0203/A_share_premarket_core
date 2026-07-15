# macOS launchd daily operation

This runbook installs user-level launch agents for the local read-only research
workspace and the bounded Daily Refresh. It requires no administrator access
and does not enable recommendations, brokers, orders, paper execution,
production trading, factor mining, or DQN/RL.

## What the daily runner does

1. With explicit network authorization, call the approved AKShare/Sina
   `tool_trade_date_hist_sina` calendar source.
2. Atomically write ignored runtime calendar and provenance metadata under
   `outputs/local/runtime/`.
3. Validate source identity, SHA-256, coverage, sorted/unique sessions, and PIT
   schedule semantics. Only source-returned dates are trading sessions.
4. Resolve target and T-1, refresh bounded evidence, run existing validation,
   and invoke the existing research-only OPM snapshot handoff on success.
5. Skip an already-completed target only when the refresh target, T-1,
   snapshot manifest version, and immutable snapshot payload checksums all
   verify.

Provider unavailability, missing coverage, corrupted metadata, checksum
failure, stale T-1 evidence, or OPM failure returns nonzero and fails closed.
Raw provider payloads are not persisted.

## Runtime schedule authority and replay fixtures

The committed `configs/project/trading_calendar.csv` is a deterministic
research fixture. It remains the historical replay default when no runtime
calendar is configured, but it is not an exchange-schedule authority for a
network-authorized macOS run.

For runtime synchronization, only sessions returned by the approved
AKShare/Sina `tool_trade_date_hist_sina` source are written. If the committed
fixture declares a date that the approved source does not, the date is not
inferred or copied into the runtime calendar. The disagreement is recorded in
the ignored metadata as `committed_fixture_conflict_count`,
`committed_fixture_conflict_dates`, and
`committed_fixture_consistency_status`. Calendar status exposes the same
fields for audit.

This separation is required because the deterministic fixture historically
marked `2026-06-19` as regular, while both the approved provider and the
[Shanghai Stock Exchange Dragon Boat Festival notice](https://www.sse.com.cn/disclosure/announcement/general/c/c_20260611_10821419.shtml)
identify `2026-06-19` as closed. Runtime metadata must still pass provider,
function, checksum, coverage, row-count, source-only-session, and PIT checks;
missing or tampered configured runtime evidence continues to fail closed.

## Prerequisites and checks

From the authoritative checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[data,test]'
npm install --prefix apps/premarket-workspace
.venv/bin/python scripts/install_macos_launchd.py --check
.venv/bin/python scripts/run_macos_daily_refresh.py --check
python scripts/run_premarket_workspace.py --check
```

The install check validates macOS, the repository virtual environment, the two
runners, and frontend dependencies. It does not call providers or write
runtime evidence.

## Install

```bash
.venv/bin/python scripts/install_macos_launchd.py
```

This writes and loads:

- `~/Library/LaunchAgents/com.ashare.premarket.workspace.plist`
- `~/Library/LaunchAgents/com.ashare.premarket.daily-refresh.plist`

The read-only workspace starts at login and is kept alive. Daily Refresh runs
Monday through Friday at 07:45 local time. To install and immediately request
one refresh:

```bash
.venv/bin/python scripts/install_macos_launchd.py --run-refresh-now
```

## Status and service checks

```bash
.venv/bin/python scripts/install_macos_launchd.py --status
launchctl print "gui/$(id -u)/com.ashare.premarket.workspace"
launchctl print "gui/$(id -u)/com.ashare.premarket.daily-refresh"
curl -fsS http://127.0.0.1:8000/api/health
curl -fsS http://127.0.0.1:8000/api/status
curl -fsS http://127.0.0.1:3000/
```

The status API separately reports system readiness, historical replay,
research-dashboard availability, quant lock state, calendar provenance and
coverage, and snapshot-resolution status. A blocked live system does not hide
verified historical replay or research snapshot panels.

## Manual daily run

```bash
.venv/bin/python scripts/run_macos_daily_refresh.py --allow-network
```

Network permission is scoped to the calendar and bounded evidence refresh.
Ordinary workspace and deterministic replay processes do not receive provider
network authorization.

The default finance-provider mode removes uppercase and lowercase proxy
variables for the synchronous call and disables Requests environment/system
proxy discovery. This prevents an enabled macOS system proxy from being
silently rediscovered after environment cleanup. A deliberately configured
proxy remains supported only when
`ASHARE_ALLOW_EXPLICIT_FINANCE_PROXY=1` is set alongside the normal network
authorization. TLS verification and provider timeouts remain enabled; provider
failure never triggers a replay or local-data fallback.

If the provider still returns empty responses while DNS answers are in
`198.18.0.0/15` and routes traverse a `utun` interface, the host VPN/TUN layer
is still intercepting so-called direct traffic. Correct the local VPN/proxy
route, then rerun the manual daily command. Do not install the launch agents
until the live run creates and verifies the current snapshot.

## Local files and logs

- Calendar: `outputs/local/runtime/trading_calendar.csv`
- Calendar metadata: `outputs/local/runtime/trading_calendar_metadata.json`
- Workspace logs: `outputs/local/runtime/launchd/workspace.*.log`
- Refresh logs: `outputs/local/runtime/launchd/daily-refresh.*.log`

These paths are ignored and must not be committed. Immutable research
snapshots retain their existing governed locations and checksum contracts.

## Uninstall

```bash
.venv/bin/python scripts/install_macos_launchd.py --uninstall
```

Uninstall unloads and removes only the two user LaunchAgent plists. It does not
delete the repository, virtual environment, local logs, or research evidence.
