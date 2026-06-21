from __future__ import annotations

import csv
from pathlib import Path

from ashare_premarket.validation.stage6c import run_goal06c_expanded_validation


ROOT = Path(__file__).resolve().parents[1]


def _rows(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal06c_scripts_and_configs_exist() -> None:
    for path in [
        "configs/validation/stage6c_validation_config.yaml",
        "configs/validation/stage6c_ranking_baseline_config.yaml",
        "scripts/build_stage6c_expanded_validation_dataset.py",
        "scripts/run_stage6c_ranking_baselines.py",
        "scripts/audit_stage6c_ranking_baselines.py",
        "scripts/run_stage6c_walk_forward_validation.py",
        "scripts/audit_stage6c_expanded_validation.py",
        "scripts/run_goal06c_expanded_validation.py",
    ]:
        assert (ROOT / path).exists()


def test_goal06c_outputs_are_generated_from_approved_symbols_only() -> None:
    assert run_goal06c_expanded_validation(ROOT)
    rows = _rows("outputs/stage6c/STAGE6C_expanded_validation_dataset.csv")
    assert rows
    assert {row["symbol"] for row in rows} == {"002475.SZ", "600036.SH"}
    assert all(row["approved_symbol_flag"] == "true" for row in rows)
    assert all(row["usable_for_validation"] == "true" for row in rows)
    assert all(row["review_only"] == "true" for row in rows)
    assert all(row["source_panel_type"] == "clean_bootstrap_review_fixture" for row in rows)
    assert all(row["leakage_flags"] == "PASS" for row in rows)
    assert not {"000625.SZ", "000858.SZ", "601138.SH", "601208.SH"} & {row["symbol"] for row in rows}


def test_goal06c_required_outputs_exist() -> None:
    assert run_goal06c_expanded_validation(ROOT)
    for path in [
        "outputs/stage6c/STAGE6C_expanded_validation_dataset.csv",
        "outputs/stage6c/STAGE6C_ranking_baseline_scores.csv",
        "outputs/stage6c/STAGE6C_ranking_metrics.csv",
        "outputs/stage6c/STAGE6C_walk_forward_diagnostics.csv",
        "outputs/stage6c/STAGE6C_ranking_stability_diagnostics.csv",
        "outputs/audits/stage6c_expanded_validation_audit.md",
        "outputs/audits/stage6c_ranking_baseline_audit.md",
        "outputs/audits/stage6c_walk_forward_audit.md",
        "outputs/audits/stage6c_leakage_and_boundary_audit.md",
        "outputs/audits/stage6c_readiness_report.md",
    ]:
        assert (ROOT / path).exists()
        assert (ROOT / path).stat().st_size > 0
