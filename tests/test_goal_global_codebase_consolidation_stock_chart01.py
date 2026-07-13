from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.governance.goal_global_codebase_consolidation_stock_chart01 import (
    AUDIT,
    MANIFEST,
    PARITY,
    _sha256,
    audit_goal_global_codebase_consolidation_stock_chart01,
    run_goal_global_codebase_consolidation_stock_chart01,
)


ROOT = Path(__file__).resolve().parents[1]


def test_global_refactor_file_hash_is_platform_line_ending_stable(tmp_path: Path) -> None:
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    lf.write_bytes(b"first\nsecond\n")
    crlf.write_bytes(b"first\r\nsecond\r\n")

    assert _sha256(lf) == _sha256(crlf)


def test_global_refactor_goal_runner_records_exact_behavior_parity() -> None:
    assert run_goal_global_codebase_consolidation_stock_chart01(ROOT) is True
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))
    parity = json.loads((ROOT / PARITY).read_text(encoding="utf-8"))

    assert manifest["status"] == "PASS"
    assert manifest["api_route_count"] == 22
    assert manifest["write_api_route_count"] == 0
    assert manifest["frontend_page_count"] == 23
    assert manifest["ready_factor_count"] == 0
    assert manifest["deleted_internal_file_count"] == 3
    assert manifest["compatibility_break_count"] == 0
    assert parity["status"] == "EXACT_PARITY"
    assert parity["critical_artifacts"]["all_exact"] is True
    assert parity["openapi"]["exact"] is True
    assert parity["api_responses"]["all_exact"] is True


def test_global_refactor_goal_audit_rejects_drift_and_keeps_locks() -> None:
    assert audit_goal_global_codebase_consolidation_stock_chart01(ROOT) is True
    audit = (ROOT / AUDIT).read_text(encoding="utf-8")
    manifest = json.loads((ROOT / MANIFEST).read_text(encoding="utf-8"))

    assert "Status: `PASS`" in audit
    assert manifest["recommendation_state"] == "locked_future"
    assert manifest["trading_state"] == "locked_future"
    assert manifest["broker_state"] == "locked_future"
    assert manifest["paper_execution_state"] == "locked_future"
    assert manifest["production_state"] == "locked_future"
    assert manifest["dqn_rl_state"] == "locked_future"


def test_deleted_frontend_internal_modules_have_no_active_references() -> None:
    deleted = [
        ROOT / "apps/premarket-workspace/src/lib/api.ts",
        ROOT / "apps/premarket-workspace/src/lib/page-data.ts",
        ROOT / "apps/premarket-workspace/src/lib/page-data.test.ts",
    ]
    assert not [path for path in deleted if path.exists()]

    active = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "apps/premarket-workspace/src").rglob("*")
        if path.suffix in {".ts", ".tsx"}
    )
    assert 'from "@/lib/page-data"' not in active
    assert 'from "@/lib/api"' not in active
