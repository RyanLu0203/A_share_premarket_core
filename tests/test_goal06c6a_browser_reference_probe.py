from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv
from ashare_premarket.providers.browser_reference_probe import run_browser_reference_probe


def _event() -> dict[str, str]:
    return {
        "event_id": "evt-1",
        "provider_id": "akshare",
        "function_name": "stock_zh_a_spot_em",
        "target_domain": "82.push2.eastmoney.com",
        "status": "FAIL",
        "primary_failure_class": "FINANCE_DIRECT_CHILD_ENV_CLEANED_BUT_PROVIDER_STILL_PROXY_FAILED",
        "failure_layer": "network_transport",
    }


def test_default_probe_tags_policy_disabled(tmp_path: Path) -> None:
    audit_dir = tmp_path / "outputs/audits"
    audit_dir.mkdir(parents=True)
    from ashare_premarket.core.io import write_csv

    write_csv(audit_dir / "provider_failure_events.csv", [_event()])
    assert run_browser_reference_probe(tmp_path)
    tags = read_csv(audit_dir / "cloakbrowser_reference_problem_tags.csv")
    assert tags[0]["cloakbrowser_reference_tag"] == "CLOAKBROWSER_REFERENCE_NOT_ATTEMPTED_POLICY_DISABLED"
    assert tags[0]["ingestion_solved_by_reference"] == "false"


def test_mocked_domain_success_is_not_ingestion_success(tmp_path: Path) -> None:
    audit_dir = tmp_path / "outputs/audits"
    audit_dir.mkdir(parents=True)
    from ashare_premarket.core.io import write_csv

    write_csv(audit_dir / "provider_failure_events.csv", [_event()])

    def runner(event: dict[str, str], target_url: str) -> dict[str, object]:
        return {
            "status": "PASS",
            "http_status_if_available": 200,
            "content_type_if_available": "text/html",
            "page_title_available": "Eastmoney",
            "structured_data_evidence": "",
            "safe_notes": "HTTP 200; landing page only",
        }

    import ashare_premarket.providers.browser_reference_probe as probe_module

    original = probe_module._dependency_status
    probe_module._dependency_status = lambda: probe_module.DependencyStatus("AVAILABLE", ())
    try:
        assert run_browser_reference_probe(tmp_path, allow_network=True, use_browser=True, probe_runner=runner)
    finally:
        probe_module._dependency_status = original
    tags = read_csv(audit_dir / "cloakbrowser_reference_problem_tags.csv")
    assert tags[0]["cloakbrowser_reference_tag"] == "SOLVED_BY_CLOAKBROWSER_REFERENCE_DOMAIN_ACCESS_ONLY"
    assert tags[0]["domain_access_solved_by_reference"] == "true"
    assert tags[0]["ingestion_solved_by_reference"] == "false"


def test_mocked_json_payload_is_ingestion_success(tmp_path: Path) -> None:
    audit_dir = tmp_path / "outputs/audits"
    audit_dir.mkdir(parents=True)
    from ashare_premarket.core.io import write_csv

    write_csv(audit_dir / "provider_failure_events.csv", [_event()])

    def runner(event: dict[str, str], target_url: str) -> dict[str, object]:
        return {
            "status": "PASS",
            "http_status_if_available": 200,
            "content_type_if_available": "application/json",
            "page_title_available": "",
            "structured_data_evidence": "JSON_PAYLOAD_DETECTED",
            "safe_notes": "HTTP 200; structured payload detected",
        }

    import ashare_premarket.providers.browser_reference_probe as probe_module

    original = probe_module._dependency_status
    probe_module._dependency_status = lambda: probe_module.DependencyStatus("AVAILABLE", ())
    try:
        assert run_browser_reference_probe(tmp_path, allow_network=True, use_browser=True, probe_runner=runner)
    finally:
        probe_module._dependency_status = original
    tags = read_csv(audit_dir / "cloakbrowser_reference_problem_tags.csv")
    assert tags[0]["cloakbrowser_reference_tag"] == "SOLVED_BY_CLOAKBROWSER_REFERENCE_INGESTION"
    assert tags[0]["ingestion_solved_by_reference"] == "true"


def test_dependency_missing_is_precise_not_generic(tmp_path: Path) -> None:
    audit_dir = tmp_path / "outputs/audits"
    audit_dir.mkdir(parents=True)
    from ashare_premarket.core.io import write_csv

    write_csv(audit_dir / "provider_failure_events.csv", [_event()])
    assert run_browser_reference_probe(tmp_path, allow_network=True, use_browser=True)
    tags = read_csv(audit_dir / "cloakbrowser_reference_problem_tags.csv")
    assert tags
    if tags[0]["browser_dependency_status"] == "MISSING":
        assert tags[0]["cloakbrowser_reference_tag"] == "CLOAKBROWSER_REFERENCE_NOT_ATTEMPTED_DEPENDENCY_MISSING"
        assert tags[0]["remaining_failure_class"] == "OPTIONAL_DEPENDENCY_MISSING"
