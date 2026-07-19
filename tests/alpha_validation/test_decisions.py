from __future__ import annotations

import pytest

from ashare_premarket.alpha_validation.decisions import decide_candidate


POLICY = {
    "version": "goal12_research_decision_policy_v1",
    "minimum_valid_dates": 252,
    "minimum_observation_rows": 5000,
    "minimum_median_breadth": 20,
    "maximum_missing_rate": 0.2,
    "maximum_zero_variance_rate": 0.1,
    "maximum_symbol_concentration": 0.1,
    "maximum_date_concentration": 0.01,
    "minimum_rank_ic_supported": 0.03,
    "minimum_rank_ic_weak": 0.01,
    "confidence_interval_lower_bound": 0.0,
    "fdr_alpha": 0.05,
    "null_comparison_alpha": 0.05,
    "minimum_sign_stability": 0.6,
    "minimum_subperiod_positive_rate": 0.6,
    "minimum_robustness_positive_rate": 0.6,
    "horizon_consistency_minimum": 2 / 3,
    "rejection_fdr_q": 0.1,
    "rejection_null_p": 0.2,
    "turnover_warning_threshold": 0.8,
}


def _evidence(**overrides: object) -> dict[str, object]:
    values: dict[str, object] = {
        "eligible": True,
        "valid_date_count": 300,
        "observation_row_count": 9000,
        "median_breadth": 30,
        "missing_rate": 0.05,
        "zero_variance_rate": 0.01,
        "symbol_concentration": 0.04,
        "date_concentration": 0.004,
        "oos_rank_ic": 0.04,
        "confidence_interval_low": 0.005,
        "fdr_q": 0.03,
        "null_p": 0.03,
        "sign_stability": 0.7,
        "subperiod_positive_rate": 0.7,
        "robustness_positive_rate": 0.7,
        "horizon_consistency": 2 / 3,
        "ranking_turnover": 0.5,
    }
    values.update(overrides)
    return values


def test_all_five_allowed_statuses_and_production_lock() -> None:
    cases = {
        "research_supported_candidate": _evidence(),
        "research_weak_evidence": _evidence(oos_rank_ic=0.02),
        "research_unstable": _evidence(sign_stability=0.59),
        "research_rejected": _evidence(oos_rank_ic=0.0),
        "research_insufficient_data": _evidence(valid_date_count=251),
    }
    for expected, evidence in cases.items():
        decision = decide_candidate("candidate", evidence, POLICY)
        assert decision["status"] == expected
        assert decision["production_ready"] is False
        assert decision["policy_version"] == POLICY["version"]


@pytest.mark.parametrize(
    ("field", "boundary", "outside"),
    [
        ("valid_date_count", 252, 251),
        ("observation_row_count", 5000, 4999),
        ("median_breadth", 20, 19.999),
        ("missing_rate", 0.2, 0.200001),
        ("zero_variance_rate", 0.1, 0.100001),
        ("symbol_concentration", 0.1, 0.100001),
        ("date_concentration", 0.01, 0.010001),
    ],
)
def test_sufficiency_boundaries_are_inclusive_and_fail_immediately_outside(
    field: str, boundary: float, outside: float
) -> None:
    assert decide_candidate("candidate", _evidence(**{field: boundary}), POLICY)[
        "status"
    ] != "research_insufficient_data"
    assert decide_candidate("candidate", _evidence(**{field: outside}), POLICY)[
        "status"
    ] == "research_insufficient_data"


@pytest.mark.parametrize(
    ("field", "boundary", "outside"),
    [
        ("oos_rank_ic", 0.03, 0.029999),
        ("confidence_interval_low", 0.000001, 0.0),
        ("fdr_q", 0.05, 0.050001),
        ("null_p", 0.05, 0.050001),
        ("sign_stability", 0.6, 0.599999),
        ("subperiod_positive_rate", 0.6, 0.599999),
        ("robustness_positive_rate", 0.6, 0.599999),
        ("horizon_consistency", 2 / 3, 0.666666),
    ],
)
def test_supported_boundaries_are_frozen_just_inside_and_outside(
    field: str, boundary: float, outside: float
) -> None:
    assert decide_candidate("candidate", _evidence(**{field: boundary}), POLICY)[
        "status"
    ] == "research_supported_candidate"
    assert decide_candidate("candidate", _evidence(**{field: outside}), POLICY)[
        "status"
    ] != "research_supported_candidate"


def test_turnover_is_warning_only_and_ineligible_candidate_fails_closed() -> None:
    warned = decide_candidate("candidate", _evidence(ranking_turnover=0.81), POLICY)
    assert warned["status"] == "research_supported_candidate"
    assert warned["warnings"] == ("HIGH_RANKING_TURNOVER",)

    ineligible = decide_candidate(
        "market_regime", _evidence(eligible=False, eligibility_reason="DATE_LEVEL_CONTEXT"), POLICY
    )
    assert ineligible["status"] == "research_insufficient_data"
    assert "DATE_LEVEL_CONTEXT" in ineligible["reason_codes"]
