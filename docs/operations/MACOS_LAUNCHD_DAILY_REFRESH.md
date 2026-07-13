# macOS launchd operation

This runbook installs user-level launch agents for the local, read-only premarket research workspace and its bounded Daily Refresh. It does not install a daemon, request administrator privileges, or unlock recommendations, orders, brokers, paper trading, or production trading.

## Prerequisites

From the authoritative `project-current` checkout:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[data]'
cd apps/premarket-workspace && npm install && cd ../..
```

## Install

```bash
.venv/bin/python scripts/install_macos_launchd.py
```

This writes and loads:

- `~/Library/LaunchAgents/com.ashare.premarket.workspace.plist`
- `~/Library/LaunchAgents/com.ashare.premarket.daily-refresh.plist`

The workspace starts at login and is kept alive. The Daily Refresh runs Monday through Friday at 07:45 local time. It first synchronizes the ignored source-backed runtime trading calendar and then uses the AKShare primary/Sina fallback ladder for the bounded T-1 refresh.

If the same target/T-1 pair already has a successful immutable refresh and snapshot manifest, the runner exits successfully as `ALREADY_SUCCEEDED`. This makes weekend pre-runs safe when the next weekday schedule resolves to the same target.

Run one refresh immediately during installation with:

```bash
.venv/bin/python scripts/install_macos_launchd.py --run-refresh-now
```

## Verify

```bash
.venv/bin/python scripts/install_macos_launchd.py --status
curl -fsS http://127.0.0.1:8000/health
curl -fsS http://127.0.0.1:3000/
```

Logs are local-only under `outputs/local/runtime/launchd/`. The runtime calendar and metadata are under `outputs/local/runtime/` and are excluded from Git.

## Uninstall

```bash
.venv/bin/python scripts/install_macos_launchd.py --uninstall
```

Uninstalling unloads and removes only these two user launch-agent plists. It does not delete the repository, virtual environment, snapshots, or logs.

## Troubleshooting

- If port 3000 or 8000 is already occupied, stop the older manually launched workspace before kickstarting the agent.
- Inspect `workspace.stderr.log`, `workspace.stdout.log`, `daily-refresh.stderr.log`, and `daily-refresh.stdout.log` in the launchd log directory.
- A provider fallback warning is recoverable evidence, not silent success. A missing expected T-1 row, missing symbol, invalid timestamp, checksum failure, or unrecovered provider failure remains blocked.
- Network ingestion remains explicitly scoped to the daily runner. Ordinary deterministic replay continues to use the committed calendar and network-disabled provider behavior.
- The workspace resolves stale mutable pointers against newer verified immutable snapshots. If the UI shows an older date after a successful refresh, restart `com.ashare.premarket.workspace` and check `/api/status` before rerunning ingestion.
- Approved symbols outside the current OPM snapshot may be added to the browser-local watchlist as `EVIDENCE_PENDING`; unavailable price, band, weight, and risk fields remain `N/A` until a separately governed evidence expansion admits them.
- Blocked/pending symbols may appear only in the browser-local observation basket as `BLOCKED_PENDING_OBSERVATION_ONLY`. This label never unlocks active outputs, paper positions, simulated orders, P&L, or advice.

Refresh selected observation-only symbols with explicit network authorization:

```bash
.venv/bin/python scripts/run_observation_basket_refresh.py --allow-network --symbols 002475.SZ 601138.SH 601208.SH
```

The command writes sanitized T-1 rows only to ignored `outputs/local/runtime/observation_basket.json`. `akshare` identifies the Eastmoney-backed primary endpoint; `akshare_sina` identifies the Sina endpoint reached through AKShare fallback.
