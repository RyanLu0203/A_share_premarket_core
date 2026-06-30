# GOAL-ARCHITECTURE-REFACTOR-03 AKShare Source Catalog and Provider Modularization Gate

Status: `PASS_WITH_WARNINGS`

## 1. Goal status
Implemented as engineering research-support metadata only.

## 2. Why refactor is needed now
Quant03 and Regime01 added large deterministic research artifacts; future provider expansion needs shared contracts before more data is added.

## 3. Current Quant03 and Regime01 state
Quant03 ready factor count remains 0. Regime01 remains PASS_WITH_WARNINGS with 120 date rows, 6000 symbol rows, and 180000 bridge rows.

## 4. Existing architecture inventory
Inventory rows: `125`.

## 5. Duplicate runner/audit/schema/lineage patterns found
Duplicate pattern rows: `12`.

## 6. New provider registry design
Provider registry rows: `4` with network disabled by default and raw payload commits forbidden.

## 7. AKShare source catalog coverage
Catalog rows: `70` across `11` top-level categories.

## 8. AKShare source priority bands
BLOCKED_boundary_or_pit_risk=5; P0_market_regime_core=20; P1_symbol_context_and_event=22; P2_macro_fundamental_medium_term=15; P3_context_only_or_experimental=8

## 9. Source approval and blocking policy
Sources are classified as approved, context-only, experimental, blocked, or future-review-only. Blocked/live execution sources are separated.

## 10. PIT / no-lookahead policy for external data
Catalog entries require explicit time fields, publication-date policy, primary keys, and lookahead risk classification before use.

## 11. Artifact-size and storage policy
No output may reach 95 MiB; raw provider payloads and local-lake writes remain forbidden.

## 12. Backward compatibility verification
Existing scripts remain registered; required validation replays older runners and audits after this gate.

## 13. What was refactored
Added common audit, runner, contract, provider-registry, provider-contract, and source-catalog foundations.

## 14. What was intentionally not refactored
Quant03, Regime01, Alpha, Risk, MVP, DC03, and Provider02B scientific logic and conclusions were not rewritten.

## 15. Locked downstream boundaries
Recommendation, position, dashboard/frontend, trading, production, broker, local-lake, factor-mining, and DQN/RL outputs remain locked.

## 16. Recommended next goal
`GOAL-DATA-EXPANSION-RESEARCH-01-MARKET-REGIME-DATA-EXPANSION-GATE` should use approved P0/P1 catalog sources only.
