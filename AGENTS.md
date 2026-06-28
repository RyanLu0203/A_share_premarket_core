# AGENTS

This file is long-term project memory for Codex and other coding agents.

## Operating Rules

- Work inside this clean target repository unless the user explicitly asks
  otherwise.
- Use GitHub as the durable source of truth.
- Treat `RyanLu0203/A_share_market_analysis_and_prediction` as historical
  legacy/evidence reference only.
- Never push raw payloads, quarantine files, SQLite DBs, credentials, `.env`,
  cache payloads, full news text, notebooks, production model artifacts,
  dashboards, or private logs.

## Current System Truth

- Approved symbols: `002475.SZ`, `600036.SH`.
- Blocked/pending: `000625.SZ`, `000858.SZ`, `601138.SH`, `601208.SH`.
- Active scoring boundary: project start through GOAL-06B.
- GOAL-06B supervised baseline training is review-only and pilot-only.
- GOAL-06C expanded validation and ranking baseline is implemented_review_only.
- GOAL-06C.5 storage, data bundle, source coverage, and engineering panel
  readiness is implemented_review_only.
- GOAL-06C.6 source-backed AKShare/provider ingestion is implemented_review_only
  and network-disabled by default.
- GOAL-06C.6A scoped finance network isolation and provider failure taxonomy is
  implemented_review_only. Network failures must be classified by specific
  failure type, not as a generic network bucket when the subtype is knowable.
- GOAL-06C.7 provider-ladder engineering data base expansion is
  implemented_review_only. Browser-assisted ingestion is optional,
  finance-domain-only, disabled by default, and requires
  `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1 --enable-browser-assisted`.
- The current source-backed GOAL-06C.7 provider-ladder panel tier is
  `engineering_pilot`: 50 symbols, 120 validation dates, and 6000 rows.
- GOAL-06D is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `score_based_alpha_ranking` as a weak review-only baseline.
- GOAL-06D.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It selected `raw_score_based_alpha_ranking` as a weak but bounded review-only
  baseline and allows GOAL-07A only as design-only preparation with warnings.
- GOAL-07A is implemented_design_only and currently `PASS_WITH_WARNINGS`. It
  defines design artifacts and audits only; no risk calculation is active.
- GOAL-07A.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It reviews GOAL-07A design convertibility and records GOAL-07B readiness for an explicit review-only unlock request.
- GOAL-07B.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It preserves GOAL-07B eligibility and does not itself calculate risk.
- GOAL-07B is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  produces deterministic, non-actionable risk diagnostics at
  `trade_date + symbol` grain.
- GOAL-08A is implemented_design_only and currently `PASS`. It defines a
  names-only future recommendation contract, warning propagation rules,
  HIGH-risk actionability blocking, and zero-row schema evidence only.
- GOAL-STORAGE-01 is implemented_infrastructure_only and currently `PASS`. It
  hardens the local research lake contract, `ASHARE_PREMARKET_DATA_ROOT`
  resolution, directory boundaries, placement rules, manifest/checksum
  requirements, schema registry governance, and GitHub hygiene only.
