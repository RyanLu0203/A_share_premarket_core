from __future__ import annotations

import csv
from collections.abc import Iterator
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

import pytest

from ashare_premarket.core.boundary import daily_refresh_evidence_valid
from ashare_premarket.core.workflow_preservation import (
    preserve_later_review_only_capabilities,
    preserve_later_review_only_workflow_states,
)
from ashare_premarket.daily_refresh import goal_daily_incremental_evidence_refresh01 as daily_refresh
from ashare_premarket.portfolio_risk import goal_premarket_position_management_operational01 as opm01


ROOT = Path(__file__).resolve().parents[1]
PREFIX = "outputs/research/goal_daily_incremental_evidence_refresh01_"
MANIFEST = "outputs/audits/goal_daily_incremental_evidence_refresh01_manifest.json"
REPLAY_MUTABLE_OPERATIONAL_OUTPUTS = (
    "configs/project/workflow_status.csv",
    "outputs/audits/goal_daily_incremental_evidence_refresh01_manifest.json",
    "outputs/audits/goal_daily_incremental_evidence_refresh01_report.md",
    "outputs/research/daily_incremental_evidence_refresh/latest_refresh.json",
    "outputs/research/goal_daily_incremental_evidence_refresh01_experiment_readiness_contract.csv",
    "outputs/research/goal_daily_incremental_evidence_refresh01_refresh_manifest.json",
    "outputs/research/goal_daily_incremental_evidence_refresh01_run_summary.csv",
    "outputs/research/goal_daily_incremental_evidence_refresh01_validation.csv",
    *opm01.REQUIRED_ARTIFACTS,
)


@pytest.fixture
def preserve_committed_operational_refresh_state() -> Iterator[None]:
    """Keep deterministic replay validation from replacing current live evidence."""

    originals = {
        relative: (ROOT / relative).read_bytes() if (ROOT / relative).exists() else None
        for relative in REPLAY_MUTABLE_OPERATIONAL_OUTPUTS
    }
    try:
        yield
    finally:
        for relative, content in originals.items():
            path = ROOT / relative
            if content is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(content)


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _context() -> dict[str, str]:
    return {
        "execution_mode": "deterministic_replay",
        "timezone": "Asia/Shanghai",
        "execution_time": "2026-07-02T08:30:00+08:00",
        "execution_date": "2026-07-02",
        "generated_at": "2026-07-02T08:30:00+08:00",
        "decision_asof_ts": "2026-07-02T08:30:00+08:00",
        "target_trading_date": "2026-07-02",
        "expected_previous_trading_date": "2026-07-01",
        "data_cutoff": "2026-07-01",
    }


def _canonical_row(
    symbol: str,
    trade_date: str,
    close: str = "10",
    source_provider: str = "akshare_sina",
    provider_timestamp: str | None = None,
) -> dict[str, object]:
    return {
        "trade_date": trade_date,
        "symbol": symbol,
        "canonical_close": close,
        "canonical_return_1d": "0.01",
        "source_provider": source_provider,
        "provider_overlap_status": "accepted_or_no_overlap",
        "canonical_price_status": "accepted",
        "canonical_return_status": "accepted",
        "adjustment_convention_status": "unresolved_cross_provider_adjustment_convention",
        "raw_adjusted_semantics": "qfq_adjusted_primary;cross_provider_adjustment_unresolved",
        "timestamp_alignment_status": "date_level_only_no_intraday_timestamp",
        "provider_timestamp": provider_timestamp or trade_date,
        "pit_available_date": trade_date,
        "suspension_status": "trading",
        "corporate_action_discontinuity_flag": "false",
        "risk_model_eligible": "true",
        "quarantine_reason": "",
        "no_lookahead_status": "passed_current_or_past_only",
        "research_only": "true",
        "not_trading_advice": "true",
        "not_for_execution": "true",
    }


def test_incremental_merge_uses_primary_provider_without_averaging() -> None:
    base = [_canonical_row("000001.SZ", "2026-06-30", close="10")]
    incremental = [
        {
            "trade_date": "2026-07-01",
            "symbol": "000001.SZ",
            "close": "12",
            "source_provider": "akshare",
            "provider_timestamp": "2026-07-01",
            "pit_available_date": "2026-07-01",
            "no_lookahead_status": "passed_current_or_past_only",
            "suspension_status": "trading",
            "adjustment_policy": "qfq",
        }
    ]

    merged = daily_refresh.merge_incremental_evidence(base, incremental, expected_date="2026-07-01")
    latest = merged[-1]

    assert latest["canonical_close"] == "12"
    assert latest["canonical_return_1d"] == "0.2"
    assert latest["source_provider"] == "akshare"
    assert latest["provider_overlap_status"] == "single_approved_provider_no_overlap_evidence"
    assert latest["adjustment_convention_status"] == "qfq_governed_single_upstream"
    assert latest["risk_model_eligible"] == "true"
    assert daily_refresh.NO_SILENT_AVERAGING is True


