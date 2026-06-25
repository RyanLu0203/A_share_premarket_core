from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_json


def preserve_later_review_only_workflow_states(root: Path, by_id: dict[str, dict[str, str]]) -> None:
    """Preserve validated later-stage review-only rows during earlier gate reruns."""

    if _goal08a_valid(root) and "goal08a_recommendation_contract_design_gate" in by_id:
        by_id["goal08a_recommendation_contract_design_gate"].update(
            {
                "display_name": "GOAL-08A Recommendation Contract Design Gate",
                "stage_or_goal": "GOAL-08A",
                "status": "implemented_design_only",
                "current_repo_role": "design_only_future_recommendation_contract_gate",
                "implemented_in_repo": "true",
                "allowed_next_action": "request_explicit_goal08b_review_only_prototype_or_fix_goal08a_warnings",
                "depends_on": "goal07b_risk_overlay_calculation",
                "produces_artifacts": "configs/recommendation/goal08a_future_recommendation_input_contract.yaml;configs/recommendation/goal08a_future_recommendation_schema.yaml;configs/recommendation/goal08a_warning_propagation_policy.yaml;configs/recommendation/goal08a_actionability_guardrails.yaml;configs/recommendation/goal08a_recommendation_state_machine.yaml;outputs/audits/goal08a_recommendation_contract_design_report.md;outputs/audits/goal08a_recommendation_contract_design_manifest.json;outputs/audits/goal08a_recommendation_contract_design_audit.md",
                "primary_docs": "docs/recommendation/GOAL08A_RECOMMENDATION_CONTRACT_DESIGN.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md",
                "primary_scripts": "scripts/run_goal08a_recommendation_contract_design_gate.py;scripts/audit_goal08a_recommendation_contract_design_gate.py",
                "primary_outputs": "outputs/audits/goal08a_recommendation_contract_design_report.md;outputs/audits/goal08a_recommendation_contract_design_manifest.json;outputs/audits/goal08a_recommendation_contract_design_audit.md",
                "promotion_rule": "implemented_design_only_after_goal08a_design_gate_pass_with_warnings",
                "notes": "Design-only future recommendation contract gate; no recommendation rows, actions, positions, dashboards, trading, production, backtests, factor-mining, broker, or DQN/RL outputs.",
            }
        )

    if _storage01_valid(root) and "goal_storage01_local_research_lake_hardening_gate" in by_id:
        by_id["goal_storage01_local_research_lake_hardening_gate"].update(
            {
                "display_name": "GOAL-STORAGE-01 Local Research Lake Hardening Gate",
                "stage_or_goal": "GOAL-STORAGE-01",
                "status": "implemented_infrastructure_only",
                "current_repo_role": "infrastructure_only_storage_governance_gate",
                "implemented_in_repo": "true",
                "allowed_next_action": "request_explicit_goal08b_review_only_prototype_or_fix_storage_hardening_warnings",
                "depends_on": "goal08a_recommendation_contract_design_gate",
                "produces_artifacts": "configs/storage/goal_storage01_local_research_lake_contract.yaml;outputs/audits/goal_storage01_local_research_lake_hardening_report.md;outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json;outputs/audits/goal_storage01_local_research_lake_hardening_audit.md",
                "primary_docs": "docs/storage/GOAL_STORAGE01_LOCAL_RESEARCH_LAKE_HARDENING_GATE.md;docs/storage/DATA_STORAGE_ARCHITECTURE.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "scripts/run_goal_storage01_local_research_lake_hardening_gate.py;scripts/audit_goal_storage01_local_research_lake_hardening_gate.py",
                "primary_outputs": "outputs/audits/goal_storage01_local_research_lake_hardening_report.md;outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json;outputs/audits/goal_storage01_local_research_lake_hardening_audit.md",
                "promotion_rule": "implemented_infrastructure_only_after_storage01_hardening_pass",
                "notes": "Infrastructure-only local research lake hardening gate; does not unlock GOAL-08B by itself and creates no recommendation, position, dashboard, trading, production, backtest, factor-mining, broker, or DQN/RL outputs.",
            }
        )

    goal08b0_valid = _goal08b0_valid(root)
    if goal08b0_valid and "goal08b0_recommendation_review_only_unlock_gate" in by_id:
        by_id["goal08b0_recommendation_review_only_unlock_gate"].update(
            {
                "display_name": "GOAL-08B.0 Recommendation Review-Only Unlock Gate",
                "stage_or_goal": "GOAL-08B.0",
                "status": "implemented_review_only",
                "current_repo_role": "review_only_unlock_governance_gate",
                "implemented_in_repo": "true",
                "allowed_next_action": "await_explicit_goal08b_review_only_recommendation_diagnostics_prototype",
                "depends_on": "goal_storage01_local_research_lake_hardening_gate",
                "produces_artifacts": "configs/recommendation/goal08b0_review_only_unlock_policy.yaml;docs/recommendation/GOAL08B0_RECOMMENDATION_REVIEW_ONLY_UNLOCK_GATE.md;outputs/audits/goal08b0_recommendation_review_only_unlock_report.md;outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json;outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md",
                "primary_docs": "docs/recommendation/GOAL08B0_RECOMMENDATION_REVIEW_ONLY_UNLOCK_GATE.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "scripts/run_goal08b0_recommendation_review_only_unlock_gate.py;scripts/audit_goal08b0_recommendation_review_only_unlock_gate.py",
                "primary_outputs": "outputs/audits/goal08b0_recommendation_review_only_unlock_report.md;outputs/audits/goal08b0_recommendation_review_only_unlock_manifest.json;outputs/audits/goal08b0_recommendation_review_only_unlock_audit.md",
                "promotion_rule": "implemented_review_only_after_goal08b0_unlock_gate_pass_with_warnings",
                "notes": "Review-only unlock gate; GOAL-08B recommendation diagnostics become eligible only for a future explicit non-actionable prototype and are not implemented here.",
            }
        )

    if _goal08b_valid(root) and "goal08b_recommendation_review_only_prototype" in by_id:
        by_id["goal08b_recommendation_review_only_prototype"].update(
            {
                "display_name": "GOAL-08B Recommendation Review-Only Prototype",
                "stage_or_goal": "GOAL-08B",
                "status": "implemented_review_only",
                "current_repo_role": "review_only_recommendation_diagnostic_prototype",
                "implemented_in_repo": "true",
                "allowed_next_action": "request_explicit_goal09_position_band_review_only_unlock_or_fix_goal08b_warnings",
                "depends_on": "goal08b0_recommendation_review_only_unlock_gate",
                "produces_artifacts": "configs/recommendation/goal08b_review_only_diagnostics_policy.yaml;outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv;docs/recommendation/GOAL08B_REVIEW_ONLY_RECOMMENDATION_DIAGNOSTICS.md;outputs/audits/goal08b_recommendation_diagnostics_report.md;outputs/audits/goal08b_recommendation_diagnostics_manifest.json;outputs/audits/goal08b_recommendation_diagnostics_audit.md",
                "primary_docs": "docs/recommendation/GOAL08B_REVIEW_ONLY_RECOMMENDATION_DIAGNOSTICS.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "scripts/run_goal08b_recommendation_diagnostics_prototype.py;scripts/audit_goal08b_recommendation_diagnostics_prototype.py",
                "primary_outputs": "outputs/recommendation/goal08b_review_only_recommendation_diagnostics.csv;outputs/audits/goal08b_recommendation_diagnostics_report.md;outputs/audits/goal08b_recommendation_diagnostics_manifest.json;outputs/audits/goal08b_recommendation_diagnostics_audit.md",
                "promotion_rule": "implemented_review_only_after_goal08b_diagnostics_pass_with_warnings",
                "notes": "Review-only non-actionable recommendation diagnostics; not buy/sell/hold, target price, position sizing, portfolio weight, dashboard, trading, production, backtest, factor-mining, broker, local-lake, or DQN/RL output.",
            }
        )
    goal090_valid = _goal090_valid(root)
    if goal090_valid and "goal090_position_band_review_only_unlock_gate" in by_id:
        by_id["goal090_position_band_review_only_unlock_gate"].update(
            {
                "display_name": "GOAL-09.0 Position-Band Review-Only Unlock Gate",
                "stage_or_goal": "GOAL-09.0",
                "status": "implemented_review_only",
                "current_repo_role": "review_only_unlock_governance_gate",
                "implemented_in_repo": "true",
                "allowed_next_action": "await_explicit_goal09_position_band_diagnostics_prototype",
                "depends_on": "goal08b_recommendation_review_only_prototype",
                "produces_artifacts": "configs/position/goal090_position_band_review_only_unlock_policy.yaml;docs/position/GOAL090_POSITION_BAND_REVIEW_ONLY_UNLOCK_GATE.md;outputs/audits/goal090_position_band_review_only_unlock_report.md;outputs/audits/goal090_position_band_review_only_unlock_manifest.json;outputs/audits/goal090_position_band_review_only_unlock_audit.md",
                "primary_docs": "docs/position/GOAL090_POSITION_BAND_REVIEW_ONLY_UNLOCK_GATE.md;docs/architecture/FULL_PROGRAM_ROADMAP_AFTER_CLEAN_BOOTSTRAP.md;docs/10_PROGRAM_ROADMAP_AND_ARCHITECTURE.md",
                "primary_scripts": "scripts/run_goal090_position_band_review_only_unlock_gate.py;scripts/audit_goal090_position_band_review_only_unlock_gate.py",
                "primary_outputs": "outputs/audits/goal090_position_band_review_only_unlock_report.md;outputs/audits/goal090_position_band_review_only_unlock_manifest.json;outputs/audits/goal090_position_band_review_only_unlock_audit.md",
                "promotion_rule": "implemented_review_only_after_goal090_unlock_gate_pass_with_warnings",
                "notes": "Review-only unlock gate; GOAL-09 position-band diagnostics become eligible only for a future explicit non-actionable prototype and are not implemented here.",
            }
        )
        if "position_band_recommendation" in by_id:
            from ashare_premarket.contract_design.goal090 import goal09_eligible_workflow_patch

            by_id["position_band_recommendation"].update(goal09_eligible_workflow_patch(root))


