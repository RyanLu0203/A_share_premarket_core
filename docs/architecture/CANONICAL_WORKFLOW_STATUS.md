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

Future review-only:

- none currently unlocked beyond GOAL-06D

Future design-only:

- GOAL-07A Risk Overlay Design

Locked future:

- GOAL-07B Risk Overlay Calculation Prototype
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
`workflow_status.csv`. Do not remove locks from risk, recommendation,
dashboard, paper/live trading, production, or DQN/RL unless a later explicit
gate allows it.

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
model promotion, or DQN/RL artifacts. GOAL-07A remains future design-only and
everything downstream remains locked.
