# Factor Metric Diagnostic Overview (research-only)

A **read-only diagnostic view** over the committed `GOAL-QUANT-RESEARCH-04`
evaluation outputs. It exists so a human can *explore* the evaluated factors by
their already-computed metrics. It is **not** the locked
`GOAL-REC-TIERING-01` recommendation-score-tiering gate and is **not** a
premarket trading signal.

## What it does

`scripts/build_factor_metric_diagnostic_overview.py` reads:

- `outputs/research/goal_quant_research04_factor_overall_status.csv`
- `outputs/research/goal_quant_research04_regime_conditional_evaluation_summary.csv`
- `outputs/research/goal_quant_research04_leakage_pit_checks.csv`

and writes `outputs/research/factor_metric_diagnostic_overview.csv`, ordering
the factors by a transparent relative `diagnostic_composite_score` built from
existing metrics (fixed weights: `abs_mean_ic_1d` 0.30, `ic_information_ratio_proxy`
0.20, `regime_consistency_score` 0.20, `stability_score` 0.20, minus a leakage
penalty of 0.10 if the Quant04 PIT checks were not all `pass`). Each metric is
min-max normalised across the factor set, so the score is a *relative ordering*,
not an absolute quality measure. `relative_diagnostic_band` is a simple tertile
label (upper / middle / lower third).

## What it deliberately does NOT do

- No `ready` classification. Every factor keeps its true Quant04
  `overall_factor_status` and `candidate_for_rec_tiering` (all `false`).
- No BUY/SELL/HOLD, no portfolio, no order/position/target-price output.
- No `outputs/premarket_signal_*` artifact; nothing at the actionable output root.
- No change to `workflow_status.csv`, `locked_capabilities.json`, or any gate.
  `GOAL-REC-TIERING-01` stays `locked_future`; `ready_factor_count` stays 0.
- No dashboard/frontend artifact (that gate is locked). This CSV could *feed* a
  future, properly-unlocked visualization, but none is built here.

A high `diagnostic_composite_score` does **not** mean a factor is ready,
recommendable, or tradable — several `not_ready` factors rank highly, which is
exactly why this is an exploration view rather than a signal.
