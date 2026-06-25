# Canonical Workflow Status

The canonical machine-readable workflow status contract is:

`configs/project/workflow_status.csv`

Future goals must update that file before they can be considered complete. The
CSV governs diagram edge type, allowed next action, promotion rules, and whether
a block is implemented in this repository.

## Status Values

- `implemented_active`: implemented and allowed to appear with solid arrows in
  the current active workflow.
- `implemented_review_only`: implemented, but review-only.
- `implemented_design_only`: implemented as design documentation only.
- `implemented_infrastructure_only`: implemented as infrastructure governance
  only; downstream execution remains locked.
- `future_review_only`: future review-only work; dotted arrows only.
- `future_design_only`: future design-only work; dotted arrows only.
- `locked_future`: locked future work; dotted arrows only.
- `not_started`: planned but not started; dotted arrows only.
- `deleted_from_active_mainline`: deleted from active mainline; side note or
  optional dotted reference only.

## Current Status Summary

Implemented active through GOAL-06B:

- Project Operating System
- Universe / Symbol Governance
- Data / Provider / Source Health
- Market / Sector / Stock / Event / NLP Contract Layers
- PIT Signal Store
- Label Builder
- Benchmark Contract
- Feature-Label Merge
- Leakage Audit
- Stage 6A Repair Panel
- GOAL-06A Baseline Scoring Skeleton
- GOAL-06B Supervised Baseline Training Gate
- Validation / Verification / Diagnostics
- Safety Gate
- Adapter Audit

Implemented review-only:

- GOAL-06C Expanded Validation and Ranking Baseline
- GOAL-06C.5 Engineering Data Coverage + Storage + Panel Expansion
- GOAL-06C.6 Source-Backed Engineering Pilot Bundle
- GOAL-06C.6A Scoped Finance Network Isolation and Failure Taxonomy
- GOAL-06C.7 Provider Ladder Engineering Data Base Expansion
- GOAL-06D Model Comparison, Calibration, Stability, and Governance
  (`PASS_WITH_WARNINGS`)
- GOAL-06D.1 Calibration Stability Warning Repair (`PASS_WITH_WARNINGS`)
- GOAL-07A.1 Risk Overlay Design Review Unlock Readiness (`PASS_WITH_WARNINGS`)
- GOAL-07B.0 Risk Overlay Review-Only Unlock Gate (`PASS_WITH_WARNINGS`)
- GOAL-07B Risk Overlay Calculation Prototype (`PASS_WITH_WARNINGS`)
- GOAL-08B.0 Recommendation Review-Only Unlock Gate (`PASS_WITH_WARNINGS`)
- GOAL-08B Recommendation Diagnostics Prototype (`PASS_WITH_WARNINGS`)

Implemented design-only:

- GOAL-07A Risk Overlay Design (`PASS_WITH_WARNINGS`)
- GOAL-08A Recommendation Contract Design Gate (`PASS`)

Implemented infrastructure-only:

- GOAL-STORAGE-01 Local Research Lake Hardening Gate (`PASS`)

Future design-only:

- none currently unlocked

Locked future:

- Position-band Recommendation
- Signal Backtest
- Portfolio Backtest
- Cost / Slippage Sensitivity
- Paper Trading Journal
- Failure Attribution
- Dashboard / Daily Report
- Production Hardening
- Broker / Live Trading
- Production DB Writes
- Production Model Promotion

Deleted from active mainline:

- DQN/RL mainline path

## Workflow Promotion Rule

A future workflow block can only be promoted from dotted/future to
solid/implemented if:

1. The corresponding goal has a readiness report.
2. The readiness report is `PASS` or acceptable `PASS_WITH_WARNINGS`.
3. Validation and verification commands pass.
4. `configs/project/workflow_status.csv` is updated.
5. README and architecture diagrams are updated.
6. `PROJECT_STATE.md` is updated.
7. Locked downstream modules remain locked unless explicitly unlocked by that
   goal.

Do not silently change the workflow diagram to make future stages look
implemented. Do not add new downstream blocks without updating
`workflow_status.csv`. Do not remove locks from downstream recommendation,
dashboard, paper/live trading, production, backtest, factor-mining, or DQN/RL
unless a later explicit gate allows it.

## Governance Audit

Run:

```bash
python scripts/audit_workflow_status.py
```

This writes:

