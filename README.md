# A Share Premarket Core

Clean private active repository for the A-share pre-market alpha diagnosis and
risk-aware position-building decision support system.

This is not an automatic trading bot and does not provide investment advice. It
is a deterministic, review-only research workflow for PIT-safe data contracts,
label construction, feature-label merging, leakage checks, baseline scoring, the
GOAL-06B supervised baseline training gate, GOAL-06C expanded validation, the
GOAL-06C.5/GOAL-06C.6/GOAL-06C.7 engineering data foundation gates, and the
GOAL-06D/GOAL-06D.1 review-only model comparison/calibration/stability
governance gates, the GOAL-07A design-only risk overlay governance gate, and
the GOAL-07B.0 review-only unlock eligibility gate, the GOAL-07B review-only
risk overlay diagnostic prototype, the GOAL-08A design-only contract gate,
GOAL-STORAGE-01 infrastructure-only local research lake hardening, and the
GOAL-08B.0 review-only unlock eligibility gate.

## Repository Roles

- `RyanLu0203/A_share_premarket_core`: clean active source of truth.
- `RyanLu0203/A_share_market_analysis_and_prediction`: historical
  legacy/evidence reference only.

This bootstrap is selective. It is not a mirror migration and does not copy the
legacy implementation tree.

## Quickstart

Supported runtime: Python `>=3.9`. The clean GOAL-06B workflow was verified
under Python `3.9.21` during fresh-clone audit.

```bash
python -m compileall src scripts tests
python -m pytest tests -q
python scripts/run_goal06b_regression_suite.py
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
python scripts/run_goal07a_risk_overlay_design_gate.py
python scripts/audit_goal07a_allowed_input_contract.py
python scripts/audit_goal07a_output_schema.py
python scripts/audit_goal07a_risk_rule_catalog.py
python scripts/audit_goal07a_state_machine.py
python scripts/audit_goal07a_upstream_warning_mapping.py
python scripts/audit_goal07a_governance_boundary.py
python scripts/audit_goal07a_boundary_locks.py
python scripts/audit_goal07a_v2_factor_lock.py
python scripts/run_goal07a1_risk_overlay_design_review_gate.py
python scripts/audit_goal07a1_input_contract_readiness.py
python scripts/audit_goal07a1_output_schema_safety.py
python scripts/audit_goal07a1_rule_convertibility.py
python scripts/audit_goal07a1_state_machine_review.py
python scripts/audit_goal07a1_warning_policy.py
python scripts/audit_goal07a1_boundary_locks.py
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
python scripts/rebuild_stage6c_from_engineering_panel.py
python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py
python scripts/run_e2e_trunk_verification_through_goal06b.py
python scripts/run_e2e_trunk_validation_through_goal06b.py
python scripts/run_safety_gate.py
python scripts/run_adapter_audit.py
```

## Active Workflow

```mermaid
flowchart TD
    A["Project Operating System"] --> B["Universe / Symbol Governance"]
    B --> C["Data / Provider / Source Health"]
    C --> D["Market / Sector / Stock / Event / NLP Contract Layers"]
    D --> E["PIT Signal Store"]
    E --> F["Label Builder"]
    F --> G["Benchmark Contract"]
    G --> H["Feature-Label Merge"]
    H --> I["Leakage Audit"]
    I --> J["Stage 6A Repair Panel"]
    J --> K["GOAL-06A Baseline Scoring Skeleton"]
    K --> L["GOAL-06B Supervised Baseline Training Gate"]
    L --> M["Validation / Verification / Diagnostics"]
    M --> N["Safety Gate / Adapter Audit"]
```

This active diagram uses solid arrows only and stops at GOAL-06B. GOAL-06C is
implemented as a review-only validation extension, not as active scoring,
recommendation, or position output.

## Review-Only Validation Extension

```mermaid
flowchart TD
    A["GOAL-06B Supervised Baseline Training Gate"] -. "review-only extension" .-> B["GOAL-06C Expanded Validation Panel<br/>(implemented_review_only)"]
    B -. "review-only ranking" .-> C["Deterministic Ranking Baselines<br/>(implemented_review_only)"]
    C -. "offline evaluation only" .-> D["Rank Metrics + Walk-Forward Diagnostics<br/>(implemented_review_only)"]
    D -. "engineering data gate" .-> E["GOAL-06C.5 Storage + Coverage + Panel Gate<br/>(implemented_review_only)"]
    E -. "source-backed provider gate" .-> G["GOAL-06C.6 AKShare Engineering Pilot Bundle Gate<br/>(implemented_review_only)"]
    G -. "failure taxonomy gate" .-> H["GOAL-06C.6A Scoped Network + Failure Taxonomy<br/>(implemented_review_only)"]
    H -. "provider ladder gate" .-> I["GOAL-06C.7 Provider Ladder Engineering Data Base Expansion<br/>(implemented_review_only)"]
    I -. "engineering_pilot reached; review-only gate" .-> F["GOAL-06D Model Comparison / Calibration / Stability<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    F -. "warning repair review-only" .-> I2["GOAL-06D.1 Calibration / Stability Warning Repair<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    I2 -. "design-only implemented" .-> J["GOAL-07A Risk Overlay Design<br/>(implemented_design_only; PASS_WITH_WARNINGS)"]
    J -. "design review readiness" .-> J2["GOAL-07A.1 Design Review + Unlock Readiness<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    J2 -. "explicit review-only unlock gate" .-> J3["GOAL-07B.0 Unlock Gate<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    J3 -. "review-only diagnostic prototype" .-> K["GOAL-07B Risk Overlay Calculation<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    K -. "implemented design-only" .-> O["GOAL-08A Recommendation Contract Design<br/>(implemented_design_only; PASS)"]
    O -. "implemented infrastructure-only" .-> S["GOAL-STORAGE-01 Local Research Lake Hardening<br/>(implemented_infrastructure_only; PASS)"]
    S -. "explicit review-only unlock gate" .-> S2["GOAL-08B.0 Unlock Gate<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    S2 -. "future review-only eligible" .-> P["GOAL-08B Recommendation Prototype<br/>(future_review_only; not implemented)"]
```

GOAL-06C ranks are audit artifacts only. They are not recommendations, buy/sell
signals, position bands, portfolio weights, or production model outputs.
GOAL-06C.5 originally classified the small clean-bootstrap panel as
`contract_demo`: 8 rows, 4 trading dates, and 2 approved symbols.
GOAL-06C.6 adds compliant AKShare/source-backed ingestion infrastructure.
Network ingestion is disabled by default and requires `ASHARE_ALLOW_NETWORK_INGESTION=1`
or `--allow-network`. It classifies provider failures on the default AKShare
path.
GOAL-06C.6A adds finance-only network isolation evidence and a provider failure
taxonomy that separates ProxyError, timeout, DNS, TLS, connection reset/refused,
HTTP access, anti-bot/challenge, schema, parser, data-quality, PIT/label,
storage, and workflow-governance failures. Network failures must not be
collapsed into a generic class when a specific class can be determined.
It also includes an explicit CloakBrowser reference probe that is optional,
tag-only, sanitized, and separate from the default provider path. That probe may
label a current access problem as solved only when it produces matching
domain-access or structured-ingestion evidence.
GOAL-06C.7 adds a deterministic provider ladder:
`akshare_direct`, `browser_assisted_optional`, `local_import`, and
`future_vendor_data_placeholder`. Browser-assisted ingestion remains disabled by
default and requires both `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1` and
`--enable-browser-assisted`. It is finance-domain-only, dynamic-import-only,
stores no raw browser artifacts, and counts only schema-valid rows. Domain
access alone is tagged separately. The latest explicit network-enabled
GOAL-06C.7 run reached `engineering_pilot` with 50 approved symbols, 120
validation trading dates, and 6000 usable rows. GOAL-06D has now run only as a
review-only model comparison/calibration/stability/governance gate. It is
`PASS_WITH_WARNINGS`, selected `score_based_alpha_ranking` as a weak
review-only baseline. GOAL-06D.1 repairs those warnings only as review-only
diagnostics and allows GOAL-07A only as design-only preparation with warnings.
GOAL-07A is now `implemented_design_only`; it defines contracts, future schema,
rule catalog, state machine, upstream-warning mapping, and governance audits
only. It does not calculate risk values or unlock recommendation, position,
dashboard, paper/live trading, production, factor mining, or DQN/RL.
GOAL-07A.1 is implemented as a review-only design review gate. It classifies upstream warnings, checks forbidden schema overlap, reviews rule/state-machine convertibility, and writes a GOAL-07B unlock readiness manifest. GOAL-07B.0 is implemented as the explicit review-only unlock gate. GOAL-07B is now implemented only as a review-only risk overlay diagnostic prototype: it writes non-actionable `trade_date + symbol` diagnostics, propagates upstream warnings, and does not create recommendation, position, dashboard, paper/live trading, production, backtest, factor-mining, broker, or DQN/RL outputs. GOAL-08A is implemented only as a design-only names-only contract gate with zero recommendation rows. GOAL-STORAGE-01 is infrastructure-only local research lake hardening; it defines storage root, directory, manifest, checksum, schema, and GitHub hygiene rules and does not unlock GOAL-08B by itself. GOAL-08B.0 is implemented as an unlock-only review gate based on prior GOAL-07B, GOAL-08A, and GOAL-STORAGE-01 PASS/PASS_WITH_WARNINGS evidence. GOAL-08B is now `future_review_only` eligible for a later explicit non-actionable diagnostics prototype request, but it is not implemented.

