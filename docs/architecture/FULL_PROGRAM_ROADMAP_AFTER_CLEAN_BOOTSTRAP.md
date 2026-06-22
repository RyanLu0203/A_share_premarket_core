# Full Program Roadmap After Clean Bootstrap

Solid arrows are implemented active workflow through GOAL-06B. Dotted arrows are
review-only extensions, future, locked, design-only, or not-started stages.

```mermaid
flowchart TD
    A["Project OS<br/>(implemented_active)"] --> B["Universe + Source Governance<br/>(implemented_active)"]
    B --> C["PIT Signal Store<br/>(implemented_active)"]
    C --> D["Label Builder<br/>(implemented_active)"]
    D --> E["Feature-Label Merge + Leakage Audit<br/>(implemented_active)"]
    E --> F["Stage 6A Repair + Baseline Scoring<br/>(implemented_active)"]
    F --> G["GOAL-06B Supervised Baseline Gate<br/>(implemented_active / review_only)"]
    G -. "implemented review-only" .-> H["GOAL-06C Expanded Validation + Ranking Baseline<br/>(implemented_review_only)"]
    H -. "implemented review-only data gate" .-> X["GOAL-06C.5 Storage + Coverage + Engineering Panel<br/>(implemented_review_only; contract_demo)"]
    X -. "source-backed ingestion gate" .-> Y["GOAL-06C.6 Source-Backed Engineering Pilot Bundle<br/>(implemented_review_only; network-disabled by default)"]
    Y -. "blocked until engineering_pilot" .-> I["GOAL-06D Model Comparison / Calibration<br/>(future_review_only)"]
    I -. "future design-only" .-> J["GOAL-07A Risk Overlay Design<br/>(future_design_only)"]
    J -. "locked future" .-> K["GOAL-07B Risk Overlay Calculation Prototype<br/>(locked_future)"]
    K -. "locked future" .-> L["Position-Band Recommendation<br/>(locked_future)"]
    L -. "locked future" .-> M["Signal Backtest<br/>(locked_future)"]
    M -. "locked future" .-> N["Portfolio Backtest<br/>(locked_future)"]
    N -. "locked future" .-> O["Cost / Slippage Sensitivity<br/>(locked_future)"]
    O -. "locked future" .-> P["Paper Trading Journal<br/>(locked_future)"]
    P -. "locked future" .-> Q["Failure Attribution<br/>(locked_future)"]
    Q -. "locked future" .-> R["Dashboard / Daily Report<br/>(locked_future)"]
    R -. "locked future" .-> S["Production Hardening<br/>(locked_future)"]
    S -. "locked future" .-> T["Broker / Live Trading<br/>(locked_future)"]
    S -. "locked future" .-> U["Production DB Writes<br/>(locked_future)"]
    I -. "locked future" .-> W["Production Model Promotion<br/>(locked_future)"]
    G -. "optional only" .-> V["DQN/RL Optional Research Benchmark<br/>(deleted_from_active_mainline)"]
```

The clean active scoring mainline is GOAL-06B and earlier. GOAL-06C and
GOAL-06C.5 and GOAL-06C.6 are implemented review-only extensions and not
recommendation, positioning, risk, trading, dashboard, production, or DQN/RL
workflows. GOAL-06C.6 uses compliant provider ingestion only when explicitly
network-enabled and does not use cloakbrowser, stealth browser automation,
captcha solving, or proxy rotation. Anything beyond GOAL-06C.6 must earn a
separate promotion gate and update
`configs/project/workflow_status.csv`.
