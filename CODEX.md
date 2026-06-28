# CODEX Project Memory

## Mission

Maintain a clean, PIT-safe, review-only A-share pre-market workflow through
GOAL-06B, plus the GOAL-06C review-only expanded validation extension, the
GOAL-06C.5/GOAL-06C.6/GOAL-06C.6A/GOAL-06C.7 engineering data foundation gates,
the GOAL-06D/GOAL-06D.1 review-only model comparison/calibration/stability
governance gates, the GOAL-07A design-only risk governance gate, and the
GOAL-07B.0 review-only unlock gate, and the GOAL-07B review-only risk overlay
diagnostic prototype, plus the GOAL-08A design-only future recommendation
contract gate, plus GOAL-STORAGE-01 infrastructure-only local research lake
hardening, plus the GOAL-08B.0 review-only unlock eligibility gate, plus the
GOAL-08B non-actionable recommendation diagnostics prototype, plus the
GOAL-09.0 position-band review-only unlock eligibility gate, plus the GOAL-09
non-actionable position-band diagnostics prototype, plus the GOAL-09.1
position-band warning review/dashboard-readiness gate, plus
GOAL-V1-INTEGRITY-01 artifact-lineage structure governance, plus the GOAL-10A
design-only future backtest contract gate, plus GOAL-DATA-PROVIDER-02A.1
review-only network-opt-in provider smoke testing, plus GOAL-DATA-PROVIDER-02B
source-backed panel evidence, GOAL-V1-DIAGNOSTIC-COVERAGE-03 source-backed
diagnostic coverage, GOAL-10B.3 DC03 recommendation revalidation diagnostics,
and GOAL-RISK-TIERING-01 risk severity numeric score tiering. Preserve
reproducibility and source governance before any future actionable
recommendation execution, position work, or dashboard work.

## Current Reliable Facts

- This target repository is the active source of truth.
- The source repository is historical legacy/evidence reference only.
- The active scoring workflow stops at GOAL-06B supervised baseline training
  gate.
- GOAL-06B is review-only and pilot-only.
- GOAL-06C is implemented_review_only for expanded validation, ranking
  baselines, metrics, walk-forward diagnostics, and stability diagnostics.
- GOAL-06C.5 is implemented_review_only for storage policy, data bundle,
  source coverage, and engineering panel readiness.
- GOAL-06C.6 is implemented_review_only for provider failure classification,
  optional AKShare ingestion, local source-backed bundle creation, and
  source-backed Stage 6C engineering panel audits.
- GOAL-06C.6A is implemented_review_only for finance-only network isolation,
  provider failure events, and specific failure taxonomy reports.
- GOAL-06C.7 is implemented_review_only for provider-ladder engineering data
  base expansion. The ladder is direct finance provider, optional
  browser-assisted provider, local import, and future vendor placeholder.
- Browser-assisted ingestion is disabled by default, requires
  `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1` plus `--enable-browser-assisted`,
  uses dynamic import only, and counts only schema-valid finance rows.
- Network failures must be classified by precise type, such as ProxyError,
  timeout, DNS, TLS, connection reset/refused, HTTP access, or anti-bot
  challenge, not as a broad generic network failure when a specific class is
  knowable.
- The current source-backed GOAL-06C.7 provider-ladder panel tier is
  `engineering_pilot`: 50 symbols, 120 validation dates, and 6000 rows.
- Network ingestion is disabled by default and requires
  `ASHARE_ALLOW_NETWORK_INGESTION=1` or `--allow-network`.
- The default GOAL-06C.6/GOAL-06C.6A provider ingestion gate uses direct
  AKShare/local-import paths. The explicit CloakBrowser reference probe is
  separate, opt-in, tag-only, sanitized, and does not unlock GOAL-06D or any
  downstream module by itself.
- GOAL-06D is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `score_based_alpha_ranking` as a weak review-only baseline.
- GOAL-06D.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `raw_score_based_alpha_ranking` as a weak but bounded review-only
  baseline and allows GOAL-07A only as design-only preparation with warnings.
