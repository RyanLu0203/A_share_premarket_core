# GOAL-12 Alpha Validation Findings

## Conclusion

GOAL-12 completed a predeclared, research-only falsification run over the
available governed history. It found no candidate that meets the frozen
research-support contract:

- `research_supported_candidate`: 0
- `research_weak_evidence`: 0
- `research_unstable`: 0
- `research_rejected`: 17
- `research_insufficient_data`: 11

This is a scientifically negative/inconclusive result, not a pipeline failure.
`production_ready=false` for every candidate and production
`ready_factor_count=0`. GOAL-13 risk or portfolio intelligence is not
scientifically authorized by this evidence.

## Governed run

| Field | Value |
| --- | --- |
| Authoritative base | `25273bb3d3cf9d6eb6c21caf1317c5c56f086489` |
| Implementation commit | `d04e3e029136bd0b2039b37e46f2f6efd75813ea` |
| Run ID | `goal12-final-evidence-v1` |
| Run status | `COMPLETE_RESEARCH_ONLY` |
| Result SHA-256 | `f8fb4fad8e4d005ba252d197072cf0523cdaeb0c27c5df1f05eac8bae9a0f985` |
| Manifest SHA-256 | `5d48d0c704740e548b46985286fd394c9b088bb42a59a5998e21f499ab839780` |
| Manifest artifacts | 11; all size and SHA-256 checks passed |
| Artifact policy | `LOCAL_IGNORED_RESEARCH_ONLY` |

## Data sufficiency

The source is the committed, checksummed AKShare/Sina qfq evidence bundle. It
contains equity close and CSI 300 index close only. It does not contain
historical open/high/low/volume/amount.

| Measure | Result |
| --- | --- |
| Equity rows | 34,543 |
| Full feature range | 2023-01-03 to 2026-06-30 |
| Source calendar dates | 843 |
| Symbols | 41 current-listing symbols |
| Common 20D-eligible signal range | 2023-01-03 to 2026-06-01 |
| Common eligible signal dates | 823 |
| Eligible-date breadth | min 40, median 41, max 41 |
| Breadth distribution | 803 dates with 41 symbols; 20 dates with 40 |
| Adjustment | qfq, proven from the committed acquisition call |
| Amount | unavailable/null, never zero-filled |
| Universe | current-listing; historical survivorship risk remains |

Feature missingness from the full 34,543-row feature table is:

| Missing rate | Features |
| --- | --- |
| 100% | `abnormal_volume_20d`, `atr_14`, `price_volume_correlation_20d`, `volume_change_1d` |
| 7.46895% | `momentum_60d`, `volatility_regime_60d` |
| 7.34447% | `drawdown_60d`, `ma_ratio_60d` |
| 4.10792% | `macd_histogram_12_26_9`, `macd_signal_9` |
| 3.11206% | `macd_line_12_26` |
| 2.84283% | `market_regime` |
| 2.48965% | `downside_volatility_20d`, `momentum_20d`, `volatility_20d` |
| 2.37385% | `index_trend_20d`, `market_volatility_20d` |
| 2.36517% | `bollinger_position_20d`, `ma_ratio_20d`, `trend_strength_20d` |
| 1.74276% | `rsi_14` |
| 0.62241% | `momentum_5d` |
| 0.58767% | `market_breadth_1d` |
| 0.49793% | `ma_ratio_5d` |
| 0.12448% | `return_1d` |

## Labels and chronology

For feature date `t` and horizon `h`, the exact label is
`qfq_close[t+h] / qfq_close[t] - 1` on the observed CSI 300 trading calendar.
The close at `t` is consumable at the next session open. Exact missing targets
remain missing; horizons are not shortened and returns are not zero-filled.
Every row carries the Issue #41 lineage, availability, eligibility, version,
commit, and checksum fields.

| Horizon | Available | Missing | Feature range with labels | Realizable label range |
| --- | ---: | ---: | --- | --- |
| 1D | 34,500 | 43 | 2023-01-03 to 2026-06-29 | 2023-01-04 to 2026-06-30 |
| 5D | 34,328 | 215 | 2023-01-03 to 2026-06-23 | 2023-01-10 to 2026-06-30 |
| 20D | 33,703 | 840 | 2023-01-03 to 2026-06-01 | 2023-02-07 to 2026-06-30 |

Missing rows consist only of exact calendar-horizon exhaustion or an exact
calendar target price unavailable for that symbol.

The primary decision horizon is 5D. There are five expanding chronological
development folds. Each uses 63 validation dates, 63 test dates, and a common
20-date purge. Training sizes are 252, 315, 378, 441, and 504 dates. The final
holdout has 126 signal dates from 2025-11-20 through 2026-06-01; final training
ends 2025-10-22 and the 20 purged dates are 2025-10-23 through 2025-11-19.
The final holdout selects no feature, direction, horizon, threshold, or model
setting.

## Nulls and multiple testing

Inference resamples dates, not symbol-date rows. Each eligible hypothesis uses
500 date-bootstrap repetitions, 1,000 sign flips, 64 within-date shuffles, and
64 seeded random rankings. It also records an invalid date-shift control and a
constant-factor control. The conservative p-value is the maximum of the three
date/sign/rank null p-values.

Benjamini-Hochberg correction covers all 51 eligible factor-by-horizon
discovery hypotheses together. No hypothesis has `q<=0.05`; nine have
`q<=0.10`. None of those nine also satisfies the frozen final-holdout,
direction, null, confidence, and stability requirements.

## Candidate decisions

