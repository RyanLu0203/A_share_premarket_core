from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import resolve_daily_refresh_context
from ashare_premarket.dashboard.repositories.snapshot_repository import CommittedEvidenceStore
from ashare_premarket.dashboard.repository import PremarketWorkspaceRepository
from ashare_premarket.data import runtime_calendar
from ashare_premarket.data.trading_calendar import CalendarEvidenceError, trading_calendar, trading_calendar_status
from ashare_premarket.ops.macos_launchd import (
    REFRESH_LABEL,
    WORKSPACE_LABEL,
    already_refreshed,
    launchd_python_runtime_is_stable,
    launchd_root_is_tcc_safe,
    refresh_plist,
    workspace_plist,
)


ROOT = Path(__file__).resolve().parents[1]


class _Rows:
    def to_dict(self, _mode: str) -> list[dict[str, object]]:
        return [
            {"trade_date": "2026-07-09"},
            {"trade_date": "2026-07-10"},
            {"trade_date": "2026-07-13"},
            {"trade_date": "2026-07-14"},
        ]


def _mock_calendar_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = runtime_calendar.importlib.import_module
    provider = SimpleNamespace(tool_trade_date_hist_sina=lambda: _Rows())

    def import_module(name: str) -> object:
        return provider if name == "akshare" else real_import(name)

    monkeypatch.setattr(runtime_calendar.importlib, "import_module", import_module)


