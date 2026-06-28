from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from ashare_premarket.mvp.goal_mvp01 import (
    ALLOWED_PRIORITY_LEVELS,
    FALSE_BOUNDARY_KEYS,
    FORBIDDEN_TABLE_LABELS,
    MARKET_CONTEXT_SUMMARY_PATH,
    SYMBOL_DIAGNOSTIC_FIELDS,
    SYMBOL_TABLE_PATH,
    audit_goal_mvp01_premarket_research_terminal_gate,
    evaluate_goal_mvp01_premarket_research_terminal,
    run_goal_mvp01_premarket_research_terminal_gate,
)

ROOT = Path(__file__).resolve().parents[1]


def _read_csv(path: str) -> list[dict[str, str]]:
    with (ROOT / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def test_goal_mvp01_evaluation_uses_latest_committed_date_and_required_schema() -> None:
    result = evaluate_goal_mvp01_premarket_research_terminal(ROOT)
    manifest = result["manifest"]

    assert manifest["status"] == "PASS_WITH_WARNINGS"
    assert manifest["report_date"] == "2026-05-21"
    assert manifest["run_mode"] == "committed_evidence_replay"
    assert manifest["symbol_table_row_count"] == 50
    assert manifest["ready_factor_count"] == 0
    assert result["symbol_rows"]
    assert list(result["symbol_rows"][0]) == SYMBOL_DIAGNOSTIC_FIELDS


def test_goal_mvp01_runner_audit_outputs_and_boundaries() -> None:
    assert run_goal_mvp01_premarket_research_terminal_gate(ROOT)
    assert audit_goal_mvp01_premarket_research_terminal_gate(ROOT)

    symbol_rows = _read_csv(SYMBOL_TABLE_PATH)
    market_rows = _read_csv(MARKET_CONTEXT_SUMMARY_PATH)
    manifest = json.loads((ROOT / "outputs/mvp/goal_mvp01_run_manifest.json").read_text(encoding="utf-8"))

    assert len(symbol_rows) == 50
    assert list(symbol_rows[0]) == SYMBOL_DIAGNOSTIC_FIELDS
    assert {row["report_date"] for row in symbol_rows} == {"2026-05-21"}
    assert len({(row["report_date"], row["symbol"]) for row in symbol_rows}) == len(symbol_rows)
    assert all(row["review_priority_level"] in ALLOWED_PRIORITY_LEVELS for row in symbol_rows)
    assert market_rows[0]["run_mode"] == "committed_evidence_replay"

    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    assert manifest["mvp_research_terminal_generated"] is True
    assert manifest["goal_alpha_factor_candidate01_locked_future"] is True
    assert manifest["goal_rec_tiering01_locked_future"] is True
    assert manifest["dashboard_daily_report_locked_future"] is True

    for row in symbol_rows:
        for value in row.values():
            tokens = re.split(r"[^A-Za-z0-9_]+", value.upper())
            assert not any(token in FORBIDDEN_TABLE_LABELS for token in tokens)

    workflow_rows = _read_csv("configs/project/workflow_status.csv")
    by_id = {row["workflow_id"]: row for row in workflow_rows}
    assert by_id["goal_mvp01_premarket_research_terminal_gate"]["status"] == "implemented_mvp_research_only"
    assert by_id["goal_alpha_factor_candidate01_research_gate"]["status"] in {
        "locked_future",
        "implemented_research_only",
    }
    assert by_id["goal_rec_tiering01_recommendation_score_tiering_gate"]["status"] == "locked_future"
