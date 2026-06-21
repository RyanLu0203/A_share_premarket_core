from __future__ import annotations

import ast
from pathlib import Path

from ashare_premarket.core.constants import BLOCKED_SYMBOLS, LOCKED_KEYWORDS
from ashare_premarket.core.io import write_text
from ashare_premarket.universe.governance import validate_symbol_governance

DANGEROUS_SUFFIXES = {
    ".arrow",
    ".db",
    ".duckdb",
    ".feather",
    ".html",
    ".ipynb",
    ".joblib",
    ".log",
    ".parquet",
    ".payload",
    ".pkl",
    ".raw",
    ".sqlite",
    ".sqlite3",
    ".zip",
}


def run_safety_gate(root: Path) -> bool:
    failures: list[str] = []
    warnings: list[str] = []
    ok, messages = validate_symbol_governance(root)
    if not ok:
        failures.extend(messages)
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if path.suffix in DANGEROUS_SUFFIXES:
            failures.append(f"Forbidden file suffix present: {rel}")
        if (rel.startswith("src/") or rel.startswith("scripts/")) and path.suffix == ".py":
            failures.extend(_locked_import_failures(path, rel))
        if rel.startswith("outputs/") and any(token in rel.lower() for token in ["raw_payload", "raw_html", "full_news_text"]):
            failures.append(f"Forbidden raw output path present: {rel}")
    blocked_refs = _blocked_symbols_in_outputs(root)
    if blocked_refs:
        failures.extend(blocked_refs)
    status = "PASS" if not failures else "BLOCKED"
    write_text(
        root / "outputs/audits/safety_gate_report.md",
        "\n".join(
            [
                "# Safety Gate Report",
                "",
                f"Status: `{status}`",
                f"Failures: `{len(failures)}`",
                f"Warnings: `{len(warnings)}`",
                "",
                "Locked downstream capabilities are not imported by active modules.",
                "",
                *[f"- {failure}" for failure in failures],
                "",
            ]
        ),
    )
    return status == "PASS"


def _locked_import_failures(path: Path, rel: str) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [f"Syntax failure in {rel}: {exc}"]
    failures = []
    for node in ast.walk(tree):
        module_name = None
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name.lower()
                failures.extend(_check_module(module_name, rel))
        elif isinstance(node, ast.ImportFrom):
            module_name = (node.module or "").lower()
            failures.extend(_check_module(module_name, rel))
    return failures


def _check_module(module_name: str, rel: str) -> list[str]:
    failures = []
    for keyword in LOCKED_KEYWORDS:
        if keyword in module_name:
            failures.append(f"Locked downstream import `{module_name}` in {rel}")
    return failures


def _blocked_symbols_in_outputs(root: Path) -> list[str]:
    failures = []
    for path in (root / "outputs").rglob("*.csv"):
        text = path.read_text(encoding="utf-8")
        for symbol in BLOCKED_SYMBOLS:
            if symbol in text:
                failures.append(f"Blocked symbol {symbol} present in output {path.relative_to(root).as_posix()}")
    return failures
