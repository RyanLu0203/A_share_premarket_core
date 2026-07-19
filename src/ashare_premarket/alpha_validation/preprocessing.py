from __future__ import annotations

import math
from statistics import median
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import canonical_checksum


def fit_training_preprocessor(
    training_rows: Sequence[Mapping[str, object]],
    feature_names: Sequence[str],
    *,
    lower_quantile: float,
    upper_quantile: float,
    allow_imputation: bool,
    maximum_missing_rate: float,
) -> dict[str, object]:
    if not training_rows or not 0 <= lower_quantile <= upper_quantile <= 1:
        raise ValueError("invalid_training_preprocessor_configuration")
    parameters: dict[str, dict[str, object]] = {}
    for feature in feature_names:
        values = [_finite_or_none(row.get(feature)) for row in training_rows]
        observed = sorted(value for value in values if value is not None)
        if not observed:
            raise ValueError(f"structurally_missing_training_feature:{feature}")
        missing_rate = (len(values) - len(observed)) / len(values)
        if allow_imputation and missing_rate > maximum_missing_rate:
            raise ValueError(f"training_imputation_not_permitted:{feature}")
        lower = _quantile(observed, lower_quantile)
        upper = _quantile(observed, upper_quantile)
        imputation = float(median(observed)) if allow_imputation else None
        prepared = [
            min(max(value if value is not None else imputation, lower), upper)
            for value in values
            if value is not None or imputation is not None
        ]
        average = sum(prepared) / len(prepared)
        scale = math.sqrt(
            sum((value - average) ** 2 for value in prepared) / len(prepared)
        )
        parameters[str(feature)] = {
            "lower_bound": _clean(lower),
            "upper_bound": _clean(upper),
            "imputation_value": _clean(imputation) if imputation is not None else None,
            "mean": _clean(average),
            "scale": _clean(scale if scale > 1e-15 else 1.0),
            "missing_rate": _clean(missing_rate),
        }
    result: dict[str, object] = {
        "fit_row_count": len(training_rows),
        "feature_names": tuple(map(str, feature_names)),
        "allow_imputation": allow_imputation,
        "fit_scope": "TRAINING_ONLY",
        "parameters": parameters,
    }
    result["checksum"] = canonical_checksum(result)
    return result


def transform_row(
    row: Mapping[str, object], fitted: Mapping[str, object]
) -> dict[str, float] | None:
    output: dict[str, float] = {}
    parameters = dict(fitted["parameters"])
    for feature in fitted["feature_names"]:
        parameter = dict(parameters[feature])
        value = _finite_or_none(row.get(feature))
        if value is None:
            imputation = parameter["imputation_value"]
            if imputation is None:
                return None
            value = float(imputation)
        clipped = min(
            max(value, float(parameter["lower_bound"])),
            float(parameter["upper_bound"]),
        )
        output[str(feature)] = _clean(
            (clipped - float(parameter["mean"])) / float(parameter["scale"])
        )
    return output


def _finite_or_none(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("non_numeric_preprocessor_value") from exc
    if not math.isfinite(number):
        raise ValueError("non_finite_preprocessor_value")
    return number


def _quantile(values: Sequence[float], probability: float) -> float:
    if len(values) == 1:
        return values[0]
    position = probability * (len(values) - 1)
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return values[lower]
    weight = position - lower
    return values[lower] * (1 - weight) + values[upper] * weight


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded
