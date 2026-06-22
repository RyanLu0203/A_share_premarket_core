# A Share Premarket Core

Clean private active repository for the A-share pre-market alpha diagnosis and
risk-aware position-building decision support system.

This is not an automatic trading bot and does not provide investment advice. It
is a deterministic, review-only research workflow for PIT-safe data contracts,
label construction, feature-label merging, leakage checks, baseline scoring, the
GOAL-06B supervised baseline training gate, GOAL-06C expanded validation, and
the GOAL-06C.5/GOAL-06C.6 engineering data foundation gates.

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
    H -. "blocked until engineering_pilot" .-> F["GOAL-06D Model Comparison / Calibration<br/>(future_review_only)"]
```

GOAL-06C ranks are audit artifacts only. They are not recommendations, buy/sell
signals, position bands, portfolio weights, or production model outputs.
GOAL-06C.5 currently classifies the panel as `contract_demo`: 8 rows, 4 trading
dates, and 2 approved symbols.
GOAL-06C.6 adds compliant AKShare/source-backed ingestion infrastructure.
Network ingestion is disabled by default and requires `ASHARE_ALLOW_NETWORK_INGESTION=1`
or `--allow-network`. It classifies provider failures and does not use
browser-based bypass tooling for this provider ingestion gate.
GOAL-06C.6A adds finance-only network isolation evidence and a provider failure
taxonomy that separates ProxyError, timeout, DNS, TLS, connection reset/refused,
HTTP access, anti-bot/challenge, schema, parser, data-quality, PIT/label,
storage, and workflow-governance failures. Network failures must not be
collapsed into a generic class when a specific class can be determined.

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

## Lock Boundary

Recommendation, risk overlay calculation, dashboard, paper trading,
broker/live trading, production DB writes, production model promotion, and
DQN/RL remain locked. GOAL-06D is future review-only work and may proceed only
after `outputs/audits/engineering_panel_readiness_report.md` allows it. The
current contract-demo panel keeps GOAL-06D blocked.
GOAL-06C.6 can unblock GOAL-06D only as future review-only work after a
source-backed Stage 6C engineering panel reaches `engineering_pilot` or higher.

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
`workflow_status.csv`. Do not remove locks from risk, recommendation,
dashboard, paper/live trading, production, or DQN/RL unless a later explicit
gate allows it.
