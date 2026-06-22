from __future__ import annotations

import importlib
import importlib.util
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode, urlparse

from ashare_premarket.core.io import read_csv, write_csv, write_json, write_text
from ashare_premarket.providers.failure_classification import classify_provider_failure
from ashare_premarket.providers.network_isolation import domain_allowed, target_domain_for_function

REFERENCE_REPO = "CloakHQ/CloakBrowser"
REFERENCE_URL = "https://github.com/CloakHQ/CloakBrowser"
REFERENCE_COMMIT = "29679a73bfc64dfb6f97094615741a0ee8022a55"
REFERENCE_PATTERN = "optional_drop_in_browser_runtime_probe"

PROBLEM_TAG_FIELDS = [
    "problem_id",
    "original_event_id",
    "provider_id",
    "function_name",
    "event_target_domain",
    "reference_target_domain",
    "reference_target_url",
    "original_failure_class",
    "original_failure_layer",
    "reference_repo",
    "reference_commit",
    "reference_pattern",
    "allow_network",
    "use_browser",
    "browser_dependency_status",
    "missing_dependencies",
    "probe_attempted",
    "probe_status",
    "browser_access_status",
    "http_status_if_available",
    "content_type_if_available",
    "page_title_available",
    "structured_data_evidence",
    "domain_access_solved_by_reference",
    "ingestion_solved_by_reference",
    "problem_resolution_scope",
    "cloakbrowser_reference_tag",
    "remaining_failure_class",
    "remaining_failure_layer",
    "safe_notes",
]

PROBE_RESULT_FIELDS = [
    "probe_id",
    "problem_id",
    "provider_id",
    "function_name",
    "target_url",
    "target_domain",
    "status",
    "http_status_if_available",
    "content_type_if_available",
    "page_title_available",
    "structured_data_evidence",
    "raw_html_stored",
    "raw_payload_stored",
    "safe_notes",
]


def _url_with_query(base_url: str, params: dict[str, str]) -> str:
    return f"{base_url}?{urlencode(params)}"


FUNCTION_TARGET_URLS = {
    "index_zh_a_hist": _url_with_query(
        "https://push2his.eastmoney.com/api/qt/stock/kline/get",
        {
            "secid": "1.000300",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "0",
            "beg": "20240101",
            "end": "20241231",
        },
    ),
    "stock_zh_a_hist": _url_with_query(
        "https://push2his.eastmoney.com/api/qt/stock/kline/get",
        {
            "secid": "0.002475",
            "ut": "7eea3edcaed734bea9cbfc24409ed989",
            "fields1": "f1,f2,f3,f4,f5,f6",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
            "klt": "101",
            "fqt": "1",
            "beg": "20240101",
            "end": "20241231",
        },
    ),
    "stock_zh_a_spot_em": _url_with_query(
        "https://82.push2.eastmoney.com/api/qt/clist/get",
        {
            "pn": "1",
            "pz": "100",
            "po": "1",
            "np": "1",
            "ut": "bd1d9ddb04089700cf9c27f6f7426281",
            "fltt": "2",
            "invt": "2",
            "fid": "f12",
            "fs": "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048",
            "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152",
        },
    ),
    "stock_info_a_code_name": "https://www.bse.cn/nqxxController/nqxxCnzq.do",
}

ProbeRunner = Callable[[dict[str, str], str], dict[str, object]]


@dataclass(frozen=True)
class DependencyStatus:
    status: str
    missing: tuple[str, ...]


def run_browser_reference_probe(
    root: Path,
    allow_network: bool = False,
    use_browser: bool = False,
    probe_runner: ProbeRunner | None = None,
) -> bool:
    events_path = root / "outputs/audits/provider_failure_events.csv"
    events = read_csv(events_path) if events_path.exists() else []
    dependency = _dependency_status()
    problem_rows: list[dict[str, object]] = []
    probe_rows: list[dict[str, object]] = []

    for index, event in enumerate(events, start=1):
        target_url = _target_url_for_event(event)
        problem_id = f"cloakbrowser_reference-{index:04d}"
        target_domain = _domain_from_url(target_url)
        base = {
            "problem_id": problem_id,
            "original_event_id": event.get("event_id", ""),
            "provider_id": event.get("provider_id", ""),
            "function_name": event.get("function_name", ""),
            "event_target_domain": event.get("target_domain", ""),
            "reference_target_domain": target_domain,
            "reference_target_url": target_url,
            "original_failure_class": event.get("primary_failure_class", ""),
            "original_failure_layer": event.get("failure_layer", ""),
            "reference_repo": REFERENCE_REPO,
            "reference_commit": REFERENCE_COMMIT,
            "reference_pattern": REFERENCE_PATTERN,
            "allow_network": allow_network,
            "use_browser": use_browser,
            "browser_dependency_status": dependency.status,
            "missing_dependencies": ";".join(dependency.missing),
        }
        row, probe_row = _evaluate_problem(base, event, target_url, allow_network, use_browser, dependency, probe_runner)
        problem_rows.append(row)
        if probe_row is not None:
            probe_rows.append(probe_row)

    write_csv(root / "outputs/audits/cloakbrowser_reference_problem_tags.csv", problem_rows, PROBLEM_TAG_FIELDS)
    write_csv(root / "outputs/audits/cloakbrowser_reference_probe_results.csv", probe_rows, PROBE_RESULT_FIELDS)
    summary = _summary(problem_rows, probe_rows, dependency, allow_network, use_browser)
    write_json(root / "outputs/audits/cloakbrowser_reference_ingestion_report.json", summary)
    _write_markdown(root, summary, problem_rows)
    return True


def _evaluate_problem(
    base: dict[str, object],
    event: dict[str, str],
    target_url: str,
    allow_network: bool,
    use_browser: bool,
    dependency: DependencyStatus,
    probe_runner: ProbeRunner | None,
) -> tuple[dict[str, object], dict[str, object] | None]:
    if event.get("status") == "PASS":
        return (
            _tag_row(
                base,
                probe_attempted=False,
                probe_status="NOT_ATTEMPTED",
                browser_access_status="NOT_APPLICABLE_PROVIDER_OK",
                tag="CLOAKBROWSER_REFERENCE_NOT_APPLICABLE_PROVIDER_OK",
                remaining_failure_class="",
                remaining_failure_layer="",
                notes="Original provider event already passed.",
            ),
            None,
        )
    if event.get("failure_layer") not in {"network_transport", "http_access", "anti_bot_access"}:
        return (
            _tag_row(
                base,
                probe_attempted=False,
                probe_status="NOT_ATTEMPTED",
                browser_access_status="NOT_APPLICABLE_NON_ACCESS_FAILURE",
                tag="CLOAKBROWSER_REFERENCE_NOT_APPLICABLE_NON_ACCESS_FAILURE",
                remaining_failure_class=event.get("primary_failure_class", ""),
                remaining_failure_layer=event.get("failure_layer", ""),
                notes="Original event is not a network, HTTP access, or anti-bot access failure.",
            ),
            None,
        )
    if not domain_allowed(_domain_from_url(target_url)):
        return (
            _tag_row(
                base,
                probe_attempted=False,
                probe_status="NOT_ATTEMPTED",
                browser_access_status="NON_FINANCE_DOMAIN_BLOCKED",
                tag="CLOAKBROWSER_REFERENCE_NOT_ATTEMPTED_NON_FINANCE_DOMAIN",
                remaining_failure_class="NON_FINANCE_DOMAIN_BLOCKED",
                remaining_failure_layer="policy",
                notes="Reference target domain is outside the allowed finance-domain scope.",
            ),
            None,
        )
    if not allow_network:
        return (
            _tag_row(
                base,
                probe_attempted=False,
                probe_status="NOT_ATTEMPTED",
                browser_access_status="NETWORK_DISABLED_BY_POLICY",
                tag="CLOAKBROWSER_REFERENCE_NOT_ATTEMPTED_POLICY_DISABLED",
                remaining_failure_class=event.get("primary_failure_class", ""),
                remaining_failure_layer=event.get("failure_layer", ""),
                notes="Browser reference probe is network-disabled by default.",
            ),
            None,
        )
    if not use_browser:
        return (
            _tag_row(
                base,
                probe_attempted=False,
                probe_status="NOT_ATTEMPTED",
                browser_access_status="BROWSER_OPT_IN_MISSING",
                tag="CLOAKBROWSER_REFERENCE_NOT_ATTEMPTED_BROWSER_OPT_IN_MISSING",
                remaining_failure_class=event.get("primary_failure_class", ""),
                remaining_failure_layer=event.get("failure_layer", ""),
                notes="Pass --use-browser to attempt the optional CloakBrowser-style runtime.",
            ),
            None,
        )
    if dependency.status != "AVAILABLE":
        return (
            _tag_row(
                base,
                probe_attempted=False,
                probe_status="NOT_ATTEMPTED",
                browser_access_status="BROWSER_DEPENDENCY_MISSING",
                tag="CLOAKBROWSER_REFERENCE_NOT_ATTEMPTED_DEPENDENCY_MISSING",
                remaining_failure_class="OPTIONAL_DEPENDENCY_MISSING",
                remaining_failure_layer="dependency",
                notes="Optional browser runtime dependencies are not installed; no browser probe was launched.",
            ),
            None,
        )

    runner = probe_runner or _run_dynamic_browser_probe
    try:
        probe = runner(event, target_url)
    except Exception as exc:  # pragma: no cover - defensive browser runtime path
        runtime_class, runtime_layer = _browser_exception_class(exc)
        probe = {
            "status": "FAIL",
            "http_status_if_available": "",
            "content_type_if_available": "",
            "page_title_available": "",
            "structured_data_evidence": "",
            "safe_notes": f"browser probe exception: {type(exc).__name__}: {_safe_note(exc)}",
            "remaining_failure_class": runtime_class,
            "remaining_failure_layer": runtime_layer,
        }
    tag = _tag_from_probe(probe)
    probe_row = {
        "probe_id": f"{base['problem_id']}-probe",
        "problem_id": base["problem_id"],
        "provider_id": base["provider_id"],
        "function_name": base["function_name"],
        "target_url": target_url,
        "target_domain": base["reference_target_domain"],
        "status": probe.get("status", "FAIL"),
        "http_status_if_available": probe.get("http_status_if_available", ""),
        "content_type_if_available": probe.get("content_type_if_available", ""),
        "page_title_available": probe.get("page_title_available", ""),
        "structured_data_evidence": probe.get("structured_data_evidence", ""),
        "raw_html_stored": False,
        "raw_payload_stored": False,
        "safe_notes": _safe_note(probe.get("safe_notes", "")),
    }
    return (
        _tag_row(
            base,
            probe_attempted=True,
            probe_status=str(probe.get("status", "FAIL")),
            browser_access_status=tag["browser_access_status"],
            tag=tag["tag"],
            http_status=probe.get("http_status_if_available", ""),
            content_type=probe.get("content_type_if_available", ""),
            page_title=probe.get("page_title_available", ""),
            structured_data=probe.get("structured_data_evidence", ""),
            domain_solved=tag["domain_solved"],
            ingestion_solved=tag["ingestion_solved"],
            scope=tag["scope"],
            remaining_failure_class=tag["remaining_failure_class"],
            remaining_failure_layer=tag["remaining_failure_layer"],
            notes=probe_row["safe_notes"],
        ),
        probe_row,
    )


