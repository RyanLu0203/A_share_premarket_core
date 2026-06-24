# GOAL-STORAGE-01 Local Research Lake Hardening Gate

Status: `PASS`

GOAL-STORAGE-01 is infrastructure-only. It hardens where future local research data may live, how bundles must be versioned, what manifests and checksums must contain, and what must never be committed to GitHub.

It does not unlock GOAL-08B by itself. GOAL-08B remains `locked_future` until a separate explicit review-only prototype request is made and accepted.

## Root Contract

Future heavy data writes must resolve the local research root from `ASHARE_PREMARKET_DATA_ROOT`. The documented fallback is `~/data/ashare_premarket/`, but it is documentation-only for this gate and is not a production deployment assumption.

## Local Boundaries

- `raw/`: provider raw payloads, local-only.
- `bundles/`: immutable research bundles and manifests, local-only.
- `lake/`: curated table-shaped PIT panels, labels, and diagnostics, local-only.
- `metadata/`: schema registry mirrors, checksums, aliases, and non-secret metadata, local-only.
- `exports/`: local generated report/export packages, local-only.
- `audit_samples/`: tiny sanitized review samples only after explicit future approval.

## Boundary

No data expansion, recommendation rows, buy/sell/hold decisions, position sizing, dashboards, paper/live trading, broker integration, production DB writes, production model behavior, backtests, factor mining, or DQN/RL outputs are created by this gate.
