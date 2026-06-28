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
- GOAL-09.0 Position-Band Review-Only Unlock Gate (`PASS_WITH_WARNINGS`)
- GOAL-09 Position-Band Diagnostics Prototype (`PASS_WITH_WARNINGS`)
- GOAL-09.1 Position-Band Warning Review and Dashboard Readiness Gate
  (`PASS_WITH_WARNINGS`)
- GOAL-10B Recommendation Diagnostics Backtest Review-Only
  (`PASS_WITH_WARNINGS`)
- GOAL-10B.1 Backtest Coverage Repair Gate (`PASS_WITH_WARNINGS`)
- GOAL-DATA-LABEL-01 Forward-Return Label Coverage Expansion
  (`PASS_WITH_WARNINGS`)
- GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics Expansion
  (`PASS_WITH_WARNINGS`)
- GOAL-10B.2 Recommendation Backtest Revalidation (`PASS_WITH_WARNINGS`)
- GOAL-10C Cost / Slippage Sensitivity (`PASS_WITH_WARNINGS`)
- GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe
  (`PASS_WITH_WARNINGS`)
- GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test
  (`PASS_WITH_WARNINGS`)
- GOAL-DATA-PROVIDER-02B Source-Backed Evaluation Panel Build Gate
  (`PASS_WITH_WARNINGS`)
- GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Multi-Symbol Diagnostics Gate
  (`PASS_WITH_WARNINGS`)
- GOAL-10B.3 DC03 Recommendation Revalidation Gate (`PASS_WITH_WARNINGS`)
- GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering Gate
  (`PASS_WITH_WARNINGS`)
- GOAL-RISK-TIERING-01.1 Downside Risk Repair Gate (`PASS_WITH_WARNINGS`)

Implemented design-only:

- GOAL-07A Risk Overlay Design (`PASS_WITH_WARNINGS`)
- GOAL-08A Recommendation Contract Design Gate (`PASS`)
- GOAL-10A Backtest Contract Design Gate (`PASS_WITH_WARNINGS`)

Implemented infrastructure-only:

- GOAL-STORAGE-01 Local Research Lake Hardening Gate (`PASS`)
- GOAL-V1-INTEGRITY-01 Artifact Lineage and Structure Gate
  (`PASS_WITH_WARNINGS`)

Future design-only:

- none currently locked as future design-only; GOAL-V1-INTEGRITY-01 still
  allows only a future explicit GOAL-DASHBOARD-00 contract/layout design gate
  request, while GOAL-10A is already implemented as design-only backtest
  contract evidence

Locked future:

- Actual position recommendations, position sizing, portfolio weights, and
  order quantities
- GOAL-REC-TIERING-01 Recommendation Score Tiering
- GOAL-DATA-PANEL-02 Evaluation Panel
- GOAL-10B.4 Recommendation Revalidation
- GOAL-POSITION-BAND-VALIDATION-01 Position-Band Validation
- GOAL-10D Failure Attribution
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

## GOAL-09.0 Status

GOAL-09.0 is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/position/goal090_position_band_review_only_unlock_policy.yaml`
- `docs/position/GOAL090_POSITION_BAND_REVIEW_ONLY_UNLOCK_GATE.md`
- `outputs/audits/goal090_position_band_review_only_unlock_report.md`
- `outputs/audits/goal090_position_band_review_only_unlock_manifest.json`
- `outputs/audits/goal090_position_band_review_only_unlock_audit.md`

The gate uses only prior GOAL-07B, GOAL-08A, GOAL-STORAGE-01, GOAL-08B.0, and
GOAL-08B PASS/PASS_WITH_WARNINGS evidence. It may mark GOAL-09 position-band
diagnostics `future_review_only` eligible or preserve a later separately
implemented GOAL-09 review-only diagnostic state. It does not implement GOAL-09, create position-band
diagnostic rows, create position rows, produce position sizing, portfolio
weights, buy/sell/hold outputs, target prices, expected returns for action,
dashboards, trading paths, production behavior, backtests, factor-mining
outputs, broker outputs, local lake files, or DQN/RL outputs.

## GOAL-09 Status

GOAL-09 is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/position/goal09_review_only_position_band_diagnostics_policy.yaml`
- `docs/position/GOAL09_REVIEW_ONLY_POSITION_BAND_DIAGNOSTICS.md`
- `outputs/position/goal09_review_only_position_band_diagnostics.csv`
- `outputs/audits/goal09_position_band_diagnostics_report.md`
- `outputs/audits/goal09_position_band_diagnostics_manifest.json`
- `outputs/audits/goal09_position_band_diagnostics_audit.md`

