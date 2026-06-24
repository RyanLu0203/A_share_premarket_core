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
- GOAL-06C.7 provider ladder engineering data base expansion gate with
  optional browser-assisted ingestion disabled by default.
- GOAL-06D review-only model comparison/calibration/stability/governance gate
  (`PASS_WITH_WARNINGS`; weak selected baseline
  `score_based_alpha_ranking`).
- GOAL-06D.1 review-only calibration/stability warning repair gate
  (`PASS_WITH_WARNINGS`; weak repaired score baseline bounded and documented).
- GOAL-07A risk overlay design-only governance gate (`PASS_WITH_WARNINGS`;
  no risk calculation, recommendation, position, dashboard, trading,
  production, factor-mining, or DQN/RL output).
- GOAL-07A.1 risk overlay design review unlock-readiness gate
  (`PASS_WITH_WARNINGS`; GOAL-07B ready for explicit review-only unlock).
- GOAL-07B.0 risk overlay review-only unlock gate (`PASS_WITH_WARNINGS`;
  GOAL-07B is `future_review_only` eligible but not implemented).
- Verification, validation, regression, safety, adapter, and diagnostics gates.
- GOAL-HYGIENE-01 deterministic runtime artifact policy.
- GOAL-DOCS-01 canonical workflow status governance.

## Next Allowed Work

GOAL-07A has implemented the risk overlay blueprint only as design governance.
GOAL-07A.1 completed the GOAL-07B unlock-readiness design review, and
GOAL-07B.0 completed the explicit review-only unlock gate. The next possible
step is a future explicit GOAL-07B review-only calculation prototype request;
GOAL-07B is eligible but not implemented.
No risk overlay calculation rows, recommendation, position, dashboard,
paper/live trading, production DB writes, production model promotion, factor
mining, or DQN/RL is unlocked.

V2 factor research is planned but inactive. It remains `planned_locked` until a
future explicit V2 goal; no factor mining, IC/RankIC mining, factor library
generation, or factor integration is active in V1.

Future goals must also update `configs/project/workflow_status.csv` and the
workflow diagrams before any future block is promoted.

## Locked Future

- GOAL-07B risk overlay calculation prototype implementation and execution.
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
- V2 factor research upgrade (`planned_locked`; inactive in V1).
