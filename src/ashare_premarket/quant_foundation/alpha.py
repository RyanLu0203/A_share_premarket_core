from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.contracts import (
    canonical_checksum,
    validate_research_output_fields,
)

_COMPONENT_NAMES = (
    "drawdown_risk",
    "instability_risk",
    "liquidity_risk",
    "momentum",
    "trend",
    "volatility_risk",
    "volume_strength",
)


def build_interpretable_alpha(
    feature_rows: Sequence[Mapping[str, object]],
    config: Mapping[str, object],
) -> list[dict[str, object]]:
    alpha_config = dict(config["alpha"])
    risk_config = dict(config["risk"])
    required = tuple(map(str, alpha_config["required_features"]))
    minimum_cross_section = int(dict(config["evaluation"])["minimum_cross_section"])
    _validate_feature_rows(feature_rows)

    by_date: dict[str, list[Mapping[str, object]]] = defaultdict(list)
    for row in feature_rows:
        by_date[str(row["date"])].append(row)

    output: list[dict[str, object]] = []
    for trade_date in sorted(by_date):
        rows = sorted(by_date[trade_date], key=lambda row: str(row["symbol"]))
        complete = [row for row in rows if all(row.get(name) is not None for name in required)]
        components = (
            _date_components(complete)
            if len(complete) >= minimum_cross_section
            else {}
        )
        for row in rows:
            missing = sorted(name for name in required if row.get(name) is None)
            reasons = {f"MISSING_REQUIRED_ALPHA_FEATURE:{name.upper()}" for name in missing}
            if not missing and len(complete) < minimum_cross_section:
                reasons.add("INSUFFICIENT_COMPLETE_CROSS_SECTION")
            key = str(row["symbol"])
            if reasons:
                component_scores = {name: None for name in _COMPONENT_NAMES}
                risk_penalty = None
                alpha_score = None
                risk_adjusted_score = None
                status = "ABSTAINED"
            else:
                component_scores = components[key]
                alpha_weights = dict(alpha_config["component_weights"])
                risk_weights = dict(risk_config["component_weights"])
                risk_penalty = sum(
                    float(risk_weights[name]) * float(component_scores[f"{name}_risk"])
                    for name in ("volatility", "drawdown", "instability", "liquidity")
                )
                alpha_score = (
                    float(alpha_weights["momentum"]) * float(component_scores["momentum"])
                    + float(alpha_weights["trend"]) * float(component_scores["trend"])
                    + float(alpha_weights["volume_strength"]) * float(component_scores["volume_strength"])
                    - float(alpha_weights["risk_penalty"]) * risk_penalty
                )
                risk_adjusted_score = alpha_score - risk_penalty
                risk_penalty = _clean(risk_penalty)
                alpha_score = _clean(alpha_score)
                risk_adjusted_score = _clean(risk_adjusted_score)
                status = "SCORED"
            result: dict[str, object] = {
                "symbol": row["symbol"],
                "date": trade_date,
                "alpha_version": alpha_config["version"],
                "risk_version": risk_config["version"],
                "source_snapshot_id": row["source_snapshot_id"],
                "source_feature_checksum": row["checksum"],
                "generation_timestamp": row["generation_timestamp"],
                "code_commit": row["code_commit"],
                "component_scores": component_scores,
                "risk_penalty": risk_penalty,
                "alpha_score": alpha_score,
                "risk_adjusted_score": risk_adjusted_score,
                "score_status": status,
                "abstention_reasons": tuple(sorted(reasons)),
                "second_stage_risk_adjustment_disclosed": True,
                "research_only": True,
            }
            validate_research_output_fields(result)
            result["checksum"] = canonical_checksum(result)
            output.append(result)
    return output


def _validate_feature_rows(rows: Sequence[Mapping[str, object]]) -> None:
    seen: set[tuple[str, str]] = set()
    lineages: set[tuple[str, str, str, str]] = set()
    for row in rows:
        expected = canonical_checksum({key: value for key, value in row.items() if key != "checksum"})
        if row.get("checksum") != expected:
            raise ValueError("feature_row_checksum_mismatch")
        key = (str(row.get("date", "")), str(row.get("symbol", "")))
        if key in seen:
            raise ValueError("duplicate_feature_row_key")
        seen.add(key)
        lineages.add(
            (
                str(row.get("source_snapshot_id", "")),
                str(row.get("feature_version", "")),
                str(row.get("code_commit", "")),
                str(row.get("adjustment", "")),
            )
        )
    if len(lineages) > 1:
        raise ValueError("mixed_feature_snapshot_lineage")


def _date_components(rows: Sequence[Mapping[str, object]]) -> dict[str, dict[str, float]]:
    raw = {
        "momentum": {str(row["symbol"]): float(row["momentum_20d"]) for row in rows},
        "trend": {str(row["symbol"]): float(row["trend_strength_20d"]) for row in rows},
        "volume_strength": {str(row["symbol"]): float(row["abnormal_volume_20d"]) for row in rows},
        "volatility_risk": {str(row["symbol"]): float(row["volatility_20d"]) for row in rows},
        "drawdown_risk": {
            str(row["symbol"]): abs(min(float(row["drawdown_60d"]), 0.0))
            for row in rows
        },
        "instability_risk": {
            str(row["symbol"]): abs(float(row["volatility_regime_60d"]) - 1.0)
            for row in rows
        },
        "liquidity_risk": {
            str(row["symbol"]): -float(row["abnormal_volume_20d"])
            for row in rows
        },
    }
    ranked = {
        name: _rank_percentiles(values, centered=not name.endswith("_risk"))
        for name, values in raw.items()
    }
    return {
        str(row["symbol"]): {
            name: _clean(ranked[name][str(row["symbol"])])
            for name in _COMPONENT_NAMES
        }
        for row in rows
    }


def _rank_percentiles(values: Mapping[str, float], *, centered: bool) -> dict[str, float]:
    ordered = sorted(values.items(), key=lambda item: (item[1], item[0]))
    denominator = len(ordered) - 1
    result: dict[str, float] = {}
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        average_rank = (index + end - 1) / 2.0
        percentile = average_rank / denominator if denominator else 0.5
        score = percentile - 0.5 if centered else percentile
        for key, _ in ordered[index:end]:
            result[key] = score
        index = end
    return result


def _clean(value: float) -> float:
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded
