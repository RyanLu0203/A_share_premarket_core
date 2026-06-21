# Active Workflow Through GOAL-06B

```mermaid
flowchart TD
    A["Project Operating System"] --> B["Universe / Symbol Governance"]
    B --> C["Data / Provider / Source Health"]
    C --> D["Market Context Contract"]
    C --> E["Sector Context Contract"]
    C --> F["Stock OHLCV Contract"]
    C --> G["Event Metadata Contract"]
    C --> H["NLP Contract Gate"]
    D --> I["PIT Signal Store"]
    E --> I
    F --> I
    G --> I
    H --> I
    I --> J["Label Builder"]
    J --> K["Benchmark Contract"]
    K --> L["Feature-Label Merge"]
    L --> M["Leakage Audit"]
    M --> N["Stage 6A Repair Panel"]
    N --> O["Baseline Scoring Skeleton"]
    O --> P["Supervised Baseline Training Gate"]
    P --> Q["Validation / Verification / Diagnostics"]
```

No active node imports legacy demo paths, old runtime-evidence modules,
obsolete step runners, DQN/RL, dashboard, paper trading, recommendation, risk
overlay, broker/live trading, production DB writes, or production model
promotion code.

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