def _tag_from_probe(probe: dict[str, object]) -> dict[str, object]:
    status = str(probe.get("status", "FAIL"))
    http_status = _int_or_none(probe.get("http_status_if_available"))
    structured = str(probe.get("structured_data_evidence", "")).upper()
    notes = str(probe.get("safe_notes", "")).lower()

    if status == "PASS" and structured in {"JSON_PAYLOAD_DETECTED", "TABULAR_DATA_DETECTED", "NORMALIZED_ROWS_DETECTED"}:
        return _tag_decision(
            "INGESTION_SOLVED",
            "SOLVED_BY_CLOAKBROWSER_REFERENCE_INGESTION",
            True,
            True,
            "ingestion",
            "",
            "",
        )
    if status == "PASS" and http_status is not None and 200 <= http_status < 400:
        return _tag_decision(
            "DOMAIN_ACCESS_SOLVED_STRUCTURED_DATA_NOT_PROVEN",
            "SOLVED_BY_CLOAKBROWSER_REFERENCE_DOMAIN_ACCESS_ONLY",
            True,
            False,
            "domain_access_only",
            "HTML_RETURNED_INSTEAD_OF_DATA",
            "anti_bot_access",
        )
    if http_status == 403:
        return _tag_decision("HTTP_403_FORBIDDEN", "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_HTTP_403", False, False, "none", "HTTP_403_FORBIDDEN", "http_access")
    if http_status == 404:
        return _tag_decision("HTTP_404_NOT_FOUND", "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_HTTP_404", False, False, "none", "HTTP_404_NOT_FOUND", "http_access")
    if http_status == 429:
        return _tag_decision("HTTP_429_RATE_LIMITED", "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_HTTP_429", False, False, "none", "HTTP_429_RATE_LIMITED", "http_access")
    if http_status is not None and 500 <= http_status <= 599:
        return _tag_decision("HTTP_5XX_PROVIDER_ERROR", "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_HTTP_5XX", False, False, "none", "HTTP_5XX_PROVIDER_ERROR", "http_access")
    if any(token in notes for token in ["captcha", "challenge", "verify", "robot", "login", "consent"]):
        return _tag_decision("ANTI_BOT_OR_CONSENT_CHALLENGE", "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_ANTI_BOT", False, False, "none", "BOT_CHALLENGE_DETECTED", "anti_bot_access")
    if status == "FAIL":
        remaining_failure_class = str(probe.get("remaining_failure_class", "UNKNOWN_PROVIDER_FAILURE") or "UNKNOWN_PROVIDER_FAILURE")
        tag = {
            "BROWSER_NET_EMPTY_RESPONSE": "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_EMPTY_RESPONSE",
            "BROWSER_PROBE_TIMEOUT": "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_TIMEOUT",
            "BROWSER_HTTP2_PROTOCOL_ERROR": "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_HTTP2_PROTOCOL",
            "DNS_RESOLUTION_FAILURE": "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_DNS",
            "TLS_SSL_FAILURE": "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_TLS",
            "CONNECTION_RESET": "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_CONNECTION_RESET",
            "CONNECTION_REFUSED": "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_CONNECTION_REFUSED",
        }.get(remaining_failure_class, "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_BROWSER_RUNTIME")
        return _tag_decision(
            "BROWSER_PROBE_FAILED",
            tag,
            False,
            False,
            "none",
            remaining_failure_class,
            str(probe.get("remaining_failure_layer", "unknown") or "unknown"),
        )
    return _tag_decision("UNKNOWN_REFERENCE_RESULT", "CLOAKBROWSER_REFERENCE_ATTEMPTED_NOT_SOLVED_UNKNOWN", False, False, "none", "UNKNOWN_PROVIDER_FAILURE", "unknown")


def _run_dynamic_browser_probe(event: dict[str, str], target_url: str) -> dict[str, object]:
    module = importlib.import_module("cloakbrowser")
    launch = getattr(module, "launch")
    browser = None
    try:
        browser = launch(headless=True, humanize=False, geoip=False)
        page = browser.new_page()
        response = page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
        status = getattr(response, "status", "") if response is not None else ""
        headers = getattr(response, "headers", {}) if response is not None else {}
        content_type = headers.get("content-type", "") if isinstance(headers, dict) else ""
        title = _call_or_blank(page, "title")
        body_text = _safe_body_text(page)
        structured = _structured_evidence(body_text, content_type, event.get("function_name", ""))
        return {
            "status": "PASS" if _int_or_none(status) is not None and 200 <= int(status) < 400 else "FAIL",
            "http_status_if_available": status,
            "content_type_if_available": content_type,
            "page_title_available": title[:120],
            "structured_data_evidence": structured,
            "safe_notes": _safe_probe_note(body_text, status),
        }
    finally:
        if browser is not None:
            close = getattr(browser, "close", None)
            if callable(close):
                close()