The prototype consumes GOAL-08B non-actionable recommendation diagnostics and
GOAL-07B risk overlay diagnostics at `trade_date + symbol` grain. Its rows are
position-band diagnostics only, with
`position_actionability_status=never_actionable`. It does not create actual
position rows, position sizing, portfolio weights, target weights, order
quantities, buy/sell/hold outputs, target prices, expected returns for action,
dashboards, trading paths, production behavior, backtests, factor-mining
outputs, broker outputs, local lake files, or DQN/RL outputs.

## GOAL-09.1 Status

GOAL-09.1 is `implemented_review_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/dashboard/goal091_dashboard_readiness_warning_policy.yaml`
- `docs/dashboard/GOAL091_POSITION_BAND_WARNING_REVIEW_AND_DASHBOARD_READINESS.md`
- `outputs/audits/goal091_dashboard_readiness_report.md`
- `outputs/audits/goal091_dashboard_readiness_manifest.json`
- `outputs/audits/goal091_dashboard_readiness_audit.md`

The gate consumes only prior GOAL-07B, GOAL-08A, GOAL-STORAGE-01, GOAL-08B.0,
GOAL-08B, GOAL-09.0, and GOAL-09 PASS/PASS_WITH_WARNINGS review, design, or
infrastructure evidence. It confirms GOAL-09 remains non-actionable at
`trade_date + symbol` grain with `position_actionability_status=never_actionable`.

GOAL-09.1 classifies the remaining GOAL-09 warnings into
`dashboard_blocking_banner`, `provider_concentration_banner`, and
`row_level_and_summary_warning` groups. It defines that any future dashboard
contract must preserve `review_only`, `never_actionable`, and non-actionable
disclaimers, show all propagated warning codes, block ranked Top-N,
buy-candidate, position-candidate, and action-oriented displays, and forbid
buy/sell/hold, target price, expected return for action, position size,
portfolio weight, target weight, order quantity, and execution fields.

GOAL-09.1 allows only a future explicit GOAL-DASHBOARD-00 design/contract gate
request. Dashboard / Daily Report UI remains `locked_future`. GOAL-09.1 does
not create dashboard output, HTML, Streamlit, frontend code, visual reports,
new recommendation rows, new position rows, actual position sizing, weights,
orders, trading paths, production behavior, backtests, factor-mining outputs,
broker outputs, local lake files, or DQN/RL outputs.

## GOAL-V1-INTEGRITY-01 Status

GOAL-V1-INTEGRITY-01 is `implemented_infrastructure_only` and currently
`PASS_WITH_WARNINGS`. It creates:

- `configs/validation/goal_v1_integrity01_artifact_lineage_contract.yaml`
- `docs/validation/GOAL_V1_INTEGRITY01_ARTIFACT_LINEAGE_STRUCTURE_GATE.md`
- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_report.md`
- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_manifest.json`
- `outputs/audits/goal_v1_integrity01_artifact_lineage_structure_audit.md`

The gate consumes only prior GOAL-07B, GOAL-08B, GOAL-09, and GOAL-09.1
PASS/PASS_WITH_WARNINGS review-only evidence. It verifies canonical artifact
lineage, `trade_date + symbol` row-key consistency, non-actionable row status,
warning classification availability, source-of-truth docs, and workflow status.

GOAL-V1-INTEGRITY-01 allows only a future explicit GOAL-DASHBOARD-00
design/contract gate request. Dashboard / Daily Report UI remains
`locked_future`. GOAL-V1-INTEGRITY-01 does not create dashboard output, HTML,
Streamlit, frontend code, visual reports, new risk rows, new recommendation
rows, new position rows, actual position sizing, weights, orders, trading paths,
production behavior, backtests, factor-mining outputs, broker outputs, local
lake files, or DQN/RL outputs.