The table reports the primary 5D oriented final-holdout Rank IC and discovery
BH q-value. `n/a` means the candidate is not responsibly measurable from the
available evidence.

| Candidate | 5D holdout Rank IC | Discovery q | Status | Primary reason |
| --- | ---: | ---: | --- | --- |
| `abnormal_volume_20d` | n/a | n/a | `research_insufficient_data` | structural volume absence |
| `atr_14` | n/a | n/a | `research_insufficient_data` | structural OHLC absence |
| `bollinger_position_20d` | 0.00614 | 0.71538 | `research_rejected` | weak and FDR unsupported |
| `downside_volatility_20d` | -0.01388 | 0.08718 | `research_rejected` | non-positive holdout |
| `drawdown_60d` | 0.00842 | 0.25960 | `research_rejected` | weak and FDR unsupported |
| `fixed_linear_ranker` | n/a | n/a | `research_insufficient_data` | requires abnormal volume |
| `index_trend_20d` | n/a | n/a | `research_insufficient_data` | date-level context, not cross-sectional |
| `interpretable_alpha` | n/a | n/a | `research_insufficient_data` | requires abnormal volume |
| `ma_ratio_20d` | 0.01479 | 0.60411 | `research_rejected` | failed null comparison |
| `ma_ratio_5d` | 0.00970 | 1.00000 | `research_rejected` | weak and FDR unsupported |
| `ma_ratio_60d` | 0.01213 | 1.00000 | `research_rejected` | failed null comparison |
| `macd_histogram_12_26_9` | -0.00913 | 0.37929 | `research_rejected` | non-positive holdout |
| `macd_line_12_26` | -0.00881 | 0.16376 | `research_rejected` | non-positive holdout |
| `macd_signal_9` | -0.01373 | 0.14011 | `research_rejected` | non-positive holdout |
| `market_breadth_1d` | n/a | n/a | `research_insufficient_data` | date-level context, not cross-sectional |
| `market_regime` | n/a | n/a | `research_insufficient_data` | date-level context, not cross-sectional |
| `market_volatility_20d` | n/a | n/a | `research_insufficient_data` | date-level context, not cross-sectional |
| `momentum_20d` | 0.00889 | 0.72639 | `research_rejected` | weak and FDR unsupported |
| `momentum_5d` | 0.00140 | 0.93306 | `research_rejected` | weak and FDR unsupported |
| `momentum_60d` | 0.03849 | 1.00000 | `research_rejected` | discovery null failed; CI crosses zero |
| `price_volume_correlation_20d` | n/a | n/a | `research_insufficient_data` | structural volume absence |
| `return_1d` | 0.00427 | 0.62094 | `research_rejected` | weak and FDR unsupported |
| `risk_adjusted_alpha` | n/a | n/a | `research_insufficient_data` | requires abnormal volume |
| `rsi_14` | 0.00857 | 0.25960 | `research_rejected` | weak and FDR unsupported |
| `trend_strength_20d` | 0.00328 | 0.37929 | `research_rejected` | weak and FDR unsupported |
| `volatility_20d` | -0.01840 | 0.08718 | `research_rejected` | non-positive holdout |
| `volatility_regime_60d` | 0.06361 | 0.60969 | `research_rejected` | discovery null/FDR unsupported |
| `volume_change_1d` | n/a | n/a | `research_insufficient_data` | structural volume absence |

`volatility_regime_60d` has a positive 5D holdout interval
`[0.03594, 0.08714]`, but its discovery q-value is 0.60969 and discovery null
p-value is 0.35265. `momentum_60d` has holdout Rank IC 0.03849, but its interval
`[-0.00244, 0.07505]` crosses zero, discovery q is 1.0, and discovery null p is
0.81538. Neither is credible support under the frozen policy. `return_1d` is
the only high-turnover warning (`0.8464 > 0.80`).

## Combined models and robustness

The two GOAL-11 interpretable scores and the fixed ridge ranker all require
`abnormal_volume_20d`. Because historical volume is structurally absent, no
valid score row or model OOS metric exists. They are insufficient-data results,
not failed model-performance results; no replacement feature or imputation was
fabricated.

Each eligible factor was checked across 30 date slices (nine fixed
subperiod/regime slices, ten rolling windows, and eleven expanding windows),
three universe slices, raw versus 1% winsorized ranks, training-only median
imputation sensitivity, and all three horizons. Raw-versus-winsorized 5D
Rank-IC deltas are zero, as expected for rank-preserving clipping in this
sample. Robustness positive rates range from 0.36364 to 0.93939, but no factor
also passes discovery FDR, null, final-holdout direction/interval, subperiod,
fold-sign, and horizon-consistency gates.

## Limitations and next gate

- Close-only history prevents ATR, volume factors, GOAL-11 alpha scores, and
  the fixed ranker from being evaluated.
- The 41-symbol current-listing universe is not a PIT constituent history and
  retains survivorship and concentration risk.
- The source proves qfq acquisition but this goal does not add an independent
  corporate-action reconciliation source.
- History spans about 3.4 years and one market/universe source; regime slices
  are therefore bounded and not broad external replication.
- A positive holdout statistic cannot override discovery/null/FDR failure.

The recommended next owner-approved goal is a governed historical evidence
remediation gate: add PIT-safe OHLCV/volume semantics, PIT universe membership,
and independent qfq/corporate-action evidence without changing GOAL-12
thresholds. GOAL-12 should then be rerun under the same frozen contract.
GOAL-13 should remain blocked unless that rerun produces at least one genuinely
supported research candidate and receives a separate owner decision.
