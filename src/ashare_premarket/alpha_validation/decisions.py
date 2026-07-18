from __future__ import annotations

import math
from typing import Mapping

from ashare_premarket.quant_foundation.contracts import (
    canonical_checksum,
    validate_research_output_fields,
)

ALLOWED_RESEARCH_STATUSES = (
    "research_supported_candidate",
    "research_weak_evidence",
    "research_unstable",
    "research_rejected",
    "research_insufficient_data",
)


def decide_candidate(
    candidate_id: str,
    evidence: Mapping[str, object],
    policy: Mapping[str, object],
) -> dict[str, object]:
    reasons: list[str] = []
    warnings: list[str] = []
    if evidence.get("eligible") is not True:
        reasons.append(str(evidence.get("eligibility_reason") or "CANDIDATE_NOT_ELIGIBLE"))
    _minimum_gate(
        evidence, policy, "valid_date_count", "minimum_valid_dates",
        "INSUFFICIENT_VALID_DATES", reasons,
    )
    _minimum_gate(
        evidence, policy, "observation_row_count", "minimum_observation_rows",
        "INSUFFICIENT_OBSERVATION_ROWS", reasons,
    )
    _minimum_gate(
        evidence, policy, "median_breadth", "minimum_median_breadth",
        "INSUFFICIENT_CROSS_SECTIONAL_BREADTH", reasons,
    )
    _maximum_gate(evidence, policy, "missing_rate", "EXCESSIVE_MISSINGNESS", reasons)
    _maximum_gate(evidence, policy, "zero_variance_rate", "EXCESSIVE_ZERO_VARIANCE_DATES", reasons)
    _maximum_gate(evidence, policy, "symbol_concentration", "EXCESSIVE_SYMBOL_CONCENTRATION", reasons)
    _maximum_gate(evidence, policy, "date_concentration", "EXCESSIVE_DATE_CONCENTRATION", reasons)

    turnover = _number(evidence, "ranking_turnover")
    if turnover is not None and turnover > float(policy["turnover_warning_threshold"]):
        warnings.append("HIGH_RANKING_TURNOVER")

    if reasons:
        status = "research_insufficient_data"
    else:
        rank_ic = _required_number(evidence, "oos_rank_ic")
        fdr_q = _required_number(evidence, "fdr_q")
        null_p = _required_number(evidence, "null_p")
        if rank_ic <= 0:
            status = "research_rejected"
            reasons.append("NON_POSITIVE_FINAL_HOLDOUT_RANK_IC")
        elif rank_ic < float(policy["minimum_rank_ic_weak"]) and fdr_q > float(
            policy["rejection_fdr_q"]
        ):
            status = "research_rejected"
            reasons.append("SUBSTANTIVELY_WEAK_AND_FDR_UNSUPPORTED")
        elif null_p > float(policy["rejection_null_p"]):
            status = "research_rejected"
            reasons.append("FAILED_NULL_COMPARISON")
        elif _unstable(evidence, policy, reasons):
            status = "research_unstable"
        elif _supported(evidence, policy):
            status = "research_supported_candidate"
            reasons.append("ALL_PREDECLARED_RESEARCH_SUPPORT_GATES_PASSED")
        else:
            status = "research_weak_evidence"
            reasons.append("POSITIVE_BUT_NOT_ALL_SUPPORT_GATES_PASSED")

    result: dict[str, object] = {
        "candidate_id": str(candidate_id),
        "status": status,
        "production_ready": False,
        "policy_version": str(policy["version"]),
        "reason_codes": tuple(sorted(set(reasons))),
        "warnings": tuple(sorted(set(warnings))),
        "evidence": dict(evidence),
    }
    validate_research_output_fields(result)
    result["checksum"] = canonical_checksum(result)
    return result


def _minimum_gate(
    evidence: Mapping[str, object],
    policy: Mapping[str, object],
    field: str,
    policy_field: str,
    reason: str,
    reasons: list[str],
) -> None:
    value = _number(evidence, field)
    threshold = float(policy[policy_field])
    if value is None or value < threshold:
        reasons.append(reason)


def _maximum_gate(
    evidence: Mapping[str, object],
    policy: Mapping[str, object],
    field: str,
    reason: str,
    reasons: list[str],
) -> None:
    value = _number(evidence, field)
    threshold = float(policy[f"maximum_{field}"])
    if value is None or value > threshold:
        reasons.append(reason)


def _unstable(
    evidence: Mapping[str, object], policy: Mapping[str, object], reasons: list[str]
) -> bool:
    checks = (
        ("sign_stability", "minimum_sign_stability", "UNSTABLE_SIGN"),
        (
            "subperiod_positive_rate",
            "minimum_subperiod_positive_rate",
            "UNSTABLE_SUBPERIODS",
        ),
        (
            "robustness_positive_rate",
            "minimum_robustness_positive_rate",
            "UNSTABLE_ROBUSTNESS_SLICES",
        ),
        (
            "horizon_consistency",
            "horizon_consistency_minimum",
            "UNSTABLE_HORIZON_DIRECTION",
        ),
    )
    failed = [
        reason
        for field, threshold, reason in checks
        if _required_number(evidence, field) < float(policy[threshold])
    ]
    reasons.extend(failed)
    return bool(failed)


def _supported(evidence: Mapping[str, object], policy: Mapping[str, object]) -> bool:
    return (
        _required_number(evidence, "oos_rank_ic")
        >= float(policy["minimum_rank_ic_supported"])
        and _required_number(evidence, "confidence_interval_low")
        > float(policy["confidence_interval_lower_bound"])
        and _required_number(evidence, "fdr_q") <= float(policy["fdr_alpha"])
        and _required_number(evidence, "null_p")
        <= float(policy["null_comparison_alpha"])
        and _required_number(evidence, "sign_stability")
        >= float(policy["minimum_sign_stability"])
        and _required_number(evidence, "subperiod_positive_rate")
        >= float(policy["minimum_subperiod_positive_rate"])
        and _required_number(evidence, "robustness_positive_rate")
        >= float(policy["minimum_robustness_positive_rate"])
        and _required_number(evidence, "horizon_consistency")
        >= float(policy["horizon_consistency_minimum"])
    )


def _number(evidence: Mapping[str, object], field: str) -> float | None:
    try:
        value = float(evidence[field])
    except (KeyError, TypeError, ValueError):
        return None
    return value if math.isfinite(value) else None


def _required_number(evidence: Mapping[str, object], field: str) -> float:
    value = _number(evidence, field)
    if value is None:
        raise ValueError(f"missing_decision_evidence:{field}")
    return value
