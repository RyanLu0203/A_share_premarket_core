# Local Mac Operation Runbook

This runbook operates the research-only A-Share Premarket Workspace on an
Apple Silicon Mac. It does not authorize recommendation tiering, orders,
paper trading, broker access, or production trading. The governed state remains
`ready_factor_count = 0`.

## Local paths and services

- Repository: `/Users/luxinyu/Desktop/A_share_premarket_core_deploy`
- Python environment: `.venv`
- Read-only API: `http://127.0.0.1:8000`
- API documentation: `http://127.0.0.1:8000/docs`
- Workspace: `http://127.0.0.1:3000`

All commands below run from the repository root unless a step says otherwise.

## One-time setup

```bash
cd /Users/luxinyu/Desktop/A_share_premarket_core_deploy
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]' pytest requests
cd apps/premarket-workspace
npm install
npm run lint
npm run build
cd ../..
python -m compileall -q .
python -m pytest -q
```

`requests` is currently required by the provider ladder but is not declared in
the package metadata. Keep it local to `.venv` until the dependency contract is
corrected through a reviewed code change.

## Daily startup

1. Activate the environment.

   ```bash
   cd /Users/luxinyu/Desktop/A_share_premarket_core_deploy
   source .venv/bin/activate
   ```

2. Refresh governed daily evidence.

   ```bash
   python scripts/run_daily_incremental_evidence_refresh.py
   ```

   Network ingestion remains disabled unless separately and explicitly
   authorized. The refresh validates evidence before invoking OPM01 and does
   not advance the latest valid snapshot when validation fails.

3. Run or re-run OPM01 after the refresh is valid.

   ```bash
   python scripts/run_premarket_position_management.py
   ```

   A fail-closed result is expected when trading-calendar coverage or T-1
   evidence is unavailable. Do not bypass freshness, PIT, provider, quarantine,
   or checksum failures.

4. Start the GET-only API in terminal A.

   ```bash
   source .venv/bin/activate
   python scripts/run_premarket_workspace_api.py
   ```

5. Start the dashboard in terminal B.

   ```bash
   cd /Users/luxinyu/Desktop/A_share_premarket_core_deploy/apps/premarket-workspace
   npm run dev
   ```

The combined launcher is available as
`python scripts/run_premarket_workspace.py`, but separate terminals make
service health and shutdown easier to inspect.

## Daily checks

Check the refresh pointer first:

```bash
python -m json.tool outputs/research/daily_incremental_evidence_refresh/latest_refresh.json
python -m json.tool outputs/research/premarket_position_management/latest_manifest.json
```

Confirm all of the following before using the workspace for shadow observation:

- Target date, expected T-1 date, and latest evidence date align.
- Refresh and snapshot timestamps are current for the governed trading date.
- Snapshot checksum status is verified and the referenced manifest exists.
- PIT and cutoff status pass; there is no future-dated evidence.
- Provider warnings and quarantines are visible and unchanged.
- Risk state, constraint count, position-band count, and abstention count are
  present.
- Live readiness is not treated as current when the workspace reports
  `BLOCKED`, `STALE_SOURCE_DATA`, or missing trading-calendar coverage.
- `ready_factor_count` remains `0`, Recommendation Tiering remains locked, and
  no BUY/SELL/HOLD or execution output exists.

Quick service checks:

```bash
python scripts/run_premarket_workspace_api.py --check
curl --fail --silent http://127.0.0.1:8000/api/health
curl --fail --silent http://127.0.0.1:8000/api/status
```

## Shutdown

Press `Ctrl+C` once in the dashboard terminal and once in the API terminal.
Then confirm the ports are no longer listening:

```bash
lsof -nP -iTCP:3000 -sTCP:LISTEN
lsof -nP -iTCP:8000 -sTCP:LISTEN
```

If either process remains after a normal interrupt, identify the exact local
PID with `lsof` and terminate only that process. Do not stop unrelated Node or
Python processes.

## Troubleshooting

### API import or test collection failure

Activate `.venv`, verify `python -m pip --version` points inside the repository,
and reinstall only project dependencies:

```bash
python -m pip install -e '.[test]' pytest requests
```

### Dashboard cannot reach the API

- Confirm `http://127.0.0.1:8000/api/health` responds.
- Confirm the frontend is using `http://127.0.0.1:8000` or set
  `NEXT_PUBLIC_PREMARKET_API_URL` before starting it.
- Restart the development server after changing that environment variable.

### Blank page during initial load

Wait for client hydration, reload once, and inspect the browser console. Run
`npm run lint` and `npm run build` before treating the issue as a route defect.

### Stale or blocked current state

Use deterministic replay only as labeled historical evidence. Do not alter the
clock, manifest, checksum, or freshness controls to make the live state appear
ready.

### Port already in use

Use `lsof -nP -iTCP:3000 -sTCP:LISTEN` or the equivalent command for port 8000.
Stop only a process that belongs to this workspace, or launch on an explicitly
chosen alternate local port.