- `outputs/audits/workflow_status_audit.md`
- `outputs/audits/workflow_status_table.csv`
- `outputs/audits/workflow_diagram_update_report.md`

## GOAL-06C Status

GOAL-06C is `implemented_review_only`. It creates:

- `outputs/stage6c/STAGE6C_expanded_validation_dataset.csv`
- `outputs/stage6c/STAGE6C_ranking_baseline_scores.csv`
- `outputs/stage6c/STAGE6C_ranking_metrics.csv`
- `outputs/stage6c/STAGE6C_walk_forward_diagnostics.csv`
- `outputs/stage6c/STAGE6C_ranking_stability_diagnostics.csv`

GOAL-06C does not generate recommendations, position bands, portfolio weights,
risk overlays, dashboard outputs, paper/live trading, production DB writes,
production model promotion, or DQN/RL artifacts.

## GOAL-06C.5 Status

GOAL-06C.5 is `implemented_review_only`. It creates storage policy, data bundle,
source coverage, provider contract, engineering PIT panel, engineering label
panel, and Stage 6C engineering panel audit evidence.

The historical clean-bootstrap panel was `contract_demo`; GOAL-06C.7 now
provides separate source-backed `engineering_pilot` evidence.

## GOAL-06C.6 Status

GOAL-06C.6 is `implemented_review_only`. It adds provider failure
classification, optional AKShare ingestion wrappers, source-backed local bundle
manifests, source-backed PIT/label panel builders, and Stage 6C source-backed
engineering panel audits.

Network ingestion is disabled by default. It must be explicitly enabled with
`ASHARE_ALLOW_NETWORK_INGESTION=1` or `--allow-network`; provider failures are
classified and reported on the default AKShare path. The explicit CloakBrowser
reference probe is separate, opt-in, tag-only, sanitized, and does not unlock
downstream workflow blocks.
GOAL-06D is no longer unlocked by GOAL-06C.6 alone; GOAL-06C.7 provides the
source-backed `engineering_pilot` evidence used by GOAL-06D.

## GOAL-06C.6A Status

GOAL-06C.6A is `implemented_review_only`. It adds finance-only network
isolation evidence, provider failure events, a failure summary, and a taxonomy
report.

Network failures are classified by specific failure type. ProxyError, timeout,
DNS, TLS, connection reset/refused, HTTP access, anti-bot/challenge, schema,
parser, data-quality, PIT/label, storage, and workflow-governance failures must
not be collapsed into a generic network class when a specific class can be
determined.

The earlier explicit AKShare failure after scoped proxy-env cleanup remains
classified as `FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED`.
Later GOAL-06C.7 provider-ladder evidence reached `engineering_pilot` through
`akshare_direct`; the older failure taxonomy remains provenance.

## GOAL-06C.7 Status

GOAL-06C.7 is `implemented_review_only`. It adds a provider ladder with:

- `akshare_direct`
- `browser_assisted_optional`
- `local_import`
- `future_vendor_data_placeholder`

The browser-assisted provider is disabled by default and requires both
`ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1` and `--enable-browser-assisted`.
It is dynamic-import-only, finance-domain-scoped, sanitized, and does not store
raw HTML, payload bodies, screenshots, cookies, browser profiles, or cache in
GitHub.

Browser outcomes are classified precisely:

- `BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED`: schema-valid rows were
  produced and may count toward the source-backed panel.
- `BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY`: the domain was reachable but ingestion
  was not solved.
- `BROWSER_NET_EMPTY_RESPONSE`: the finance endpoint/browser path returned an
  empty response.

`outputs/audits/goal06c7_readiness_report.md` proves `engineering_pilot`.

## GOAL-07A.1 Status

GOAL-07A.1 is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It creates:

- `outputs/audits/goal07a1_design_review_report.md`
- `outputs/audits/goal07a1_unlock_readiness_manifest.json`
- `outputs/audits/goal07a1_warning_classification.csv`

The gate may mark GOAL-07B as ready for a future explicit review-only unlock request. It does not implement GOAL-07B and does not create risk calculation, recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs.

## GOAL-07B.0 Status

