from __future__ import annotations

ALLOWED_PRIORITY_BANDS = {"P0_market_regime_core", "P1_symbol_context_and_event"}
ALLOWED_APPROVED_USAGE = {
    "approved_for_regime_label",
    "approved_for_symbol_diagnostics",
    "approved_for_research_context",
    "approved_for_provider_health_only",
}

BLOCKED_APPROVED_USAGE = {
    "blocked",
    "future_review_only",
    "experimental_requires_review",
}


def is_goal_data_expansion_source(row: dict[str, str]) -> bool:
    return row.get("priority_band") in ALLOWED_PRIORITY_BANDS and row.get("approved_usage") in ALLOWED_APPROVED_USAGE


def selection_reason(row: dict[str, str]) -> str:
    usage = row.get("approved_usage", "")
    if usage == "approved_for_regime_label":
        return "approved_p0_p1_regime_label_context"
    if usage == "approved_for_symbol_diagnostics":
        return "approved_p0_p1_symbol_context"
    if usage == "approved_for_provider_health_only":
        return "provider_health_only_no_research_values_committed"
    return "approved_p0_p1_research_context"


def expected_commit_policy(row: dict[str, str]) -> str:
    policy = row.get("commit_policy", "")
    if "raw" in policy.lower():
        return "metadata_or_bounded_normalized_only_raw_payload_forbidden"
    return policy or "bounded_normalized_or_summary_only"


def select_market_regime_sources(catalog_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for row in catalog_rows:
        selected_for_goal = is_goal_data_expansion_source(row)
        selected.append(
            {
                "source_id": row.get("source_id", ""),
                "akshare_category": row.get("akshare_category", ""),
                "akshare_subcategory": row.get("akshare_subcategory", ""),
                "akshare_function_name_if_known": row.get("akshare_function_name_if_known", ""),
                "priority_band": row.get("priority_band", ""),
                "approved_usage": row.get("approved_usage", ""),
                "selected_for_goal": "true" if selected_for_goal else "false",
                "selection_reason": selection_reason(row) if selected_for_goal else "not_selected_not_approved_p0_p1_scope",
                "fetch_mode": "committed_evidence_replay" if selected_for_goal else "not_fetched",
                "expected_grain": row.get("expected_grain", ""),
                "expected_primary_keys": row.get("expected_primary_keys", ""),
                "pit_policy": _pit_policy(row),
                "storage_policy": row.get("storage_policy", ""),
                "commit_policy": expected_commit_policy(row),
                "provider_stability_risk": row.get("provider_stability_risk", ""),
                "lookahead_risk": row.get("lookahead_risk", ""),
                "implementation_status": "selected_for_offline_replay_or_provider_health" if selected_for_goal else "not_selected",
                "notes": row.get("notes", ""),
            }
        )
    return selected


def _pit_policy(row: dict[str, str]) -> str:
    if row.get("publication_date_required") == "true":
        return "publication_or_as_of_date_required_before_research_use"
    if row.get("expected_time_field"):
        return f"use_{row['expected_time_field']}_as_pit_available_date"
    return "pit_policy_required_before_research_use"

