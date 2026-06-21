from __future__ import annotations

from pathlib import Path

from ashare_premarket.core.io import read_csv
from ashare_premarket.data.coverage import audit_data_source_coverage

ROOT = Path(__file__).resolve().parents[1]


def test_source_coverage_outputs_exist_and_report_gap() -> None:
    assert audit_data_source_coverage(ROOT)
    required = [
        "outputs/audits/data_source_coverage_audit.md",
        "outputs/audits/source_symbol_coverage_matrix.csv",
        "outputs/audits/source_date_coverage_matrix.csv",
        "outputs/audits/symbol_data_availability_summary.csv",
        "outputs/audits/source_availability_summary.csv",
        "outputs/audits/source_gap_analysis.md",
        "outputs/audits/universe_expansion_audit.md",
        "outputs/audits/trading_calendar_expansion_audit.md",
        "outputs/audits/provider_ingestion_contract_audit.md",
    ]
    for rel in required:
        assert (ROOT / rel).exists(), rel
    text = (ROOT / "outputs/audits/data_source_coverage_audit.md").read_text(encoding="utf-8")
    assert "current_stage6c_rows: `8`" in text
    assert "target_engineering_pilot_rows: `6000`" in text


def test_universe_and_calendar_expansion_configs_exist() -> None:
    assert (ROOT / "configs/universe/universe_expansion_config.yaml").exists()
    assert (ROOT / "configs/universe/candidate_symbols.csv").exists()
    assert (ROOT / "configs/project/trading_calendar_expansion_config.yaml").exists()
    assert len(read_csv(ROOT / "configs/universe/approved_symbols.csv")) == 2
