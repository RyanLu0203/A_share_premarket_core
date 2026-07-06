"""Research-only diagnostic overview of Quant04 factors.

This is NOT a recommendation, ranking-for-action, or signal layer. It does not
unlock, request, or reference the locked GOAL-REC-TIERING-01 gate, does not
touch governance state, and assigns no ``ready`` status. It only reads the
already-committed GOAL-QUANT-RESEARCH-04 evaluation outputs and produces a
transparent, relative *diagnostic ordering* of the evaluated factors by their
existing IC / stability / regime-consistency metrics, so a human can explore
them. Every factor keeps its true Quant04 ``overall_factor_status`` and
``candidate_for_rec_tiering`` value; nothing here promotes a factor.
"""

from __future__ import annotations

import csv
from pathlib import Path

FACTOR_STATUS_PATH = "outputs/research/goal_quant_research04_factor_overall_status.csv"
REGIME_SUMMARY_PATH = "outputs/research/goal_quant_research04_regime_conditional_evaluation_summary.csv"
LEAKAGE_PATH = "outputs/research/goal_quant_research04_leakage_pit_checks.csv"
OUTPUT_PATH = "outputs/research/factor_metric_diagnostic_overview.csv"

# Transparent, fixed weights for the relative diagnostic composite. These are a
# human-readable exploration heuristic, not a validated scoring model.
WEIGHTS = {
    "abs_mean_ic_1d": 0.30,
    "ic_information_ratio_proxy": 0.20,
    "regime_consistency_score": 0.20,
    "stability_score": 0.20,
}
LEAKAGE_PENALTY_WEIGHT = 0.10

DISCLAIMER = (
    "research_only_diagnostic_view_not_a_signal_not_a_recommendation_"
    "no_ready_classification_does_not_unlock_rec_tiering"
)

OUTPUT_FIELDS = [
    "factor_id",
    "factor_family",
    "overall_factor_status",
    "candidate_for_rec_tiering",
    "diagnostic_composite_score",
    "relative_diagnostic_band",
    "abs_mean_ic_1d",
    "ic_information_ratio_proxy",
    "regime_consistency_score",
    "stability_score",
    "evaluated_regime_count",
    "conditionally_useful_regime_count",
    "regime_mean_ic_1d_breakdown",
    "leakage_pit_status",
    "no_lookahead_status",
    "non_actionable_disclaimer",
]


def build_factor_diagnostic_overview(root: Path) -> Path:
    status_rows = _read_csv(root / FACTOR_STATUS_PATH)
    regime_rows = _read_csv(root / REGIME_SUMMARY_PATH)
    leakage_status = _leakage_status(_read_csv(root / LEAKAGE_PATH))

    by_factor: dict[str, list[dict[str, str]]] = {}
    for row in regime_rows:
        by_factor.setdefault(row.get("refined_factor_id", ""), []).append(row)

    records: list[dict[str, object]] = []
    for status in status_rows:
        factor_id = status.get("refined_factor_id", "")
        regimes = by_factor.get(factor_id, [])
        ics = [_float(r.get("mean_ic_1d")) for r in regimes]
        ics = [v for v in ics if v is not None]
        abs_mean_ic = _mean([abs(v) for v in ics]) if ics else 0.0
        ir_proxy = _information_ratio_proxy(ics)
        consistency = _regime_consistency(ics)
        stability = _stability_score(regimes)
        records.append(
            {
                "factor_id": factor_id,
                "factor_family": status.get("factor_family", ""),
                "overall_factor_status": status.get("overall_factor_status", ""),
                "candidate_for_rec_tiering": status.get("candidate_for_rec_tiering", ""),
                "abs_mean_ic_1d": abs_mean_ic,
                "ic_information_ratio_proxy": ir_proxy,
                "regime_consistency_score": consistency,
                "stability_score": stability,
                "evaluated_regime_count": status.get("evaluated_regime_count", ""),
                "conditionally_useful_regime_count": status.get("conditionally_useful_regime_count", ""),
                "regime_mean_ic_1d_breakdown": _regime_breakdown(regimes),
                "no_lookahead_status": status.get("no_lookahead_status", ""),
            }
        )

    _attach_composite(records, leakage_status)
    records.sort(key=lambda r: (-float(r["diagnostic_composite_score"]), r["factor_id"]))
    _attach_relative_band(records)

    output_path = root / OUTPUT_PATH
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow(
                {
                    **{k: record.get(k, "") for k in OUTPUT_FIELDS if k not in {"leakage_pit_status", "non_actionable_disclaimer"}},
                    "leakage_pit_status": leakage_status,
                    "non_actionable_disclaimer": DISCLAIMER,
                }
            )
    return output_path


def _attach_composite(records: list[dict[str, object]], leakage_status: str) -> None:
    penalty = 0.0 if leakage_status == "pass" else LEAKAGE_PENALTY_WEIGHT
    norms = {
        key: _minmax([float(r[key]) if key != "ic_information_ratio_proxy" else abs(float(r[key])) for r in records])
        for key in WEIGHTS
    }
    for idx, record in enumerate(records):
        score = sum(WEIGHTS[key] * norms[key][idx] for key in WEIGHTS) - penalty
        record["diagnostic_composite_score"] = round(score, 6)
        for key in ("abs_mean_ic_1d", "ic_information_ratio_proxy", "regime_consistency_score", "stability_score"):
            record[key] = round(float(record[key]), 6)


def _attach_relative_band(records: list[dict[str, object]]) -> None:
    n = len(records)
    for idx, record in enumerate(records):
        if n < 3:
            band = "single_group"
        elif idx < n / 3:
            band = "upper_third"
        elif idx < 2 * n / 3:
            band = "middle_third"
        else:
            band = "lower_third"
        record["relative_diagnostic_band"] = band


def _information_ratio_proxy(ics: list[float]) -> float:
    if len(ics) < 2:
        return 0.0
    mean = _mean(ics)
    std = _std(ics, mean)
    return mean / std if std > 0 else 0.0


def _regime_consistency(ics: list[float]) -> float:
    if not ics:
        return 0.0
    mean = _mean(ics)
    if mean == 0:
        return 0.5
    dominant = 1 if mean > 0 else -1
    same = sum(1 for v in ics if (1 if v > 0 else -1 if v < 0 else 0) == dominant)
    return round(same / len(ics), 6)


def _stability_score(regimes: list[dict[str, str]]) -> float:
    stable = sum(int(_float(r.get("stable_window_count")) or 0) for r in regimes)
    unstable = sum(int(_float(r.get("unstable_window_count")) or 0) for r in regimes)
    total = stable + unstable
    return round(stable / total, 6) if total else 0.0


def _regime_breakdown(regimes: list[dict[str, str]]) -> str:
    parts = []
    for r in sorted(regimes, key=lambda x: x.get("regime_label", "")):
        label = r.get("regime_label", "").replace("_review_only", "")
        ic = _float(r.get("mean_ic_1d"))
        parts.append(f"{label}={ic:.4f}" if ic is not None else f"{label}=na")
    return ";".join(parts)


def _leakage_status(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "unknown"
    return "pass" if all(r.get("result") == "pass" for r in rows) else "flagged"


def _minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi == lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _std(values: list[float], mean: float) -> float:
    if len(values) < 2:
        return 0.0
    return (sum((v - mean) ** 2 for v in values) / len(values)) ** 0.5


def _float(value: object) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
