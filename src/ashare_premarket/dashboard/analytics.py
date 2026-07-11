from __future__ import annotations

import math
from collections import defaultdict


def display_correlation_matrix(
    canonical_rows: tuple[dict[str, str], ...],
    symbols: list[str],
    cutoff: str,
) -> dict[str, object]:
    """Build a display-only matrix from already validated canonical returns."""
    by_symbol: dict[str, dict[str, float]] = defaultdict(dict)
    selected = set(symbols)
    for row in canonical_rows:
        if row.get("symbol") not in selected or row.get("trade_date", "") > cutoff:
            continue
        if row.get("risk_model_eligible") != "true":
            continue
        value = _float(row.get("canonical_return_1d"))
        if value is not None:
            by_symbol[row["symbol"]][row["trade_date"]] = value

    values: list[list[float | None]] = []
    for left in symbols:
        row_values: list[float | None] = []
        for right in symbols:
            if left == right:
                row_values.append(1.0)
                continue
            dates = sorted(set(by_symbol[left]).intersection(by_symbol[right]))
            corr = _correlation(
                [by_symbol[left][date] for date in dates],
                [by_symbol[right][date] for date in dates],
            )
            row_values.append(round(corr, 6) if corr is not None else None)
        values.append(row_values)
    return {
        "symbols": symbols,
        "values": values,
        "asof_date": cutoff,
        "derivation": "display_only_server_derived_from_validated_canonical_returns",
        "decision_input": False,
    }


def _correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) < 2 or len(left) != len(right):
        return None
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    left_ss = sum((value - left_mean) ** 2 for value in left)
    right_ss = sum((value - right_mean) ** 2 for value in right)
    denominator = math.sqrt(left_ss * right_ss)
    return numerator / denominator if denominator else None


def _float(value: str | None) -> float | None:
    try:
        return float(value) if value not in {None, ""} else None
    except ValueError:
        return None
