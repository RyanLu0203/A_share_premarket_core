# Program Roadmap And Architecture

This document summarizes the clean active workflow after the private bootstrap.

See also:

- `docs/architecture/CANONICAL_WORKFLOW_STATUS.md`
- `docs/architecture/ACTIVE_WORKFLOW_THROUGH_GOAL06B.md`
- `docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md`

```mermaid
flowchart TD
    A["Project Operating System"] --> B["Universe / Symbol Governance"]
    B --> C["Source Health + Context Contracts"]
    C --> D["PIT Signal Store"]
    D --> E["Label Builder + Benchmark Contract"]
    E --> F["Feature-Label Merge"]
    F --> G["Leakage Audit"]
    G --> H["Stage 6A Repair Panel"]
    H --> I["Baseline Scoring Skeleton"]
    I --> J["GOAL-06B Review-Only Supervised Training"]
    J --> K["Verification / Validation / Diagnostics"]
    K -. "implemented review-only" .-> L["GOAL-06C Expanded Validation + Ranking"]
    L -. "implemented review-only data gate" .-> N["GOAL-06C.5 Storage + Coverage + Engineering Panel"]
    N -. "source-backed provider gate" .-> O["GOAL-06C.6 Source-Backed Engineering Pilot Bundle"]
    O -. "failure taxonomy gate" .-> P["GOAL-06C.6A Scoped Network + Failure Taxonomy"]
    P -. "provider ladder gate" .-> Q["GOAL-06C.7 Provider Ladder Engineering Data Base Expansion"]
    Q -. "implemented review-only after engineering_pilot" .-> M["GOAL-06D Model Comparison / Calibration / Stability"]
    M -. "warning repair review-only" .-> M2["GOAL-06D.1 Calibration / Stability Warning Repair"]
    M2 -. "implemented design-only" .-> R["GOAL-07A Risk Overlay Design<br/>(implemented_design_only; PASS_WITH_WARNINGS)"]
    R -. "review-only unlock readiness" .-> R2["GOAL-07A.1 Design Review<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R2 -. "explicit unlock gate" .-> R3["GOAL-07B.0 Unlock Gate<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R3 -. "review-only diagnostics" .-> R4["GOAL-07B Risk Overlay Calculation<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R4 -. "implemented design-only" .-> R5["GOAL-08A Recommendation Contract Design<br/>(implemented_design_only; PASS)"]
    R5 -. "implemented infrastructure-only" .-> R7["GOAL-STORAGE-01 Local Research Lake Hardening<br/>(implemented_infrastructure_only; PASS)"]
    R7 -. "explicit review-only unlock gate" .-> R8["GOAL-08B.0 Unlock Gate<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R8 -. "review-only diagnostics" .-> R6["GOAL-08B Recommendation Diagnostics<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R6 -. "explicit review-only unlock gate" .-> R9A["GOAL-09.0 Position-Band Unlock Gate<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R9A -. "review-only diagnostics" .-> R9["GOAL-09 Position-Band Diagnostics<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R9 -. "warning review / dashboard readiness" .-> R91["GOAL-09.1 Dashboard Readiness<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    R91 -. "artifact-lineage integrity only" .-> V1["GOAL-V1-INTEGRITY-01 Structure Gate<br/>(implemented_infrastructure_only; PASS_WITH_WARNINGS)"]
    V1 -. "implemented design-only" .-> T10A["GOAL-10A Backtest Contract Design<br/>(implemented_design_only; PASS_WITH_WARNINGS)"]
    T10A -. "review-only diagnostics" .-> T10B["GOAL-10B Recommendation Diagnostics Backtest<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    T10B -. "coverage repair diagnostics" .-> T10B1["GOAL-10B.1 Coverage Repair Gate<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    T10B1 -. "label coverage expansion" .-> DL01["GOAL-DATA-LABEL-01 Forward-Return Label Coverage<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    DL01 -. "review-only diagnostics" .-> DC02["GOAL-V1-DIAGNOSTIC-COVERAGE-02 Multi-Symbol Diagnostics<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    DC02 -. "review-only revalidation" .-> T10B2["GOAL-10B.2 Recommendation Backtest Revalidation<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    T10B2 -. "review-only sensitivity" .-> T10C["GOAL-10C Cost / Slippage Sensitivity<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    T10C -. "provider capability probe" .-> P02A["GOAL-DATA-PROVIDER-02A Multi-Provider Capability Probe<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    P02A -. "network opt-in smoke test" .-> P02A1["GOAL-DATA-PROVIDER-02A.1 Network Opt-In Provider Smoke Test<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    P02A1 -. "source-backed panel gate" .-> P02B["GOAL-DATA-PROVIDER-02B Source-Backed Panel Build<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    P02B -. "evaluation panel remains locked" .-> PANEL02["GOAL-DATA-PANEL-02 Evaluation Panel<br/>(locked_future)"]
    P02B -. "source-backed diagnostics" .-> DC03["GOAL-V1-DIAGNOSTIC-COVERAGE-03 Source-Backed Diagnostics<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    DC03 -. "review-only revalidation" .-> T10B3["GOAL-10B.3 DC03 Recommendation Revalidation<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    T10B3 -. "risk tiering" .-> RISK01["GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    RISK01 -. "downside repair" .-> RISK011["GOAL-RISK-TIERING-01.1 Downside Risk Repair<br/>(implemented_review_only; PASS_WITH_WARNINGS)"]
    RISK011 -. "research-only factor lab" .-> QRESEARCH01["GOAL-QUANT-RESEARCH-01 Factor Research Lab<br/>(implemented_research_only; PASS_WITH_WARNINGS)"]
    QRESEARCH01 -. "research-only terminal" .-> MVP01["GOAL-MVP-01 Premarket Research Diagnostic Terminal<br/>(implemented_mvp_research_only; PASS_WITH_WARNINGS)"]
    MVP01 -. "research-only alpha candidates" .-> ALPHA01["GOAL-ALPHA-FACTOR-CANDIDATE-01 Alpha Factor Candidate Research Gate<br/>(implemented_research_only; PASS_WITH_WARNINGS)"]
    ALPHA01 -. "research-only validity evaluation" .-> QRESEARCH02["GOAL-QUANT-RESEARCH-02 Alpha Candidate Validity Evaluation<br/>(implemented_research_only; PASS_WITH_WARNINGS)"]
    QRESEARCH02 -. "rolling-stability refinement" .-> REFINE01["GOAL-ALPHA-RESEARCH-REFINEMENT-01 Rolling Stability and Candidate Refinement<br/>(implemented_research_only; PASS_WITH_WARNINGS)"]
    REFINE01 -. "research-only refined candidates" .-> ALPHA02["GOAL-ALPHA-FACTOR-CANDIDATE-02 Refined Alpha Candidate Construction<br/>(implemented_research_only; PASS_WITH_WARNINGS)"]
    ALPHA02 -. "research-only refined validity evaluation" .-> QRESEARCH03["GOAL-QUANT-RESEARCH-03 Refined Alpha Factor Validity Evaluation<br/>(implemented_research_only; PASS_WITH_WARNINGS)"]
    QRESEARCH03 -. "research-only regime labels" .-> REGIME01["GOAL-REGIME-LABEL-RESEARCH-01 Market Regime Label Construction<br/>(implemented_research_only; PASS_WITH_WARNINGS)"]
    REGIME01 -. "engineering support" .-> ARCH03["GOAL-ARCHITECTURE-REFACTOR-03 AKShare Source Catalog + Provider Modularization<br/>(implemented_engineering_research_support; PASS_WITH_WARNINGS)"]
    ARCH03 -. "locked future" .-> DATAEXP01["GOAL-DATA-EXPANSION-RESEARCH-01 Market Regime Data Expansion<br/>(locked_future)"]
    DATAEXP01 -. "locked future" .-> QRESEARCH04["GOAL-QUANT-RESEARCH-04 Regime-Conditional Factor Evaluation<br/>(locked_future)"]
    QRESEARCH04 -. "locked future" .-> RECTIER01["GOAL-REC-TIERING-01 Recommendation Score Tiering<br/>(locked_future)"]
    RECTIER01 -. "locked future" .-> T10B4["GOAL-10B.4 Recommendation Revalidation<br/>(locked_future)"]
    T10B4 -. "locked future" .-> PBV01["GOAL-POSITION-BAND-VALIDATION-01<br/>(locked_future)"]
    T10C -. "locked future" .-> T10D["GOAL-10D Failure Attribution<br/>(locked_future)"]
    V1 -. "dashboard UI locked" .-> D1["Dashboard / Daily Report UI<br/>(locked_future)"]
    M2 -. "planned locked" .-> V2["V2 Factor Research<br/>(planned_locked; inactive in V1)"]
```

Locked future modules are documented in the roadmap and are not imported by the
active trunk.

The canonical status contract is `configs/project/workflow_status.csv`.
Implemented active blocks use solid arrows. GOAL-06C and GOAL-06C.5 are
implemented as review-only dotted extensions; GOAL-06C.6 is also
implemented_review_only and network-disabled by default. GOAL-06C.6A is
implemented_review_only and classifies provider/network failures by specific
failure type, with a separate opt-in CloakBrowser reference probe for sanitized
tag-only access diagnostics. GOAL-06C.7 is implemented_review_only for a
provider ladder whose browser-assisted provider is explicit opt-in only and
counts only schema-valid finance rows. The latest GOAL-06C.7 readiness report
is `PASS` at `engineering_pilot`. GOAL-06D is implemented_review_only and
currently `PASS_WITH_WARNINGS`; it selected `score_based_alpha_ranking` as a
weak review-only baseline and requires calibration/stability warning fixes
before any GOAL-07A design-only preparation. GOAL-06D.1 is implemented
review-only and bounds those warnings with repaired score variants,
target-horizon diagnostics, calibration reliability checks, feature sign
stability diagnostics, and provider concentration disclosure. GOAL-07A is
implemented only as design governance with warnings and no risk overlay
calculation. GOAL-07A.1 is implemented only as review-only design review and
GOAL-07B.0 is implemented only as a review-only unlock gate. GOAL-07B is
implemented only as a review-only, non-actionable risk diagnostic prototype.
GOAL-08A is implemented only as a design-only names-only contract gate with zero
recommendation rows. GOAL-STORAGE-01 is implemented only as infrastructure
hardening for local research lake governance and does not unlock GOAL-08B by
itself. GOAL-08B.0 is implemented only as a review-only unlock gate. GOAL-08B
is implemented only as non-actionable review-only diagnostics with 100
`trade_date + symbol` rows and no actionable recommendation or execution
outputs. GOAL-09.0 is implemented only as a review-only unlock gate. GOAL-09
is implemented only as non-actionable review-only position-band diagnostics and
does not create actual positions, sizing, weights, orders, or execution output.
GOAL-09.1 is implemented only as warning-review and dashboard-readiness
evidence. GOAL-V1-INTEGRITY-01 is implemented only as infrastructure
artifact-lineage/structure evidence over the canonical GOAL-07B -> GOAL-08B ->
GOAL-09 -> GOAL-09.1 chain. GOAL-10A is implemented only as design-only future
backtest contract evidence over GOAL-08B/GOAL-09 diagnostics; it defines
input, date alignment, T+1/no-lookahead, metrics, grouping, benchmark,
cost/slippage, and tradability rules but runs no backtest. GOAL-10B is
implemented only as a review-only, non-actionable recommendation diagnostics
backtest over GOAL-08B rows and existing PIT-safe forward-return labels; it
creates grouped diagnostic metrics and IC/RankIC availability evidence only.
GOAL-10B.1 is implemented only as review-only coverage repair diagnostics; it
audits current label and recommendation coverage, records that repair is not
possible with current artifacts, and writes no repaired rows or metrics.
GOAL-DATA-LABEL-01 is implemented only as review-only label coverage evidence,
and GOAL-V1-DIAGNOSTIC-COVERAGE-02 is implemented only as non-actionable
multi-symbol diagnostic coverage evidence. GOAL-10B.2 and GOAL-10C are
implemented only as review-only non-actionable revalidation and sensitivity
diagnostics over bounded DC02 rows. GOAL-DATA-PROVIDER-02A is implemented only
as review-only provider capability metadata for future source-backed planning;
it builds no evaluation panel and creates no diagnostics or backtests.
GOAL-DATA-PROVIDER-02A.1 is implemented only as review-only network-opt-in
provider smoke-test metadata; live access is attempted only with explicit env
opt-ins, Tushare tokens are environment-only, and no raw payloads or tokens are
persisted.
GOAL-DATA-PROVIDER-02B is implemented only as bounded source-backed normalized
panel evidence plus provider/coverage audit metadata. GOAL-V1-DIAGNOSTIC-
COVERAGE-03 is implemented only as non-actionable source-backed diagnostic
coverage over that 02B panel; it does not overwrite canonical GOAL-07B/08B/09
artifacts or unlock backtests, dashboards, trading, production, local-lake,
broker, factor-mining, or DQN/RL outputs. GOAL-10B.3 is implemented only as
review-only DC03 recommendation revalidation diagnostics and records weak /
unreliable signal evidence due group imbalance and unavailable numeric-score
IC/RankIC. GOAL-RISK-TIERING-01 Risk Severity Numeric Score Tiering is
implemented only as review-only separate non-actionable risk-tier diagnostics;
it excludes future returns from score construction, uses forward returns only
post-hoc, preserves canonical GOAL-07B/DC03 risk artifacts, and records weak /
unreliable tiering evidence due the small insufficient-evidence bucket.
GOAL-RISK-TIERING-01.1 Downside Risk Repair is implemented only as review-only
separate non-actionable downside-risk repair diagnostics; it reconstructs
component contributions, separates volatility/momentum flags, excludes future
returns from score construction, and records weak / unreliable downside-risk
signal evidence. GOAL-QUANT-RESEARCH-01 is implemented only as a research-only
factor lab and score validity gate over committed Provider02B, DC03,
GOAL-10B.3, GOAL-RISK-TIERING-01, and GOAL-RISK-TIERING-01.1 evidence; it
creates no recommendation, position, portfolio, dashboard, trading,
production, local-lake, broker, factor-mining, or DQN/RL outputs.
GOAL-MVP-01 is implemented only as a research-only premarket diagnostic
terminal over committed evidence. GOAL-ALPHA-FACTOR-CANDIDATE-01 is
implemented only as research-only candidate factor construction over committed
Provider02B, MVP, Quant Research, and risk-tiering evidence. It creates
candidate values only, excludes future labels from construction, and creates
no recommendations, positions, portfolios, dashboard/frontend files, trading,
production, local-lake, broker, factor-mining, DQN/RL output, or predictive
validity claims. GOAL-QUANT-RESEARCH-02 is implemented only as research-only
alpha candidate validity evaluation from committed evidence. It writes
evaluation, coverage, bucket, IC/RankIC, monotonicity, stability, horizon,
score-validity, and trial-registry diagnostics only, records ready factor count
0, and recommends alpha refinement before recommendation tiering.
GOAL-ALPHA-RESEARCH-REFINEMENT-01 is implemented only as research-only
rolling-stability attribution and refined candidate design planning from
committed evidence. It defines proposed refined candidates only, creates no
refined factor panel, and does not evaluate or promote predictive validity.
GOAL-ALPHA-FACTOR-CANDIDATE-02 is implemented only as research-only refined
candidate construction from committed evidence. It creates refined factor
values only, writes 30 refined candidates and 180000 refined panel rows, and
does not evaluate predictive validity or promote any factor. GOAL-QUANT-RESEARCH-03
is implemented only as research-only refined alpha factor validity evaluation
from committed evidence. It writes partitioned evaluation rows and diagnostics,
records ready factor count 0, and does not create recommendations, positions,
portfolios, dashboards, trading, production, local-lake, broker, factor-mining,
or DQN/RL outputs. GOAL-REGIME-LABEL-RESEARCH-01 is implemented only as
research-only no-lookahead market regime label construction from committed
Provider02B, Quant03, Candidate02, MVP, and risk-tiering evidence. It creates
date, symbol, and factor-regime bridge context only, with no market timing,
recommendation, position, portfolio, dashboard, trading, production, local-lake,
broker, factor-mining, or DQN/RL outputs. GOAL-ARCHITECTURE-REFACTOR-03 is
implemented only as engineering research-support AKShare source catalog,
provider registry, architecture inventory, and common helper metadata; it
creates no data expansion, scientific output changes, recommendations,
positions, portfolio output, dashboard/frontend files, trading, production,
local-lake, broker, factor-mining, or DQN/RL outputs.
GOAL-DATA-EXPANSION-RESEARCH-01, GOAL-QUANT-RESEARCH-04,
GOAL-REC-TIERING-01, GOAL-10B.4,
GOAL-POSITION-BAND-VALIDATION-01,
GOAL-DATA-PANEL-02, GOAL-10D, Dashboard / Daily Report UI, and downstream
execution stages remain locked future work;
the generic Dashboard / Daily Report workflow remains locked. Issue #24 now
separately authorizes and implements only the named local research workspace
`GOAL-PREMARKET-RESEARCH-AND-POSITION-WORKSPACE-DASHBOARD-01`; it is GET-only,
non-actionable, and does not unlock the generic workflow. V2 factor
research is planned but inactive; no V2 factor mining, IC/RankIC mining, factor
library generation, or factor integration is active in V1. Future,
design-only, infrastructure-only, locked, planned-locked, and
deleted-from-active-mainline blocks use dotted arrows or side-note references.

### Issue #24 Local Workspace Node

The named workspace depends on
`GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01` and exposes 23 governed
pages over committed evidence through 22 GET-only API routes. Live stale data
fails closed; immutable replay remains explicit. The browser does not calculate
scientific decisions, and absent fundamentals remain unavailable.

This node has no outgoing promotion edge to Recommendation Tiering, Issue #10,
trading, broker, paper trading, production, or generic dashboard workflows.