- GOAL-07A is implemented_design_only and currently `PASS_WITH_WARNINGS`. It
  defines contracts, future schema, rule catalog, state machine,
  upstream-warning mapping, governance boundary, and V2 lock audits only.
- GOAL-07A.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It reviews GOAL-07A design convertibility and marks GOAL-07B ready for an explicit review-only unlock request; it does not implement GOAL-07B.
- GOAL-07B.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It preserves GOAL-07B eligibility and does not itself calculate risk.
- GOAL-07B is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It produces deterministic, non-actionable risk overlay diagnostics at
  `trade_date + symbol` grain.
- GOAL-08A is implemented_design_only and currently `PASS`. It defines a
  names-only future recommendation input contract from GOAL-07B diagnostics,
  warning propagation, HIGH-risk actionability blocking, and zero-row future
  schema evidence only.
- GOAL-STORAGE-01 is implemented_infrastructure_only and currently `PASS`. It
  defines the local research lake contract, `ASHARE_PREMARKET_DATA_ROOT`
  resolution rule, directory boundaries, placement rules, manifest/checksum
  requirements, schema registry governance, and GitHub hygiene checks only.
- GOAL-08B.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It marks GOAL-08B review-only eligibility using only prior GOAL-07B,
  GOAL-08A, and GOAL-STORAGE-01 PASS/PASS_WITH_WARNINGS evidence. It creates no
  recommendation diagnostics rows itself.
- GOAL-08B is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  generates 100 deterministic, non-actionable recommendation diagnostic rows at
  `trade_date + symbol` grain from GOAL-07B risk diagnostics and GOAL-08A
  contract rules. `actionability_status` is always `never_actionable`.
- GOAL-09.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  marks GOAL-09 position-band diagnostics `future_review_only` eligible using
  only prior PASS/PASS_WITH_WARNINGS review evidence and creates no
  position-band rows.
- GOAL-09 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  generates deterministic, non-actionable position-band diagnostic rows at
  `trade_date + symbol` grain from GOAL-08B recommendation diagnostics and
  GOAL-07B risk overlay diagnostics. `position_actionability_status` is always
  `never_actionable`.
- GOAL-09.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  classifies remaining GOAL-09 warnings for future dashboard contract display
  rules, allows only an explicit future GOAL-DASHBOARD-00 design/contract gate
  request, and keeps Dashboard / Daily Report UI `locked_future`.
- GOAL-V1-INTEGRITY-01 is implemented_infrastructure_only and currently
  `PASS_WITH_WARNINGS`. It verifies only the GOAL-07B -> GOAL-08B -> GOAL-09 ->
  GOAL-09.1 review-only artifact lineage and structure before any future
  GOAL-DASHBOARD-00 design/contract request.
- GOAL-10A is implemented_design_only and currently `PASS_WITH_WARNINGS`. It
  defines future review-only backtest input, execution alignment, T+1,
  no-lookahead, metric, grouping, benchmark, cost/slippage, and tradability
  contracts from GOAL-08B and GOAL-09 diagnostics only. It runs no backtest and
  creates no performance rows, equity curves, portfolio returns, dashboard,
  trading, production, local-lake, broker, factor-mining, or DQN/RL outputs.
- GOAL-10B is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  computes non-actionable recommendation diagnostic forward-return metrics and
  IC/RankIC availability checks from GOAL-08B plus existing PIT-safe labels.
- GOAL-10B.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  audits GOAL-10B coverage and group variation using existing artifacts only,
  records `coverage_repair_not_possible_with_current_artifacts`, and writes no
  repaired rows or repaired metrics.
- GOAL-DATA-LABEL-01 is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It expands forward-return label coverage from existing
  committed OHLCV and benchmark samples only; it creates no new diagnostics,
  backtests, dashboards, local-lake data, trading, production, factor-mining,
  broker, or DQN/RL outputs.
- GOAL-V1-DIAGNOSTIC-COVERAGE-02 is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It creates separate non-actionable multi-symbol
  diagnostic coverage rows from committed Stage 6C approved-symbol evidence
  only; it does not overwrite canonical GOAL-07B/08B/09 diagnostics or run
  backtests.
