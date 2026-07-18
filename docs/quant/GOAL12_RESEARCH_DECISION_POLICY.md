# GOAL-12 Research Decision Policy

## Allowed states

Every GOAL-11 feature and each combined score receives exactly one state:

- `research_supported_candidate`
- `research_weak_evidence`
- `research_unstable`
- `research_rejected`
- `research_insufficient_data`

All states carry `production_ready=false`. Even a supported research candidate
may only proceed to a future, separately governed risk-research goal.

## Hard sufficiency gate

The primary 5D evaluation must have at least 252 valid dates, 5,000 rows, and
median cross-sectional breadth of 20. Missingness may not exceed 20%,
zero-variance dates 10%, maximum symbol concentration 10%, or maximum date
concentration 1%. A contextual/categorical feature, a structurally absent
field, or any candidate failing these boundaries is
`research_insufficient_data`.

## Evidence rules and precedence

After sufficiency, the deterministic precedence is:

1. `research_rejected`: oriented final-holdout Rank IC is non-positive, or it
   is below 0.01 while BH q exceeds 0.10, or its null-comparison p exceeds 0.20.
2. `research_unstable`: Rank IC is at least 0.01 but sign stability, subperiod
   positive rate, robustness positive rate, or horizon consistency falls below
   its frozen threshold.
3. `research_supported_candidate`: final-holdout Rank IC is at least 0.03,
   its 95% lower confidence bound is above zero, BH q and null p are at most
   0.05, sign/subperiod/robustness rates are at least 0.60, and at least two of
   three horizons agree in sign.
4. `research_weak_evidence`: sufficient evidence remains positive but does not
   satisfy every supported-candidate gate.

Turnover above 0.80 is a warning, not evidence of alpha and not an automatic
rejection. Every output includes current values, thresholds, deterministic
reason codes, warnings, lineage, and policy version. Unit tests exercise each
status and values immediately inside and outside every decision boundary.

The governed decision row explicitly carries `feature_or_model_version`, the
primary `horizon`, `research_status`, `evidence_summary`, `warning_codes`,
`sample_counts`, `metric_summary`, `null_comparison`, `stability_summary`, and
snapshot/source/code provenance in addition to its canonical checksum.

## Governance invariants

The decision engine cannot emit action fields, production promotion, or a
positive production-ready count. Top-level results must contain
`ready_factor_count=0`, `production_model_promoted=false`, and
`production_ready=false`. Any contract or artifact violating these invariants
fails the GOAL-12 audit.
