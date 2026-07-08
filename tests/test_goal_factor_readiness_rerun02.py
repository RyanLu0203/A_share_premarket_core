from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path

from ashare_premarket.research.goal_factor_readiness_research01 import (
    MIN_HOLDOUT_VALID_ROWS,
    SIGN_STABLE_MIN,
)
from ashare_premarket.research.goal_quant_research03 import MIN_VALID_ROWS
from ashare_premarket.research.goal_quant_research04 import STRONG_IC_THRESHOLD

ROOT = Path(__file__).resolve().parents[1]

PREFIX = "outputs/research/goal_factor_readiness_rerun02_"
MANIFEST_PATH = "outputs/audits/goal_factor_readiness_rerun02_manifest.json"
AUDIT_PATH = "outputs/audits/goal_factor_readiness_rerun02_audit.md"
REPORT_PATH = "outputs/audits/goal_factor_readiness_rerun02_report.md"
HANDOFF_PATH = "docs/research/GOAL_FACTOR_READINESS_RERUN02_GOVERNANCE_HANDOFF.md"

REQUIRED_OUTPUTS = [
    PREFIX + "evidence_integration_map.csv",
    PREFIX + "old_new_panel_comparison.csv",
    PREFIX + "reconstructed_panel_summary.csv",
    PREFIX + "feature_lineage.csv",
    PREFIX + "target_horizon_contract.csv",
    PREFIX + "extended_regime_coverage.csv",
    PREFIX + "walk_forward_validation_summary.csv",
    PREFIX + "holdout_validation_summary.csv",
    PREFIX + "factor_readiness_status.csv",
    PREFIX + "old_new_readiness_comparison.csv",
    PREFIX + "provider_robustness_summary.csv",
    PREFIX + "provider_discrepancy_warnings.csv",
    PREFIX + "index_context_contribution.csv",
    PREFIX + "anti_overfitting_review.csv",
    PREFIX + "readiness_decision_reasons.csv",
    PREFIX + "remaining_gap_map.csv",
    PREFIX + "construction_warnings.csv",
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    HANDOFF_PATH,
]


def _module():
    try:
        return importlib.import_module("ashare_premarket.research.goal_factor_readiness_rerun02")
    except ModuleNotFoundError as exc:
        assert False, f"missing rerun02 module: {exc}"


def _run_gate() -> dict:
    module = _module()
    assert module.run_goal_factor_readiness_rerun02(ROOT)
    assert module.audit_goal_factor_readiness_rerun02(ROOT)
    return json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))