- GOAL-10B.2 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It creates only non-actionable recommendation revalidation diagnostics over
  GOAL-V1-DIAGNOSTIC-COVERAGE-02 rows.
- GOAL-10C is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  creates only non-actionable row-level position-band cost/slippage sensitivity
  diagnostics.
- GOAL-DATA-PROVIDER-02A is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It creates only provider capability metadata for
  Tushare Pro, Baostock, AkShare, efinance, qstock, yfinance auxiliary, and
  local import fallback; it does not build an evaluation panel or run
  diagnostics/backtests.
- GOAL-DATA-PROVIDER-02A.1 is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It creates only review-only provider smoke-test
  metadata; live access is attempted only with `ASHARE_ALLOW_NETWORK_INGESTION=1`,
  Tushare Pro additionally requires `ASHARE_ALLOW_TUSHARE=1` and
  `TUSHARE_TOKEN` from the environment, and no provider tokens or raw payloads
  are printed or persisted.
- GOAL-DATA-PROVIDER-02B is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It creates only bounded source-backed normalized panel
  evidence and provider/coverage audit metadata; it does not create
  diagnostics, backtests, dashboards, trading, production, local-lake, broker,
  factor-mining, or DQN/RL outputs.
- GOAL-V1-DIAGNOSTIC-COVERAGE-03 is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It creates only source-backed non-actionable risk,
  recommendation eligibility, and position-band diagnostics from the committed
  GOAL-DATA-PROVIDER-02B normalized panel, preserves canonical GOAL-07B/08B/09
  artifacts, and does not create backtests, dashboards, trading, production,
  local-lake, broker, factor-mining, or DQN/RL outputs.
- GOAL-10B.3 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It creates only non-actionable DC03 recommendation revalidation diagnostics
  from GOAL-V1-DIAGNOSTIC-COVERAGE-03 plus GOAL-DATA-PROVIDER-02B evidence,
  classifies the current signal as weak/unreliable due group imbalance and
  unavailable numeric-score IC/RankIC, and recommends tiering repair before any
  position-band validation.
- GOAL-RISK-TIERING-01 is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It creates only separate non-actionable numeric risk
  score and severity tier diagnostics from DC03 and GOAL-DATA-PROVIDER-02B
  evidence, excludes future returns from score construction, uses forward
  returns only post-hoc, and classifies the current tiering signal as
  weak/unreliable.
- GOAL-REC-TIERING-01 remains `locked_future`.
- GOAL-10B.4 remains `locked_future`.
- GOAL-POSITION-BAND-VALIDATION-01 remains `locked_future`.
- GOAL-DATA-PANEL-02 remains `locked_future`.
- GOAL-10D remains `locked_future`.
- Production model promotion is false.
- Actionable recommendation execution, position output, dashboard, paper trading,
  broker/live trading, production DB writes, V2 factor mining, and DQN/RL are
  locked or not implemented.
- Python `>=3.9` is supported for the clean GOAL-06B workflow; Python `3.9.21`
  passed fresh-clone verification.
- Stable committed reports intentionally use `runtime_seconds=local_only`;
  volatile timing details belong in ignored files under `outputs/local/runtime/`.

## Reading Order

1. `PROJECT_STATE.md`
2. `README.md`
3. `CODEX.md`
4. `docs/09_STEP_ITERATION_LOG.md`
5. `docs/02_DATA_ENGINE.md`
6. `ROADMAP.md`

## Validation Habit

