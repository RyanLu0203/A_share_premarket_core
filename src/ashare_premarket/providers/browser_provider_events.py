from __future__ import annotations

from collections import Counter
from pathlib import Path

from ashare_premarket.core.io import read_json, write_csv, write_json, write_text

BROWSER_EVENT_FIELDS = [
    "run_id",
    "bundle_id",
    "provider_id",
    "provider_mode",
    "function_name",
    "data_role",
    "target_domain",
    "attempt_status",
    "raw_failure_type",
    "primary_failure_class",
    "secondary_failure_class",
    "failure_layer",
    "rows_returned",
    "schema_valid",
    "fallback_provider_used",
    "fallback_reason",
    "safe_notes",
]


def write_browser_assisted_audit(
    root: Path,
    events: list[dict[str, object]],
    summary: dict[str, object],
) -> None:
    browser_events = [row for row in events if row.get("provider_mode") == "browser_assisted_optional"]
    write_csv(root / "outputs/audits/browser_assisted_provider_events.csv", browser_events, BROWSER_EVENT_FIELDS)
    payload = {
        **summary,
        "domain_access_solved_count": _count(browser_events, "primary_failure_class", "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY"),
        "structured_ingestion_solved_count": _count(browser_events, "primary_failure_class", "BROWSER_ASSISTED_STRUCTURED_INGESTION_SOLVED"),
        "domain_access_only_count": _count(browser_events, "primary_failure_class", "BROWSER_ASSISTED_DOMAIN_ACCESS_ONLY"),
        "remaining_unsolved_count": sum(1 for row in browser_events if row.get("attempt_status") != "PASS"),
        "event_count": len(browser_events),
        "failure_class_counts": dict(Counter(str(row.get("primary_failure_class", "")) for row in browser_events)),
    }
    write_json(root / "outputs/audits/browser_assisted_provider_audit.json", payload)
    status = "PASS" if payload.get("raw_html_stored") is False and payload.get("raw_payload_stored") is False else "BLOCKED"
    write_text(
        root / "outputs/audits/browser_assisted_provider_audit.md",
        "\n".join(
            [
                "# Browser-Assisted Provider Audit",
                "",
                f"Browser-Assisted Provider Audit: {status}",
                f"Status: `{status}`",
                f"Browser assisted enabled: `{str(payload.get('browser_assisted_enabled', False)).lower()}`",
                f"Browser assisted project default: `{str(payload.get('browser_assisted_project_default', False)).lower()}`",
                f"Explicit opt-in used: `{str(payload.get('explicit_opt_in_used', False)).lower()}`",
                f"Browser dependency status: `{payload.get('browser_dependency_status', '')}`",
                f"Temporary venv used: `{str(payload.get('temporary_venv_used', False)).lower()}`",
                f"Temporary cache used: `{str(payload.get('temporary_cache_used', False)).lower()}`",
                f"Temporary cache cleaned: `{str(payload.get('temporary_cache_cleaned', True)).lower()}`",
                f"Raw HTML stored: `{str(payload.get('raw_html_stored', False)).lower()}`",
                f"Raw payload stored: `{str(payload.get('raw_payload_stored', False)).lower()}`",
                f"Cookies stored: `{str(payload.get('cookies_stored', False)).lower()}`",
                f"Session data stored: `{str(payload.get('session_data_stored', False)).lower()}`",
                f"Captcha or challenge detected: `{str(payload.get('captcha_or_challenge_detected', False)).lower()}`",
                f"Access restriction detected: `{str(payload.get('access_restriction_detected', False)).lower()}`",
                f"Domain-access solved count: `{payload.get('domain_access_solved_count', 0)}`",
                f"Structured ingestion solved count: `{payload.get('structured_ingestion_solved_count', 0)}`",
                f"Domain-access-only count: `{payload.get('domain_access_only_count', 0)}`",
                f"Remaining unsolved count: `{payload.get('remaining_unsolved_count', 0)}`",
                f"Provider-mode rows in panel: `{payload.get('provider_mode_rows_in_panel', 0)}`",
                f"GOAL-06D allowed to proceed: `{str(payload.get('goal06d_allowed_to_proceed', False)).lower()}`",
                "",
                "Raw browser artifacts are not committed.",
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/browser_assisted_provider_summary.md",
        "\n".join(
            [
                "# Browser-Assisted Provider Summary",
                "",
                f"Structured ingestion solved: `{payload.get('structured_ingestion_solved_count', 0)}`",
                f"Domain access only: `{payload.get('domain_access_only_count', 0)}`",
                f"Remaining unsolved: `{payload.get('remaining_unsolved_count', 0)}`",
                f"Project default enabled: `{str(payload.get('browser_assisted_project_default', False)).lower()}`",
                "",
            ]
        ),
    )


def audit_browser_assisted_provider(root: Path) -> bool:
    audit_path = root / "outputs/audits/browser_assisted_provider_audit.json"
    if not audit_path.exists():
        write_browser_assisted_audit(
            root,
            [],
            {
                "browser_assisted_enabled": False,
                "browser_assisted_project_default": False,
                "explicit_opt_in_used": False,
                "browser_dependency_status": "not_checked",
                "temporary_venv_used": False,
                "temporary_cache_used": False,
                "temporary_cache_cleaned": True,
                "raw_html_stored": False,
                "raw_payload_stored": False,
                "cookies_stored": False,
                "session_data_stored": False,
                "captcha_or_challenge_detected": False,
                "access_restriction_detected": False,
                "provider_mode_rows_in_panel": 0,
                "goal06d_allowed_to_proceed": False,
            },
        )
    payload = read_json(audit_path)
    failures: list[str] = []
    warnings: list[str] = []
    if payload.get("browser_assisted_project_default") is not False:
        failures.append("browser-assisted provider is enabled by default")
    if payload.get("browser_assisted_enabled") is True and payload.get("explicit_opt_in_used") is not True:
        failures.append("browser-assisted provider was enabled without explicit dual opt-in evidence")
    for field in ["raw_html_stored", "raw_payload_stored", "cookies_stored", "session_data_stored"]:
        if payload.get(field) is not False:
            failures.append(f"forbidden browser artifact storage detected: {field}")
    if payload.get("captcha_or_challenge_detected") is True and int(payload.get("structured_ingestion_solved_count", 0) or 0) > 0:
        failures.append("structured ingestion was counted after captcha/challenge detection")
    if int(payload.get("domain_access_only_count", 0) or 0) > 0:
        warnings.append("browser-assisted domain access occurred but is not counted as structured ingestion")
    if int(payload.get("provider_mode_rows_in_panel", 0) or 0) > 0 and int(payload.get("structured_ingestion_solved_count", 0) or 0) <= 0:
        failures.append("browser-assisted panel rows exist without structured ingestion success tags")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/browser_assisted_provider_audit_review.md",
        "\n".join(
            [
                "# Browser-Assisted Provider Audit Review",
                "",
                f"Browser-Assisted Provider Audit: {status}",
                "",
                f"Project default: `{str(payload.get('browser_assisted_project_default', False)).lower()}`",
                f"Enabled this run: `{str(payload.get('browser_assisted_enabled', False)).lower()}`",
                f"Explicit opt-in used: `{str(payload.get('explicit_opt_in_used', False)).lower()}`",
                f"Structured ingestion solved count: `{payload.get('structured_ingestion_solved_count', 0)}`",
                f"Domain access only count: `{payload.get('domain_access_only_count', 0)}`",
                f"Provider-mode rows in panel: `{payload.get('provider_mode_rows_in_panel', 0)}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )
    return not failures


def _count(rows: list[dict[str, object]], field: str, expected: str) -> int:
    return sum(1 for row in rows if row.get(field) == expected)