- GOAL-08B.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`.
  It marks GOAL-08B review-only eligibility using only prior GOAL-07B,
  GOAL-08A, and GOAL-STORAGE-01 PASS/PASS_WITH_WARNINGS evidence. It does not
  itself create recommendation diagnostics rows.
- GOAL-08B is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  generates 100 deterministic, non-actionable recommendation diagnostic rows at
  `trade_date + symbol` grain from GOAL-07B risk diagnostics and GOAL-08A
  contract rules. `actionability_status` is always `never_actionable`.
- GOAL-09.0 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  marks GOAL-09 position-band diagnostics `future_review_only` eligible only
  for a future explicit non-actionable prototype request.
- GOAL-09 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  generates deterministic, non-actionable position-band diagnostic rows at
  `trade_date + symbol` grain from GOAL-08B recommendation diagnostics and
  GOAL-07B risk overlay diagnostics. `position_actionability_status` is always
  `never_actionable`.
- GOAL-09.1 is implemented_review_only and currently `PASS_WITH_WARNINGS`. It
  classifies remaining GOAL-09 warnings for future dashboard contract display
  rules, allows only a future explicit GOAL-DASHBOARD-00 design/contract gate
  request, and keeps Dashboard / Daily Report UI `locked_future`.
- GOAL-V1-INTEGRITY-01 is implemented_infrastructure_only and currently
  `PASS_WITH_WARNINGS`. It verifies only the GOAL-07B -> GOAL-08B -> GOAL-09 ->
  GOAL-09.1 review-only artifact lineage and structure before any future
  GOAL-DASHBOARD-00 design/contract request.
- GOAL-10A is implemented_design_only and currently `PASS_WITH_WARNINGS`. It
  defines future review-only backtest input, date alignment, T+1/no-lookahead,
  metric, grouping, benchmark, cost/slippage, and tradability contracts only.
  It does not run backtests, generate performance rows, create equity curves,
  create portfolio returns, fetch new data, write local lake data, create
  dashboards, trade, write production data, integrate brokers, activate
  factor-mining, or create DQN/RL outputs.
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
  GOAL-DATA-PROVIDER-02B normalized panel and preserves canonical
  GOAL-07B/08B/09 artifacts.
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
- GOAL-RISK-TIERING-01.1 is implemented_review_only and currently
  `PASS_WITH_WARNINGS`. It creates only separate non-actionable downside-risk
  repair diagnostics from GOAL-RISK-TIERING-01 plus DC03 and
  GOAL-DATA-PROVIDER-02B evidence, separates volatility/momentum from downside
  score construction, excludes future returns from score construction, and
  classifies the current downside-risk tiering signal as weak/unreliable.
- GOAL-REC-TIERING-01 remains `locked_future`.
- GOAL-10B.4 remains `locked_future`.
- GOAL-POSITION-BAND-VALIDATION-01 remains `locked_future`.
- GOAL-DATA-PANEL-02 remains `locked_future`.
- GOAL-10D remains `locked_future`.
- Feature-label merge and leakage audit are active.
- Actionable recommendation execution, position output, position sizing,
  dashboard, paper/live trading, production DB writes, production model
  promotion, V2 factor mining, and DQN/RL remain locked or not implemented.
- The default GOAL-06C.6/GOAL-06C.6A provider ingestion gate uses direct
  AKShare/local-import paths. The explicit CloakBrowser reference probe is
  separate, opt-in, tag-only, sanitized, and does not unlock GOAL-06D or any
  downstream module by itself.
- Python `>=3.9` is supported for the clean GOAL-06B workflow.
- Committed validation summaries must be deterministic; volatile runtime timing
  belongs in ignored local diagnostics under `outputs/local/runtime/`.

## Required Agent Reading Order

1. `PROJECT_STATE.md`
2. `README.md`
3. `CODEX.md`
4. `docs/09_STEP_ITERATION_LOG.md`
5. `docs/02_DATA_ENGINE.md`
6. `ROADMAP.md`

## Update Discipline

Every meaningful program advance must update:

- `PROJECT_STATE.md`
- `docs/09_STEP_ITERATION_LOG.md`
- `CHANGELOG.md`
- relevant docs under `docs/`

Do not leave major state changes only in chat transcripts or local output files.

## Validation Habit

Minimum normal validation:

```bash
python -m compileall src scripts tests
python -m pytest tests -q
python scripts/run_goal06c_expanded_validation.py
python scripts/audit_storage_policy.py
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
python scripts/run_goal_risk_tiering011_downside_risk_repair_gate.py
python scripts/audit_goal_risk_tiering011_downside_risk_repair_gate.py
python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py
python scripts/rebuild_stage6c_from_engineering_panel.py
python scripts/audit_stage6c_expanded_validation.py
python scripts/audit_stage6c_ranking_baselines.py
python scripts/run_stage6c_walk_forward_validation.py
python scripts/run_safety_gate.py
python scripts/run_adapter_audit.py
```

For GOAL-06B active-trunk changes, also run:

```bash
python scripts/audit_workflow_status.py
python scripts/run_goal06b_regression_suite.py
python scripts/run_e2e_trunk_verification_through_goal06b.py
python scripts/run_e2e_trunk_validation_through_goal06b.py
python scripts/run_workflow_diagnostics.py
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

## Git Safety

- Branch from `main`; do not push directly to `main` unless the user has
  explicitly requested the clean bootstrap to land on `main`.
- Stage explicit files only.
- Keep generated runtime evidence out of commits unless it is a deliberately
  sanitized, tiny, review-facing fixture or required GOAL-06B audit output.
- Do not commit local-only runtime timing files.
- Report branch, commit hash, validation, excluded files, and review items.

## GOAL-06D.1 Agent Note

GOAL-06D.1 is implemented review-only warning repair. The repaired baseline may
remain weak but bounded; GOAL-07A has proceeded only as design-only governance
with warnings. Do not create recommendation, position, risk calculation,
dashboard, paper/live trading, production, factor-mining, or DQN/RL outputs.

## GOAL-07A Agent Note
## GOAL-07A.1 Agent Note

