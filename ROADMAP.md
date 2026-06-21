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
- Verification, validation, regression, safety, adapter, and diagnostics gates.
- GOAL-HYGIENE-01 deterministic runtime artifact policy.

## Next Allowed Work

GOAL-06C may begin only if
`outputs/audits/goal06b_clean_repo_bootstrap_readiness_report.md` explicitly
unlocks it. The first GOAL-06C work must remain review-only expanded validation
and must not implement recommendation, risk overlay, dashboard, paper/live
trading, production DB writes, production model promotion, or DQN/RL.

Before GOAL-06C starts, keep committed reports deterministic and treat
`runtime_seconds` as local-only diagnostics.

## Locked Future

- GOAL-06D model comparison / calibration.
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