## GOAL-10A Status

GOAL-10A is `implemented_design_only` and currently `PASS_WITH_WARNINGS`. It
creates:

- `configs/backtest/goal10a_backtest_input_contract.yaml`
- `configs/backtest/goal10a_backtest_metric_contract.yaml`
- `configs/backtest/goal10a_backtest_grouping_contract.yaml`
- `configs/backtest/goal10a_execution_alignment_policy.yaml`
- `docs/backtest/GOAL10A_BACKTEST_CONTRACT_DESIGN_GATE.md`
- `outputs/audits/goal10a_backtest_contract_design_report.md`
- `outputs/audits/goal10a_backtest_contract_design_manifest.json`
- `outputs/audits/goal10a_backtest_contract_design_audit.md`

GOAL-10A defines future review-only validation contracts over GOAL-08B
recommendation diagnostics and GOAL-09 position-band diagnostics at
`trade_date + symbol` grain. It defines `signal_date`, `trade_date`,
`execution_date`, `target_horizon`, benchmark alignment, T+1/no-lookahead
rules, future metrics, grouping rules, cost/slippage sensitivity contracts, and
suspended/limit/missing-price policy.

GOAL-10A runs no backtest, generates no backtest performance rows, creates no
equity curves, creates no portfolio returns, creates no dashboard files, creates
no HTML/Streamlit/frontend files, creates no buy/sell/hold actions, target
prices, position sizes, order quantities, local lake files, trading paths,
production behavior, factor-mining outputs, broker outputs, or DQN/RL outputs.

GOAL-10B is implemented only as review-only recommendation diagnostics
backtest evidence. GOAL-10B.1 is implemented only as review-only coverage
repair diagnostics over existing artifacts and records that repair is not
possible with current artifacts. GOAL-DATA-LABEL-01 is implemented only as
review-only label coverage evidence from committed OHLCV and benchmark samples.
GOAL-V1-DIAGNOSTIC-COVERAGE-02 is implemented only as review-only
multi-symbol diagnostic coverage evidence from committed Stage 6C
approved-symbol samples. GOAL-10B.2 is implemented only as review-only
recommendation backtest revalidation diagnostics over DC02 rows. GOAL-10C is
implemented only as review-only row-level position-band cost/slippage
sensitivity diagnostics. GOAL-DATA-PROVIDER-02A is implemented only as
review-only provider capability metadata for future source-backed planning and
does not build an evaluation panel, run diagnostics, or run backtests.
GOAL-DATA-PROVIDER-02A.1 is implemented only as review-only network-opt-in
provider smoke-test metadata; it attempts live provider access only when
explicit environment opt-ins are present, reads Tushare tokens only from the
environment, and persists no raw provider payloads or tokens.
GOAL-DATA-PROVIDER-02B is implemented only as bounded source-backed normalized
panel evidence plus provider/coverage audit metadata. GOAL-V1-DIAGNOSTIC-
COVERAGE-03 is implemented only as non-actionable source-backed diagnostic
coverage over that 02B panel; it does not overwrite canonical GOAL-07B/08B/09
artifacts or unlock backtests, dashboards, trading, production, local-lake,
broker, factor-mining, or DQN/RL outputs. GOAL-10B.3 is implemented only as
review-only DC03 recommendation revalidation diagnostics and records weak /
unreliable signal evidence due group imbalance and unavailable numeric-score
IC/RankIC. GOAL-DATA-PANEL-02 and GOAL-10D remain `locked_future`.

## GOAL-DATA-PROVIDER-02A Status

GOAL-DATA-PROVIDER-02A is `implemented_review_only` and currently
`PASS_WITH_WARNINGS`. It creates:

