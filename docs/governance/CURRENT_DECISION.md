# Current Decision

Last reviewed: 2026-08-28 after public-release integration of the factor and
liquidity evidence gates

This is the single current decision entrypoint for selecting the next project
goal. Historical `next`, `next goal`, and `allowed next` statements elsewhere
record the state at the time they were written; they do not override this
document, `PROJECT_STATE.md`, or `configs/project/workflow_status.csv`.

## Authoritative Baseline

- Authoritative branch: `project-current`.
- Integration baseline: public-release merge
  `0ca2b8648c01ae2af6c342c468aa79694ec4ce9e`.
- Stable rollback branch and tag: `checkpoint/arch03-stable-310559`.
- DataExpansion01, Regime02, Quant04, GOAL-11, the read-only Workspace, and
  the governed daily refresh are implemented within their documented
  research-only or operational-support boundaries.
- `ready_factor_count = 0`.
- The expanded readiness rerun evaluated 120 fixed candidates over 41
  acquired symbols and 843 trading dates; all candidates remained
  `not_ready`.
- iFinD S0 and S1 identity metadata acceptance are verified. The only
  authorized S2 attempt stopped after call 1 of 4 on a response-schema
  mismatch and accepted zero normalized or canonical rows.

## Current Program Decision

GOAL-FACTOR-FAILURE-ATTRIBUTION-01 is implemented research-only and reports
that all 120 candidates fail the base precondition, strong-IC, 1-day sign
stability, and two-aligned-horizon criteria. Sixty-three candidates lost prior
conditional status and 104 are redundant under exact existing holdout and
walk-forward metric fingerprints.

The five existing factor families are frozen under their present definitions.
GOAL-ALPHA-HYPOTHESIS-REDESIGN-01 is implemented design-only and pre-registers
four orthogonal hypotheses. The preferred first hypothesis is bounded
liquidity-shock normalization, but all four remain evidence-not-ready.

GOAL-LIQUIDITY-EVIDENCE-ACCEPTANCE-CONTRACT-01 is implemented infrastructure-
only. The contract passes, but current evidence is `NOT_READY`: 41 versus 100
required symbols, one versus two providers, and no accepted complete liquidity
field/PIT bundle. Zero rows are accepted and factor construction is blocked.

Further progress requires provider-schema and historical free-float-source
acceptance first. A later bounded evidence-acquisition goal would require
separate authority for external provider calls or an owner-supplied governed
bundle. This checkpoint grants neither.

GOAL-LIQUIDITY-EVIDENCE-ACQUISITION-FOUNDATION-01 is implemented
infrastructure-only. It provides the default-off preflight, normalizer, atomic
bundle validator and failure taxonomy, but remains blocked before network at
41/100 symbols, 1/2 verified providers, and no verified historical free-float
source. The next legitimate work is provider-schema and free-float-source
acceptance; a live pilot remains unauthorized.

The implemented failure-attribution goal was bounded to:

- readiness-criterion failure frequency and severity;
- temporal, regime, horizon, provider, universe, and liquidity instability;
- sign reversals and effective independent cross-sectional sample size;
- candidate redundancy and family-level concentration using existing
  candidate values and metrics only;
- an evidence-backed continue, redesign, or stop decision for each existing
  candidate family.

It constructed no new factors, mined no thresholds, weakened no readiness
rules, created no recommendations or positions, ran no portfolio backtest,
called no provider, wrote no local-lake or production data, and unlocked no
downstream stage.

## Independent Provider Decision

iFinD S2 remains a separate provider-acceptance track. No retry is authorized
by this control-plane checkpoint. If the owner later authorizes another call,
the preferred next action is one fixed, zero-retry
`002475.SZ:get_stock_info` diagnostic call under the existing S2 gates before
considering the remaining three calls.

Accepted iFinD evidence must remain isolated from immutable replay and the
canonical research panel until its complete bundle contract passes.

## Locked Boundaries

The following remain locked: GOAL-REC-TIERING-01, GOAL-10B.4,
GOAL-POSITION-BAND-VALIDATION-01, GOAL-DATA-PANEL-02, GOAL-10D, generic
Dashboard / Daily Report promotion, signal and portfolio backtests, paper and
live trading, broker integration, production writes and promotion, V2 factor
mining, and DQN/RL.

No `conditionally_useful` factor may be reclassified as ready by relaxing a
threshold. A positive ready-factor result and explicit owner approval remain
mandatory before recommendation tiering can be considered.

## Superseded Planning Statements

The following planning statements are historical-only because their named
work is already complete:

| Historical statement | Current interpretation |
| --- | --- |
| Immediate next goal is GOAL-CODEX-OPERATING-SYSTEM-01 | Completed governance-only; retain as history |
| Next data/research goal is DataExpansion01 | Completed research-only; retain as history |
| Next research goal is Regime02 or Quant04 | Completed research-only; retain as history |
| Merge the S2 response-diagnostic/read gate | Completed in PR #56; retain as history |

Historical implementation logs remain immutable evidence. They should be
labelled as historical when summarized, not deleted or rewritten.

## Promotion Rule

This document records prioritization only. A future goal becomes implemented
only after its own approved scope, readiness report, validation, workflow CSV
update, required project-memory updates, and explicit preservation of locked
downstream boundaries.