GOAL-07B.0 is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/risk/goal07b0_review_only_unlock_policy.yaml`
- `docs/risk/GOAL07B0_RISK_OVERLAY_REVIEW_ONLY_UNLOCK_GATE.md`
- `outputs/audits/goal07b0_unlock_gate_report.md`
- `outputs/audits/goal07b0_unlock_gate_manifest.json`
- `outputs/audits/goal07b0_unlock_gate_audit_report.md`

The gate uses only prior GOAL-07A and GOAL-07A.1 PASS/PASS_WITH_WARNINGS
evidence. It moves GOAL-07B to `future_review_only` eligibility before a
prototype exists, or preserves an existing `implemented_review_only` GOAL-07B
diagnostic state on rerun. It does not itself calculate risk, create
symbol-level risk rows, generate recommendations or positions, create
dashboards, run backtests, write trading or production data, activate factor
mining, or create DQN/RL outputs.

## GOAL-07B Status

GOAL-07B is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/risk/goal07b_risk_overlay_calculation_policy.yaml`
- `docs/risk/GOAL07B_RISK_OVERLAY_CALCULATION_PROTOTYPE.md`
- `outputs/risk_overlay/goal07b_review_only_risk_overlay.csv`
- `outputs/diagnostics/goal07b_risk_overlay_diagnostics.csv`
- `outputs/audits/goal07b_risk_overlay_calculation_report.md`
- `outputs/audits/goal07b_risk_overlay_calculation_manifest.json`
- `outputs/audits/goal07b_risk_overlay_calculation_audit.md`

The prototype writes deterministic `trade_date + symbol` risk diagnostics only.
It is non-actionable, uses prior review evidence and committed sample/pilot
artifacts, and keeps GOAL-08B plus recommendation, position,
dashboard, paper/live trading, production, backtest, factor-mining, broker, and
DQN/RL execution outputs locked.

## GOAL-08A Status

GOAL-08A is `implemented_design_only` and currently `PASS`. It creates:

- `configs/recommendation/goal08a_future_recommendation_input_contract.yaml`
- `configs/recommendation/goal08a_future_recommendation_schema.yaml`
- `configs/recommendation/goal08a_warning_propagation_policy.yaml`
- `configs/recommendation/goal08a_actionability_guardrails.yaml`
- `configs/recommendation/goal08a_recommendation_state_machine.yaml`
- `docs/recommendation/GOAL08A_RECOMMENDATION_CONTRACT_DESIGN_GATE.md`
- `docs/recommendation/GOAL08A_DESIGN_ONLY_BOUNDARY.md`
- `outputs/audits/goal08a_recommendation_contract_design_report.md`
- `outputs/audits/goal08a_recommendation_contract_design_manifest.json`
- `outputs/audits/goal08a_recommendation_contract_design_audit.md`

The gate is names-only design evidence. It requires GOAL-07B
`trade_date + symbol` diagnostic input grain, propagates GOAL-07B warnings into
future non-actionable metadata, and defines that HIGH risk severity blocks any
future actionable recommendation output. The schema sample has row count `0`.
It does not generate recommendations, positions, dashboards, trading outputs,
production behavior, backtests, factor-mining outputs, broker outputs, or
DQN/RL outputs.

## GOAL-STORAGE-01 Status

GOAL-STORAGE-01 is `implemented_infrastructure_only` and currently `PASS`. It
creates:

- `configs/storage/goal_storage01_local_research_lake_contract.yaml`
- `docs/storage/GOAL_STORAGE01_LOCAL_RESEARCH_LAKE_HARDENING_GATE.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_report.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json`
- `outputs/audits/goal_storage01_local_research_lake_hardening_audit.md`

The gate requires future heavy data roots to resolve from
`ASHARE_PREMARKET_DATA_ROOT`; the fallback path is documentation-only. It
defines local `raw/`, `bundles/`, `lake/`, `metadata/`, `exports/`, and
`audit_samples/` boundaries plus placement, bundle versioning, manifest,
checksum, schema registry, and GitHub hygiene rules. It does not fetch data,
materialize lake files, create recommendation or position diagnostics, run
backtests, create dashboards, write production data, activate factor mining, or
unlock GOAL-08B by itself.

## GOAL-08B.0 Status