- `outputs/providers/goal_data_provider02a_provider_capability_probe.csv`
- `outputs/providers/goal_data_provider02a_provider_schema_mapping.csv`
- `outputs/providers/goal_data_provider02a_provider_failure_taxonomy.csv`
- `configs/providers/goal_data_provider02a_provider_ladder_contract.yaml`
- `docs/providers/GOAL_DATA_PROVIDER02A_MULTI_PROVIDER_CAPABILITY_PROBE_GATE.md`
- `outputs/audits/goal_data_provider02a_multi_provider_capability_probe_report.md`
- `outputs/audits/goal_data_provider02a_multi_provider_capability_probe_manifest.json`
- `outputs/audits/goal_data_provider02a_multi_provider_capability_probe_audit.md`

The gate probes provider capability metadata for Tushare Pro, Baostock,
AkShare, efinance, qstock, yfinance auxiliary, and local import fallback over
the current approved-symbol smoke universe and a 30-trading-day contract
window. It records package availability, token/network policy, schema mapping,
failure taxonomy, and panel-readiness metadata only.

GOAL-DATA-PROVIDER-02A does not expand the approved universe, build a final
evaluation panel, create recommendation diagnostics, create position-band
diagnostics, run backtests, generate portfolio returns, create equity curves,
create dashboard/frontend/HTML/Streamlit outputs, write local-lake data, write
trading or production data, integrate brokers, activate factor mining, or
create DQN/RL outputs. GOAL-DATA-PROVIDER-02B is implemented only by its own
source-backed panel evidence gate. GOAL-V1-DIAGNOSTIC-COVERAGE-03 is
implemented only as non-actionable source-backed diagnostic coverage from the
02B panel. GOAL-10B.3 is implemented only by its own separate review-only DC03
recommendation revalidation gate. GOAL-DATA-PANEL-02, GOAL-10D, Dashboard /
Daily Report UI, and all execution paths remain `locked_future`.

## GOAL-DATA-PROVIDER-02A.1 Status

GOAL-DATA-PROVIDER-02A.1 is `implemented_review_only` and currently
`PASS_WITH_WARNINGS`. It creates:

- `outputs/providers/goal_data_provider02a1_network_smoke_test_results.csv`
- `outputs/providers/goal_data_provider02a1_schema_mapping_results.csv`
- `outputs/providers/goal_data_provider02a1_failure_taxonomy.csv`
- `configs/providers/goal_data_provider02a1_network_smoke_test_contract.yaml`
- `docs/providers/GOAL_DATA_PROVIDER02A1_NETWORK_OPT_IN_PROVIDER_SMOKE_TEST.md`
- `outputs/audits/goal_data_provider02a1_network_smoke_test_report.md`
- `outputs/audits/goal_data_provider02a1_network_smoke_test_manifest.json`
- `outputs/audits/goal_data_provider02a1_network_smoke_test_audit.md`

The gate records provider smoke-test metadata for Tushare Pro, Baostock,
AkShare, efinance, qstock, yfinance auxiliary, and local import fallback over
the current approved-symbol smoke universe and a 30-trading-day contract
window. Live provider access is attempted only when
`ASHARE_ALLOW_NETWORK_INGESTION=1` is set. Tushare Pro additionally requires
`ASHARE_ALLOW_TUSHARE=1` and `TUSHARE_TOKEN` from the environment.

GOAL-DATA-PROVIDER-02A.1 does not select a provider, expand the approved
universe, build a final evaluation panel, treat smoke-test data as final panel
evidence, create recommendation diagnostics, create position-band diagnostics,
run GOAL-10B.3 itself, run GOAL-10C, generate portfolio returns, create equity curves,
create dashboard/frontend/HTML/Streamlit outputs, commit raw provider payloads,
persist provider tokens, write local-lake data, write trading or production
data, integrate brokers, activate factor mining, or create DQN/RL outputs.
GOAL-DATA-PROVIDER-02B is implemented only by its own source-backed panel
evidence gate. GOAL-V1-DIAGNOSTIC-COVERAGE-03 is implemented only as
non-actionable source-backed diagnostic coverage from the 02B panel. GOAL-10B.3
is implemented only by its own separate review-only DC03 recommendation
revalidation gate. GOAL-DATA-PANEL-02, GOAL-10D, Dashboard / Daily Report UI,
and all execution paths remain `locked_future`.