GOAL-07A.1 is review-only/design-review-only. It can maintain readiness reports, warning classifications, and unlock-readiness manifests, but must not itself implement GOAL-07B or create risk calculation, recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs. GOAL-07B.0 can mark GOAL-07B `future_review_only` eligible or preserve an existing GOAL-07B `implemented_review_only` diagnostic state using prior PASS/PASS_WITH_WARNINGS design-review evidence only; it must not create any calculation or downstream output. GOAL-07B can produce only review-only, non-actionable risk diagnostics. GOAL-08A may define only names-only future recommendation contract evidence with zero rows. GOAL-STORAGE-01 may harden only local research lake governance and GitHub hygiene; it must not materialize a lake, expand data coverage, create diagnostics, or unlock GOAL-08B by itself. GOAL-08B.0 can mark GOAL-08B review-only eligible using prior evidence only, but must not itself create recommendation diagnostics rows. GOAL-08B can produce only review-only, non-actionable recommendation diagnostics at `trade_date + symbol` grain. GOAL-09.0 can mark GOAL-09 position-band diagnostics future_review_only eligible using prior evidence only, but must not itself implement GOAL-09 or create position-band, position sizing, portfolio weight, dashboard, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL outputs. GOAL-09 can produce only non-actionable review-only position-band diagnostics at `trade_date + symbol` grain; it must not produce actual positions, sizing, weights, orders, buy/sell/hold actions, target prices, dashboards, trading, production, backtests, factor-mining, broker, local-lake, or DQN/RL outputs. GOAL-09.1 can classify GOAL-09 warnings and define future dashboard contract/display blockers only; it must not implement Dashboard / Daily Report UI, create dashboard files, HTML, Streamlit, frontend, visual reports, new recommendation rows, new position rows, actual position sizing, trading, production, backtests, factor-mining, broker, local-lake, or DQN/RL outputs. GOAL-V1-INTEGRITY-01 can verify only artifact lineage and structure over GOAL-07B, GOAL-08B, GOAL-09, and GOAL-09.1 evidence; it must not create new risk, recommendation, position, dashboard, local-lake, trading, production, backtest, factor-mining, broker, or DQN/RL outputs. GOAL-10A can define only design-only future backtest contracts; it must not run a backtest, generate backtest rows, create equity curves, create portfolio returns, fetch new data, create dashboards, write local-lake/trading/production data, integrate a broker, activate factor-mining, or create DQN/RL outputs. GOAL-10B may produce only review-only, non-actionable recommendation diagnostic forward-return metrics and IC/RankIC availability evidence; it must not generate actions, portfolios, equity curves, dashboards, trading, production, local-lake, broker, factor-mining, or DQN/RL outputs. GOAL-10B.1 may audit coverage only. GOAL-DATA-LABEL-01 may produce only review-only label coverage evidence from committed samples. GOAL-V1-DIAGNOSTIC-COVERAGE-02 may produce only review-only non-actionable diagnostic coverage rows from committed Stage 6C approved-symbol evidence. GOAL-10B.2 may produce only review-only non-actionable recommendation revalidation diagnostics. GOAL-10C may produce only review-only non-actionable row-level position-band cost/slippage sensitivity diagnostics. GOAL-DATA-PROVIDER-02A may produce only review-only provider capability metadata; it must not build an evaluation panel or run diagnostics/backtests. GOAL-DATA-PROVIDER-02A.1 may produce only review-only network-opt-in provider smoke-test metadata; it must not select a provider, build a panel, treat smoke data as final panel evidence, persist raw payloads or tokens, or unlock diagnostics/backtests. GOAL-DATA-PROVIDER-02B may produce only bounded source-backed normalized panel evidence and provider/coverage audit metadata. GOAL-V1-DIAGNOSTIC-COVERAGE-03 may produce only non-actionable source-backed diagnostic coverage from the 02B panel; it must not overwrite canonical GOAL-07B/08B/09 artifacts or run backtests. GOAL-10B.3 may produce only non-actionable DC03 recommendation revalidation diagnostics; it must not create positions, portfolios, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs. GOAL-RISK-TIERING-01 may produce only separate non-actionable risk-tier diagnostics; it must not overwrite canonical GOAL-07B or DC03 outputs, use future returns in score construction, create recommendation rows, position rows, portfolios, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs. GOAL-RISK-TIERING-01.1 may produce only separate non-actionable downside-risk repair diagnostics; it must not overwrite GOAL-RISK-TIERING-01 or DC03 outputs, use future returns in score construction, create recommendation rows, position rows, portfolios, dashboards, trading, production, broker, local-lake, factor-mining, or DQN/RL outputs. GOAL-REC-TIERING-01, GOAL-10B.4, GOAL-POSITION-BAND-VALIDATION-01, GOAL-DATA-PANEL-02, and GOAL-10D remain locked. All actionable recommendation/execution paths remain locked.



GOAL-07A is design-only. It may maintain contracts, schema definitions, rule
catalogs, state machine designs, warning mappings, governance docs, and audits.
It must not calculate risk overlay values, assign risk tags to real symbols,
produce recommendations or positions, create dashboards, write trading or
production data, activate factor mining, or implement GOAL-07B.

V2 factor research is planned but inactive. Keep
`configs/factors/v2_factor_research_contract.yaml` locked unless a future
explicit V2 goal authorizes activation.