GOAL-08B.0 is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/recommendation/goal08b0_review_only_unlock_policy.yaml`
- `docs/recommendation/GOAL08B0_RECOMMENDATION_REVIEW_ONLY_UNLOCK_GATE.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_report.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md`

The gate uses only prior GOAL-07B, GOAL-08A, and GOAL-STORAGE-01
PASS/PASS_WITH_WARNINGS evidence. It marks GOAL-08B review-only eligibility but
does not itself create recommendation diagnostics rows, create recommendation
rows, produce buy/sell/hold outputs, target prices, positions, dashboards,
trading paths, production behavior, backtests, factor-mining outputs, broker
outputs, local lake files, or DQN/RL outputs.

## GOAL-08B Status

GOAL-08B is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/recommendation/goal08b_review_only_diagnostics_policy.yaml`
- `docs/recommendation/GOAL08B_REVIEW_ONLY_RECOMMENDATION_DIAGNOSTICS.md`
- `outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv`
- `outputs/audits/goal08b_recommendation_diagnostics_report.md`
- `outputs/audits/goal08b_recommendation_diagnostics_manifest.json`
- `outputs/audits/goal08b_recommendation_diagnostics_audit.md`

The prototype consumes only prior GOAL-07B risk overlay diagnostics, GOAL-08A
contract evidence, GOAL-STORAGE-01 infrastructure evidence, and GOAL-08B.0
unlock evidence. It writes 100 deterministic non-actionable diagnostic rows at
`trade_date + symbol` grain. `actionability_status` is always
`never_actionable`, `actionability_blocked` is always `true`, and no
actionable recommendation rows, buy/sell/hold outputs, target prices, expected
returns for action, position sizing, portfolio weights, dashboards, trading
paths, production behavior, backtests, factor-mining outputs, local lake files,
broker outputs, or DQN/RL outputs are generated.

## GOAL-06D Status

GOAL-06D is `implemented_review_only` and currently
`PASS_WITH_WARNINGS`. It creates lightweight review-only model comparison,
calibration, stability, and governance artifacts:

- `outputs/models/goal06d/model_comparison_summary.csv`
- `outputs/models/goal06d/model_metric_by_fold.csv`
- `outputs/models/goal06d/model_metric_by_target.csv`
- `outputs/models/goal06d/calibration_summary.csv`
- `outputs/models/goal06d/stability_summary.csv`
- `outputs/models/goal06d/model_selection_rationale.md`
- `outputs/audits/goal06d_readiness_report.md`
- `outputs/audits/goal06d_governance_audit.md`
- `outputs/audits/goal06d_boundary_lock_audit.md`

The selected baseline is `score_based_alpha_ranking`, labeled only as a weak
review-only baseline. Calibration/stability/provider concentration warnings
remain, so the allowed next action is
`fix_goal06d_model_stability_or_calibration_warnings`.

GOAL-06D does not generate recommendations, position bands, portfolio weights,
risk overlays, dashboards, paper/live trading, production DB writes, production
model promotion, or DQN/RL artifacts. GOAL-06D.1 is the review-only warning
repair layer that allows GOAL-07A only as design-only preparation.

## GOAL-06D.1 Status

GOAL-06D.1 is `implemented_review_only` and currently
`PASS_WITH_WARNINGS`. It repairs GOAL-06D warnings by comparing target horizons,
PIT-safe score variants, calibration reliability, feature sign stability, and
provider/source concentration.

The repaired baseline remains weak but bounded and review-only. Calibration may
be marked `calibration_not_reliable_for_thresholding`; this means no trading
threshold, position band, risk cutoff, or recommendation threshold is allowed.

GOAL-07A has proceeded only as design-only preparation with warnings. V2 factor
research is `planned_locked`, disabled in V1, and has no active factor mining,
IC/RankIC mining, factor library generation, factor outputs, or factor
integration.

## GOAL-07A Status

GOAL-07A is `implemented_design_only` and currently `PASS_WITH_WARNINGS`. It
creates risk design artifacts only:

- `configs/risk/goal07a_allowed_input_contract.yaml`
- `configs/risk/goal07a_future_risk_overlay_output_schema.yaml`
- `configs/risk/goal07a_risk_rule_catalog.yaml`
- `configs/risk/goal07a_risk_state_machine.yaml`
- `configs/risk/goal07a_upstream_warning_mapping.yaml`
- `docs/risk/GOAL07A_RISK_OVERLAY_DESIGN.md`
- `outputs/audits/goal07a_readiness_report.md`

GOAL-07A does not calculate risk values, assign symbol-level risk tags, generate
recommendations, create positions, create dashboards, write trading or
production data, activate V2 factor mining, or implement GOAL-07B. GOAL-07B is
implemented only by its own review-only diagnostic prototype; all downstream
modules remain `locked_future`.
