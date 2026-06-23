from __future__ import annotations

import json
import subprocess
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_text
from ashare_premarket.providers.browser_provider_switches import browser_provider_project_default


FORBIDDEN_SUFFIXES = (
    ".db",
    ".sqlite",
    ".sqlite3",
    ".parquet",
    ".pkl",
    ".joblib",
    ".zip",
    ".ipynb",
    ".html",
    ".log",
    ".env",
)

ALLOWED_SHARED_OUTPUTS = {
    "outputs/features/daily_premarket_signal_snapshot.csv",
    "outputs/labels/daily_label_snapshot.csv",
}


def audit_workflow_cleanliness(root: Path) -> bool:
    failures: list[str] = []
    warnings: list[str] = []
    workflow_path = root / "configs/project/workflow_status.csv"
    rows = read_csv(workflow_path) if workflow_path.exists() else []
    by_id = {row["workflow_id"]: row for row in rows}
    goal06c7 = by_id.get("goal06c7_provider_ladder_browser_assisted_engineering_data_base_expansion", {})
    goal06d = by_id.get("goal06d_model_comparison_calibration", {})
    manifest = _read_json(root / "outputs/audits/source_backed_bundle_manifest_summary.json")
    engineering_pilot_met = manifest.get("engineering_pilot_met") is True

    if not goal06c7:
        failures.append("GOAL-06C.7 workflow row is missing")
    elif goal06c7.get("status") != "implemented_review_only":
        failures.append("GOAL-06C.7 must be implemented_review_only, not active production")
    if goal06d.get("status") == "future_review_only":
        if "engineering_pilot" not in goal06d.get("allowed_next_action", ""):
            failures.append("GOAL-06D future row must wait for engineering_pilot evidence")
    elif goal06d.get("status") == "implemented_review_only":
        readiness = _read(root / "outputs/audits/goal06d_readiness_report.md")
        if "GOAL-06D Model Comparison Calibration Readiness: PASS" not in readiness:
            failures.append("GOAL-06D implemented_review_only requires PASS/PASS_WITH_WARNINGS readiness evidence")
        if goal06d.get("allowed_next_action") not in {
            "prepare_goal07a_risk_overlay_design_only",
            "fix_goal06d_model_stability_or_calibration_warnings",
        }:
            failures.append("GOAL-06D implemented_review_only has an invalid next action")
    else:
        failures.append("GOAL-06D must be future_review_only or implemented_review_only")
    if not engineering_pilot_met:
        warnings.append("latest source-backed bundle summary does not yet prove engineering_pilot coverage")
    if browser_provider_project_default(root) is not False:
        failures.append("browser-assisted provider switch is enabled by default")

    forbidden_tracked = _tracked_forbidden_files(root)
    if forbidden_tracked:
        failures.extend(f"forbidden tracked artifact: {path}" for path in forbidden_tracked)
    duplicate_paths = _duplicate_active_paths(rows)
    if duplicate_paths:
        failures.extend(f"duplicate active canonical output path: {path}" for path in duplicate_paths)
    static_browser_imports = _static_browser_imports(root)
    if static_browser_imports:
        failures.extend(f"default static browser runtime import: {path}" for path in static_browser_imports)

    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/workflow_cleanliness_audit.md",
        "\n".join(
            [
                "# Workflow Cleanliness Audit",
                "",
                f"Workflow Cleanliness Audit: {status}",
                "",
                f"Workflow rows: `{len(rows)}`",
                f"GOAL-06C.7 status: `{goal06c7.get('status', 'missing')}`",
                f"GOAL-06D status: `{goal06d.get('status', 'missing')}`",
                f"Engineering pilot met: `{str(engineering_pilot_met).lower()}`",
                f"Browser-assisted project default: `{str(browser_provider_project_default(root)).lower()}`",
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


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _tracked_forbidden_files(root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
        paths = result.stdout.splitlines()
    except Exception:  # pragma: no cover - defensive fallback
        paths = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    allowed = {"data/cached_evidence/.gitkeep"}
    return sorted(path for path in paths if path not in allowed and path.lower().endswith(FORBIDDEN_SUFFIXES))


def _duplicate_active_paths(rows: list[dict[str, str]]) -> list[str]:
    seen: dict[str, str] = {}
    duplicates: list[str] = []
    for row in rows:
        if row.get("status") not in {"implemented_active", "implemented_review_only"}:
            continue
        for output in row.get("primary_outputs", "").split(";"):
            output = output.strip()
            if not output or output == "not_yet":
                continue
            if output in ALLOWED_SHARED_OUTPUTS:
                continue
            prior = seen.get(output)
            if prior and prior != row["workflow_id"]:
                duplicates.append(output)
            seen[output] = row["workflow_id"]
    return sorted(set(duplicates))


def _static_browser_imports(root: Path) -> list[str]:
    hits: list[str] = []
    for base in ["src", "scripts", "tests"]:
        for path in (root / base).rglob("*.py"):
            rel = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip().lower()
                if stripped.startswith("import cloakbrowser") or stripped.startswith("from cloakbrowser"):
                    hits.append(rel)
                    break
    return hits
