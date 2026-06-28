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

            if by_id["position_band_recommendation"].get("status") != "implemented_review_only":
                by_id["position_band_recommendation"].update(goal09_eligible_workflow_patch(root))
    if _goal09_valid(root) and "position_band_recommendation" in by_id:
        from ashare_premarket.review_diagnostics.goal09 import goal09_implemented_workflow_patch

        by_id["position_band_recommendation"].update(goal09_implemented_workflow_patch())
    if _goal091_valid(root) and "goal091_position_band_warning_dashboard_readiness_gate" in by_id:
        from ashare_premarket.contract_design.goal091 import goal091_implemented_workflow_patch

        by_id["goal091_position_band_warning_dashboard_readiness_gate"].update(goal091_implemented_workflow_patch())
    if _goal_v1_integrity01_valid(root) and "goal_v1_integrity01_artifact_lineage_structure_gate" in by_id:
        from ashare_premarket.validation.goal_v1_integrity01 import goal_v1_integrity01_implemented_workflow_patch

        by_id["goal_v1_integrity01_artifact_lineage_structure_gate"].update(goal_v1_integrity01_implemented_workflow_patch())
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"].update(
                {
                    "status": "locked_future",
                    "current_repo_role": "locked_downstream_boundary",
                    "implemented_in_repo": "false",
                    "allowed_next_action": "request_explicit_goal_dashboard00_contract_design_gate",
                    "depends_on": "goal_v1_integrity01_artifact_lineage_structure_gate",
                    "promotion_rule": "locked_until_explicit_goal_dashboard00_contract_design_gate",
                    "notes": "Locked dashboard workflow; GOAL-V1-INTEGRITY-01 verifies lineage before any future explicit design-only contract/layout gate request and creates no dashboard outputs.",
                }
            )
    goal10a_valid = _goal10a_valid(root)
    if goal10a_valid and "goal10a_backtest_contract_design_gate" in by_id:
        from ashare_premarket.contract_design.goal10a import goal10a_implemented_workflow_patch

        by_id["goal10a_backtest_contract_design_gate"].update(goal10a_implemented_workflow_patch())
    goal10b_valid = _goal10b_valid(root)
    if goal10b_valid:
        from ashare_premarket.backtest.goal10b import (
            goal10b_implemented_workflow_patch,
            locked_goal10c_patch,
            locked_goal10d_patch,
        )

        if "goal10b_backtest_review_only_validation_gate" in by_id:
            by_id["goal10b_backtest_review_only_validation_gate"].update(goal10b_implemented_workflow_patch())
        has_later_backtest_gate = (
            by_id.get("goal10b1_backtest_coverage_repair_gate", {}).get("status") == "implemented_review_only"
            or by_id.get("goal_data_label01_forward_return_label_coverage_expansion", {}).get("status") == "implemented_review_only"
        )
        if "goal10c_backtest_cost_slippage_sensitivity_gate" in by_id and not has_later_backtest_gate:
            by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].update(locked_goal10c_patch())
        if "goal10d_backtest_failure_attribution_gate" in by_id and not has_later_backtest_gate:
            by_id["goal10d_backtest_failure_attribution_gate"].update(locked_goal10d_patch())
        for workflow_id in [
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10b"
        if "signal_backtest" in by_id:
            by_id["signal_backtest"]["allowed_next_action"] = "remain_locked_review_only_diagnostics_represented_by_goal10b_only"
            by_id["signal_backtest"]["notes"] = (
                "Locked production signal backtest workflow. GOAL-10B represents only "
                "non-actionable review-only recommendation diagnostic forward-return metrics."
            )
    goal10b1_valid = _goal10b1_valid(root)
    if goal10b1_valid:
        from ashare_premarket.backtest.goal10b1 import (
            goal10b1_implemented_workflow_patch,
            locked_goal10c_patch as locked_goal10c_after_goal10b1_patch,
            locked_goal10d_patch as locked_goal10d_after_goal10b1_patch,
        )

        if "goal10b1_backtest_coverage_repair_gate" in by_id:
            by_id["goal10b1_backtest_coverage_repair_gate"].update(goal10b1_implemented_workflow_patch())
        if (
            "goal10c_backtest_cost_slippage_sensitivity_gate" in by_id
            and by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].get("status") != "implemented_review_only"
        ):
            by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].update(locked_goal10c_after_goal10b1_patch())
        if "goal10d_backtest_failure_attribution_gate" in by_id:
            by_id["goal10d_backtest_failure_attribution_gate"].update(locked_goal10d_after_goal10b1_patch())
        for workflow_id in [
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10b1"
    goal_data_label01_valid = _goal_data_label01_valid(root)
    if goal_data_label01_valid:
        from ashare_premarket.labels.goal_data_label01 import (
            goal_data_label01_implemented_workflow_patch,
            locked_goal10b2_patch,
            locked_goal10c_patch as locked_goal10c_after_goal_data_label01_patch,
            locked_goal_v1_diagnostic_coverage02_patch,
        )

        if "goal_data_label01_forward_return_label_coverage_expansion" in by_id:
            by_id["goal_data_label01_forward_return_label_coverage_expansion"].update(goal_data_label01_implemented_workflow_patch())
        if (
            "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion" in by_id
            and by_id["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"].get("status")
            != "implemented_review_only"
        ):
            by_id["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"].update(locked_goal_v1_diagnostic_coverage02_patch())
        if (
            "goal10b2_recommendation_backtest_revalidation" in by_id
            and by_id["goal10b2_recommendation_backtest_revalidation"].get("status") != "implemented_review_only"
        ):
            by_id["goal10b2_recommendation_backtest_revalidation"].update(locked_goal10b2_patch())
        if (
            "goal10c_backtest_cost_slippage_sensitivity_gate" in by_id
            and by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].get("status") != "implemented_review_only"
        ):
            by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].update(locked_goal10c_after_goal_data_label01_patch())
        for workflow_id in [
            "goal10d_backtest_failure_attribution_gate",
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "goal10d_backtest_failure_attribution_gate" in by_id:
            by_id["goal10d_backtest_failure_attribution_gate"]["depends_on"] = "goal10c_backtest_cost_slippage_sensitivity_gate"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_label01"
    goal_v1_diagnostic_coverage02_valid = _goal_v1_diagnostic_coverage02_valid(root)
    if goal_v1_diagnostic_coverage02_valid:
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import (
            goal_v1_diagnostic_coverage02_implemented_workflow_patch,
            locked_goal10b2_patch,
            locked_goal10c_patch as locked_goal10c_after_diagnostic_coverage02_patch,
        )

        if "goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion" in by_id:
            by_id["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"].update(goal_v1_diagnostic_coverage02_implemented_workflow_patch())
        if (
            "goal10b2_recommendation_backtest_revalidation" in by_id
            and by_id["goal10b2_recommendation_backtest_revalidation"].get("status") != "implemented_review_only"
        ):
            by_id["goal10b2_recommendation_backtest_revalidation"].update(locked_goal10b2_patch())
        if (
            "goal10c_backtest_cost_slippage_sensitivity_gate" in by_id
            and by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].get("status") != "implemented_review_only"
        ):
            by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].update(locked_goal10c_after_diagnostic_coverage02_patch())
        for workflow_id in [
            "goal10d_backtest_failure_attribution_gate",
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "goal10d_backtest_failure_attribution_gate" in by_id:
            by_id["goal10d_backtest_failure_attribution_gate"]["depends_on"] = "goal10c_backtest_cost_slippage_sensitivity_gate"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_v1_diagnostic_coverage02"
    goal10b2_valid = _goal10b2_valid(root)
    if goal10b2_valid:
        from ashare_premarket.backtest.goal10b2 import (
            goal10b2_implemented_workflow_patch,
            locked_goal10c_patch as locked_goal10c_after_goal10b2_patch,
            locked_goal10d_patch as locked_goal10d_after_goal10b2_patch,
        )

        if "goal10b2_recommendation_backtest_revalidation" in by_id:
            by_id["goal10b2_recommendation_backtest_revalidation"].update(goal10b2_implemented_workflow_patch())
        if (
            "goal10c_backtest_cost_slippage_sensitivity_gate" in by_id
            and by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].get("status") != "implemented_review_only"
        ):
            by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].update(locked_goal10c_after_goal10b2_patch())
        if "goal10d_backtest_failure_attribution_gate" in by_id:
            by_id["goal10d_backtest_failure_attribution_gate"].update(locked_goal10d_after_goal10b2_patch())
        for workflow_id in [
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10b2"
    goal10c_valid = _goal10c_valid(root)
    if goal10c_valid:
        from ashare_premarket.backtest.goal10c import (
            goal10c_implemented_workflow_patch,
            locked_goal10d_patch as locked_goal10d_after_goal10c_patch,
        )

        if "goal10c_backtest_cost_slippage_sensitivity_gate" in by_id:
            by_id["goal10c_backtest_cost_slippage_sensitivity_gate"].update(goal10c_implemented_workflow_patch())
        if "goal10d_backtest_failure_attribution_gate" in by_id:
            by_id["goal10d_backtest_failure_attribution_gate"].update(locked_goal10d_after_goal10c_patch())
        for workflow_id in [
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10c"
    goal_data_provider02a_valid = _goal_data_provider02a_valid(root)
    if goal_data_provider02a_valid:
        from ashare_premarket.providers.goal_data_provider02a import (
            GOAL10B3_WORKFLOW_ID,
            GOAL_DATA_PANEL02_WORKFLOW_ID,
            GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
            GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
            goal_data_provider02a_implemented_workflow_patch,
            locked_goal10b3_patch,
            locked_goal_data_panel02_patch,
            locked_goal_data_provider02b_patch,
            locked_goal_v1_diagnostic_coverage03_patch,
        )

        if "goal_data_provider02a_multi_provider_capability_probe" in by_id:
            by_id["goal_data_provider02a_multi_provider_capability_probe"].update(goal_data_provider02a_implemented_workflow_patch())
        goal_data_provider02b_valid = _goal_data_provider02b_valid(root)
        goal_v1_diagnostic_coverage03_valid = _goal_v1_diagnostic_coverage03_valid(root)
        if GOAL_DATA_PROVIDER02B_WORKFLOW_ID in by_id and not goal_data_provider02b_valid:
            by_id[GOAL_DATA_PROVIDER02B_WORKFLOW_ID].update(locked_goal_data_provider02b_patch())
        if GOAL_DATA_PANEL02_WORKFLOW_ID in by_id:
            by_id[GOAL_DATA_PANEL02_WORKFLOW_ID].update(locked_goal_data_panel02_patch())
        if GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID in by_id and not goal_v1_diagnostic_coverage03_valid:
            by_id[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID].update(locked_goal_v1_diagnostic_coverage03_patch())
        if GOAL10B3_WORKFLOW_ID in by_id and not _goal10b3_valid(root):
            by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_patch())
        for workflow_id in [
            "goal10d_backtest_failure_attribution_gate",
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02a"
    goal_data_provider02a1_valid = _goal_data_provider02a1_valid(root)
    if goal_data_provider02a1_valid:
        from ashare_premarket.providers.goal_data_provider02a1 import (
            WORKFLOW_ID as GOAL_DATA_PROVIDER02A1_WORKFLOW_ID,
            GOAL10B3_WORKFLOW_ID,
            GOAL_DATA_PANEL02_WORKFLOW_ID,
            GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
            GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
            goal_data_provider02a1_implemented_workflow_patch,
            locked_goal10b3_after_goal_data_provider02a_patch,
            locked_goal_data_panel02_after_goal_data_provider02a_patch,
            locked_goal_data_provider02b_patch as locked_goal_data_provider02b_after_goal_data_provider02a1_patch,
            locked_goal_v1_diagnostic_coverage03_after_goal_data_provider02a_patch,
        )

        if GOAL_DATA_PROVIDER02A1_WORKFLOW_ID in by_id:
            by_id[GOAL_DATA_PROVIDER02A1_WORKFLOW_ID].update(goal_data_provider02a1_implemented_workflow_patch())
        goal_data_provider02b_valid = _goal_data_provider02b_valid(root)
        goal_v1_diagnostic_coverage03_valid = _goal_v1_diagnostic_coverage03_valid(root)
        if GOAL_DATA_PROVIDER02B_WORKFLOW_ID in by_id and not goal_data_provider02b_valid:
            by_id[GOAL_DATA_PROVIDER02B_WORKFLOW_ID].update(locked_goal_data_provider02b_after_goal_data_provider02a1_patch())
        if GOAL_DATA_PANEL02_WORKFLOW_ID in by_id:
            by_id[GOAL_DATA_PANEL02_WORKFLOW_ID].update(locked_goal_data_panel02_after_goal_data_provider02a_patch())
        if GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID in by_id and not goal_v1_diagnostic_coverage03_valid:
            by_id[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID].update(locked_goal_v1_diagnostic_coverage03_after_goal_data_provider02a_patch())
        if GOAL10B3_WORKFLOW_ID in by_id and not _goal10b3_valid(root):
            by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_after_goal_data_provider02a_patch())
        for workflow_id in [
            "goal10d_backtest_failure_attribution_gate",
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02a1"
    goal_data_provider02b_valid = _goal_data_provider02b_valid(root)
    if goal_data_provider02b_valid:
        from ashare_premarket.providers.goal_data_provider02b import (
            GOAL10B3_WORKFLOW_ID,
            GOAL_DATA_PANEL02_WORKFLOW_ID,
            GOAL_DATA_PROVIDER02B_WORKFLOW_ID,
            GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
            goal_data_provider02b_implemented_workflow_patch,
            locked_goal10b3_patch,
            locked_goal_data_panel02_patch,
            locked_goal_v1_diagnostic_coverage03_patch,
        )

        if GOAL_DATA_PROVIDER02B_WORKFLOW_ID in by_id:
            by_id[GOAL_DATA_PROVIDER02B_WORKFLOW_ID].update(goal_data_provider02b_implemented_workflow_patch())
        if GOAL_DATA_PANEL02_WORKFLOW_ID in by_id:
            by_id[GOAL_DATA_PANEL02_WORKFLOW_ID].update(locked_goal_data_panel02_patch())
        goal_v1_diagnostic_coverage03_valid = _goal_v1_diagnostic_coverage03_valid(root)
        if GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID in by_id and not goal_v1_diagnostic_coverage03_valid:
            by_id[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID].update(locked_goal_v1_diagnostic_coverage03_patch())
        if GOAL10B3_WORKFLOW_ID in by_id and not _goal10b3_valid(root):
            by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_patch())
        for workflow_id in [
            "goal10d_backtest_failure_attribution_gate",
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_data_provider02b"
    if _goal_v1_diagnostic_coverage03_valid(root):
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
            GOAL10B3_WORKFLOW_ID,
            GOAL10D_WORKFLOW_ID,
            WORKFLOW_ID as GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID,
            goal_v1_diagnostic_coverage03_implemented_workflow_patch,
            locked_goal10b3_patch,
        )

        if GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID in by_id:
            by_id[GOAL_V1_DIAGNOSTIC_COVERAGE03_WORKFLOW_ID].update(goal_v1_diagnostic_coverage03_implemented_workflow_patch())
        if GOAL10B3_WORKFLOW_ID in by_id and not _goal10b3_valid(root):
            by_id[GOAL10B3_WORKFLOW_ID].update(locked_goal10b3_patch())
        for workflow_id in [
            GOAL10D_WORKFLOW_ID,
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_v1_diagnostic_coverage03"
    if _goal10b3_valid(root):
        from ashare_premarket.backtest.goal10b3 import (
            GOAL10D_WORKFLOW_ID,
            WORKFLOW_ID as GOAL10B3_WORKFLOW_ID,
            goal10b3_implemented_workflow_patch,
            locked_goal10d_patch as locked_goal10d_after_goal10b3_patch,
        )

        if GOAL10B3_WORKFLOW_ID in by_id:
            by_id[GOAL10B3_WORKFLOW_ID].update(goal10b3_implemented_workflow_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_after_goal10b3_patch())
        for workflow_id in [
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal10b3"
    if _goal_risk_tiering01_valid(root):
        from ashare_premarket.risk_tiering.goal_risk_tiering01 import (
            GOAL10B4_WORKFLOW_ID,
            GOAL10D_WORKFLOW_ID,
            GOAL_REC_TIERING01_WORKFLOW_ID,
            POSITION_BAND_VALIDATION_WORKFLOW_ID,
            WORKFLOW_ID as GOAL_RISK_TIERING01_WORKFLOW_ID,
            goal_risk_tiering01_implemented_workflow_patch,
            locked_goal10b4_patch,
            locked_goal10d_patch as locked_goal10d_after_goal_risk_tiering01_patch,
            locked_goal_rec_tiering01_patch,
            locked_position_band_validation_patch,
        )

        if GOAL_RISK_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_RISK_TIERING01_WORKFLOW_ID].update(goal_risk_tiering01_implemented_workflow_patch())
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
        if GOAL10B4_WORKFLOW_ID in by_id:
            by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
        if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
            by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_after_goal_risk_tiering01_patch())
        for workflow_id in [
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_risk_tiering01"
    if _goal_risk_tiering011_valid(root):
        from ashare_premarket.risk_tiering.goal_risk_tiering011 import (
            GOAL10B4_WORKFLOW_ID,
            GOAL10D_WORKFLOW_ID,
            GOAL_REC_TIERING01_WORKFLOW_ID,
            POSITION_BAND_VALIDATION_WORKFLOW_ID,
            WORKFLOW_ID as GOAL_RISK_TIERING011_WORKFLOW_ID,
            goal_risk_tiering011_implemented_workflow_patch,
            locked_goal10b4_patch,
            locked_goal10d_patch as locked_goal10d_after_goal_risk_tiering011_patch,
            locked_goal_rec_tiering01_patch,
            locked_position_band_validation_patch,
        )

        if GOAL_RISK_TIERING011_WORKFLOW_ID in by_id:
            by_id[GOAL_RISK_TIERING011_WORKFLOW_ID].update(goal_risk_tiering011_implemented_workflow_patch())
        if GOAL_REC_TIERING01_WORKFLOW_ID in by_id:
            by_id[GOAL_REC_TIERING01_WORKFLOW_ID].update(locked_goal_rec_tiering01_patch())
        if GOAL10B4_WORKFLOW_ID in by_id:
            by_id[GOAL10B4_WORKFLOW_ID].update(locked_goal10b4_patch())
        if POSITION_BAND_VALIDATION_WORKFLOW_ID in by_id:
            by_id[POSITION_BAND_VALIDATION_WORKFLOW_ID].update(locked_position_band_validation_patch())
        if GOAL10D_WORKFLOW_ID in by_id:
            by_id[GOAL10D_WORKFLOW_ID].update(locked_goal10d_after_goal_risk_tiering011_patch())
        for workflow_id in [
            "dashboard_daily_report",
            "signal_backtest",
            "portfolio_backtest",
            "cost_slippage_sensitivity",
            "paper_trading_journal",
            "failure_attribution",
            "production_hardening",
            "broker_live_trading",
            "production_db_writes",
            "production_model_promotion",
        ]:
            if workflow_id in by_id:
                by_id[workflow_id]["status"] = "locked_future"
                by_id[workflow_id]["implemented_in_repo"] = "false"
        if "dashboard_daily_report" in by_id:
            by_id["dashboard_daily_report"]["allowed_next_action"] = "remain_locked_not_unlocked_by_goal_risk_tiering011"


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
        if payload.get("position_band_recommendation") != "implemented_review_only":
            payload["position_band_recommendation"] = goal09_eligible_workflow_patch(root)["status"]
    if _goal09_valid(root):
        payload["position_band_recommendation"] = "implemented_review_only"
    if _goal091_valid(root):
        payload["goal091_position_band_warning_dashboard_readiness_gate"] = "implemented_review_only"
    if _goal_v1_integrity01_valid(root):
        payload["goal_v1_integrity01_artifact_lineage_structure_gate"] = "implemented_infrastructure_only"
    if _goal10a_valid(root):
        payload["goal10a_backtest_contract_design_gate"] = "implemented_design_only"
    if _goal10b_valid(root):
        payload["goal10b_backtest_review_only_validation_gate"] = "implemented_review_only"
    if _goal10b1_valid(root):
        payload["goal10b1_backtest_coverage_repair_gate"] = "implemented_review_only"
        if payload.get("goal10c_backtest_cost_slippage_sensitivity_gate") != "implemented_review_only":
            payload["goal10c_backtest_cost_slippage_sensitivity_gate"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_data_label01_valid(root):
        payload["goal_data_label01_forward_return_label_coverage_expansion"] = "implemented_review_only"
        if payload.get("goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion") != "implemented_review_only":
            payload["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"] = False
        if payload.get("goal10b2_recommendation_backtest_revalidation") != "implemented_review_only":
            payload["goal10b2_recommendation_backtest_revalidation"] = False
        if payload.get("goal10c_backtest_cost_slippage_sensitivity_gate") != "implemented_review_only":
            payload["goal10c_backtest_cost_slippage_sensitivity_gate"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_v1_diagnostic_coverage02_valid(root):
        payload["goal_v1_diagnostic_coverage02_multi_symbol_diagnostics_expansion"] = "implemented_review_only"
        if payload.get("goal10b2_recommendation_backtest_revalidation") != "implemented_review_only":
            payload["goal10b2_recommendation_backtest_revalidation"] = False
        if payload.get("goal10c_backtest_cost_slippage_sensitivity_gate") != "implemented_review_only":
            payload["goal10c_backtest_cost_slippage_sensitivity_gate"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal10b2_valid(root):
        payload["goal10b2_recommendation_backtest_revalidation"] = "implemented_review_only"
        if payload.get("goal10c_backtest_cost_slippage_sensitivity_gate") != "implemented_review_only":
            payload["goal10c_backtest_cost_slippage_sensitivity_gate"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal10c_valid(root):
        payload["goal10c_backtest_cost_slippage_sensitivity_gate"] = "implemented_review_only"
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_data_provider02a_valid(root):
        payload["goal_data_provider02a_multi_provider_capability_probe"] = "implemented_review_only"
        if not _goal_data_provider02b_valid(root):
            payload["goal_data_provider02b_provider_selection_gate"] = False
        payload["goal_data_panel02_evaluation_panel_gate"] = False
        if not _goal_v1_diagnostic_coverage03_valid(root):
            payload["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"] = False
        if not _goal10b3_valid(root):
            payload["goal10b3_recommendation_backtest_revalidation"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_data_provider02a1_valid(root):
        payload["goal_data_provider02a1_network_opt_in_provider_smoke_test"] = "implemented_review_only"
        if not _goal_data_provider02b_valid(root):
            payload["goal_data_provider02b_provider_selection_gate"] = False
        payload["goal_data_panel02_evaluation_panel_gate"] = False
        if not _goal_v1_diagnostic_coverage03_valid(root):
            payload["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"] = False
        if not _goal10b3_valid(root):
            payload["goal10b3_recommendation_backtest_revalidation"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_data_provider02b_valid(root):
        payload["goal_data_provider02b_provider_selection_gate"] = "implemented_review_only"
        payload["goal_data_panel02_evaluation_panel_gate"] = False
        if not _goal_v1_diagnostic_coverage03_valid(root):
            payload["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"] = False
        if not _goal10b3_valid(root):
            payload["goal10b3_recommendation_backtest_revalidation"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_v1_diagnostic_coverage03_valid(root):
        payload["goal_v1_diagnostic_coverage03_multi_provider_diagnostics"] = "implemented_review_only"
        if not _goal10b3_valid(root):
            payload["goal10b3_recommendation_backtest_revalidation"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal10b3_valid(root):
        payload["goal10b3_recommendation_backtest_revalidation"] = "implemented_review_only"
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_risk_tiering01_valid(root):
        payload["goal_risk_tiering01_risk_severity_numeric_score_gate"] = "implemented_review_only"
        payload["goal_rec_tiering01_recommendation_score_tiering_gate"] = False
        payload["goal10b4_recommendation_backtest_revalidation"] = False
        payload["goal_position_band_validation01_position_band_validation_gate"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False
    if _goal_risk_tiering011_valid(root):
        payload["goal_risk_tiering011_downside_risk_repair_gate"] = "implemented_review_only"
        payload["goal_rec_tiering01_recommendation_score_tiering_gate"] = False
        payload["goal10b4_recommendation_backtest_revalidation"] = False
        payload["goal_position_band_validation01_position_band_validation_gate"] = False
        payload["goal10d_backtest_failure_attribution_gate"] = False


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


def _goal09_valid(root: Path) -> bool:
    try:
        from ashare_premarket.review_diagnostics.goal09 import goal09_valid_position_band_diagnostics_evidence

        return goal09_valid_position_band_diagnostics_evidence(root)
    except Exception:
        return False


def _goal091_valid(root: Path) -> bool:
    try:
        from ashare_premarket.contract_design.goal091 import goal091_valid_dashboard_readiness_evidence

        return goal091_valid_dashboard_readiness_evidence(root)
    except Exception:
        return False


def _goal_v1_integrity01_valid(root: Path) -> bool:
    try:
        from ashare_premarket.validation.goal_v1_integrity01 import goal_v1_integrity01_valid_evidence

        return goal_v1_integrity01_valid_evidence(root)
    except Exception:
        return False


def _goal10a_valid(root: Path) -> bool:
    try:
        from ashare_premarket.contract_design.goal10a import goal10a_valid_design_evidence

        return goal10a_valid_design_evidence(root)
    except Exception:
        return False


def _goal10b_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10b import goal10b_valid_review_only_evidence

        return goal10b_valid_review_only_evidence(root)
    except Exception:
        return False


def _goal10b1_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10b1 import goal10b1_valid_coverage_repair_evidence

        return goal10b1_valid_coverage_repair_evidence(root)
    except Exception:
        return False


def _goal_data_label01_valid(root: Path) -> bool:
    try:
        from ashare_premarket.labels.goal_data_label01 import goal_data_label01_valid_forward_return_label_coverage_evidence

        return goal_data_label01_valid_forward_return_label_coverage_evidence(root)
    except Exception:
        return False


def _goal_v1_diagnostic_coverage02_valid(root: Path) -> bool:
    try:
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage02 import (
            goal_v1_diagnostic_coverage02_valid_multi_symbol_diagnostic_evidence,
        )

        return goal_v1_diagnostic_coverage02_valid_multi_symbol_diagnostic_evidence(root)
    except Exception:
        return False


def _goal10b2_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10b2 import goal10b2_valid_revalidation_evidence

        return goal10b2_valid_revalidation_evidence(root)
    except Exception:
        return False


def _goal10c_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10c import goal10c_valid_cost_slippage_evidence

        return goal10c_valid_cost_slippage_evidence(root)
    except Exception:
        return False


def _goal_data_provider02a_valid(root: Path) -> bool:
    try:
        from ashare_premarket.providers.goal_data_provider02a import goal_data_provider02a_valid_capability_probe_evidence

        return goal_data_provider02a_valid_capability_probe_evidence(root)
    except Exception:
        return False


def _goal_data_provider02a1_valid(root: Path) -> bool:
    try:
        from ashare_premarket.providers.goal_data_provider02a1 import goal_data_provider02a1_valid_network_smoke_test_evidence

        return goal_data_provider02a1_valid_network_smoke_test_evidence(root)
    except Exception:
        return False


def _goal_data_provider02b_valid(root: Path) -> bool:
    try:
        from ashare_premarket.providers.goal_data_provider02b import goal_data_provider02b_valid_source_backed_panel_evidence

        return goal_data_provider02b_valid_source_backed_panel_evidence(root)
    except Exception:
        return False


def _goal_v1_diagnostic_coverage03_valid(root: Path) -> bool:
    try:
        from ashare_premarket.diagnostics.goal_v1_diagnostic_coverage03 import (
            goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence,
        )

        return goal_v1_diagnostic_coverage03_valid_source_backed_diagnostics_evidence(root)
    except Exception:
        return False


def _goal10b3_valid(root: Path) -> bool:
    try:
        from ashare_premarket.backtest.goal10b3 import goal10b3_valid_dc03_revalidation_evidence

        return goal10b3_valid_dc03_revalidation_evidence(root)
    except Exception:
        return False


def _goal_risk_tiering01_valid(root: Path) -> bool:
    try:
        from ashare_premarket.risk_tiering.goal_risk_tiering01 import goal_risk_tiering01_valid_evidence

        return goal_risk_tiering01_valid_evidence(root)
    except Exception:
        return False


def _goal_risk_tiering011_valid(root: Path) -> bool:
    try:
        from ashare_premarket.risk_tiering.goal_risk_tiering011 import goal_risk_tiering011_valid_evidence

        return goal_risk_tiering011_valid_evidence(root)
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