def _rows(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


_RERUN_MANIFEST: dict | None = None


def _manifest_once() -> dict:
    global _RERUN_MANIFEST
    if _RERUN_MANIFEST is None:
        _RERUN_MANIFEST = _run_gate()
    return _RERUN_MANIFEST


def test_consumes_network_bundle_and_validates_checksums() -> None:
    manifest = _manifest_once()
    assert manifest["network_bundle_rows_consumed"] == 34543
    assert manifest["network_bundle_dates_consumed"] == 843
    assert manifest["network_bundle_symbols_consumed"] == 41
    assert manifest["network_bundle_symbols_attempted"] == 50
    assert manifest["failed_network_symbols_retained"] == 9
    assert manifest["materially_expanded_input"] is True
    assert manifest["bundle_checksum_validation_passed"] is True
    assert manifest["credential_dependency_required"] is False
    assert manifest["providers_represented"] == ["akshare_sina", "baostock"]
    assert set(manifest["index_context_series_consumed"]) == {"sh000001", "sh000300", "sz399001"}
    assert "market_relative_return_20d" in manifest["index_context_fields_consumed"]

    evidence_rows = _rows(PREFIX + "evidence_integration_map.csv")
    by_dimension = {row["dimension"]: row for row in evidence_rows}
    assert by_dimension["date_coverage"]["new_state"] == "843_dates"
    assert by_dimension["date_extension"]["new_state"] == "2023-01-03..2026-06-30"
    assert by_dimension["provider_lineage"]["new_state"] == "akshare_sina_plus_baostock_crosscheck"
    assert by_dimension["symbol_fetch_failures"]["new_state"] == "9_failed_or_empty_retained"
    assert "index_return_20d" in by_dimension["index_context_availability"]["new_context_fields_consumed"]


def test_required_outputs_old_new_relationship_and_no_old_only_fallback() -> None:
    manifest = _manifest_once()
    for rel in REQUIRED_OUTPUTS:
        assert (ROOT / rel).exists(), rel

    assert manifest["old_panel_rows"] == 180000
    assert manifest["new_panel_rows"] > manifest["old_panel_rows"]
    assert manifest["new_panel_dates"] == 843
    assert manifest["old_panel_dates"] == 120
    assert manifest["new_panel_rows_from_network_bundle"] is True
    assert manifest["old_only_panel_rerun"] is False

    panel_rows = _rows(PREFIX + "old_new_panel_comparison.csv")
    by_metric = {row["metric"]: row for row in panel_rows}
    assert by_metric["panel_rows"]["new_value"] == str(manifest["new_panel_rows"])
    assert by_metric["dates"]["old_value"] == "120"
    assert by_metric["dates"]["new_value"] == "843"
    assert by_metric["source_relation"]["change_class"] == "materially_expanded_committed_network_bundle"


def test_target_isolation_chronological_holdout_thresholds_and_locks() -> None:
    manifest = _manifest_once()
    assert manifest["strong_ic_threshold_used"] == STRONG_IC_THRESHOLD == 0.03
    assert manifest["min_valid_rows_used"] == MIN_VALID_ROWS
    assert manifest["min_holdout_valid_rows_used"] == MIN_HOLDOUT_VALID_ROWS
    assert manifest["sign_stable_min"] == SIGN_STABLE_MIN
    assert manifest["final_holdout_untouched"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True
    assert manifest["rec_tiering_unlocked_by_this_goal"] is False
    assert manifest["workflow_status_modified_by_this_goal"] is False
    assert manifest["locked_capabilities_modified_by_this_goal"] is False

    feature_headers = set(_rows(PREFIX + "feature_lineage.csv")[0])
    assert not any(col.startswith("forward_return_") for col in feature_headers)
    assert not any(col.startswith("benchmark_excess_return_") for col in feature_headers)

    target_rows = _rows(PREFIX + "target_horizon_contract.csv")
    assert {row["horizon"] for row in target_rows} == {"1d", "5d", "20d"}
    assert all(row["feature_cutoff"] == "trade_date_close" for row in target_rows)
    assert all(row["target_usage"] == "evaluation_only_not_feature" for row in target_rows)

    holdout_rows = _rows(PREFIX + "holdout_validation_summary.csv")
    assert holdout_rows
    assert all(row["final_holdout_used_for_selection"] == "false" for row in holdout_rows)
    assert all(row["split_policy"] == "chronological_last_20pct_final_holdout" for row in holdout_rows)


def test_provider_failed_symbol_disclosures_and_honest_transitions() -> None:
    manifest = _manifest_once()
    assert manifest["ready_factor_count_before"] == 0
    assert manifest["ready_factor_count_after"] >= 0
    assert manifest["ready_status_fabricated"] is False

    status_rows = _rows(PREFIX + "factor_readiness_status.csv")
    ready_rows = [row for row in status_rows if row["readiness_status"] == "ready"]
    assert manifest["ready_factor_count_after"] == len({row["base_refined_factor_id"] for row in ready_rows})
    assert all(row["base_precondition_pass"] == "true" for row in ready_rows)

    comparison_rows = _rows(PREFIX + "old_new_readiness_comparison.csv")
    allowed = {
        "unchanged_not_ready",
        "degraded",
        "newly_conditionally_useful",
        "remained_conditionally_useful",
        "lost_conditional_status",
        "newly_ready",
        "remained_ready",
    }
    assert comparison_rows
    assert all(row["transition_category"] in allowed for row in comparison_rows)

    provider_rows = _rows(PREFIX + "provider_robustness_summary.csv")
    assert any(row["check_id"] == "baostock_akshare_overlap_return_consistency" for row in provider_rows)

    warnings = _rows(PREFIX + "construction_warnings.csv")
    assert any(row["warning_code"] == "FAILED_NETWORK_SYMBOLS_RETAINED" and row["count"] == "9" for row in warnings)


def test_deterministic_offline_replay() -> None:
    first_manifest = _run_gate()
    first_status = (ROOT / (PREFIX + "factor_readiness_status.csv")).read_text(encoding="utf-8")
    first_comparison = (ROOT / (PREFIX + "old_new_readiness_comparison.csv")).read_text(encoding="utf-8")

    second_manifest = _run_gate()
    second_status = (ROOT / (PREFIX + "factor_readiness_status.csv")).read_text(encoding="utf-8")
    second_comparison = (ROOT / (PREFIX + "old_new_readiness_comparison.csv")).read_text(encoding="utf-8")

    assert first_manifest == second_manifest
    assert first_status == second_status
    assert first_comparison == second_comparison
