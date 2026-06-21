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

Future review-only:

- GOAL-06C Expanded Validation and Ranking Baseline
- GOAL-06D Model Comparison and Calibration

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
