# Active Workflow Through GOAL-06B

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

This is the only implemented active workflow. It uses solid arrows only and
does not include GOAL-06C or any downstream future block as active. No active
node imports legacy demo paths, old runtime-evidence modules, obsolete step
runners, DQN/RL, dashboard, paper trading, recommendation, risk overlay,
broker/live trading, production DB writes, or production model promotion code.

## Module Dependency Structure

```mermaid
flowchart TD
    Core["core"] --> Universe["universe"]
    Core --> Data["data"]
    Data --> Market["market"]
    Data --> Sector["sector"]
    Data --> Events["events"]
    Data --> NLP["nlp"]
    Market --> Features["features"]
    Sector --> Features
    Events --> Features
    NLP --> Features
    Features --> Labels["labels"]
    Labels --> Datasets["datasets"]
    Features --> Datasets
    Datasets --> Scoring["scoring"]
    Scoring --> Training["training"]
    Training --> Validation["validation"]
    Validation --> Diagnostics["diagnostics"]
    Ops["ops / safety gates"] --> Validation
    Diagnostics -. "reads workflow results only" .-> Outputs["outputs"]
    Legacy["legacy implementation"] -. "not imported" .-> Core
    Locked["locked downstream modules"] -. "not imported" .-> Core
```

Diagnostics reads workflow results and helps the next worker triage failures; it
does not drive business logic.
