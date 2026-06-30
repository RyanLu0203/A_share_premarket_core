from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable

from ashare_premarket.contracts.common import FORBIDDEN_LOOKAHEAD_COLUMNS, FORBIDDEN_OUTPUT_TERMS, SIZE_LIMIT_BYTES
from ashare_premarket.core.io import read_csv

SECRET_PATTERN = re.compile(r"(TUSHARE_TOKEN\s*=|AKSHARE_TOKEN\s*=|SECRET\s*=|PASSWORD\s*=|API[_-]?KEY\s*=|TOKEN\s*=)", re.IGNORECASE)


def scan_artifact_sizes(root: Path, paths: Iterable[str], limit_bytes: int = SIZE_LIMIT_BYTES) -> list[str]:
    failures: list[str] = []
    for path_text in paths:
        path = root / path_text
        if path.exists() and path.is_file() and path.stat().st_size >= limit_bytes:
            failures.append(f"artifact_size_limit_exceeded:{path_text}:{path.stat().st_size}")
    return failures


def duplicate_key_failures(root: Path, csv_path: str, key_fields: tuple[str, ...]) -> list[str]:
    rows = read_csv(root / csv_path)
    seen: set[tuple[str, ...]] = set()
    duplicate_count = 0
    for row in rows:
        key = tuple(row.get(field, "") for field in key_fields)
        if key in seen:
            duplicate_count += 1
        seen.add(key)
    return [f"duplicate_key:{csv_path}:{','.join(key_fields)}:{duplicate_count}"] if duplicate_count else []


def forbidden_lookahead_columns(headers: Iterable[str]) -> list[str]:
    bad: list[str] = []
    for header in headers:
        lowered = header.lower()
        if lowered in FORBIDDEN_LOOKAHEAD_COLUMNS or lowered.startswith("future_return_") or lowered.startswith("benchmark_excess_return_"):
            bad.append(header)
    return bad


def scan_forbidden_output_terms(root: Path, paths: Iterable[str]) -> list[str]:
    failures: list[str] = []
    for path_text in paths:
        path = root / path_text
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for term in FORBIDDEN_OUTPUT_TERMS:
            if term in text and _term_is_actionable(term, text):
                failures.append(f"forbidden_output_term:{path_text}:{term}")
    return failures


def scan_token_secret_leakage(root: Path, paths: Iterable[str]) -> list[str]:
    failures: list[str] = []
    for path_text in paths:
        path = root / path_text
        if path.exists() and path.is_file() and SECRET_PATTERN.search(path.read_text(encoding="utf-8", errors="ignore")):
            failures.append(f"possible_secret_leakage:{path_text}")
    return failures


def lineage_failures(required_inputs: Iterable[str], manifest: dict[str, object]) -> list[str]:
    manifest_text = repr(manifest)
    return [f"lineage_missing:{path}" for path in required_inputs if path not in manifest_text]


def workflow_lock_failures(workflow: dict[str, dict[str, str]], locked_ids: Iterable[str]) -> list[str]:
    failures: list[str] = []
    for workflow_id in locked_ids:
        row = workflow.get(workflow_id, {})
        if row.get("status") != "locked_future" or row.get("implemented_in_repo") != "false":
            failures.append(f"workflow_lock_not_preserved:{workflow_id}")
    return failures


def _term_is_actionable(term: str, text: str) -> bool:
    if term in {"buy", "sell", "hold"}:
        return bool(re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE))
    return True

