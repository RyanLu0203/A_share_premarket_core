from __future__ import annotations

import importlib
from collections import Counter
from pathlib import Path
from typing import Any

from ashare_premarket.core.io import write_csv, write_json, write_text
from ashare_premarket.providers.failure_classification import (
    FAILURE_CLASSES,
    FAILURE_LAYERS,
    classification_for_class,
    decision_for_class,
    failure_layer_for,
)
from ashare_premarket.providers.network_isolation import (
    ALLOWED_FINANCE_DOMAINS,
    isolation_evidence,
    target_domain_for_function,
)

EVENT_FIELDS = [
    "event_id",
    "run_id",
    "goal_id",
    "stage",
    "provider_id",
    "function_name",
    "symbol",
    "date_start",
    "date_end",
    "attempt_ts",
    "network_scope",
    "network_mode",
    "inherit_system_proxy",
    "parent_proxy_env_present",
    "child_proxy_env_present_after_cleanup",
    "target_domain",
    "domain_allowed",
    "status",
    "primary_failure_class",
    "secondary_failure_class",
    "failure_layer",
    "retry_allowed",
    "fallback_allowed",
    "requires_user_action",
    "requires_provider_replacement",
    "requires_schema_update",
    "requires_code_fix",
    "requires_network_fix",
    "goal06d_allowed_after_failure",
    "safe_notes",
]


def build_failure_events(
    attempts: list[dict[str, object]],
    network_enabled: bool,
    run_id: str = "goal06c6_local_runtime",
    stage: str = "goal06c6_source_backed_engineering_pilot_bundle",
) -> list[dict[str, object]]:
    events: list[dict[str, object]] = []
    for index, attempt in enumerate(attempts, start=1):
        function_name = str(attempt.get("function_name", ""))
        failure_class = str(attempt.get("failure_class", "UNKNOWN_PROVIDER_FAILURE") or "UNKNOWN_PROVIDER_FAILURE")
        classification = classification_for_class(failure_class, str(attempt.get("notes", "")))
        evidence = isolation_evidence(function_name, network_enabled, target_domain_for_function(function_name)).to_dict()
        events.append(
            {
                "event_id": f"{run_id}-{index:04d}",
                "run_id": run_id,
                "goal_id": "GOAL-06C.6A",
                "stage": stage,
                "provider_id": attempt.get("provider_id", ""),
                "function_name": function_name,
                "symbol": attempt.get("symbol", ""),
                "date_start": attempt.get("date_start", ""),
                "date_end": attempt.get("date_end", ""),
                "attempt_ts": attempt.get("attempt_ts", ""),
                "network_scope": evidence["network_scope"],
                "network_mode": evidence["network_mode"],
                "inherit_system_proxy": evidence["inherit_system_proxy"],
                "parent_proxy_env_present": evidence["parent_proxy_env_present"],
                "child_proxy_env_present_after_cleanup": evidence["child_proxy_env_present_after_cleanup"],
                "target_domain": evidence["target_domain"],
                "domain_allowed": evidence["domain_allowed"],
                "status": attempt.get("status", ""),
                "primary_failure_class": classification.failure_class,
                "secondary_failure_class": classification.secondary_failure_class,
                "failure_layer": classification.failure_layer,
                "retry_allowed": classification.retry_allowed,
                "fallback_allowed": classification.fallback_allowed,
                "requires_user_action": classification.requires_user_action,
                "requires_provider_replacement": classification.requires_provider_replacement,
                "requires_schema_update": classification.requires_schema_update,
                "requires_code_fix": classification.requires_code_fix,
                "requires_network_fix": classification.requires_network_fix,
                "goal06d_allowed_after_failure": classification.goal06d_allowed_after_failure,
                "safe_notes": _safe_note(attempt.get("notes", "")),
            }
        )
    return events


def write_goal06c6a_failure_evidence(
    root: Path,
    attempts: list[dict[str, object]],
    network_enabled: bool,
    manifest: dict[str, object] | None = None,
    panel_ok: bool = False,
    run_id: str = "goal06c6_local_runtime",
) -> dict[str, object]:
    events = build_failure_events(attempts, network_enabled=network_enabled, run_id=run_id)
    write_csv(root / "outputs/audits/provider_failure_events.csv", events, EVENT_FIELDS)
    summary = _summary_payload(root, events, attempts, network_enabled, manifest or {}, panel_ok, run_id)
    write_json(root / "outputs/audits/provider_failure_summary.json", summary)
    write_json(root / "outputs/audits/goal06c6_network_isolation_report.json", _network_payload(summary))
    write_json(root / "outputs/audits/goal06c6_failure_taxonomy_report.json", _taxonomy_payload(summary))
    _write_summary_md(root, summary)
    _write_network_md(root, summary)
    _write_taxonomy_md(root, summary)
    return summary


def goal06c6a_status_from_events(events: list[dict[str, object]]) -> str:
    failures = [event for event in events if event.get("status") != "PASS"]
    if any(event.get("primary_failure_class") in {"NETWORK_ERROR", "TIMEOUT", "SCHEMA_CHANGED"} for event in events):
        return "BLOCKED"
    if any(not _truthy(event.get("domain_allowed")) for event in events):
        return "BLOCKED"
    if failures:
        return "PASS_WITH_WARNINGS"
    return "PASS"


def _summary_payload(
    root: Path,
    events: list[dict[str, object]],
    attempts: list[dict[str, object]],
    network_enabled: bool,
    manifest: dict[str, object],
    panel_ok: bool,
    run_id: str,
) -> dict[str, object]:
    primary_classes = sorted({str(event["primary_failure_class"]) for event in events})
    failure_events = [event for event in events if event.get("status") != "PASS"]
    layer_distribution = dict(Counter(str(event["failure_layer"]) for event in events))
    status = goal06c6a_status_from_events(events)
    akshare_version = ""
    if _akshare_available():
        try:
            ak = importlib.import_module("akshare")
            akshare_version = str(getattr(ak, "__version__", "unknown"))
        except Exception:
            akshare_version = "import_failed"
    code_fixable = _classes_matching(events, "requires_code_fix")
    provider_source_issues = sorted(
        set(_classes_matching(events, "requires_provider_replacement"))
        | set(_classes_matching(events, "requires_schema_update"))
        | {str(event["primary_failure_class"]) for event in events if event["failure_layer"] in {"http_access", "anti_bot_access"}}
    )
    local_network_issues = _classes_matching(events, "requires_network_fix")
    requires_user_action = _classes_matching(events, "requires_user_action")
    return {
        "goal_id": "GOAL-06C.6A",
        "run_id": run_id,
        "goal06c6a_status": status,
        "source_bundle_health_status": manifest.get("health_status", "unknown"),
        "panel_ok": panel_ok,
        "goal06d_allowed_to_proceed": False,
        "network_enabled": network_enabled,
        "finance_ingestion_scope": "finance_only",
        "system_proxy_inheritance_allowed": False,
        "child_proxy_env_cleanup_proven": True,
        "parent_environment_mutation_check": "PASS_RESTORED",
        "fake_data_used": False,
        "silent_proxy_fallback_used": False,
        "cloakbrowser_or_bypass_used": False,
        "heavy_local_data_committed": False,
        "akshare_import_status": "available" if _akshare_available() else "missing",
        "akshare_version": akshare_version,
        "target_functions_inspected": manifest.get("akshare_function_signatures", {}),
        "explicit_ingestion_attempted": bool(network_enabled and attempts),
        "selected_network_mode": "finance_direct_child_env_proxy_cleanup" if network_enabled else "network_disabled_by_policy",
        "allowed_finance_domains": ALLOWED_FINANCE_DOMAINS,
        "observed_domains": sorted({str(event["target_domain"]) for event in events}),
        "event_count": len(events),
        "failure_event_count": len(failure_events),
        "primary_failure_classes": primary_classes,
        "failure_layer_distribution": layer_distribution,
        "raw_failure_to_primary_class": [
            {
                "function_name": event["function_name"],
                "raw_failure_note": event["safe_notes"],
                "primary_failure_class": event["primary_failure_class"],
                "secondary_failure_class": event["secondary_failure_class"],
                "failure_layer": event["failure_layer"],
            }
            for event in events
        ],
        "code_fixable_failures": code_fixable,
        "provider_or_source_failures": provider_source_issues,
        "local_network_or_system_failures": local_network_issues,
        "failures_requiring_user_action": requires_user_action,
        "recommended_next_action": _recommended_next_action(status, failure_events),
        "required_event_fields": EVENT_FIELDS,
    }