def preserve_later_review_only_capabilities(root: Path, payload: dict[str, object]) -> None:
    if _goal08a_valid(root):
        payload["goal08a_recommendation_contract_design_gate"] = "implemented_design_only"
    if _storage01_valid(root):
        payload["goal_storage01_local_research_lake_hardening_gate"] = "implemented_infrastructure_only"
    if _goal08b0_valid(root):
        payload["goal08b0_recommendation_review_only_unlock_gate"] = "implemented_review_only"
    if _goal08b_valid(root):
        payload["goal08b_recommendation_review_only_prototype"] = "implemented_review_only"
    if _goal090_valid(root):
        from ashare_premarket.contract_design.goal090 import goal09_eligible_workflow_patch

        payload["goal090_position_band_review_only_unlock_gate"] = "implemented_review_only"
        payload["position_band_recommendation"] = goal09_eligible_workflow_patch(root)["status"]


def _goal08a_valid(root: Path) -> bool:
    report = _read(root / "outputs/audits/goal08a_recommendation_contract_design_report.md")
    audit = _read(root / "outputs/audits/goal08a_recommendation_contract_design_audit.md")
    manifest = _read_json(root / "outputs/audits/goal08a_recommendation_contract_design_manifest.json")
    return (
        "GOAL-08A Recommendation Contract Design Gate: PASS" in report
        and "Status: `PASS`" in audit
        and manifest.get("mode") == "design_only"
        and manifest.get("future_schema_row_count") == 0
        and manifest.get("recommendation_rows_generated") is False
    )


