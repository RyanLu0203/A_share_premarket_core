# Research Diagnostic Dashboard V0 (GOAL-RESEARCH-DIAGNOSTIC-DASHBOARD-V0)

A **read-only, research-only** local viewer for morning review over already-committed
Quant04 / Regime02 / factor-diagnostic evidence. It is **not** GOAL-REC-TIERING-01,
**not** a recommendation dashboard, and **not** a trading interface. It renders
existing metrics; it never creates signal, readiness, recommendation, or position
semantics, and it changes no governance/workflow state.

## Why stdlib, not Streamlit

The issue prefers Streamlit *"unless repository constraints make another lightweight
local UI clearly safer."* They do: `streamlit` and `.html`/`.htm` are **forbidden
output tokens** in `scripts/audit_destructive_changes.py`, and `outputs/dashboard*`
is forbidden by the V1-integrity gate. So this V0 uses only the Python standard
library (`http.server`) and renders HTML **in memory per request** — no HTML/CSS/JS
or any frontend artifact is written or committed.

## Launch

```bash
# serve locally (renders committed evidence on each request)
python apps/research_diagnostic_dashboard_v0.py            # http://127.0.0.1:8760
python apps/research_diagnostic_dashboard_v0.py --host 127.0.0.1 --port 8760

# startup smoke test (renders once, no server)
python apps/research_diagnostic_dashboard_v0.py --check

# (re)write the review manifest
python apps/research_diagnostic_dashboard_v0.py --manifest
```

Exploration query params when serving: `?sort=<column>&status=<overall_factor_status>&top=<N>`
(e.g. `?sort=diagnostic_composite_score&status=conditionally_useful&top=10`). Sorting,
filtering, and Top-N are presentation-only and confer no readiness or recommendation.

## Modules

1. **Market / Regime Context** — Regime02 refined regime coverage + transition summaries.
2. **Factor Diagnostic Overview** — all evaluated factors from
   `outputs/research/factor_metric_diagnostic_overview.csv` with their *true* Quant04
   `overall_factor_status` (`conditionally_useful` / `not_ready`), diagnostic composite
   score, diagnostic band, IC / stability / regime-consistency fields, and regime breakdown.
3. **Warnings / Integrity** — PIT/leakage checks, Quant04 & Regime02 construction /
   weak-signal warnings, data-quality summary, provider health.
4. **Evidence / Provenance** — the committed source files consumed, presence flags, disclaimer.

## Inputs consumed (read-only)

See `src/ashare_premarket/research/research_diagnostic_view.py::INPUTS` and the review
manifest at `outputs/research/research_diagnostic_view_v0_manifest.json`.

## Boundary confirmation

No BUY/SELL/HOLD, no target prices, no recommendation tags, no strong/medium/weak action
tiers, no `ready` fabrication (no factor is shown as `ready`; `candidate_for_rec_tiering`
stays `false`), no new alpha/recommendation score, no premarket signal output, no positions
or weights, no trading/broker/production/local-lake/factor-mining/DQN-RL. `GOAL-REC-TIERING-01`
and `dashboard_daily_report` remain `locked_future`; `ready_factor_count` remains 0. The
only committed artifacts are Python code, tests, this doc, and a JSON review manifest.
