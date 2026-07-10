from __future__ import annotations

import ast
import os
from pathlib import Path

from ashare_premarket.core.boundary import forbidden_locked_import_terms
from ashare_premarket.core.constants import BLOCKED_SYMBOLS, LOCKED_KEYWORDS
from ashare_premarket.core.io import write_text
from ashare_premarket.universe.governance import validate_symbol_governance

DANGEROUS_SUFFIXES = {
    ".arrow",
    ".db",
    ".duckdb",
    ".feather",
    ".h5",
    ".html",
    ".ipynb",
    ".joblib",
    ".log",
    ".npy",
    ".npz",
    ".onnx",
    ".parquet",
    ".payload",
    ".pkl",
    ".pt",
    ".pth",
    ".raw",
    ".sqlite",
    ".sqlite3",
    ".zip",
}

IGNORED_GENERATED_PARTS = {".git", ".next", "coverage", "node_modules", "playwright-report", "test-results"}


def run_safety_gate(root: Path) -> bool:
    failures: list[str] = []
    warnings: list[str] = []
    ok, messages = validate_symbol_governance(root)
    if not ok:
        failures.extend(messages)
    for path in _iter_scannable_files(root):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if path.suffix in DANGEROUS_SUFFIXES:
            failures.append(f"Forbidden file suffix present: {rel}")
        if (rel.startswith("src/") or rel.startswith("scripts/")) and path.suffix == ".py":
            failures.extend(_locked_import_failures(root, path, rel))
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


def _iter_scannable_files(root: Path):
    root = root.resolve()
    for current, directories, filenames in os.walk(root):
        current_path = Path(current)
        relative_parts = current_path.relative_to(root).parts
        if relative_parts[:2] == ("outputs", "local"):
            directories.clear()
            continue
        directories[:] = sorted(name for name in directories if name not in IGNORED_GENERATED_PARTS)
        for filename in sorted(filenames):
            yield current_path / filename


def _locked_import_failures(root: Path, path: Path, rel: str) -> list[str]:
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
                failures.extend(_check_module(root, module_name, rel))
        elif isinstance(node, ast.ImportFrom):
            module_name = (node.module or "").lower()
            failures.extend(_check_module(root, module_name, rel))
    return failures


def _check_module(root: Path, module_name: str, rel: str) -> list[str]:
    return [
        f"Locked downstream import `{module_name}` in {rel}"
        for _ in forbidden_locked_import_terms(root, module_name, rel, LOCKED_KEYWORDS)
    ]


def _blocked_symbols_in_outputs(root: Path) -> list[str]:
    failures = []
    for path in (root / "outputs").rglob("*.csv"):
        if path.relative_to(root).as_posix().startswith("outputs/local/"):
            continue
        text = path.read_text(encoding="utf-8")
        for symbol in BLOCKED_SYMBOLS:
            if symbol in text:
                failures.append(f"Blocked symbol {symbol} present in output {path.relative_to(root).as_posix()}")
    return failures