def _dependency_status() -> DependencyStatus:
    missing = []
    if not _module_available("cloakbrowser"):
        missing.append("cloakbrowser")
    if not _module_available("playwright.sync_api"):
        missing.append("playwright")
    return DependencyStatus("AVAILABLE" if not missing else "MISSING", tuple(missing))


def _module_available(name: str) -> bool:
    try:
        return importlib.util.find_spec(name) is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        return False


def _target_url_for_event(event: dict[str, str]) -> str:
    function_name = event.get("function_name", "")
    if function_name in FUNCTION_TARGET_URLS:
        return FUNCTION_TARGET_URLS[function_name]
    domain = event.get("target_domain") or target_domain_for_function(function_name)
    if domain in {"", "local_dependency_import", "akshare_finance_domains", "unknown_finance_provider_domain"}:
        return "https://www.akshare.xyz/"
    return f"https://{domain}/"


def _tag_row(
    base: dict[str, object],
    probe_attempted: bool,
    probe_status: str,
    browser_access_status: str,
    tag: str,
    remaining_failure_class: str,
    remaining_failure_layer: str,
    notes: str,
    http_status: object = "",
    content_type: object = "",
    page_title: object = "",
    structured_data: object = "",
    domain_solved: bool = False,
    ingestion_solved: bool = False,
    scope: str = "none",
) -> dict[str, object]:
    return {
        **base,
        "probe_attempted": probe_attempted,
        "probe_status": probe_status,
        "browser_access_status": browser_access_status,
        "http_status_if_available": http_status,
        "content_type_if_available": content_type,
        "page_title_available": page_title,
        "structured_data_evidence": structured_data,
        "domain_access_solved_by_reference": domain_solved,
        "ingestion_solved_by_reference": ingestion_solved,
        "problem_resolution_scope": scope,
        "cloakbrowser_reference_tag": tag,
        "remaining_failure_class": remaining_failure_class,
        "remaining_failure_layer": remaining_failure_layer,
        "safe_notes": _safe_note(notes),
    }


def _tag_decision(
    access_status: str,
    tag: str,
    domain_solved: bool,
    ingestion_solved: bool,
    scope: str,
    remaining_failure_class: str,
    remaining_failure_layer: str,
) -> dict[str, object]:
    return {
        "browser_access_status": access_status,
        "tag": tag,
        "domain_solved": domain_solved,
        "ingestion_solved": ingestion_solved,
        "scope": scope,
        "remaining_failure_class": remaining_failure_class,
        "remaining_failure_layer": remaining_failure_layer,
    }