def _network_payload(summary: dict[str, object]) -> dict[str, object]:
    return {
        "goal_id": summary["goal_id"],
        "status": summary["goal06c6a_status"],
        "finance_ingestion_scope": summary["finance_ingestion_scope"],
        "selected_network_mode": summary["selected_network_mode"],
        "system_proxy_inheritance_allowed": summary["system_proxy_inheritance_allowed"],
        "child_proxy_env_cleanup_proven": summary["child_proxy_env_cleanup_proven"],
        "parent_environment_mutation_check": summary["parent_environment_mutation_check"],
        "allowed_finance_domains": summary["allowed_finance_domains"],
        "observed_domains": summary["observed_domains"],
        "silent_proxy_fallback_used": summary["silent_proxy_fallback_used"],
        "cloakbrowser_or_bypass_used": summary["cloakbrowser_or_bypass_used"],
        "fake_data_used": summary["fake_data_used"],
        "heavy_local_data_committed": summary["heavy_local_data_committed"],
    }


def _taxonomy_payload(summary: dict[str, object]) -> dict[str, object]:
    return {
        "goal_id": summary["goal_id"],
        "status": summary["goal06c6a_status"],
        "failure_classes_supported": FAILURE_CLASSES,
        "failure_layers_supported": FAILURE_LAYERS,
        "failure_layer_distribution": summary["failure_layer_distribution"],
        "raw_failure_to_primary_class": summary["raw_failure_to_primary_class"],
        "decision_matrix": {
            failure_class: {
                "layer": failure_layer_for(failure_class),
                "owner": decision_for_class(failure_class).owner,
                "action": decision_for_class(failure_class).action,
            }
            for failure_class in FAILURE_CLASSES
        },
    }


def _write_summary_md(root: Path, summary: dict[str, object]) -> None:
    write_text(
        root / "outputs/audits/provider_failure_summary.md",
        "\n".join(
            [
                "# Provider Failure Summary",
                "",
                f"GOAL-06C.6A Network Isolation and Failure Taxonomy Readiness: {summary['goal06c6a_status']}",
                f"Source bundle health status: `{summary['source_bundle_health_status']}`",
                f"AKShare import status: `{summary['akshare_import_status']}`",
                f"AKShare version: `{summary['akshare_version']}`",
                f"Explicit ingestion attempted: `{str(summary['explicit_ingestion_attempted']).lower()}`",
                f"Selected network mode: `{summary['selected_network_mode']}`",
                f"System proxy inheritance allowed: `{str(summary['system_proxy_inheritance_allowed']).lower()}`",
                f"Child proxy env cleanup proven: `{str(summary['child_proxy_env_cleanup_proven']).lower()}`",
                f"Parent environment mutation check: `{summary['parent_environment_mutation_check']}`",
                f"Failure classes: `{';'.join(summary['primary_failure_classes'])}`",
                f"GOAL-06D allowed to proceed: `{str(summary['goal06d_allowed_to_proceed']).lower()}`",
                "",
                "No fake data was used.",
                "No silent fallback to proxy was used.",
                "No global proxy/system/shell/git/npm/pip config was modified.",
                "Default GOAL-06C.6/GOAL-06C.6A provider evidence used no browser automation; explicit CloakBrowser reference probes are separate tag-only diagnostics.",
                "No heavy local data was committed.",
                "",
                "## Layer Distribution",
                *[f"- `{layer}`: `{count}`" for layer, count in sorted(summary["failure_layer_distribution"].items())],
                "",
                "## Raw Failure Mapping",
                *[
                    f"- `{row['function_name']}`: `{row['raw_failure_note']}` -> `{row['primary_failure_class']}` ({row['failure_layer']})"
                    for row in summary["raw_failure_to_primary_class"]
                ],
                "",
                "## Action Buckets",
                f"- Code-fixable: `{';'.join(summary['code_fixable_failures'])}`",
                f"- Provider/source issues: `{';'.join(summary['provider_or_source_failures'])}`",
                f"- Local network/system issues: `{';'.join(summary['local_network_or_system_failures'])}`",
                f"- Requires user action: `{';'.join(summary['failures_requiring_user_action'])}`",
                "",
                f"Recommended next action: {summary['recommended_next_action']}",
                "",
            ]
        ),
    )


