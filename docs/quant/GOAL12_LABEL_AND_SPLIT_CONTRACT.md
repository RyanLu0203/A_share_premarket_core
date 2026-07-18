# GOAL-12 Label and Split Contract

## Signal and availability time

A feature row dated `t` uses only qfq closes at or before the close of `t`.
The committed source declares that close as consumable at the next trading
session open. The row therefore records both its observation date and its next
session feature-availability date. A label is never visible to feature
construction.

The historical calendar is the sorted, unique CSI 300 dates in the checksummed
bundle, bounded to the equity-panel range. This is the
`GOAL12_CSI300_OBSERVED_TRADING_CALENDAR_V1` research calendar. It is separate
from the short operational calendar used by daily refresh.

## Forward-return definition

For a predeclared horizon `h` in `{1, 5, 20}`:

`forward_return_h(t, s) = qfq_close(s, calendar[t + h]) / qfq_close(s, t) - 1`

The target must be the exact `h`-th subsequent calendar session. If the
calendar target does not exist, or the symbol lacks a close on that exact
date, the label row is explicitly missing. The implementation does not use a
later date, shorten the horizon, carry a price, or fill zero. Suspension and
missing-price effects therefore remain visible.

Each label exposes the Issue #41 metadata names `symbol`, `feature_date`,
`horizon`, `label_date`, `forward_return`, `label_version`,
`source_snapshot_id`, `source_data_checksum`, `calendar_version`,
`code_commit`, `eligibility_status`, and `exclusion_reason`. The more explicit
internal aliases (`date`, `horizon_trading_days`, `target_date`,
`source_checksum`, `calendar_contract`, `label_status`, and `missing_reason`)
remain in the local artifact so existing research joins stay unambiguous. The
row also records feature/label availability, qfq adjustment, and its own
canonical checksum. Duplicate source or label keys and ambiguous
feature-label joins fail closed.

## Chronological split

All split sizes were frozen before final evidence:

- expanding chronological windows only;
- 252 effective training dates minimum;
- 63 validation dates and 63 test dates per development fold;
- final 126 dates held out from threshold, direction, and feature decisions;
- maximum-label-horizon purge of 20 trading dates for every horizon;
- zero additional embargo because exact label-end purging already removes all
  overlapping outcomes.

For every fold, a training row is eligible only when its exact 20D label end
is strictly earlier than the validation boundary. For final-holdout fitting,
all training labels must end strictly before the first holdout date. Validation
and test dates are never randomly mixed, and later folds may expand only after
prior labels have become available.

Normalization, clipping thresholds, and permitted non-structural imputation
are fitted on training dates only. Structurally absent fields such as volume
in the current close-only source are never imputed. The final holdout cannot
select features, directions, thresholds, horizons, or model settings.
