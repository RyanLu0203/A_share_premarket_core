from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_json, write_text

STORAGE_POLICY = "configs/storage/storage_policy.yaml"
DATA_PATHS = "configs/storage/data_paths.example.yaml"
DATA_BUNDLE_SCHEMA = "configs/storage/data_bundle_schema.yaml"
TABLE_SCHEMA_REGISTRY = "configs/storage/table_schema_registry.yaml"
SUMMARY_JSON = "outputs/audits/data_bundle_manifest_summary.json"


def resolve_data_root(root: Path) -> Path:
    config = _load_json(root / DATA_PATHS)
    env_var = str(config["data_root_env_var"])
    value = os.environ.get(env_var, str(config["default_data_root"]))
    return Path(value).expanduser().resolve()


def audit_storage_policy(root: Path) -> bool:
    policy = _load_json(root / STORAGE_POLICY)
    data_root = resolve_data_root(root)
    failures: list[str] = []
    warnings: list[str] = []
    required_files = [
        STORAGE_POLICY,
        DATA_PATHS,
        DATA_BUNDLE_SCHEMA,
        TABLE_SCHEMA_REGISTRY,
        "docs/storage/DATA_STORAGE_ARCHITECTURE.md",
    ]
    for rel in required_files:
        if not (root / rel).exists():
            failures.append(f"missing storage contract file: {rel}")
    if _is_relative_to(data_root, root.resolve()):
        failures.append(f"data root is inside repository: {data_root}")
    gitignore = (root / ".gitignore").read_text(encoding="utf-8")
    for pattern in policy["forbidden_github_artifacts"]:
        if str(pattern).startswith("*") and str(pattern) not in gitignore:
            failures.append(f"missing gitignore pattern: {pattern}")
    tracked_forbidden = _tracked_forbidden_files(root, policy["forbidden_github_artifacts"])
    if tracked_forbidden:
        failures.extend(f"forbidden tracked artifact: {path}" for path in tracked_forbidden)
    if not data_root.exists():
        warnings.append(f"local data root does not exist yet: {data_root}")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/storage_policy_audit.md",
        "\n".join(
            [
                "# Storage Policy Audit",
                "",
                f"Status: `{status}`",
                f"Data root env var: `{policy['data_root_env_var']}`",
                f"Resolved data root: `{data_root}`",
                "Storage role: local research store, not production database.",
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


def build_data_bundle_manifest(root: Path) -> Path:
    data_root = resolve_data_root(root)
    approved = read_csv(root / "configs/universe/approved_symbols.csv")
    blocked = read_csv(root / "configs/universe/blocked_symbols.csv")
    trading_calendar = read_csv(root / "configs/project/trading_calendar.csv")
    source_rows = read_csv(root / "configs/providers/source_health_contract.csv")
    stage6c = read_csv(root / "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv")
    pit_rows = _read_optional_csv(root / "outputs/features/daily_premarket_signal_snapshot.csv")
    label_rows = _read_optional_csv(root / "outputs/labels/daily_label_snapshot.csv")
    symbols = sorted({row["symbol"] for row in approved})
    dates = sorted({row["trade_date"] for row in stage6c})
    blocked_symbols = {row["symbol"] for row in blocked}
    blocked_symbol_rows = sum(1 for row in stage6c if row["symbol"] in blocked_symbols)
    pit_ready_rows = sum(1 for row in pit_rows if row.get("pit_ready") == "true")
    label_ready_rows = sum(1 for row in label_rows if row.get("label_is_pit_safe") == "true")
    manifest = {
        "bundle_id": "contract_demo_current_clean_bootstrap",
        "bundle_tier": "contract_demo",
        "created_at": "2026-06-21T00:00:00Z",
        "as_of_date": max(dates) if dates else "",
        "source_commit_sha": "stable_committed_summary",
        "workflow_status_version": "goal06c5.workflow_status.v1",
        "universe_version": "goal06c5.universe.v1",
        "calendar_version": "goal06c5.calendar.contract_demo.v1",
        "provider_versions": "provider_registry.goal06c5.v1",
        "data_root": str(data_root),
        "local_bundle_path": str(data_root / "bundles/engineering_pilot/contract_demo_current_clean_bootstrap"),
        "symbols_requested": len(symbols),
        "symbols_succeeded": len(symbols),
        "symbols_failed": 0,
        "trading_dates_requested": len(dates),
        "trading_dates_succeeded": len(dates),
        "raw_rows": len(pit_rows),
        "clean_rows": len(stage6c),
        "pit_ready_rows": pit_ready_rows,
        "label_ready_rows": label_ready_rows,
        "stage6c_rows": len(stage6c),
        "blocked_symbol_rows": blocked_symbol_rows,
        "missing_rate": 0.0 if stage6c else 1.0,
        "source_coverage_summary": _source_coverage_summary(source_rows),
        "field_coverage_summary": "contract_demo_fields_available_for_1d_stage6c;3d_5d_labels_missing",
        "quality_flags": ["CONTRACT_DEMO_ONLY", "NOT_ENGINEERING_PILOT", "LOCAL_DATA_ROOT_NOT_MATERIALIZED"]
        if not data_root.exists()
        else ["CONTRACT_DEMO_ONLY", "NOT_ENGINEERING_PILOT"],
        "health_status": "PASS_WITH_WARNINGS",
        "notes": "Committed manifest is a deterministic summary. Heavy data and local bundle contents are not committed.",
        "calendar_rows_in_config": len(trading_calendar),
    }
    write_json(root / SUMMARY_JSON, manifest)
    write_text(
        root / "outputs/audits/data_bundle_manifest_summary.md",
        "\n".join(
            [
                "# Data Bundle Manifest Summary",
                "",
                "Status: `PASS_WITH_WARNINGS`",
                f"Bundle id: `{manifest['bundle_id']}`",
                f"Bundle tier: `{manifest['bundle_tier']}`",
                f"Symbols succeeded: `{manifest['symbols_succeeded']}`",
                f"Trading dates succeeded: `{manifest['trading_dates_succeeded']}`",
                f"Stage 6C rows: `{manifest['stage6c_rows']}`",
                "The current committed bundle summary describes a contract-demo fixture, not an engineering-pilot data bundle.",
                "",
            ]
        ),
    )
    return root / SUMMARY_JSON


def audit_data_bundle_manifest(root: Path) -> bool:
    summary_path = root / SUMMARY_JSON
    if not summary_path.exists():
        build_data_bundle_manifest(root)
    manifest = json.loads(summary_path.read_text(encoding="utf-8"))
    schema = _load_json(root / DATA_BUNDLE_SCHEMA)
    failures: list[str] = []
    warnings: list[str] = []
    for field in schema["required_fields"]:
        if field not in manifest:
            failures.append(f"missing manifest field: {field}")
    if _is_relative_to(Path(manifest["data_root"]).expanduser().resolve(), root.resolve()):
        failures.append("manifest data_root is inside repository")
    if manifest.get("blocked_symbol_rows") != 0:
        failures.append("manifest reports blocked symbol rows")
    if manifest.get("bundle_tier") == "contract_demo":
        warnings.append("current bundle tier is contract_demo; engineering_pilot not reached")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    write_text(
        root / "outputs/audits/data_bundle_manifest_audit.md",
        "\n".join(
            [
                "# Data Bundle Manifest Audit",
                "",
                f"Status: `{status}`",
                f"Fields checked: `{len(schema['required_fields'])}`",
                f"Bundle tier: `{manifest.get('bundle_tier', '')}`",
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


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_optional_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def _source_coverage_summary(rows: list[dict[str, str]]) -> dict[str, object]:
    sources = sorted({row["source_id"] for row in rows})
    pit_ready = sum(1 for row in rows if row["pit_ready"] == "true")
    return {
        "sources": len(sources),
        "source_ids": sources,
        "pit_ready_contract_rows": pit_ready,
        "total_contract_rows": len(rows),
    }


def _tracked_forbidden_files(root: Path, forbidden_patterns: list[str]) -> list[str]:
    suffixes = tuple(pattern[1:] for pattern in forbidden_patterns if str(pattern).startswith("*."))
    try:
        result = subprocess.run(["git", "ls-files"], cwd=root, text=True, capture_output=True, check=True)
        tracked = result.stdout.splitlines()
    except Exception:  # pragma: no cover - fallback for non-git contexts
        tracked = [path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()]
    allowed = {"data/cached_evidence/.gitkeep"}
    return sorted(path for path in tracked if path not in allowed and path.endswith(suffixes))


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False