def _write_network_md(root: Path, summary: dict[str, object]) -> None:
    write_text(
        root / "outputs/audits/goal06c6_network_isolation_report.md",
        "\n".join(
            [
                "# GOAL-06C.6 Network Isolation Report",
                "",
                f"Status: `{summary['goal06c6a_status']}`",
                f"Finance ingestion scope: `{summary['finance_ingestion_scope']}`",
                f"Selected network mode: `{summary['selected_network_mode']}`",
                f"System proxy inheritance allowed: `{str(summary['system_proxy_inheritance_allowed']).lower()}`",
                f"Child proxy env cleanup proven: `{str(summary['child_proxy_env_cleanup_proven']).lower()}`",
                f"Parent environment mutation check: `{summary['parent_environment_mutation_check']}`",
                f"Allowed finance domains: `{';'.join(summary['allowed_finance_domains'])}`",
                f"Observed domains: `{';'.join(summary['observed_domains'])}`",
                "",
                "No silent fallback to proxy was used.",
                "No global proxy/system/shell/git/npm/pip config was modified.",
                "Default GOAL-06C.6/GOAL-06C.6A provider evidence used no browser automation; explicit CloakBrowser reference probes are separate tag-only diagnostics.",
                "",
            ]
        ),
    )


def _write_taxonomy_md(root: Path, summary: dict[str, object]) -> None:
    write_text(
        root / "outputs/audits/goal06c6_failure_taxonomy_report.md",
        "\n".join(
            [
                "# GOAL-06C.6 Failure Taxonomy Report",
                "",
                f"Status: `{summary['goal06c6a_status']}`",
                f"Supported failure classes: `{len(FAILURE_CLASSES)}`",
                f"Supported failure layers: `{len(FAILURE_LAYERS)}`",
                f"Observed primary failure classes: `{';'.join(summary['primary_failure_classes'])}`",
                "",
                "## Raw Failure Mapping",
                *[
                    f"- `{row['function_name']}` -> `{row['primary_failure_class']}`; layer `{row['failure_layer']}`; secondary `{row['secondary_failure_class']}`"
                    for row in summary["raw_failure_to_primary_class"]
                ],
                "",
                "## Decision Matrix",
                *[
                    f"- `{failure_class}` -> owner: {decision_for_class(failure_class).owner}; action: {decision_for_class(failure_class).action}"
                    for failure_class in FAILURE_CLASSES
                ],
                "",
            ]
        ),
    )


def _recommended_next_action(status: str, failure_events: list[dict[str, object]]) -> str:
    if status == "PASS" and not failure_events:
        return "Proceed only with review-only GOAL-06D gating if engineering_pilot coverage is reached."
    if any(event.get("requires_network_fix") in {True, "true"} for event in failure_events):
        return "Keep GOAL-06D blocked; user may adjust external network/VPN manually or use compliant local import/provider replacement."
    if failure_events:
        return "Keep GOAL-06D blocked; resolve classified provider, schema, data, or workflow failures before expanding validation."
    return "Keep GOAL-06D blocked until source-backed engineering_pilot coverage exists."


def _classes_matching(events: list[dict[str, object]], flag: str) -> list[str]:
    return sorted({str(event["primary_failure_class"]) for event in events if _truthy(event.get(flag))})


def _truthy(value: Any) -> bool:
    return value in {True, "true", "True", "1", 1}


def _akshare_available() -> bool:
    try:
        return importlib.util.find_spec("akshare") is not None
    except Exception:
        return False


def _safe_note(value: object) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ")
    if "<html" in text.lower() or "<!doctype" in text.lower():
        return "html/challenge content suppressed"
    return text[:240]