def test_incremental_merge_rejects_conflicting_existing_symbol_date() -> None:
    base = [_canonical_row("000001.SZ", "2026-07-01", close="10")]
    incremental = [
        {
            "trade_date": "2026-07-01",
            "symbol": "000001.SZ",
            "close": "12",
            "source_provider": "akshare",
            "provider_timestamp": "2026-07-01",
            "pit_available_date": "2026-07-01",
            "no_lookahead_status": "passed_current_or_past_only",
            "suspension_status": "trading",
            "adjustment_policy": "qfq",
        }
    ]

    with pytest.raises(ValueError, match="conflicting_existing_symbol_date"):
        daily_refresh.merge_incremental_evidence(base, incremental, expected_date="2026-07-01")


def test_source_checksum_is_stable_across_git_line_endings(tmp_path: Path) -> None:
    lf = tmp_path / "lf.csv"
    crlf = tmp_path / "crlf.csv"
    lf.write_bytes(b"trade_date,symbol\n2026-06-30,000001.SZ\n")
    crlf.write_bytes(b"trade_date,symbol\r\n2026-06-30,000001.SZ\r\n")

    assert daily_refresh._sha256_normalized_text_file(lf) == daily_refresh._sha256_normalized_text_file(crlf)


def test_daily_refresh_atomic_write_replaces_complete_bytes_without_temp_residue(tmp_path: Path) -> None:
    path = tmp_path / "nested/evidence.json"
    daily_refresh.write_text(path, "first\n")
    daily_refresh.write_text(path, "second\n")
    assert path.read_bytes() == b"second\n"
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []


def test_interrupted_atomic_replace_preserves_last_valid_bytes(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "snapshot/latest.json"
    daily_refresh.write_text(path, "last-valid\n")

    def interrupted_replace(source: object, target: object) -> None:
        raise InterruptedError("deterministic interruption during atomic replacement")

    monkeypatch.setattr(daily_refresh.os, "replace", interrupted_replace)
    with pytest.raises(InterruptedError, match="deterministic interruption"):
        daily_refresh.write_text(path, "partial-new\n")
    assert path.read_text(encoding="utf-8") == "last-valid\n"
    assert list(path.parent.glob(f".{path.name}.*.tmp")) == []


def test_provider_attempt_idempotency_ignores_only_request_timing(tmp_path: Path) -> None:
    path = tmp_path / "attempts.csv"
    base = {field: "" for field in daily_refresh.ATTEMPT_FIELDS}
    base.update({"symbol": "000002.SZ", "status": "PASS", "attempt_ts": "first", "elapsed_seconds": "1.0"})
    assert daily_refresh._write_idempotent_provider_attempts(path, [base]) == "FIRST_IMMUTABLE_ATTEMPT_EVIDENCE_WRITE"
    rerun = {**base, "attempt_ts": "second", "elapsed_seconds": "2.0"}
    assert daily_refresh._write_idempotent_provider_attempts(path, [rerun]) == "PASS_SEMANTIC_MATCH_EXISTING_IMMUTABLE_EVIDENCE"
    with pytest.raises(RuntimeError, match="refuse_non_idempotent_provider_attempt_overwrite"):
        daily_refresh._write_idempotent_provider_attempts(path, [{**rerun, "status": "FAIL"}])


@pytest.mark.parametrize(
    ("rows", "required_symbols", "source_checksum", "expected_checksum", "reason"),
    [
        ([_canonical_row("000001.SZ", "2026-06-30")], {"000001.SZ"}, "same", "same", "STALE_SOURCE_DATA"),
        ([_canonical_row("000001.SZ", "2026-07-01")], {"000001.SZ", "000002.SZ"}, "same", "same", "MISSING_REQUIRED_EVIDENCE"),
        ([_canonical_row("000001.SZ", "2026-07-01", source_provider="unknown")], {"000001.SZ"}, "same", "same", "INVALID_PROVIDER_STATE"),
        ([_canonical_row("000001.SZ", "2026-07-01", provider_timestamp="2026-07-02")], {"000001.SZ"}, "same", "same", "INVALID_TIMESTAMP"),
        ([_canonical_row("000001.SZ", "2026-07-01")], {"000001.SZ"}, "actual", "expected", "CHECKSUM_MISMATCH"),
    ],
)
def test_evidence_validation_fails_closed_with_stable_reason_codes(
    rows: list[dict[str, object]],
    required_symbols: set[str],
    source_checksum: str,
    expected_checksum: str,
    reason: str,
) -> None:
    result = daily_refresh.validate_refresh_evidence(
        _context(),
        rows,
        required_symbols=required_symbols,
        source_checksum=source_checksum,
        expected_source_checksum=expected_checksum,
    )

    assert result["status"] == "BLOCKED"
    assert reason in result["reason_codes"]
    assert all(row["fail_closed"] == "true" for row in result["rows"])


def test_validation_failure_does_not_call_opm(tmp_path: Path) -> None:
    calendar = [
        {"date": "2026-06-30", "is_trading_day": "true", "session_note": "regular"},
        {"date": "2026-07-01", "is_trading_day": "true", "session_note": "regular"},
        {"date": "2026-07-02", "is_trading_day": "true", "session_note": "regular"},
    ]
    _write_csv(tmp_path / "configs/project/trading_calendar.csv", calendar)
    _write_csv(
        tmp_path / daily_refresh.CANONICAL_MARKET,
        [_canonical_row("000001.SZ", "2026-06-30")],
    )
    _write_csv(
        tmp_path / daily_refresh.REFERENCE_PORTFOLIO,
        [{"symbol": "000001.SZ", "reference_weight": "1"}],
    )
    called = False

    def fake_opm(*args: object, **kwargs: object) -> bool:
        nonlocal called
        called = True
        return True

    result = daily_refresh.run_goal_daily_incremental_evidence_refresh01(
        tmp_path,
        replay_date="2026-07-02",
        opm_runner=fake_opm,
    )

    latest = json.loads((tmp_path / daily_refresh.LATEST_REFRESH).read_text(encoding="utf-8"))
    assert result is False
    assert called is False
    goal_manifest = json.loads((tmp_path / daily_refresh.MANIFEST).read_text(encoding="utf-8"))
    assert goal_manifest["status"] == "PASS"
    assert goal_manifest["refresh_fail_closed"] is True
    assert goal_manifest["opm_executed"] is False
    assert latest["refresh_status"] == "BLOCKED"
    assert "STALE_SOURCE_DATA" in latest["blocked_reasons"]
    assert latest["snapshot_manifest_path"] == ""


def test_refresh_passes_deterministic_decision_clock_to_immutable_opm_snapshot(tmp_path: Path) -> None:
    _write_csv(
        tmp_path / "configs/project/trading_calendar.csv",
        [
            {"date": "2026-06-30", "is_trading_day": "true", "session_note": "regular"},
            {"date": "2026-07-01", "is_trading_day": "true", "session_note": "regular"},
            {"date": "2026-07-02", "is_trading_day": "true", "session_note": "regular"},
        ],
    )
    _write_csv(tmp_path / daily_refresh.CANONICAL_MARKET, [_canonical_row("000001.SZ", "2026-06-30")])
    _write_csv(tmp_path / daily_refresh.REFERENCE_PORTFOLIO, [{"symbol": "000001.SZ", "reference_weight": "1"}])
    evidence = tmp_path / "incremental.csv"
    _write_csv(
        evidence,
        [
            {
                "trade_date": "2026-07-01",
                "symbol": "000001.SZ",
                "close": "11",
                "source_provider": "akshare",
                "provider_timestamp": "2026-07-01",
                "pit_available_date": "2026-07-01",
                "no_lookahead_status": "passed_current_or_past_only",
                "suspension_status": "trading",
                "adjustment_policy": "qfq",
            }
        ],
    )
    received: dict[str, object] = {}

    def fake_opm(*args: object, **kwargs: object) -> bool:
        received.update(kwargs)
        return True

    result = daily_refresh.run_goal_daily_incremental_evidence_refresh01(
        tmp_path,
        execution_time="2026-07-02T09:01:02+08:00",
        target_trading_date="2026-07-02",
        replay_date=None,
        evidence_file=evidence,
        opm_runner=fake_opm,
    )

    assert result is False  # the fake runner intentionally writes no snapshot
    assert received["execution_time"] == "2026-07-02T08:30:00+08:00"
    assert received["target_trading_date"] == "2026-07-02"
    assert received["replay_date"] is None


def test_calendar_coverage_gap_is_fail_closed_without_guessing_a_trading_day(tmp_path: Path) -> None:
    _write_csv(
        tmp_path / "configs/project/trading_calendar.csv",
        [{"date": "2026-07-10", "is_trading_day": "true", "session_note": "regular"}],
    )
    context = daily_refresh.resolve_daily_refresh_context(
        tmp_path,
        execution_time="2026-07-11T08:00:00+08:00",
        replay_date=None,
    )

    assert context["calendar_status"] == "BLOCKED"
    assert context["calendar_reason"] == "TRADING_CALENDAR_COVERAGE_MISSING"
    assert context["target_trading_date"] == "UNRESOLVED"
    assert context["expected_previous_trading_date"] == "UNRESOLVED"


def test_opm_accepts_only_repository_local_validated_canonical_evidence() -> None:
    local_root = ROOT / "outputs/local"
    local_root.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix="daily_refresh_opm_", dir=local_root))
    try:
        candidate = temp_dir / "canonical_market_data.csv"
        candidate.write_bytes((ROOT / daily_refresh.CANONICAL_MARKET).read_bytes())
        relative = candidate.relative_to(ROOT).as_posix()
        result = opm01._build(
            ROOT,
            replay_date="2026-07-01",
            canonical_evidence_path=relative,
            refresh_metadata={"goal": daily_refresh.GOAL_ID, "evidence_mode": "local_incremental_evidence"},
        )
        snapshot = result["snapshot_manifest"]
        assert snapshot["canonical_evidence_path"] == relative
        assert snapshot["canonical_evidence_checksum"] == hashlib.sha256(candidate.read_bytes()).hexdigest()
        assert snapshot["daily_refresh_lineage"]["goal"] == daily_refresh.GOAL_ID
        assert daily_refresh.GOAL_ID in snapshot["source_lineage"]

        with pytest.raises(ValueError, match="inside repository root"):
            opm01._build(ROOT, replay_date="2026-07-01", canonical_evidence_path=ROOT.parent / "outside.csv")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_checksummed_canonical_base_preserves_line_endings_across_checkouts() -> None:
    attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")

    assert (
        "outputs/research/goal_premarket_portfolio_risk_management01_canonical_market_data.csv -text"
        in attributes
    )


