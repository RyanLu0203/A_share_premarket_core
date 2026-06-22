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

This is the only implemented active scoring workflow. It uses solid arrows only
and does not include GOAL-06C or any downstream future block as active scoring.
GOAL-06C is implemented separately as review-only validation evidence. No
active node imports legacy demo paths, old runtime-evidence modules, obsolete
step runners, DQN/RL, dashboard, paper trading, recommendation, risk overlay,
broker/live trading, production DB writes, or production model promotion code.

## GOAL-06C Review-Only Validation Extension

```mermaid
flowchart TD
    A["GOAL-06B Supervised Baseline Training Gate"] -. "review-only validation extension" .-> B["Expanded Validation Panel<br/>(implemented_review_only)"]
    B -. "deterministic offline ranks" .-> C["Ranking Baselines<br/>(implemented_review_only)"]
    C -. "offline evaluation only" .-> D["Rank Metrics + Walk-Forward Diagnostics<br/>(implemented_review_only)"]
    D -. "engineering data gate" .-> E["GOAL-06C.5 Storage + Coverage + Panel Gate<br/>(implemented_review_only)"]
    E -. "source-backed provider gate" .-> F["GOAL-06C.6 Source-Backed Bundle Gate<br/>(implemented_review_only)"]
    F -. "future review-only after engineering_pilot" .-> G["GOAL-06D Model Comparison / Calibration<br/>(future_review_only)"]
```

The extension writes review-only evidence under `outputs/stage6c/` and
`outputs/audits/`. It does not emit recommendations, position bands, portfolio
weights, risk overlays, dashboard outputs, trading instructions, production
writes, production model promotion, or DQN/RL artifacts. GOAL-06C.6 provider
ingestion is network-disabled by default on the direct AKShare path. The
explicit CloakBrowser reference probe is separate tag-only evidence and does not
change the active workflow through GOAL-06B.

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
    Validation -. "review-only extension" .-> Stage6C["stage6c validation"]
    Data -. "optional source-backed provider ingestion" .-> Providers["providers"]
    Providers -. "local-only heavy bundle" .-> Stage6C
    Validation --> Diagnostics["diagnostics"]
    Ops["ops / safety gates"] --> Validation
    Diagnostics -. "reads workflow results only" .-> Outputs["outputs"]
    Legacy["legacy implementation"] -. "not imported" .-> Core
    Locked["locked downstream modules"] -. "not imported" .-> Core
```

Diagnostics reads workflow results and helps the next worker triage failures; it
does not drive business logic.