def _summary(
    problem_rows: list[dict[str, object]],
    probe_rows: list[dict[str, object]],
    dependency: DependencyStatus,
    allow_network: bool,
    use_browser: bool,
) -> dict[str, object]:
    tag_counts = dict(Counter(str(row["cloakbrowser_reference_tag"]) for row in problem_rows))
    remaining_counts = dict(Counter(str(row["remaining_failure_class"]) for row in problem_rows if row["remaining_failure_class"]))
    ingestion_solved = sum(1 for row in problem_rows if row["ingestion_solved_by_reference"] is True)
    domain_solved = sum(1 for row in problem_rows if row["domain_access_solved_by_reference"] is True)
    attempted = sum(1 for row in problem_rows if row["probe_attempted"] is True)
    status = "PASS" if problem_rows and ingestion_solved == len(problem_rows) else "PASS_WITH_WARNINGS"
    if not problem_rows:
        status = "PASS_WITH_WARNINGS"
    return {
        "goal_id": "GOAL-06C.6A-CloakBrowser-Reference-Probe",
        "status": status,
        "reference_repo": REFERENCE_REPO,
        "reference_url": REFERENCE_URL,
        "reference_commit": REFERENCE_COMMIT,
        "reference_pattern": REFERENCE_PATTERN,
        "allow_network": allow_network,
        "use_browser": use_browser,
        "browser_dependency_status": dependency.status,
        "missing_dependencies": list(dependency.missing),
        "problem_count": len(problem_rows),
        "probe_attempt_count": attempted,
        "probe_result_count": len(probe_rows),
        "domain_access_solved_count": domain_solved,
        "ingestion_solved_count": ingestion_solved,
        "remaining_unsolved_count": len(problem_rows) - ingestion_solved,
        "tag_counts": tag_counts,
        "remaining_failure_counts": remaining_counts,
        "raw_html_stored": False,
        "raw_payload_stored": False,
        "default_akshare_provider_path_changed": False,
        "goal06d_allowed_to_proceed": False,
        "interpretation": _interpretation(problem_rows, dependency, allow_network, use_browser),
        "output_files": [
            "outputs/audits/cloakbrowser_reference_problem_tags.csv",
            "outputs/audits/cloakbrowser_reference_probe_results.csv",
            "outputs/audits/cloakbrowser_reference_ingestion_report.md",
            "outputs/audits/cloakbrowser_reference_ingestion_report.json",
        ],
    }


def _write_markdown(root: Path, summary: dict[str, object], problem_rows: list[dict[str, object]]) -> None:
    lines = [
        "# CloakBrowser Reference Ingestion Probe",
        "",
        f"Status: `{summary['status']}`",
        f"Reference repo: `{summary['reference_repo']}`",
        f"Reference commit inspected: `{summary['reference_commit']}`",
        f"Reference pattern: `{summary['reference_pattern']}`",
        f"Network opt-in: `{str(summary['allow_network']).lower()}`",
        f"Browser opt-in: `{str(summary['use_browser']).lower()}`",
        f"Browser dependency status: `{summary['browser_dependency_status']}`",
        f"Missing dependencies: `{';'.join(summary['missing_dependencies'])}`",
        f"Problem rows inspected: `{summary['problem_count']}`",
        f"Browser probes attempted: `{summary['probe_attempt_count']}`",
        f"Domain-access solved by reference: `{summary['domain_access_solved_count']}`",
        f"Ingestion solved by reference: `{summary['ingestion_solved_count']}`",
        f"Remaining unsolved for source-backed ingestion: `{summary['remaining_unsolved_count']}`",
        "Raw HTML stored: `false`",
        "Raw payload stored: `false`",
        "Default AKShare provider path changed: `false`",
        "GOAL-06D allowed to proceed: `false`",
        "",
        "## Interpretation",
        str(summary["interpretation"]),
        "",
        "## Tag Counts",
        *[f"- `{tag}`: `{count}`" for tag, count in sorted(summary["tag_counts"].items())],
        "",
        "## Problem Tags",
    ]
    lines.extend(
        [
            (
                f"- `{row['problem_id']}` `{row['function_name']}`: `{row['cloakbrowser_reference_tag']}`; "
                f"remaining `{row['remaining_failure_class']}`; notes: {row['safe_notes']}"
            )
            for row in problem_rows
        ]
    )
    write_text(root / "outputs/audits/cloakbrowser_reference_ingestion_report.md", "\n".join(lines) + "\n")