## Required Public Commands

The target repo preserves the active GOAL-06B command surface and GOAL-06C
review-only validation wrappers:

- `python scripts/audit_existing_modules.py`
- `python scripts/build_pit_signal_snapshot.py`
- `python scripts/audit_pit_signal_snapshot.py`
- `python scripts/build_label_snapshot.py`
- `python scripts/audit_label_snapshot.py`
- `python scripts/build_model_ready_candidate_dataset.py`
- `python scripts/audit_feature_label_leakage.py`
- `python scripts/run_stage6a_blocker_repair.py --no-network`
- `python scripts/run_baseline_scoring_skeleton.py`
- `python scripts/audit_baseline_scoring_skeleton.py`
- `python scripts/run_supervised_baseline_training.py`
- `python scripts/audit_supervised_baseline_training.py`
- `python scripts/build_stage6c_expanded_validation_dataset.py`
- `python scripts/audit_stage6c_expanded_validation.py`
- `python scripts/run_stage6c_ranking_baselines.py`
- `python scripts/audit_stage6c_ranking_baselines.py`
- `python scripts/run_stage6c_walk_forward_validation.py`
- `python scripts/run_goal06c_expanded_validation.py`
- `python scripts/audit_storage_policy.py`
- `python scripts/build_data_bundle_manifest.py`
- `python scripts/audit_data_bundle_manifest.py`
- `python scripts/audit_data_source_coverage.py`
- `python scripts/audit_provider_failure_classification.py`
- `python scripts/run_akshare_engineering_pilot_ingestion.py`
- `python scripts/run_goal06c7_provider_ladder_engineering_data_base_expansion.py`
- `ASHARE_ENABLE_BROWSER_ASSISTED_PROVIDER=1 python scripts/run_browser_assisted_finance_ingestion.py --allow-network --enable-browser-assisted`
- `python scripts/audit_browser_assisted_provider.py`
- `python scripts/audit_workflow_cleanliness.py`
- `python scripts/run_goal06d_model_comparison_calibration.py`
- `python scripts/audit_goal06d_feature_contract.py`
- `python scripts/audit_goal06d_split.py`
- `python scripts/audit_goal06d_model_comparison.py`
- `python scripts/audit_goal06d_calibration.py`
- `python scripts/audit_goal06d_stability.py`
- `python scripts/audit_goal06d_governance.py`
- `python scripts/audit_goal06d_boundary_locks.py`
- `python scripts/run_goal07a_risk_overlay_design_gate.py`
- `python scripts/audit_goal07a_allowed_input_contract.py`
- `python scripts/audit_goal07a_output_schema.py`
- `python scripts/audit_goal07a_risk_rule_catalog.py`
- `python scripts/audit_goal07a_state_machine.py`
- `python scripts/audit_goal07a_upstream_warning_mapping.py`
- `python scripts/audit_goal07a_governance_boundary.py`
- `python scripts/audit_goal07a_boundary_locks.py`
- `python scripts/audit_goal07a_v2_factor_lock.py`
- `python scripts/run_goal07a1_risk_overlay_design_review_gate.py`
- `python scripts/audit_goal07a1_input_contract_readiness.py`
- `python scripts/audit_goal07a1_output_schema_safety.py`
- `python scripts/audit_goal07a1_rule_convertibility.py`
- `python scripts/audit_goal07a1_state_machine_review.py`
- `python scripts/audit_goal07a1_warning_policy.py`
- `python scripts/audit_goal07a1_boundary_locks.py`
- `python scripts/run_goal07b0_risk_overlay_review_only_unlock_gate.py`
- `python scripts/audit_goal07b0_risk_overlay_review_only_unlock_gate.py`
- `python scripts/run_goal07b_risk_overlay_calculation_prototype.py`
- `python scripts/audit_goal07b_risk_overlay_calculation_prototype.py`
- `python scripts/run_goal08a_recommendation_contract_design_gate.py`
- `python scripts/audit_goal08a_recommendation_contract_design_gate.py`
- `python scripts/run_goal_storage01_local_research_lake_hardening_gate.py`
- `python scripts/audit_goal_storage01_local_research_lake_hardening_gate.py`
- `python scripts/run_goal08b0_recommendation_review_only_unlock_gate.py`
- `python scripts/audit_goal08b0_recommendation_review_only_unlock_gate.py`
- `python scripts/build_engineering_pilot_universe.py`
- `python scripts/build_source_backed_local_bundle.py`
- `python scripts/audit_source_backed_local_bundle.py`
- `python scripts/build_source_backed_pit_signal_panel.py`
- `python scripts/build_source_backed_label_panel.py`
- `python scripts/rebuild_stage6c_source_backed_engineering_panel.py`
- `python scripts/audit_stage6c_source_backed_engineering_panel.py`
- `python scripts/run_goal06c6_source_backed_engineering_pilot_bundle.py`
- `python scripts/build_engineering_pit_signal_panel.py`
- `python scripts/audit_engineering_pit_signal_panel.py`
- `python scripts/build_engineering_label_panel.py`
- `python scripts/audit_engineering_label_panel.py`
- `python scripts/rebuild_stage6c_from_engineering_panel.py`
- `python scripts/run_current_trunk_validation.py`
- `python scripts/run_program_validation_profile.py`
- `python scripts/run_safety_gate.py`
- `python scripts/run_adapter_audit.py`
- `python scripts/run_workflow_diagnostics.py`
- `python scripts/audit_workflow_status.py`
- `python scripts/run_cloakbrowser_reference_probe.py`

