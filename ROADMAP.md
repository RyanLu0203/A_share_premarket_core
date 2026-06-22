# Roadmap

## Implemented Active

- Project operating system.
- Universe and symbol governance.
- Trading calendar.
- Source health and context contracts.
- PIT signal snapshot.
- Label snapshot and benchmark contract.
- Feature-label merge and leakage audit.
- Stage 6A repair panel.
- GOAL-06A baseline scoring skeleton.
- GOAL-06B review-only supervised baseline training gate.
- GOAL-06C review-only expanded validation and ranking baseline gate.
- GOAL-06C.5 engineering data coverage, local storage, data bundle, and panel
  expansion gate.
- GOAL-06C.6 source-backed AKShare/provider engineering pilot bundle ingestion
  gate, network-disabled by default.
- GOAL-06C.6A scoped finance network isolation and provider failure taxonomy
  gate; network failures are classified by specific subtype.
- GOAL-06C.6A CloakBrowser reference probe for opt-in, sanitized, tag-only
  provider-access diagnostics.
- Verification, validation, regression, safety, adapter, and diagnostics gates.
- GOAL-HYGIENE-01 deterministic runtime artifact policy.
- GOAL-DOCS-01 canonical workflow status governance.

## Next Allowed Work

GOAL-06D may begin only if
`outputs/audits/goal06c6_readiness_report.md` explicitly allows it after the
source-backed Stage 6C engineering panel reaches `engineering_pilot`, and
GOAL-06C.6A failure taxonomy evidence remains non-blocking. GOAL-06D must
remain review-only model comparison/calibration and must not implement
recommendation, risk overlay, dashboard, paper/live trading, production DB
writes, production model promotion, or DQN/RL.

Before GOAL-06D starts, keep committed reports deterministic and treat
`runtime_seconds` as local-only diagnostics.
Future goals must also update `configs/project/workflow_status.csv` and the
workflow diagrams before any future block is promoted.

## Locked Future

- GOAL-07A risk overlay design.
- GOAL-07B risk overlay calculation prototype.
- Position-band recommendation.
- Signal and portfolio backtests.
- Cost/slippage sensitivity.
- Paper trading journal.
- Failure attribution.
- Dashboard / daily report.
- Production hardening.
- Broker/live trading.
- Production DB writes.
- DQN/RL optional research benchmark.