def _storage01_valid(root: Path) -> bool:
    report = _read(root / "outputs/audits/goal_storage01_local_research_lake_hardening_report.md")
    audit = _read(root / "outputs/audits/goal_storage01_local_research_lake_hardening_audit.md")
    manifest = _read_json(root / "outputs/audits/goal_storage01_local_research_lake_hardening_manifest.json")
    return (
        "GOAL-STORAGE-01 Local Research Lake Hardening Gate: PASS" in report
        and "Status: `PASS`" in audit
        and manifest.get("mode") == "infrastructure_only"
        and manifest.get("local_data_files_created") is False
    )


def _goal08b0_valid(root: Path) -> bool:
    try:
        from ashare_premarket.contract_design.goal08b0 import goal08b0_valid_unlock_evidence

        return goal08b0_valid_unlock_evidence(root)
    except Exception:
        return False


def _goal08b_valid(root: Path) -> bool:
    try:
        from ashare_premarket.review_diagnostics.goal08b import goal08b_valid_diagnostics_evidence

        return goal08b_valid_diagnostics_evidence(root)
    except Exception:
        return False


def _goal090_valid(root: Path) -> bool:
    try:
        from ashare_premarket.contract_design.goal090 import goal090_valid_unlock_evidence

        return goal090_valid_unlock_evidence(root)
    except Exception:
        return False


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {}
