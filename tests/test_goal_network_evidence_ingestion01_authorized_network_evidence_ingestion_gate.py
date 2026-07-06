from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

from ashare_premarket.data_expansion.goal_network_evidence_ingestion01 import (
    ACQUISITION_LOG,
    DAILY_PANEL,
    FALSE_BOUNDARY_KEYS,
    INDEX_PANEL,
    LEAKAGE_QUARANTINE,
    MANIFEST_PATH,
    MATERIALITY,
    PIT_CONTRACT,
    SOURCE_SELECTION,
    SYMBOL_BEFORE_AFTER,
    audit_goal_network_evidence_ingestion01_authorized_network_evidence_ingestion_gate as audit_gate,
    goal_network_evidence_ingestion01_valid_evidence,
    run_goal_network_evidence_ingestion01_authorized_network_evidence_ingestion_gate as run_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _rows(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as h:
        return list(csv.DictReader(h))


def _manifest() -> dict:
    return json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))


def test_gate_audit_evidence_valid_offline() -> None:
    # runs entirely offline against the committed evidence snapshot
    assert run_gate(ROOT)
    assert audit_gate(ROOT)
    assert goal_network_evidence_ingestion01_valid_evidence(ROOT)


def test_acquisition_script_refuses_without_authorization() -> None:
    env = {k: v for k, v in _env().items() if k != "ASHARE_ALLOW_NETWORK_INGESTION"}
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/acquire_goal_network_evidence_ingestion01.py")],
        cwd=ROOT, capture_output=True, text=True, env=env,
    )
    assert result.returncode == 2
    assert "REFUSED" in result.stdout


def test_no_credentials_or_secrets_persisted() -> None:
    run_gate(ROOT)
    m = _manifest()
    assert m["credentials_embedded"] is False
    assert m["tokens_or_secrets_persisted"] is False
    assert m["raw_payloads_committed"] is False
    for rel in ["outputs/research/network_ingestion/evidence_bundle_manifest.json", SOURCE_SELECTION, ACQUISITION_LOG]:
        text = (ROOT / rel).read_text(encoding="utf-8", errors="ignore").lower()
        for pat in ("token=", "password=", "secret=", "api_key=", "-----begin", "akia"):
            assert pat not in text


def test_pit_contract_and_leakage_quarantine() -> None:
    run_gate(ROOT)
    pit = _rows(PIT_CONTRACT)
    assert pit
    for r in pit:
        assert r["event_timestamp"] and r["availability_timestamp"] and r["pit_declaration"]
    for r in _rows(LEAKAGE_QUARANTINE):
        assert r["result"] == "pass"  # all PIT/leakage checks pass -> nothing needs quarantine
    # no forward-return columns in acquired panels
    for rel in [DAILY_PANEL, INDEX_PANEL]:
        for h in _rows(rel)[0].keys():
            assert not h.startswith("forward_return_")


def test_universe_selection_pit_safe_and_disclosed() -> None:
    run_gate(ROOT)
    row = _rows(SYMBOL_BEFORE_AFTER)[0]
    assert row["future_informed_selection"] == "false"
    assert row["cherry_picking"] == "false"
    assert "survivorship" in row["selection_contract"]


def test_materiality_derived_not_fabricated() -> None:
    run_gate(ROOT)
    m = _manifest()
    # after-values must equal what the offline evidence actually contains (no hardcoded inflation)
    daily = _rows(DAILY_PANEL)
    coverage_ok = [c for c in _rows("outputs/research/network_ingestion/symbol_coverage.csv") if c["status"] == "acquired"]
    assert m["symbols_with_independent_evidence"] == len(coverage_ok)  # crosscheck coverage = actually acquired
    assert m["dates_after"] == len({r["trade_date"] for r in daily})
    mat = {r["criterion"]: r["met"] for r in _rows(MATERIALITY)}
    assert mat["materially_expanded"] == str(m["materially_expanded"]).lower()


def test_no_downstream_auto_unlock_and_locks_preserved() -> None:
    run_gate(ROOT)
    m = _manifest()
    for k in FALSE_BOUNDARY_KEYS:
        assert m[k] is False, k
    assert m["ready_factor_count"] == 0
    assert m["readiness_thresholds_preserved"] is True
    assert m["workflow_status_modified_by_this_goal"] is False
    wf = {r["workflow_id"]: r for r in _rows("configs/project/workflow_status.csv")}
    assert wf["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
    assert wf["dashboard_daily_report"]["status"] == "locked_future"


def test_deterministic_reconstruction() -> None:
    run_gate(ROOT)
    first = (ROOT / MATERIALITY).read_text(encoding="utf-8")
    run_gate(ROOT)
    assert first == (ROOT / MATERIALITY).read_text(encoding="utf-8")


def _env() -> dict:
    import os
    return dict(os.environ)
