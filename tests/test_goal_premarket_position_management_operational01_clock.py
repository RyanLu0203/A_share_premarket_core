from __future__ import annotations

import csv
import shutil
import tempfile
from pathlib import Path

from ashare_premarket.portfolio_risk import goal_premarket_position_management_operational01 as opm01

ROOT = Path(__file__).resolve().parents[1]


def _calendar_root(tmp_path: Path, rows: list[dict[str, str]]) -> Path:
    path = tmp_path / "configs" / "project"
    path.mkdir(parents=True)
    with (path / "trading_calendar.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "is_trading_day", "session_note"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return tmp_path


def test_daily_context_uses_execution_time_and_fresh_t_minus_one_data() -> None:
    context = opm01.resolve_run_context(
        ROOT,
        execution_time="2026-07-01T07:45:00+08:00",
        target_trading_date="2026-07-01",
    )

    assert context["execution_mode"] == "daily_operational"
    assert context["execution_time"] == "2026-07-01T07:45:00+08:00"
    assert context["generated_at"] == "2026-07-01T07:45:00+08:00"
    assert context["decision_asof_ts"] == "2026-07-01T08:30:00+08:00"
    assert context["target_trading_date"] == "2026-07-01"
    assert context["expected_previous_trading_date"] == "2026-06-30"
    assert context["data_cutoff"] == "2026-06-30"

    freshness = opm01.evaluate_canonical_freshness(["2026-06-29", "2026-06-30"], context)
    assert freshness["state"] == "READY"
    assert freshness["freshness_code"] == "FRESH_T_MINUS_ONE_DATA"


def test_current_run_with_stale_data_fails_closed_not_ready() -> None:
    context = opm01.resolve_run_context(
        ROOT,
        execution_time="2026-07-09T07:45:00+08:00",
        target_trading_date="2026-07-09",
    )

    freshness = opm01.evaluate_canonical_freshness(["2026-06-30"], context)
    assert freshness["state"] == "BLOCKED"
    assert freshness["freshness_code"] == "STALE_SOURCE_DATA"
    assert freshness["latest_available_canonical_date"] == "2026-06-30"
    assert freshness["expected_previous_trading_date"] == "2026-07-08"


def test_weekend_execution_resolves_to_next_trading_day() -> None:
    context = opm01.resolve_run_context(ROOT, execution_time="2026-07-04T09:00:00+08:00")

    assert context["execution_mode"] == "daily_operational"
    assert context["execution_date"] == "2026-07-04"
    assert context["target_trading_date"] == "2026-07-06"
    assert context["expected_previous_trading_date"] == "2026-07-03"


def test_exchange_holiday_execution_resolves_with_governed_calendar() -> None:
    local_tmp = ROOT / "outputs" / "local"
    local_tmp.mkdir(parents=True, exist_ok=True)
    tmp_path = Path(tempfile.mkdtemp(prefix="opm01_calendar_", dir=local_tmp))
    try:
        root = _calendar_root(
            tmp_path,
            [
                {"date": "2026-12-31", "is_trading_day": "true", "session_note": "regular"},
                {"date": "2027-01-01", "is_trading_day": "false", "session_note": "exchange_holiday"},
                {"date": "2027-01-02", "is_trading_day": "false", "session_note": "weekend"},
                {"date": "2027-01-03", "is_trading_day": "false", "session_note": "weekend"},
                {"date": "2027-01-04", "is_trading_day": "true", "session_note": "regular"},
            ],
        )

        context = opm01.resolve_run_context(root, execution_time="2027-01-01T08:00:00+08:00")
        assert context["target_trading_date"] == "2027-01-04"
        assert context["expected_previous_trading_date"] == "2026-12-31"
    finally:
        shutil.rmtree(tmp_path, ignore_errors=True)


def test_future_canonical_data_after_pit_cutoff_blocks() -> None:
    context = opm01.resolve_run_context(
        ROOT,
        execution_time="2026-07-01T07:45:00+08:00",
        target_trading_date="2026-07-01",
    )

    freshness = opm01.evaluate_canonical_freshness(["2026-06-30", "2026-07-01"], context)
    assert freshness["state"] == "BLOCKED"
    assert freshness["freshness_code"] == "FUTURE_DATA_AFTER_PIT_CUTOFF"


def test_deterministic_replay_is_explicit_and_separate_from_live_context() -> None:
    replay = opm01.resolve_run_context(ROOT, replay_date="2026-07-01")
    live = opm01.resolve_run_context(
        ROOT,
        execution_time="2026-07-01T09:12:34+08:00",
        target_trading_date="2026-07-01",
    )

    assert replay["execution_mode"] == "deterministic_replay"
    assert replay["target_trading_date"] == "2026-07-01"
    assert replay["generated_at"] == replay["decision_asof_ts"]
    assert live["execution_mode"] == "daily_operational"
    assert live["generated_at"] == "2026-07-01T09:12:34+08:00"
    assert live["generated_at"] != live["decision_asof_ts"]


def test_stale_canonical_data_cannot_be_ready_by_self_reference() -> None:
    context = opm01.resolve_run_context(
        ROOT,
        execution_time="2026-07-09T07:45:00+08:00",
        target_trading_date="2026-07-09",
    )

    freshness = opm01.evaluate_canonical_freshness(["2026-06-30"], context)
    assert freshness["latest_available_canonical_date"] == "2026-06-30"
    assert freshness["target_trading_date"] == "2026-07-09"
    assert freshness["state"] != "READY"
    assert freshness["freshness_code"] == "STALE_SOURCE_DATA"
