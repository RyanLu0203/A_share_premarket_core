# GOAL-12 Statistical Validation Method

## Predeclared candidates and primary test

Every stock-varying numeric GOAL-11 feature is tested independently using its
direction fixed in `goal12_alpha_validation_v1.json`. The primary decision
horizon is 5D. The 1D and 20D results are mandatory horizon-sensitivity tests,
not alternative opportunities from which to select the best result. Date-level
market context is used for regime slicing and is not misrepresented as a
cross-sectional factor.

The three combined candidates are the unchanged GOAL-11 interpretable alpha,
risk-adjusted alpha, and fixed-ridge linear ranker. No model zoo, factor mining,
or hyperparameter sweep is introduced.

## Single-factor diagnostics

For each date with at least 20 valid symbol rows, GOAL-12 computes Pearson IC,
Spearman Rank IC, five deterministic quantile buckets, top-minus-bottom return,
and bucket monotonicity. Aggregate evidence includes mean/median/standard
deviation/information ratio, positive-IC ratio, valid dates, effective breadth,
quantile means and medians, decay by horizon, missingness, zero-variance dates,
rank ties, raw-versus-1% winsorized sensitivity, top-K persistence/turnover,
and date/symbol concentration.

Quantile returns are equal-date research diagnostics. They are not compounded,
cost-adjusted, described as an equity curve, or presented as investable
performance.

## Date-aware inference and controls

Dates, not symbol-date rows, are the independent resampling units. The fixed
inference budget is:

- 500 date-bootstrap repetitions for 95% confidence intervals;
- 1,000 date-level sign-flip repetitions;
- 64 within-date rank shuffles;
- 64 seeded random-rank controls;
- base seed 12041, with candidate-specific seeds derived by SHA-256.

Additional controls are a deliberately invalid shifted-date alignment, a
constant factor, and the repository's trailing 1D-return naive baseline. Null
matrices and seeds remain in ignored local artifacts. The conservative
candidate p-value is the maximum of the date sign-flip, within-date shuffle,
and seeded random-rank empirical p-values. Benjamini-Hochberg correction is
applied once across every eligible
feature-by-horizon discovery hypothesis. An isolated raw p-value cannot support
a candidate.

## Combined-model evidence

Out-of-sample folds report Pearson IC, Rank IC, Precision@5, Recall@5, NDCG@5,
top-five overlap, ranking turnover, prediction dispersion, effective date and
row sample sizes, coefficient/sign stability, and feature-contribution
stability. Relevance is the top-five realized return rank within that date;
NDCG uses non-negative ordinal realized ranks rather than raw negative returns.

The linear model retains fixed ridge regularization and training-only
standardization. Missing exclusion is primary. Training-median imputation is a
bounded sensitivity only when a feature is not structurally absent. The final
holdout is evaluated once with all settings frozen.

## Robustness matrix

The fixed matrix covers early/late development periods, 126-date rolling
windows stepped by 63 dates, expanding windows starting at 126 dates and
stepped by 63 dates through the complete development period, exclusion of the
last 126 dates, high/low market volatility using a development-only median,
positive/negative index trend, broad/narrow snapshot breadth at 0.5, all
symbols, at least 504-date history, at least 80% calendar observation
coverage, raw versus 1% winsorized ranks, permitted training-only imputation,
and all three label horizons. Weak symbols or slices are never removed after
inspecting their outcomes.