```bash
python -m compileall src scripts tests
python -m pytest tests -q
python scripts/run_goal06c_expanded_validation.py
python scripts/audit_storage_policy.py
python scripts/build_data_bundle_manifest.py
python scripts/audit_data_bundle_manifest.py
python scripts/audit_data_source_coverage.py
python scripts/audit_provider_failure_classification.py
python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py
python scripts/audit_browser_assisted_provider.py
python scripts/audit_workflow_cleanliness.py
python scripts/run_goal06d_model_comparison_calibration.py
python scripts/audit_goal06d_feature_contract.py
python scripts/audit_goal06d_split.py
python scripts/audit_goal06d_model_comparison.py
python scripts/audit_goal06d_calibration.py
python scripts/audit_goal06d_stability.py
python scripts/audit_goal06d_governance.py
python scripts/audit_goal06d_boundary_locks.py
python scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py
python scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py
python scripts/run_goal07b_risk_overlay_calculation_prototype.py
python scripts/audit_goal07b_risk_overlay_calculation_prototype.py
python scripts/run_goal08a_recommendation_contract_design_gate.py
python scripts/audit_goal08a_recommendation_contract_design_gate.py
python scripts/run_goal_storage01_local_research_lake_hardening_gate.py
python scripts/audit_goal_storage01_local_research_lake_hardening_gate.py
python scripts/run_goal08b0_recommendation_review_only_unlock_gate.py
python scripts/audit_goal08b0_recommendation_review_only_unlock_gate.py
python scripts/run_goal08b_recommendation_diagnostics_prototype.py
python scripts/audit_goal08b_recommendation_diagnostics_prototype.py
python scripts/run_goal090_position_band_review_only_unlock_gate.py
python scripts/audit_goal090_position_band_review_only_unlock_gate.py
python scripts/run_goal09_position_band_diagnostics_prototype.py
python scripts/audit_goal09_position_band_diagnostics_prototype.py
python scripts/run_goal091_position_band_warning_dashboard_readiness_gate.py
python scripts/audit_goal091_position_band_warning_dashboard_readiness_gate.py
python scripts/run_goal_v1_integrity01_artifact_lineage_structure_gate.py
python scripts/audit_goal_v1_integrity01_artifact_lineage_structure_gate.py
python scripts/run_goal10a_backtest_contract_design_gate.py
python scripts/audit_goal10a_backtest_contract_design_gate.py
python scripts/run_goal10b_recommendation_backtest_review_only.py
python scripts/audit_goal10b_recommendation_backtest_review_only.py
python scripts/run_goal10b1_backtest_coverage_repair_gate.py
python scripts/audit_goal10b1_backtest_coverage_repair_gate.py
python scripts/run_goal_data_label01_forward_return_label_coverage_expansion.py
python scripts/audit_goal_data_label01_forward_return_label_coverage_expansion.py
python scripts/run_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion.py
python scripts/audit_goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion.py
python scripts/run_goal10b2_recommendation_backtest_revalidation.py
python scripts/audit_goal10b2_recommendation_backtest_revalidation.py
python scripts/run_goal10c_cost_slippage_sensitivity_gate.py
python scripts/audit_goal10c_cost_slippage_sensitivity_gate.py
python scripts/run_goal_data_provider02a_multi_provider_capability_probe_gate.py
python scripts/audit_goal_data_provider02a_multi_provider_capability_probe_gate.py
python scripts/run_goal_data_provider02a1_network_smoke_test.py
python scripts/audit_goal_data_provider02a1_network_smoke_test.py
python scripts/run_goal_data_provider02b_source_backed_panel_build_gate.py
python scripts/audit_goal_data_provider02b_source_backed_panel_build_gate.py
python scripts/run_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate.py
python scripts/audit_goal_v1_diagnostic_coverage03_source_backed_diagnostics_gate.py
python scripts/run_goal10b3_dc03_recommendation_revalidation_gate.py
python scripts/audit_goal10b3_dc03_recommendation_revalidation_gate.py
python scripts/run_goal_risk_tiering01_risk_severity_numeric_score_gate.py
python scripts/audit_goal_risk_tiering01_risk_severity_numeric_score_gate.py
python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py
python scripts/rebuild_stage6c_from_engineering_panel.py
python scripts/audit_stage6c_expanded_validation.py
python scripts/audit_stage6c_ranking_baselines.py
python scripts/run_stage6c_walk_forward_validation.py
python scripts/audit_workflow_status.py
python scripts/run_goal06b_regression_suite.py
python scripts/run_e2e_trunk_verification_through_goal06b.py
python scripts/run_e2e_trunk_validation_through_goal06b.py
python scripts/run_safety_gate.py
python scripts/run_adapter_audit.py
```

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

