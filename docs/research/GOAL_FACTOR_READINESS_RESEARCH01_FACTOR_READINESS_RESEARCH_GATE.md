# GOAL-FACTOR-READINESS-RESEARCH-01 Factor Readiness Research Gate

Research-only gate that determines whether any factor can legitimately become `ready` for downstream RecTiering.
It never fabricates readiness, never lowers existing thresholds, and never unlocks GOAL-REC-TIERING-01.
Readiness requires the immovable in-sample bar plus an out-of-sample holdout and walk-forward stability.

Run: `python scripts/run_goal_factor_readiness_research01_factor_readiness_research_gate.py`

Outputs: readiness gap analysis, panel-expansion summary, candidate lineage/catalog, walk-forward and regime
validation summaries, anti-overfitting review, factor readiness status, decision reasons, construction warnings,
plus report/manifest/audit and a governance handoff. No actionable/recommendation/dashboard/trading output.