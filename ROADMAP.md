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
  preserves GOAL-07B eligibility and remains unlock-only).
- GOAL-07B risk overlay calculation prototype (`PASS_WITH_WARNINGS`;
  implemented_review_only non-actionable diagnostics at `trade_date + symbol`
  grain).
- GOAL-08A recommendation contract design gate (`PASS`; implemented_design_only
  names-only future schema, warning propagation, HIGH-risk actionability block,
  and zero recommendation rows).
- GOAL-STORAGE-01 local research lake hardening gate (`PASS`;
  implemented_infrastructure_only storage governance and GitHub hygiene only).
- GOAL-08B.0 recommendation review-only unlock gate (`PASS_WITH_WARNINGS`;
  implemented_review_only unlock-only evidence, no recommendation diagnostics
  rows created by that gate).
- GOAL-08B non-actionable recommendation diagnostics prototype
  (`PASS_WITH_WARNINGS`; implemented_review_only diagnostics at
  `trade_date + symbol` grain).
- Verification, validation, regression, safety, adapter, and diagnostics gates.
- GOAL-HYGIENE-01 deterministic runtime artifact policy.
- GOAL-DOCS-01 canonical workflow status governance.

## Next Allowed Work

GOAL-07A has implemented the risk overlay blueprint only as design governance.
GOAL-07A.1 completed the GOAL-07B unlock-readiness design review, and
GOAL-07B.0 completed the explicit review-only unlock gate. GOAL-07B now
implements a deterministic review-only risk overlay calculation prototype.
GOAL-08A now implements only a design-only future recommendation contract gate.
GOAL-STORAGE-01 now implements only an infrastructure hardening gate for the
local research lake contract and does not unlock GOAL-08B by itself.
GOAL-08B.0 completed the explicit review-only unlock gate. GOAL-08B now
implements only a deterministic non-actionable recommendation diagnostics
prototype with 100 `trade_date + symbol` rows. The exact allowed next action is
to request a future explicit GOAL-09 position-band review-only unlock or fix
GOAL-08B warnings.
No actionable recommendation execution, position, dashboard, paper/live trading,
production DB writes, production model promotion, backtest, factor mining,
broker, or DQN/RL is unlocked.

V2 factor research is planned but inactive. It remains `planned_locked` until a
future explicit V2 goal; no factor mining, IC/RankIC mining, factor library
generation, or factor integration is active in V1.

Future goals must also update `configs/project/workflow_status.csv` and the
workflow diagrams before any future block is promoted.

## Locked Future

- GOAL-09 position-band review-only unlock and any position-band
  recommendation.
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