## Protected Outputs

The active evidence chain is regenerated locally and committed only as concise,
sanitized CSV/Markdown/JSON artifacts. Raw provider payloads, raw HTML, full news
text, DBs, notebooks, caches, private logs, dashboards, and model artifacts for
production promotion are forbidden.

Stable committed reports do not store volatile wall-clock timings. Runtime
details are preserved in ignored local diagnostics under `outputs/local/runtime/`.

GOAL-06C.6A provider failure evidence is stored as sanitized metadata only:

- `outputs/audits/provider_failure_events.csv`
- `outputs/audits/provider_failure_summary.md`
- `outputs/audits/provider_failure_summary.json`
- `outputs/audits/goal06c6_network_isolation_report.md`
- `outputs/audits/goal06c6_failure_taxonomy_report.md`
- `outputs/audits/cloakbrowser_reference_problem_tags.csv`
- `outputs/audits/cloakbrowser_reference_probe_results.csv`
- `outputs/audits/cloakbrowser_reference_ingestion_report.md`
- `outputs/audits/cloakbrowser_reference_ingestion_report.json`
- `outputs/audits/browser_assisted_provider_events.csv`
- `outputs/audits/browser_assisted_provider_audit.md`
- `outputs/audits/browser_assisted_provider_audit.json`
- `outputs/audits/workflow_cleanliness_audit.md`
- `outputs/audits/goal06c7_readiness_report.md`
- `outputs/models/goal06d/model_comparison_summary.csv`
- `outputs/models/goal06d/calibration_summary.csv`
- `outputs/models/goal06d/stability_summary.csv`
- `outputs/audits/goal06d_readiness_report.md`
- `outputs/audits/goal06d_governance_audit.md`
- `outputs/audits/goal06d_boundary_lock_audit.md`
- `outputs/audits/goal07a_readiness_report.md`
- `outputs/audits/goal07a_governance_boundary_audit.md`
- `outputs/audits/goal07a_boundary_lock_audit.md`
- `outputs/audits/goal07a1_design_review_report.md`
- `outputs/audits/goal07a1_unlock_readiness_manifest.json`
- `outputs/audits/goal07b0_unlock_gate_report.md`
- `outputs/audits/goal07b0_unlock_gate_manifest.json`
- `outputs/audits/goal07b0_unlock_gate_audit_report.md`
- `outputs/risk_overlay/goal07b_review_only_risk_overlay.csv`
- `outputs/diagnostics/goal07b_risk_overlay_diagnostics.csv`
- `outputs/audits/goal07b_risk_overlay_calculation_report.md`
- `outputs/audits/goal07b_risk_overlay_calculation_manifest.json`
- `outputs/audits/goal07b_risk_overlay_calculation_audit.md`
- `configs/recommendation/goal08a_future_recommendation_input_contract.yaml`
- `configs/recommendation/goal08a_future_recommendation_schema.yaml`
- `configs/recommendation/goal08a_warning_propagation_policy.yaml`
- `configs/recommendation/goal08a_actionability_guardrails.yaml`
- `configs/recommendation/goal08a_recommendation_state_machine.yaml`
- `outputs/audits/goal08a_recommendation_contract_design_report.md`
- `outputs/audits/goal08a_recommendation_contract_design_manifest.json`
- `outputs/audits/goal08a_recommendation_contract_design_audit.md`
- `configs/storage/goal_storage01_local_research_lake_contract.yaml`
- `docs/storage/GOAL_STORAGE01_LOCAL_RESEARCH_LAKE_HARDENING_GATE.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_report.md`
- `outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json`
- `outputs/audits/goal_storage01_local_research_lake_hardening_audit.md`
- `configs/recommendation/goal08b0_review_only_unlock_policy.yaml`
- `docs/recommendation/GOAL08B0_RECOMMENDATION_REVIEW_ONLY_UNLOCK_GATE.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_report.md`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json`
- `outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md`

## Lock Boundary

Recommendation, position sizing, dashboard, paper trading, broker/live trading,
production DB writes, production model promotion, backtests, V2 factor mining,
and DQN/RL remain locked. GOAL-07A is implemented only as design-only
governance; GOAL-07B is implemented only as a review-only diagnostic prototype.
GOAL-08A is implemented only as a design-only names-only contract gate with
zero recommendation rows. GOAL-STORAGE-01 is infrastructure-only storage
hardening and does not materialize a data lake, fetch broader data, or unlock
GOAL-08B by itself. GOAL-08B.0 is unlock-only and marks GOAL-08B
`future_review_only` eligible for a later explicit non-actionable diagnostics
prototype request. GOAL-08B is still not implemented.

GOAL-06D.1 is the review-only warning repair layer for those GOAL-06D warnings.
It tests PIT-safe score variants, target horizons, calibration reliability,
feature sign stability, and provider concentration disclosure. GOAL-07A carries
those warnings into design-only risk governance; GOAL-07B carries them into
non-actionable risk diagnostics. No recommendation, position, dashboard,
trading, production, factor-mining, or DQN/RL outputs are produced.

V2 factor research is planned but inactive. The placeholder contract is locked,
disabled in V1, and forbids factor mining, IC/RankIC mining, factor library
generation, factor-to-model integration, and factor-to-recommendation
integration.

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