def test_runtime_calendar_uses_only_approved_source_sessions_and_exposes_freshness(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_csv(
        tmp_path / "configs/project/trading_calendar.csv",
        [
            {"date": "2026-07-09", "is_trading_day": "true", "session_note": "regular"},
            {"date": "2026-07-10", "is_trading_day": "true", "session_note": "regular"},
        ],
    )
    _mock_calendar_provider(monkeypatch)

    output = runtime_calendar.sync_runtime_trading_calendar(tmp_path, allow_network=True)
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_PATH", str(output))
    monkeypatch.setenv(
        "ASHARE_TRADING_CALENDAR_METADATA_PATH",
        str(tmp_path / runtime_calendar.RUNTIME_CALENDAR_METADATA),
    )

    rows = trading_calendar(tmp_path)
    status = trading_calendar_status(tmp_path, "2026-07-13")
    assert [row["date"] for row in rows] == ["2026-07-09", "2026-07-10", "2026-07-13", "2026-07-14"]
    assert "2026-07-11" not in {row["date"] for row in rows}
    assert status["status"] == "VERIFIED"
    assert status["source"] == "akshare_sina"
    assert status["coverage_end"] == "2026-07-14"
    assert status["pit_status"] == "PASSED_SCHEDULE_EVIDENCE_ONLY"
    assert status["runtime_authority"] == "approved_provider_schedule"
    assert status["committed_fixture_consistency_status"] == "MATCH"
    assert status["committed_fixture_conflict_count"] == 0

    context = resolve_daily_refresh_context(tmp_path, execution_time="2026-07-13T07:45:00+08:00")
    assert context["calendar_status"] == "PASS"
    assert context["target_trading_date"] == "2026-07-13"
    assert context["expected_previous_trading_date"] == "2026-07-10"


def test_runtime_calendar_records_non_authoritative_committed_fixture_conflicts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_csv(
        tmp_path / "configs/project/trading_calendar.csv",
        [
            {"date": "2026-07-10", "is_trading_day": "true", "session_note": "regular"},
            {"date": "2026-07-11", "is_trading_day": "true", "session_note": "regular"},
        ],
    )
    _mock_calendar_provider(monkeypatch)

    output = runtime_calendar.sync_runtime_trading_calendar(tmp_path, allow_network=True)
    metadata_path = tmp_path / runtime_calendar.RUNTIME_CALENDAR_METADATA
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_PATH", str(output))
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_METADATA_PATH", str(metadata_path))

    assert "2026-07-11" not in output.read_text(encoding="utf-8")
    assert metadata["runtime_authority"] == "approved_provider_schedule"
    assert metadata["committed_fixture_consistency_status"] == "DIFFERENCES_RECORDED_NON_AUTHORITATIVE"
    assert metadata["committed_fixture_conflict_count"] == 1
    assert metadata["committed_fixture_conflict_dates"] == ["2026-07-11"]
    assert trading_calendar_status(tmp_path, "2026-07-13")["status"] == "VERIFIED"


def test_configured_runtime_calendar_fails_closed_if_missing_or_tampered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    committed = tmp_path / "configs/project/trading_calendar.csv"
    _write_csv(committed, [{"date": "2026-07-10", "is_trading_day": "true", "session_note": "regular"}])
    missing = tmp_path / runtime_calendar.RUNTIME_CALENDAR
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_PATH", str(missing))
    with pytest.raises(CalendarEvidenceError, match="unavailable"):
        trading_calendar(tmp_path)

    _mock_calendar_provider(monkeypatch)
    runtime_calendar.sync_runtime_trading_calendar(tmp_path, allow_network=True)
    missing.write_text(missing.read_text(encoding="utf-8") + "2026-07-15,true,tampered\n", encoding="utf-8")
    with pytest.raises(CalendarEvidenceError, match="checksum"):
        trading_calendar(tmp_path)
    assert trading_calendar_status(tmp_path, "2026-07-13")["status"] == "BLOCKED"


def test_calendar_provider_failure_does_not_replace_last_verified_runtime_evidence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _write_csv(
        tmp_path / "configs/project/trading_calendar.csv",
        [{"date": "2026-07-10", "is_trading_day": "true", "session_note": "regular"}],
    )
    _mock_calendar_provider(monkeypatch)
    output = runtime_calendar.sync_runtime_trading_calendar(tmp_path, allow_network=True)
    metadata = tmp_path / runtime_calendar.RUNTIME_CALENDAR_METADATA
    before = (output.read_bytes(), metadata.read_bytes())

    def unavailable(_name: str) -> object:
        raise ConnectionError("provider unavailable")

    monkeypatch.setattr(runtime_calendar.importlib, "import_module", unavailable)
    with pytest.raises(RuntimeError, match="approved trading-calendar source unavailable"):
        runtime_calendar.sync_runtime_trading_calendar(tmp_path, allow_network=True)
    assert (output.read_bytes(), metadata.read_bytes()) == before


def test_snapshot_resolution_recovers_stale_pointer_only_to_newer_verified_snapshot(tmp_path: Path) -> None:
    _write_snapshot(tmp_path, "2026-07-01")
    _write_snapshot(tmp_path, "2026-07-13")
    _write_pointer(tmp_path, "2026-07-01")
    store = CommittedEvidenceStore(tmp_path)

    resolution = store.resolve_snapshot()
    assert resolution["selected_date"] == "2026-07-13"
    assert resolution["resolution_status"] == "POINTER_STALE_RECOVERED"
    assert resolution["warnings"] == ["STALE_SNAPSHOT_POINTER:2026-07-01->2026-07-13"]
    assert resolution["system_blocking"] is False
    with pytest.raises(ValueError, match="live target boundary"):
        store.resolve_snapshot("2026-07-13", max_date="2026-07-01")


def test_snapshot_resolution_never_silently_uses_older_snapshot_when_latest_is_invalid(tmp_path: Path) -> None:
    _write_snapshot(tmp_path, "2026-07-01")
    _write_snapshot(tmp_path, "2026-07-13")
    _write_pointer(tmp_path, "2026-07-01")
    (tmp_path / "outputs/research/premarket_position_management/2026-07-13/data.csv").write_text(
        "value\ntampered\n", encoding="utf-8"
    )
    store = CommittedEvidenceStore(tmp_path)

    resolution = store.resolve_snapshot()
    assert resolution["selected_date"] == "2026-07-01"
    assert resolution["resolution_status"] == "LATEST_INVALID_RESEARCH_FALLBACK"
    assert resolution["stale"] is True
    assert resolution["system_blocking"] is True
    with pytest.raises(ValueError, match="checksum validation failed"):
        store.resolve_snapshot("2026-07-13", replay=True)


def test_dashboard_separates_system_research_replay_and_quant_states(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ASHARE_TRADING_CALENDAR_PATH", raising=False)
    monkeypatch.delenv("ASHARE_TRADING_CALENDAR_METADATA_PATH", raising=False)
    status = PremarketWorkspaceRepository(ROOT).status(
        mode="live", execution_time="2026-07-13T07:45:00+08:00"
    )

    assert status["system_readiness_status"] == "BLOCKED"
    assert status["freshness_code"] == "TRADING_CALENDAR_COVERAGE_MISSING"
    assert status["historical_replay_status"] == "AVAILABLE"
    assert status["research_dashboard_status"] == "AVAILABLE_WITH_WARNING"
    assert status["research_panels_enabled"] is True
    assert status["quant_page_status"] == "LOCKED_GOVERNANCE"


def test_launchd_contract_is_local_bounded_and_checksum_guarded(tmp_path: Path) -> None:
    workspace = workspace_plist(tmp_path)
    refresh = refresh_plist(tmp_path)
    assert workspace["Label"] == WORKSPACE_LABEL
    assert workspace["RunAtLoad"] is True
    assert refresh["Label"] == REFRESH_LABEL
    assert refresh["ProgramArguments"][-1] == "--allow-network"
    assert refresh["StartCalendarInterval"] == {"Hour": 8, "Minute": 0}
    assert refresh["EnvironmentVariables"]["ASHARE_ALLOW_NETWORK_INGESTION"] == "1"
    assert workspace["EnvironmentVariables"].get("ASHARE_ALLOW_NETWORK_INGESTION") is None
    assert "ASHARE_TRADING_CALENDAR_METADATA_PATH" in refresh["EnvironmentVariables"]

    snapshot_manifest = _write_snapshot(tmp_path, "2026-07-13")
    version = hashlib.sha256(snapshot_manifest.read_bytes()).hexdigest()[:16]
    latest = tmp_path / "outputs/research/daily_incremental_evidence_refresh/latest_refresh.json"
    latest.parent.mkdir(parents=True, exist_ok=True)
    latest.write_text(
        json.dumps(
            {
                "refresh_status": "SUCCEEDED",
                "target_trading_date": "2026-07-13",
                "expected_previous_trading_date": "2026-07-10",
                "snapshot_version": f"sha256:{version}",
                "snapshot_manifest_path": snapshot_manifest.relative_to(tmp_path).as_posix(),
            }
        ),
        encoding="utf-8",
    )
    context = {"target_trading_date": "2026-07-13", "expected_previous_trading_date": "2026-07-10"}
    assert already_refreshed(tmp_path, context) is True
    (snapshot_manifest.parent / "data.csv").write_text("value\ntampered\n", encoding="utf-8")
    assert already_refreshed(tmp_path, context) is False


def test_launchd_rejects_tcc_protected_roots_and_codex_cache_python(tmp_path: Path) -> None:
    home = tmp_path / "home"
    assert launchd_root_is_tcc_safe(home / "Library/Application Support/AsharePremarket", home)
    assert not launchd_root_is_tcc_safe(home / "Desktop/A_share_premarket_core_current", home)
    assert not launchd_root_is_tcc_safe(home / "Documents/A_share_premarket_core_current", home)
    assert not launchd_root_is_tcc_safe(home / "Downloads/A_share_premarket_core_current", home)

    stable = tmp_path / "stable"
    stable_python = stable / ".venv/bin/python"
    stable_python.parent.mkdir(parents=True)
    stable_python.write_text("#!/bin/sh\n", encoding="utf-8")
    assert launchd_python_runtime_is_stable(stable)

    codex = tmp_path / ".cache/codex-runtimes/runtime/python3"
    codex.parent.mkdir(parents=True)
    codex.write_text("#!/bin/sh\n", encoding="utf-8")
    unstable = tmp_path / "unstable"
    unstable_python = unstable / ".venv/bin/python"
    unstable_python.parent.mkdir(parents=True)
    unstable_python.symlink_to(codex)
    assert not launchd_python_runtime_is_stable(unstable)


def test_tencent_operational_adapter_dependency_is_pinned() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"akshare==1.18.64"' in pyproject


def test_macos_daily_refresh_explicitly_selects_live_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    import scripts.run_macos_daily_refresh as macos_refresh

    # main() intentionally mutates these in its short-lived launchd process;
    # register them with monkeypatch so the in-process test restores them.
    monkeypatch.setenv("ASHARE_ALLOW_NETWORK_INGESTION", "test-placeholder")
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_PATH", "test-placeholder")
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_METADATA_PATH", "test-placeholder")

    context = {
        "calendar_status": "PASS",
        "calendar_source": "akshare_sina",
        "calendar_coverage_end": "2026-12-31",
        "calendar_freshness_status": "CURRENT",
        "target_trading_date": "2026-07-14",
        "expected_previous_trading_date": "2026-07-13",
    }
    received: dict[str, object] = {}
    monkeypatch.setattr(
        macos_refresh,
        "sync_runtime_trading_calendar",
        lambda _root, allow_network: macos_refresh.ROOT / "outputs/local/runtime/trading_calendar.csv",
    )
    monkeypatch.setattr(macos_refresh, "resolve_daily_refresh_context", lambda _root: context)
    monkeypatch.setattr(macos_refresh, "already_refreshed", lambda _root, _context: False)

    def run_refresh(_root: Path, **kwargs: object) -> bool:
        received.update(kwargs)
        return True

    monkeypatch.setattr(macos_refresh, "run_goal_daily_incremental_evidence_refresh01", run_refresh)
    monkeypatch.setattr(sys, "argv", ["run_macos_daily_refresh.py", "--allow-network"])

    assert macos_refresh.main() == 0
    assert received["allow_network"] is True
    assert "replay_date" in received
    assert received["replay_date"] is None


def test_macos_daily_refresh_force_network_reacquisition_bypasses_shortcut(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.syspath_prepend(str(ROOT / "scripts"))
    import scripts.run_macos_daily_refresh as macos_refresh

    # main() intentionally mutates these in its short-lived launchd process;
    # register them so this in-process test cannot leak runtime paths.
    monkeypatch.setenv("ASHARE_ALLOW_NETWORK_INGESTION", "test-placeholder")
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_PATH", "test-placeholder")
    monkeypatch.setenv("ASHARE_TRADING_CALENDAR_METADATA_PATH", "test-placeholder")

    context = {
        "calendar_status": "PASS",
        "calendar_source": "akshare_sina",
        "calendar_coverage_end": "2026-12-31",
        "calendar_freshness_status": "CURRENT",
        "target_trading_date": "2026-07-14",
        "expected_previous_trading_date": "2026-07-13",
    }
    invoked = {"count": 0}
    monkeypatch.setattr(
        macos_refresh,
        "sync_runtime_trading_calendar",
        lambda _root, allow_network: macos_refresh.ROOT / "outputs/local/runtime/trading_calendar.csv",
    )
    monkeypatch.setattr(macos_refresh, "resolve_daily_refresh_context", lambda _root: context)
    monkeypatch.setattr(macos_refresh, "already_refreshed", lambda _root, _context: True)
    monkeypatch.setattr(
        macos_refresh,
        "run_goal_daily_incremental_evidence_refresh01",
        lambda _root, **_kwargs: invoked.__setitem__("count", invoked["count"] + 1) or True,
    )
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_macos_daily_refresh.py", "--allow-network", "--force-network-reacquisition"],
    )

    assert macos_refresh.main() == 0
    assert invoked["count"] == 1


def test_macos_runtime_preserves_tracked_baselines_but_keeps_immutable_evidence(
    tmp_path: Path,
) -> None:
    from scripts.run_macos_daily_refresh import preserve_tracked_runtime_baselines

    tracked = tmp_path / "outputs/research/goal_daily_incremental_evidence_refresh01_run_summary.csv"
    tracked.parent.mkdir(parents=True)
    tracked.write_text("state\ncommitted\n", encoding="utf-8")
    created_mirror = tmp_path / "outputs/research/goal_daily_incremental_evidence_refresh01_idempotency.json"
    immutable = tmp_path / "outputs/research/daily_incremental_evidence_refresh/2026-07-17/refresh_manifest.json"

    with preserve_tracked_runtime_baselines(tmp_path):
        tracked.write_text("state\nlive\n", encoding="utf-8")
        created_mirror.write_text('{"status":"PASS"}\n', encoding="utf-8")
        immutable.parent.mkdir(parents=True)
        immutable.write_text('{"refresh_status":"SUCCEEDED"}\n', encoding="utf-8")

    assert tracked.read_text(encoding="utf-8") == "state\ncommitted\n"
    assert not created_mirror.exists()
    assert immutable.is_file()


def _write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _write_snapshot(root: Path, snapshot_date: str) -> Path:
    directory = root / f"outputs/research/premarket_position_management/{snapshot_date}"
    directory.mkdir(parents=True, exist_ok=True)
    data = directory / "data.csv"
    data.write_text("value\nverified\n", encoding="utf-8")
    manifest = directory / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "snapshot_date": snapshot_date,
                "target_trading_date": snapshot_date,
                "checksums": {"data.csv": hashlib.sha256(data.read_bytes()).hexdigest()},
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return manifest


def _write_pointer(root: Path, snapshot_date: str) -> None:
    manifest = root / f"outputs/research/premarket_position_management/{snapshot_date}/manifest.json"
    pointer = root / "outputs/research/premarket_position_management/latest_manifest.json"
    pointer.write_text(
        json.dumps(
            {
                "snapshot_date": snapshot_date,
                "snapshot_manifest_path": manifest.relative_to(root).as_posix(),
                "snapshot_manifest_checksum": hashlib.sha256(manifest.read_bytes()).hexdigest(),
            }
        ),
        encoding="utf-8",
    )
