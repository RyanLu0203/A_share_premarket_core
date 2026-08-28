# GOAL-ALPHA-HYPOTHESIS-REDESIGN-01

Status: `PASS_WITH_WARNINGS` (`implemented_design_only`)

## Decision

Freeze the five existing price-derived factor families. Do not create Candidate03 variants or relax readiness thresholds. Four orthogonal hypotheses are pre-registered, but all are blocked pending separate acceptance of materially different PIT-safe evidence.

The preferred first hypothesis is bounded liquidity-shock normalization because its required evidence is conceptually closest to the governed market-data path while remaining distinct from the failed price-only variants. It still requires at least 100 symbols, verified volume/turnover/free-float/trade-status fields, and the pre-registered falsification rule before construction.

## Boundary

No factor values, labels, provider calls, evaluation rows, recommendations, positions, backtests, dashboards, trading, production, local-lake, broker, factor mining, or DQN/RL outputs are created. All downstream locks remain unchanged.
