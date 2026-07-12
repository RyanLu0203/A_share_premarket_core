from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from ashare_premarket.data import runtime_calendar
from ashare_premarket.data.trading_calendar import trading_calendar
from ashare_premarket.ops.macos_launchd import REFRESH_LABEL, WORKSPACE_LABEL, already_refreshed, refresh_plist, workspace_plist


class _Rows:
    def to_dict(self, _mode: str) -> list[dict[str, object]]:
        return [{"trade_date": "2026-07-10"}, {"trade_date": "2026-07-13"}]


def test_runtime_calendar_is_source_backed_and_local(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    committed = tmp_path / "configs/project/trading_calendar.csv"
    committed.parent.mkdir(parents=True)
    committed.write_text("date,is_trading_day,session_note\n2026-07-10,true,regular\n", encoding="utf-8")
    monkeypatch.setattr(runtime_calendar.importlib, "import_module", lambda _name: SimpleNamespace(tool_trade_date_hist_sina=lambda: _Rows()))

    output = runtime_calendar.sync_runtime_trading_calendar(tmp_path, allow_network=True)

    assert output == tmp_path / runtime_calendar.RUNTIME_CALENDAR
    text = output.read_text(encoding="utf-8")
    assert "2026-07-11,false,weekend" in text
    assert "2026-07-13,true,regular_source_akshare_sina" in text


def test_trading_calendar_honors_root_confined_runtime_override(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    committed = tmp_path / "configs/project/trading_calendar.csv"
    committed.parent.mkdir(parents=True)
    committed.write_text("date,is_trading_day,session_note\n2026-07-10,true,regular\n", encoding="utf-8")
    runtime = tmp_path / "outputs/local/runtime/trading_calendar.csv"
    runtime.parent.mkdir(parents=True)
    runtime.write_text("date,is_trading_day,session_note\n2026-07-13,true,source\n", encoding="utf-8")
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_PATH", runtime.relative_to(tmp_path).as_posix())
    assert trading_calendar(tmp_path)[0]["date"] == "2026-07-13"
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_PATH", str(tmp_path.parent / "outside.csv"))
    with pytest.raises(ValueError, match="inside repository root"):
        trading_calendar(tmp_path)


def test_launchd_plists_define_persistent_workspace_and_weekday_refresh(tmp_path: Path) -> None:
    workspace = workspace_plist(tmp_path)
    refresh = refresh_plist(tmp_path)

    assert workspace["Label"] == WORKSPACE_LABEL
    assert workspace["RunAtLoad"] is True
    assert workspace["KeepAlive"] is True
    assert refresh["Label"] == REFRESH_LABEL
    assert refresh["ProgramArguments"][-1] == "--allow-network"
    assert {item["Weekday"] for item in refresh["StartCalendarInterval"]} == {2, 3, 4, 5, 6}
    assert refresh["EnvironmentVariables"]["ASHARE_ALLOW_NETWORK_INGESTION"] == "1"
    assert workspace["EnvironmentVariables"].get("ASHARE_ALLOW_NETWORK_INGESTION") is None


def test_macos_runner_skips_only_verified_same_target_success(tmp_path: Path) -> None:
    snapshot = tmp_path / "outputs/research/premarket_position_management/2026-07-13/manifest.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("{}\n", encoding="utf-8")
    latest = tmp_path / "outputs/research/daily_incremental_evidence_refresh/latest_refresh.json"
    latest.parent.mkdir(parents=True)
    latest.write_text(
        json.dumps(
            {
                "refresh_status": "SUCCEEDED",
                "target_trading_date": "2026-07-13",
                "expected_previous_trading_date": "2026-07-10",
                "snapshot_version": "sha256:test",
                "snapshot_manifest_path": str(snapshot.relative_to(tmp_path)),
            }
        ),
        encoding="utf-8",
    )
    context = {"target_trading_date": "2026-07-13", "expected_previous_trading_date": "2026-07-10"}
    assert already_refreshed(tmp_path, context) is True
    assert already_refreshed(tmp_path, {**context, "target_trading_date": "2026-07-14"}) is False
    latest.write_text("{}\n", encoding="utf-8")
    immutable = tmp_path / "outputs/research/daily_incremental_evidence_refresh/2026-07-13/refresh_manifest.json"
    immutable.parent.mkdir(parents=True)
    immutable.write_text(
        json.dumps(
            {
                "refresh_status": "SUCCEEDED",
                "target_trading_date": "2026-07-13",
                "expected_previous_trading_date": "2026-07-10",
                "snapshot_version": "sha256:test",
                "snapshot_manifest_path": str(snapshot.relative_to(tmp_path)),
            }
        ),
        encoding="utf-8",
    )
    assert already_refreshed(tmp_path, context) is True
