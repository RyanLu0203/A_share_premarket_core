# Full Program Roadmap After Clean Bootstrap

Solid arrows are implemented active workflow through GOAL-06B. Dotted arrows are
future, locked, design-only, or not-started stages.

```mermaid
flowchart TD
    A["Project OS (implemented_active)"] --> B["Universe + Source Governance (implemented_active)"]
    B --> C["PIT Signal Store (implemented_active)"]
    C --> D["Label Builder (implemented_active)"]
    D --> E["Feature-Label Merge + Leakage Audit (implemented_active)"]
    E --> F["Stage 6A Repair + Baseline Scoring (implemented_active)"]
    F --> G["GOAL-06B Supervised Baseline Gate (implemented_active / review_only)"]
    G -. "future review-only" .-> H["GOAL-06C Expanded Validation + Ranking Baseline (review_only_future)"]
    H -. "future review-only" .-> I["GOAL-06D Model Comparison / Calibration (review_only_future)"]
    I -. "design only" .-> J["GOAL-07A Risk Overlay Design (design_only_future)"]
    J -. "locked future" .-> K["GOAL-07B Risk Overlay Calculation Prototype (locked_future)"]
    K -. "locked future" .-> L["Position-Band Recommendation (locked_future)"]
    L -. "not started" .-> M["Signal Backtest (not_started)"]
    M -. "not started" .-> N["Portfolio Backtest (not_started)"]
    N -. "not started" .-> O["Cost / Slippage Sensitivity (not_started)"]
    O -. "not started" .-> P["Paper Trading Journal (locked_future)"]
    P -. "not started" .-> Q["Failure Attribution (not_started)"]
    Q -. "not started" .-> R["Dashboard / Daily Report (locked_future)"]
    R -. "not started" .-> S["Production Hardening (locked_future)"]
    S -. "locked future" .-> T["Broker / Live Trading (locked_future)"]
    S -. "locked future" .-> U["Production DB Writes (locked_future)"]
    G -. "optional only" .-> V["DQN/RL Optional Research Benchmark (deleted_from_active_mainline)"]
```

The clean active mainline is GOAL-06B and earlier. Anything beyond GOAL-06B must
earn a separate promotion gate.
