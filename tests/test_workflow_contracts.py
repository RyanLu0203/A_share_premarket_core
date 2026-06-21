from __future__ import annotations

from pathlib import Path

from ashare_premarket.datasets.feature_label_merge import FEATURE_COLUMNS, LABEL_COLUMNS
from ashare_premarket.features.pit_signal_store import build_pit_signal_snapshot
from ashare_premarket.labels.label_builder import build_label_snapshot
from ashare_premarket.universe.governance import validate_symbol_governance


ROOT = Path(__file__).resolve().parents[1]


def test_symbol_governance_has_no_overlap() -> None:
    ok, messages = validate_symbol_governance(ROOT)
    assert ok, messages


def test_pit_signal_snapshot_uses_only_approved_symbols() -> None:
    path = build_pit_signal_snapshot(ROOT)
    text = path.read_text(encoding="utf-8")
    assert "002475.SZ" in text
    assert "600036.SH" in text
    assert "000625.SZ" not in text


def test_label_snapshot_is_review_only_contract() -> None:
    path = build_label_snapshot(ROOT)
    text = path.read_text(encoding="utf-8")
    assert "label_positive" in text
    assert "label_is_pit_safe" in text


def test_feature_manifest_excludes_label_columns() -> None:
    assert not (set(FEATURE_COLUMNS) & set(LABEL_COLUMNS))
