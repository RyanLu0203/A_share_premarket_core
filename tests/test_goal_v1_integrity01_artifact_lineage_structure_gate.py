from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.validation.goal_v1_integrity01 import (
    AUDIT_PATH,
    FALSE_BOUNDARY_KEYS,
    FORBIDDEN_FIELD_NAMES,
    FORBIDDEN_OUTPUT_DIRS,
    MANIFEST_PATH,
    WORKFLOW_ID,
    audit_goal_v1_integrity01_artifact_lineage_structure_gate,
    run_goal_v1_integrity01_artifact_lineage_structure_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _json(path: str) -> dict[str, object]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _workflow() -> dict[str, dict[str, str]]:
    return {row["workflow_id"]: row for row in _rows("configs/project/workflow_status.csv")}


def test_goal_v1_integrity01_runner_is_deterministic_and_audit_passes() -> None:
    assert run_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT)
    first = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert run_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT)
    second = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert audit_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT)
    assert "Status: `PASS`" in (ROOT / AUDIT_PATH).read_text(encoding="utf-8")


def test_goal_v1_integrity01_verifies_canonical_lineage_and_non_actionability() -> None:
    assert run_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    lineage = manifest["artifact_lineage_summary"]
    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["mode"] == "infrastructure_integrity_only"
    assert manifest["canonical_artifact_lineage_verified"] is True
    assert lineage["risk_overlay_rows"] == 100
    assert lineage["recommendation_diagnostics_rows"] == 100
    assert lineage["position_band_diagnostics_rows"] == 100
    assert lineage["trade_date_symbol_keys_match"] is True
    assert manifest["goal08b_actionability_status_values"] == ["never_actionable"]
    assert manifest["goal09_position_actionability_status_values"] == ["never_actionable"]
    assert manifest["goal08b_rows_never_actionable"] is True
    assert manifest["goal09_rows_never_actionable"] is True


def test_goal_v1_integrity01_limits_future_dashboard_inputs_to_audited_artifacts() -> None:
    assert run_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    allowed_inputs = set(manifest["future_dashboard_allowed_inputs"])
    assert "outputs/risk_overlay/goal07b_review_only_risk_overlay.csv" in allowed_inputs
    assert "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv" in allowed_inputs
    assert "outputs/position/goal09_review_only_position_band_diagnostics.csv" in allowed_inputs
    assert "outputs/audits/goal_v1_integrity01_artifact_lineage_structure_audit.md" in allowed_inputs
    assert manifest["future_dashboard_may_read_only_canonical_outputs_and_audit_metadata"] is True
    assert manifest["future_dashboard_forbidden_source_inputs_blocked"] is True
    assert "outputs/local" in manifest["future_dashboard_forbidden_source_inputs"]
    assert set(manifest["forbidden_field_names"]) == FORBIDDEN_FIELD_NAMES
    assert manifest["forbidden_field_names_absent_from_diagnostic_outputs"] is True
    assert manifest["forbidden_field_names_absent_from_future_dashboard_required_fields"] is True


def test_goal_v1_integrity01_workflow_unlocks_only_future_design_contract_eligibility() -> None:
    assert run_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    workflow = _workflow()
    assert workflow[WORKFLOW_ID]["status"] == "implemented_infrastructure_only"
    assert workflow[WORKFLOW_ID]["implemented_in_repo"] == "true"
    assert workflow[WORKFLOW_ID]["depends_on"] == "goal091_position_band_warning_dashboard_readiness_gate"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["implemented_in_repo"] == "false"
    assert workflow["dashboard_daily_report"]["depends_on"] == WORKFLOW_ID
    assert manifest["goal_dashboard00_request_status"] == "eligible_for_explicit_design_only_contract_gate"
    assert manifest["dashboard_daily_report_status_after_goal_v1_integrity01"] == "locked_future"
    assert manifest["dashboard_outputs_generated"] is False


def test_goal_v1_integrity01_generates_no_forbidden_downstream_outputs_or_rows() -> None:
    assert run_goal_v1_integrity01_artifact_lineage_structure_gate(ROOT)
    manifest = _json(MANIFEST_PATH)
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    for rel in FORBIDDEN_OUTPUT_DIRS:
        assert not (ROOT / rel).exists()
    assert len(_rows("outputs/risk_overlay/goal07b_review_only_risk_overlay.csv")) == 100
    assert len(_rows("outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv")) == 100
    assert len(_rows("outputs/position/goal09_review_only_position_band_diagnostics.csv")) == 100
