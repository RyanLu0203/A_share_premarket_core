from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv
from ashare_premarket.features.panel_expansion import audit_engineering_pit_signal_panel, build_engineering_pit_signal_panel
from ashare_premarket.labels.panel_expansion import audit_engineering_label_panel, build_engineering_label_panel
from ashare_premarket.validation.engineering_panel import rebuild_stage6c_from_engineering_panel

ROOT = Path(__file__).resolve().parents[1]


def test_engineering_pit_panel_is_fixture_flagged_and_label_free() -> None:
    path = build_engineering_pit_signal_panel(ROOT)
    assert audit_engineering_pit_signal_panel(ROOT)
    rows = read_csv(path)
    assert len(rows) == 8
    assert {row["panel_source_type"] for row in rows} == {"clean_bootstrap_fixture"}
    header = set(rows[0])
    assert not any(name.startswith("fwd_") or name.startswith("label") or name.endswith("_return") for name in header)


def test_engineering_label_panel_marks_missing_horizons() -> None:
    path = build_engineering_label_panel(ROOT)
    assert audit_engineering_label_panel(ROOT)
    rows = read_csv(path)
    assert len(rows) == 8
    assert all(row["fwd_3d_return"] == "" and row["fwd_5d_return"] == "" for row in rows)
    assert all("CLEAN_BOOTSTRAP_FIXTURE" in row["label_quality_flags"] for row in rows)


def test_stage6c_engineering_panel_is_contract_demo_and_blocks_goal06d() -> None:
    assert rebuild_stage6c_from_engineering_panel(ROOT)
    coverage = read_csv(ROOT / "outputs/stage6c/STAGE6C_engineering_panel_coverage_summary.csv")[0]
    assert coverage["panel_tier"] == "contract_demo"
    assert coverage["engineering_pilot_met"] == "false"
    assert coverage["goal06d_allowed"] == "false"
    readiness = (ROOT / "outputs/audits/engineering_panel_readiness_report.md").read_text(encoding="utf-8")
    assert "Engineering Panel Readiness: PASS_WITH_WARNINGS" in readiness
    assert "GOAL-06D allowed to proceed: false" in readiness
