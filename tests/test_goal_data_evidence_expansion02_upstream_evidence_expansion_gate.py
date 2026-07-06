from __future__ import annotations

import csv
import json
from pathlib import Path

from ashare_premarket.data_expansion.goal_data_evidence_expansion02 import (
    EVIDENCE_GAP_MAP,
    FALSE_BOUNDARY_KEYS,
    FEATURE_CATALOG,
    MANIFEST_PATH,
    PANEL_BEFORE_AFTER,
    PIT_CONTRACT,
    REQ_BUNDLE,
    REQ_CREDENTIAL,
    REQ_NETWORK,
    REQ_PROVIDER,
    SOLVABLE_OFFLINE,
    UNAVAILABLE,
    audit_goal_data_evidence_expansion02_upstream_evidence_expansion_gate as audit_gate,
    goal_data_evidence_expansion02_valid_evidence,
    run_goal_data_evidence_expansion02_upstream_evidence_expansion_gate as run_gate,
)

ROOT = Path(__file__).resolve().parents[1]
CLASSES = {SOLVABLE_OFFLINE, REQ_NETWORK, REQ_PROVIDER, REQ_CREDENTIAL, REQ_BUNDLE, UNAVAILABLE}


def _rows(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _manifest() -> dict:
    return json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))


def test_gate_audit_and_evidence_valid() -> None:
    assert run_gate(ROOT)
    assert audit_gate(ROOT)
    assert goal_data_evidence_expansion02_valid_evidence(ROOT)
    assert _manifest()["status"] in {"PASS", "PASS_WITH_WARNINGS"}


def test_no_fabricated_expansion_before_equals_after() -> None:
    run_gate(ROOT)
    m = _manifest()
    assert m["symbols_after"] == m["symbols_before"]
    assert m["dates_after"] == m["dates_before"]
    assert m["providers_after"] == m["providers_before"]
    assert m["materially_expanded_offline"] is False
    for row in _rows(PANEL_BEFORE_AFTER):
        if row["dimension"] in {"distinct_symbols", "distinct_dates", "offline_providers"}:
            assert row["materially_expanded"] == "false"


def test_gap_map_fully_classified() -> None:
    run_gate(ROOT)
    gap = _rows(EVIDENCE_GAP_MAP)
    assert gap
    for row in gap:
        assert row["solvability_class"] in CLASSES, row
    # the two binding material gaps must be classified as needing a new bundle (not fabricated as solved)
    by_dim = {r["gap_dimension"]: r for r in gap}
    assert by_dim["symbol_count"]["solvability_class"] == REQ_BUNDLE
    assert by_dim["date_count"]["solvability_class"] == REQ_BUNDLE


def test_boundaries_locks_and_no_governance_mutation() -> None:
    run_gate(ROOT)
    m = _manifest()
    for key in FALSE_BOUNDARY_KEYS:
        assert m[key] is False, key
    assert m["credentials_embedded"] is False
    assert m["readiness_thresholds_preserved"] is True
    assert m["goal_rec_tiering01_locked_future"] is True
    assert m["workflow_status_modified_by_this_goal"] is False
    assert m["locked_capabilities_modified_by_this_goal"] is False
    workflow = {r["workflow_id"]: r for r in _rows("configs/project/workflow_status.csv")}
    assert workflow["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert workflow["dashboard_daily_report"]["status"] == "locked_future"


def test_pit_contract_and_feature_catalog_declared() -> None:
    run_gate(ROOT)
    pit = _rows(PIT_CONTRACT)
    assert pit
    for row in pit:
        assert row["pit_declaration"]
        assert row["contract_status"]
    feat = _rows(FEATURE_CATALOG)
    assert feat
    for row in feat:
        assert row["solvability_class"] in CLASSES
        assert row["provider"]


def test_no_forward_return_columns() -> None:
    run_gate(ROOT)
    for rel in [EVIDENCE_GAP_MAP, FEATURE_CATALOG, PIT_CONTRACT, PANEL_BEFORE_AFTER]:
        for h in _rows(rel)[0].keys():
            assert not h.startswith("forward_return_")
            assert not h.startswith("benchmark_excess_return_")


def test_deterministic_reconstruction() -> None:
    run_gate(ROOT)
    first = (ROOT / EVIDENCE_GAP_MAP).read_text(encoding="utf-8")
    run_gate(ROOT)
    assert first == (ROOT / EVIDENCE_GAP_MAP).read_text(encoding="utf-8")