## Do Not Drift

- Do not import legacy implementation code.
- Do not run legacy-only tests as active validation.
- Do not add absolute user-specific paths.
- Do not reintroduce volatile wall-clock timings into committed audit reports.
- Do not commit raw payloads, DBs, notebooks, caches, dashboards, or private
  logs.
- Do not create actionable recommendations, buy/sell/hold outputs, target
  prices, expected returns for action, position sizing, portfolio weights,
  dashboard, paper/live trading, production, backtest, factor-mining, broker,
  local-lake, or DQN/RL outputs. GOAL-07B is review-only risk diagnostics only,
  GOAL-08A is names-only design evidence only, GOAL-STORAGE-01 is
  infrastructure-only, GOAL-08B.0 is unlock-only eligibility evidence, and
  GOAL-08B is review-only non-actionable diagnostics only. GOAL-09.0 is
  unlock-only eligibility evidence. GOAL-09 is review-only non-actionable
  position-band diagnostics only. GOAL-09.1 is warning-review and
  dashboard-readiness evidence only. GOAL-V1-INTEGRITY-01 is artifact-lineage
  structure evidence only; it creates no new diagnostic rows or dashboard output
  and only allows a future explicit GOAL-DASHBOARD-00 design/contract gate
  request. GOAL-10A is design-only backtest contract evidence only; it runs no
  backtest and creates no performance rows, equity curves, portfolio returns, or
  cost/slippage outputs. GOAL-10B is review-only recommendation diagnostics
  backtest evidence only. GOAL-10B.1 is review-only coverage repair diagnostic
  evidence only and writes no repaired rows or metrics. GOAL-DATA-LABEL-01 is
  review-only label coverage evidence only. GOAL-V1-DIAGNOSTIC-COVERAGE-02 is
  review-only non-actionable diagnostic coverage evidence only and writes no
  backtests. GOAL-10B.2 is review-only recommendation revalidation diagnostics
  over DC02 rows. GOAL-10C is review-only row-level position-band cost/slippage
  sensitivity diagnostics. GOAL-DATA-PROVIDER-02A is review-only provider
  capability metadata only and builds no panel. GOAL-DATA-PROVIDER-02A.1 is
  review-only network-opt-in provider smoke-test metadata only; it is not
  provider selection, final panel evidence, diagnostics, backtest evidence, or
  an execution unlock. GOAL-DATA-PROVIDER-02B is review-only source-backed
  panel evidence only; GOAL-V1-DIAGNOSTIC-COVERAGE-03 is review-only
  source-backed diagnostic coverage only; GOAL-10B.3 is review-only DC03
  recommendation revalidation diagnostics only. GOAL-DATA-PANEL-02,
  GOAL-10D, actual positions, dashboards, and execution remain locked.

## GOAL-06D.1 Agent Note

GOAL-06D.1 is review-only warning repair for GOAL-06D. It may compare target
horizons and PIT-safe score variants, but it must not generate recommendations,
positions, risk overlays, dashboards, trading outputs, production model
promotion, or factor-mining outputs.

## GOAL-07A Agent Note
## GOAL-07A.1 Agent Note

