from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_runtime_outputs_are_ignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "outputs/local/" in gitignore
    assert "outputs/diagnostics/local_runtime_*.csv" in gitignore


def test_python39_is_declared_supported() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'requires-python = ">=3.9"' in pyproject


def test_python39_dependency_resolution_excludes_python310_only_httpx2() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"httpx2>=2.7,<3; python_version >= \'3.10\'"' in pyproject


def test_stable_regression_report_has_local_only_runtime() -> None:
    path = ROOT / "outputs/audits/goal06b_regression_suite_report.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["runtime_seconds"] for row in rows} == {"local_only"}


def test_stable_program_validation_report_has_local_only_runtime() -> None:
    path = ROOT / "outputs/audits/program_validation_profile_results.csv"
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows
    assert {row["runtime_seconds"] for row in rows} == {"local_only"}
