from __future__ import annotations

import pytest

from ashare_premarket.alpha_validation.preprocessing import (
    fit_training_preprocessor,
    transform_row,
)


def test_clipping_imputation_and_standardization_are_fit_on_training_only() -> None:
    training = [{"x": 1.0}, {"x": 2.0}, {"x": 100.0}, {"x": None}]
    fitted = fit_training_preprocessor(
        training,
        ("x",),
        lower_quantile=0.0,
        upper_quantile=0.5,
        allow_imputation=True,
        maximum_missing_rate=0.3,
    )

    assert fitted["parameters"]["x"]["imputation_value"] == 2.0
    assert fitted["parameters"]["x"]["upper_bound"] == 2.0
    assert fitted["fit_row_count"] == 4
    assert transform_row({"x": 10_000.0}, fitted) == {"x": 0.57735026919}
    assert transform_row({"x": None}, fitted) == {"x": 0.57735026919}


def test_structural_or_excess_missingness_cannot_be_imputed() -> None:
    with pytest.raises(ValueError, match="structurally_missing_training_feature:x"):
        fit_training_preprocessor(
            [{"x": None}, {"x": None}],
            ("x",),
            lower_quantile=0.01,
            upper_quantile=0.99,
            allow_imputation=True,
            maximum_missing_rate=0.2,
        )
    with pytest.raises(ValueError, match="training_imputation_not_permitted:x"):
        fit_training_preprocessor(
            [{"x": 1.0}, {"x": None}],
            ("x",),
            lower_quantile=0.01,
            upper_quantile=0.99,
            allow_imputation=True,
            maximum_missing_rate=0.2,
        )


def test_primary_missing_exclusion_does_not_silently_impute() -> None:
    fitted = fit_training_preprocessor(
        [{"x": 1.0}, {"x": 2.0}],
        ("x",),
        lower_quantile=0.0,
        upper_quantile=1.0,
        allow_imputation=False,
        maximum_missing_rate=0.2,
    )
    assert transform_row({"x": None}, fitted) is None