def _interpretation(problem_rows: list[dict[str, object]], dependency: DependencyStatus, allow_network: bool, use_browser: bool) -> str:
    if not problem_rows:
        return "No provider failure events were available to tag."
    if not allow_network:
        return "The report tagged current provider failures, but did not launch any network probe because the browser reference path is disabled by default."
    if not use_browser:
        return "Network was allowed but browser execution was not explicitly requested; no CloakBrowser-style probe was launched."
    if dependency.status != "AVAILABLE":
        return "The CloakBrowser reference path is documented and tagged, but the current runtime lacks optional browser dependencies, so no access or ingestion problem was solved by it."
    if any(row["ingestion_solved_by_reference"] is True for row in problem_rows):
        return "At least one provider access problem produced structured-data evidence through the CloakBrowser reference path; only those rows are tagged as ingestion solved."
    if any(row["domain_access_solved_by_reference"] is True for row in problem_rows):
        return "At least one provider domain became reachable through the reference path, but structured ingestion was not proven and GOAL-06D remains blocked."
    return "The optional browser probe was attempted, but no current source-backed ingestion problem was solved."


def _domain_from_url(url: str) -> str:
    return urlparse(url).netloc


def _int_or_none(value: object) -> int | None:
    try:
        if value in {"", None}:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _call_or_blank(obj: object, method_name: str) -> str:
    method = getattr(obj, method_name, None)
    if not callable(method):
        return ""
    try:
        return str(method())
    except Exception:
        return ""


def _safe_body_text(page: object) -> str:
    for method_name in ["text_content", "inner_text"]:
        method = getattr(page, method_name, None)
        if callable(method):
            try:
                text = method("body", timeout=1000)
                if text:
                    return str(text)[:5000]
            except Exception:
                continue
    return ""


def _structured_evidence(body_text: str, content_type: str, function_name: str) -> str:
    lower_type = content_type.lower()
    stripped = body_text.strip()
    lowered = stripped.lower()
    if function_name in {"index_zh_a_hist", "stock_zh_a_hist"} and '"klines"' in lowered:
        return "JSON_PAYLOAD_DETECTED"
    if function_name == "stock_zh_a_spot_em" and '"diff"' in lowered and '"data"' in lowered:
        return "JSON_PAYLOAD_DETECTED"
    if "application/json" in lower_type and ('"data"' in lowered or "'data'" in lowered):
        return "JSON_PAYLOAD_DETECTED"
    if stripped.startswith("[") and "," in stripped:
        return "TABULAR_DATA_DETECTED"
    if "," in stripped and "\n" in stripped:
        return "TABULAR_DATA_DETECTED"
    return ""


def _browser_exception_class(exc: BaseException) -> tuple[str, str]:
    message = str(exc).lower()
    if "timeout" in message:
        return "BROWSER_PROBE_TIMEOUT", "browser_runtime"
    if "err_name_not_resolved" in message or "name resolution" in message:
        return "DNS_RESOLUTION_FAILURE", "network_transport"
    if "err_connection_reset" in message:
        return "CONNECTION_RESET", "network_transport"
    if "err_connection_refused" in message:
        return "CONNECTION_REFUSED", "network_transport"
    if "err_empty_response" in message:
        return "BROWSER_NET_EMPTY_RESPONSE", "network_transport"
    if "err_ssl" in message or "certificate" in message:
        return "TLS_SSL_FAILURE", "network_transport"
    if "http2" in message:
        return "BROWSER_HTTP2_PROTOCOL_ERROR", "browser_runtime"
    classification = classify_provider_failure(exc=exc)
    if classification.failure_class == "UNHANDLED_EXCEPTION":
        return "BROWSER_RUNTIME_ERROR", "browser_runtime"
    return classification.failure_class, classification.failure_layer


def _safe_probe_note(body_text: str, status: object) -> str:
    lower = body_text.lower()
    if any(token in lower for token in ["captcha", "challenge", "robot", "verify"]):
        return f"HTTP {status}; anti-bot/challenge text detected; body suppressed"
    if any(token in lower for token in ["login", "consent"]):
        return f"HTTP {status}; login or consent wall text detected; body suppressed"
    return f"HTTP {status}; body inspected in memory only"


def _safe_note(value: object) -> str:
    text = str(value).replace("\n", " ").replace("\r", " ")
    if "<html" in text.lower() or "<!doctype" in text.lower():
        return "html/challenge content suppressed"
    return text[:240]