## GOAL-DATA-PROVIDER-02B Status

GOAL-DATA-PROVIDER-02B is `implemented_review_only` and currently
`PASS_WITH_WARNINGS`. It creates:

- `outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
- `outputs/diagnostics/goal_data_provider02b_panel_coverage_summary.csv`
- `outputs/providers/goal_data_provider02b_provider_usage_summary.csv`
- `outputs/providers/goal_data_provider02b_provider_failure_taxonomy.csv`
- `configs/providers/goal_data_provider02b_panel_build_contract.yaml`
- `docs/providers/GOAL_DATA_PROVIDER02B_SOURCE_BACKED_EVALUATION_PANEL_BUILD_GATE.md`
- `outputs/audits/goal_data_provider02b_source_backed_panel_report.md`
- `outputs/audits/goal_data_provider02b_source_backed_panel_manifest.json`
- `outputs/audits/goal_data_provider02b_source_backed_panel_audit.md`

The gate builds bounded source-backed normalized panel evidence for future
review-only diagnostics planning. The current evidence has 6000 rows,
50 symbols, 120 trade dates, provider usage metadata, coverage checks, and
failure-taxonomy rows. It records a warning when a provider-panel candidate
universe is used because the canonical approved universe is below the required
50-symbol threshold.

GOAL-DATA-PROVIDER-02B does not promote GOAL-DATA-PANEL-02, expand the
approved trading universe, run GOAL-10B.3 itself, run GOAL-10C, run backtests,
generate portfolio returns, create equity curves, create
dashboard/frontend/HTML/Streamlit outputs, commit raw provider payloads,
persist provider tokens, write local-lake data, write trading or production
data, integrate brokers, activate factor mining, or create DQN/RL outputs.
GOAL-V1-DIAGNOSTIC-COVERAGE-03 is implemented only by its own non-actionable
diagnostic coverage gate. GOAL-10B.3 is implemented only by its own separate
review-only DC03 recommendation revalidation gate. GOAL-DATA-PANEL-02,
GOAL-10D, Dashboard / Daily Report UI, and all execution paths remain
`locked_future`.

## GOAL-V1-DIAGNOSTIC-COVERAGE-03 Status

GOAL-V1-DIAGNOSTIC-COVERAGE-03 is `implemented_review_only` and currently
`PASS_WITH_WARNINGS`. It creates:

- `outputs/diagnostics/goal_v1_diagnostic_coverage03_risk_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_recommendation_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_position_band_diagnostics.csv`
- `outputs/diagnostics/goal_v1_diagnostic_coverage03_distribution_summary.csv`
- `configs/diagnostics/goal_v1_diagnostic_coverage03_contract.yaml`
- `docs/diagnostics/GOAL_V1_DIAGNOSTIC_COVERAGE03_SOURCE_BACKED_MULTI_SYMBOL_DIAGNOSTICS_GATE.md`
- `outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_report.md`
- `outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_manifest.json`
- `outputs/audits/goal_v1_diagnostic_coverage03_source_backed_diagnostics_audit.md`

The gate consumes only
`outputs/datasets/goal_data_provider02b_source_backed_evaluation_panel.csv`
and creates separate non-actionable risk, recommendation eligibility, and
position-band diagnostics at `trade_date + symbol` grain. Current evidence has
6000 rows per family, 50 symbols, 120 trade dates, and natural group variation
without fabricated tiers.

GOAL-V1-DIAGNOSTIC-COVERAGE-03 does not overwrite canonical GOAL-07B/08B/09
artifacts, run GOAL-10C, run portfolio backtests, generate portfolio returns,
create equity curves, create dashboard/frontend/HTML/Streamlit outputs, fetch
new provider data, write local-lake data, write trading or production data,
integrate brokers, activate factor mining, or create DQN/RL outputs. GOAL-10B.3
is implemented separately as non-actionable DC03 recommendation revalidation
diagnostics only. GOAL-DATA-PANEL-02, GOAL-10D, Dashboard / Daily Report UI,
and all execution paths remain `locked_future`.

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
implemented only by its own review-only diagnostic prototype; downstream
execution modules remain `locked_future`.