GOAL-07A.1 is a review-only design review gate. It may classify warnings and write GOAL-07B unlock-readiness evidence, but it must not itself implement GOAL-07B, calculate risk values, assign symbol-level risk rows, or generate recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs. GOAL-07B.0 may mark GOAL-07B `future_review_only` eligible or preserve an existing GOAL-07B `implemented_review_only` diagnostic state using prior PASS/PASS_WITH_WARNINGS evidence only; it also must not calculate risk values or create downstream outputs. GOAL-07B may produce only review-only, non-actionable risk diagnostics. GOAL-08A may define only names-only future recommendation contract evidence with zero rows. GOAL-STORAGE-01 may harden only local research lake governance and GitHub hygiene; it does not unlock GOAL-08B by itself. GOAL-08B.0 may mark GOAL-08B review-only eligible using prior evidence only, but it must not itself generate recommendation diagnostics rows. GOAL-08B may produce only review-only, non-actionable recommendation diagnostics at `trade_date + symbol` grain. GOAL-09.0 may mark GOAL-09 future_review_only eligible using prior GOAL-08B evidence only, but it must not itself implement GOAL-09 or create position-band rows. GOAL-09 may produce only non-actionable review-only position-band diagnostics at `trade_date + symbol` grain; it must not produce actual positions, sizing, weights, orders, buy/sell/hold actions, target prices, dashboards, trading, production, backtests, factor-mining, broker, local-lake, or DQN/RL outputs. GOAL-09.1 may classify warnings and define future dashboard contract/display blockers only; it must not implement Dashboard / Daily Report UI, create dashboard files, HTML, Streamlit, frontend, visual reports, new recommendation rows, new position rows, actual position sizing, trading, production, backtests, factor-mining, local-lake, broker, or DQN/RL outputs. GOAL-V1-INTEGRITY-01 may verify only artifact lineage and structure over GOAL-07B, GOAL-08B, GOAL-09, and GOAL-09.1 evidence; it must not create new risk, recommendation, position, dashboard, local-lake, trading, production, backtest, factor-mining, broker, or DQN/RL outputs. GOAL-10A may define only design-only future backtest contracts; it must not run a backtest, generate backtest rows, create equity curves, create portfolio returns, fetch new data, create dashboards, write local-lake/trading/production data, integrate a broker, activate factor mining, or create DQN/RL outputs. GOAL-10B may produce only review-only, non-actionable recommendation diagnostic forward-return metrics and IC/RankIC availability evidence; it must not generate actions, portfolios, equity curves, dashboards, trading, production, local-lake, broker, factor-mining, or DQN/RL outputs. GOAL-10B.1 may audit coverage only. GOAL-DATA-LABEL-01 may produce only review-only label coverage evidence from committed samples. GOAL-V1-DIAGNOSTIC-COVERAGE-02 may produce only review-only non-actionable diagnostic coverage rows from committed Stage 6C approved-symbol evidence. GOAL-10B.2 may produce only review-only non-actionable recommendation revalidation diagnostics. GOAL-10C may produce only review-only non-actionable row-level position-band cost/slippage sensitivity diagnostics. GOAL-DATA-PROVIDER-02A may produce only review-only provider capability metadata; it must not build an evaluation panel or run diagnostics/backtests. GOAL-DATA-PROVIDER-02A.1 may produce only review-only network-opt-in provider smoke-test metadata; it must not select a provider, build a panel, treat smoke data as final panel evidence, persist raw payloads or tokens, or unlock diagnostics/backtests. GOAL-DATA-PROVIDER-02B may produce only bounded source-backed normalized panel evidence and provider/coverage audit metadata. GOAL-V1-DIAGNOSTIC-COVERAGE-03 may produce only non-actionable source-backed diagnostic coverage from the 02B panel; it must not overwrite canonical GOAL-07B/08B/09 artifacts or run backtests. GOAL-10B.3 may produce only non-actionable DC03 recommendation revalidation diagnostics; it must not create positions, portfolios, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs. GOAL-RISK-TIERING-01 may produce only separate non-actionable risk-tier diagnostics; it must not overwrite canonical GOAL-07B or DC03 outputs, use future returns in score construction, create recommendation rows, position rows, portfolios, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs. GOAL-REC-TIERING-01, GOAL-10B.4, GOAL-POSITION-BAND-VALIDATION-01, GOAL-DATA-PANEL-02, and GOAL-10D remain locked. All decision/execution paths remain locked.



GOAL-07A is implemented only as design governance. It may define input
contracts, future schemas, rule catalogs, state machines, warning mappings, and
audits. It must not calculate risk values, assign symbol-level risk tags,
generate recommendations or positions, create dashboards, write trading or
production data, activate factor mining, or implement GOAL-07B.

V2 factor research is `planned_locked` and disabled in V1. Do not create factor
mining, IC/RankIC mining, factor library generation, or factor integration
runners unless a future explicit V2 goal unlocks them.