def test_goal_replay_is_deterministic_integrates_opm_and_keeps_locks(
    preserve_committed_operational_refresh_state: None,
) -> None:
    assert daily_refresh.run_goal_daily_incremental_evidence_refresh01(ROOT) is True
    first = (ROOT / MANIFEST).read_text(encoding="utf-8")
    assert daily_refresh.audit_goal_daily_incremental_evidence_refresh01(ROOT) is True
    assert daily_refresh.run_goal_daily_incremental_evidence_refresh01(ROOT) is True
    second = (ROOT / MANIFEST).read_text(encoding="utf-8")

    assert first == second
    manifest = json.loads(first)
    assert manifest["goal"] == "GOAL-DAILY-INCREMENTAL-EVIDENCE-REFRESH-01"
    assert manifest["status"] == "PASS"
    assert manifest["refresh_status"] == "SUCCEEDED"
    assert manifest["validation_status"] == "PASS"
    assert manifest["opm_executed"] is True
    assert manifest["opm_snapshot_integrity"] == "VERIFIED"
    assert manifest["risk_model_recalculated"] is False
    assert manifest["risk_model_source"] == "validated_predecessor_portfolio_risk_outputs"
    assert manifest["ready_factor_count"] == 0
    assert manifest["recommendation_state"] == "locked_future"
    assert manifest["trading_state"] == "locked_future"
    assert manifest["orders_created"] is False
    assert manifest["paper_trading_started"] is False

    latest = json.loads((ROOT / daily_refresh.LATEST_REFRESH).read_text(encoding="utf-8"))
    assert latest["target_trading_date"] == "2026-07-01"
    assert latest["expected_previous_trading_date"] == "2026-06-30"
    assert latest["latest_available_data_date"] == "2026-06-30"
    assert latest["execution_mode"] == "deterministic_replay"
    assert latest["last_successful_refresh_time"] == "2026-07-01T08:30:00+08:00"
    assert latest["snapshot_version"]
    assert latest["refresh_manifest_checksum"]
    refresh_manifest_path = ROOT / latest["refresh_manifest_path"]
    assert hashlib.sha256(refresh_manifest_path.read_bytes()).hexdigest() == latest["refresh_manifest_checksum"]

    with (ROOT / (PREFIX + "experiment_readiness_contract.csv")).open(encoding="utf-8") as handle:
        experiment = list(csv.DictReader(handle))
    assert {row["field_name"] for row in experiment} == {
        "experiment_date_range",
        "snapshot_lineage",
        "evaluation_metadata",
        "baseline_reference",
    }
    assert all(row["experiment_status"] == "PREPARED_NOT_STARTED" for row in experiment)
    assert all(row["performance_claim"] == "none" for row in experiment)
    assert daily_refresh_evidence_valid(ROOT) is True

    workflows: dict[str, dict[str, str]] = {}
    capabilities: dict[str, object] = {"dashboard": True, "paper_trading": True}
    preserve_later_review_only_workflow_states(ROOT, workflows)
    preserve_later_review_only_capabilities(ROOT, capabilities)
    assert workflows[daily_refresh.WORKFLOW_ID]["status"] == "implemented_research_only"
    assert capabilities[daily_refresh.CAPABILITY_KEY] == "implemented_research_only"
    assert capabilities["dashboard"] is False
    assert capabilities["paper_trading"] is False
