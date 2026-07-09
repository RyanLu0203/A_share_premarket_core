from __future__ import annotations

import csv
import importlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PREFIX = "outputs/research/goal_premarket_position_management_operational01_"
SNAPSHOT_ROOT = "outputs/research/premarket_position_management"
MANIFEST_PATH = "outputs/audits/goal_premarket_position_management_operational01_manifest.json"
AUDIT_PATH = "outputs/audits/goal_premarket_position_management_operational01_audit.md"
REPORT_PATH = "outputs/audits/goal_premarket_position_management_operational01_report.md"
HANDOFF_PATH = "docs/research/GOAL_PREMARKET_POSITION_MANAGEMENT_OPERATIONAL01_GOVERNANCE_HANDOFF.md"
DOC_PATH = "docs/research/GOAL_PREMARKET_POSITION_MANAGEMENT_OPERATIONAL01_PREMARKET_POSITION_MANAGEMENT.md"

REQUIRED_OUTPUTS = [
    PREFIX + "holdings_snapshot_contract.csv",
    PREFIX + "daily_data_readiness.csv",
    PREFIX + "daily_portfolio_risk_state.csv",
    PREFIX + "daily_constraint_evaluation.csv",
    PREFIX + "daily_position_band_status.csv",
    PREFIX + "daily_exposure_envelope.csv",
    PREFIX + "daily_abstention_summary.csv",
    PREFIX + "daily_warnings.csv",
    PREFIX + "immutable_snapshot_manifest.json",
    PREFIX + "operational_run_summary.csv",
    PREFIX + "shadow_experiment_contract.csv",
    PREFIX + "experiment_freeze_manifest.json",
    PREFIX + "read_only_console.md",
    SNAPSHOT_ROOT + "/latest_manifest.json",
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    HANDOFF_PATH,
    DOC_PATH,
]

FORBIDDEN_PATTERN = re.compile(r"\b(BUY|SELL|HOLD)\b|order_quantity|target_price|broker_order|live_broker", re.I)


def _module():
    try:
        return importlib.import_module("ashare_premarket.portfolio_risk.goal_premarket_position_management_operational01")
    except ModuleNotFoundError as exc:
        assert False, f"missing operational position-management module: {exc}"


def _run_gate() -> dict[str, object]:
    module = _module()
    assert module.run_goal_premarket_position_management_operational01(ROOT)
    assert module.audit_goal_premarket_position_management_operational01(ROOT)
    return json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))


def _rows(rel: str) -> list[dict[str, str]]:
    with (ROOT / rel).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


_MANIFEST: dict[str, object] | None = None


def _manifest_once() -> dict[str, object]:
    global _MANIFEST
    if _MANIFEST is None:
        _MANIFEST = _run_gate()
    return _MANIFEST


def test_required_outputs_predecessor_gate_and_governance_locks() -> None:
    manifest = _manifest_once()
    for rel in REQUIRED_OUTPUTS:
        assert (ROOT / rel).exists(), rel

    assert manifest["goal"] == "GOAL-PREMARKET-POSITION-MANAGEMENT-OPERATIONAL-01"
    assert manifest["depends_on_goal"] == "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01"
    assert manifest["predecessor_status"] == "PASS_WITH_WARNINGS"
    assert manifest["predecessor_ready_factor_count"] == 0
    assert manifest["rec_tiering_state"] == "locked_future"
    assert manifest["trading_state"] == "locked_future"
    assert manifest["broker_state"] == "locked_future"
    assert manifest["production_state"] == "locked_future"
    assert manifest["live_broker_connection_created"] is False
    assert manifest["orders_created"] is False
    assert manifest["buy_sell_hold_outputs_created"] is False
    assert manifest["target_price_outputs_created"] is False
    assert manifest["recommendation_tiering_unlocked"] is False
    assert manifest["issue10_unlocked"] is False
    assert manifest["dqn_rl_unlocked"] is False


def test_holdings_contract_validation_and_reference_mode_are_explicit() -> None:
    manifest = _manifest_once()
    assert manifest["holdings_mode"] == "research_reference_portfolio"
    assert manifest["real_holdings_snapshot_supplied"] is False
    assert manifest["holdings_fabricated"] is False

    contract = _rows(PREFIX + "holdings_snapshot_contract.csv")
    assert {row["field_name"] for row in contract} >= {
        "asof_ts",
        "portfolio_id",
        "symbol",
        "quantity",
        "market_value",
        "current_weight",
        "cash_weight",
        "source",
        "snapshot_id",
    }
    assert all(row["missing_behavior"] for row in contract)

    module = _module()
    duplicate = [
        {
            "asof_ts": "2026-06-30T08:30:00+08:00",
            "portfolio_id": "demo",
            "symbol": "000002.SZ",
            "current_weight": "0.50",
            "cash_weight": "0.00",
            "source": "manual",
            "snapshot_id": "dup",
        },
        {
            "asof_ts": "2026-06-30T08:30:00+08:00",
            "portfolio_id": "demo",
            "symbol": "000002.SZ",
            "current_weight": "0.50",
            "cash_weight": "0.00",
            "source": "manual",
            "snapshot_id": "dup",
        },
    ]
    dup_result = module.validate_holdings_snapshot(
        duplicate,
        allowed_symbols={"000002.SZ"},
        previous_trading_date="2026-06-29",
    )
    assert "duplicate_snapshot_key" in dup_result["errors"]

    stale = [
        {
            "asof_ts": "2026-06-28T08:30:00+08:00",
            "portfolio_id": "demo",
            "symbol": "000002.SZ",
            "current_weight": "1.00",
            "cash_weight": "0.00",
            "source": "manual",
            "snapshot_id": "stale",
        }
    ]
    stale_result = module.validate_holdings_snapshot(
        stale,
        allowed_symbols={"000002.SZ"},
        previous_trading_date="2026-06-29",
    )
    assert "stale_snapshot" in stale_result["errors"]


def test_daily_readiness_gate_surfaces_freshness_pit_quarantine_and_holdings_state() -> None:
    manifest = _manifest_once()
    assert manifest["daily_readiness_state"] in {"READY", "READY_WITH_WARNINGS"}
    assert manifest["pit_status"] == "passed_current_or_past_only"
    assert manifest["provider_quarantined_rows"] == 6

    rows = {row["check_id"]: row for row in _rows(PREFIX + "daily_data_readiness.csv")}
    assert set(rows) >= {
        "trading_date",
        "previous_trading_date",
        "asof_timestamp",
        "source_freshness",
        "provider_availability",
        "provider_discrepancy_state",
        "canonical_data_availability",
        "index_context_availability",
        "regime_availability",
        "holdings_snapshot_freshness",
        "holdings_snapshot_validity",
        "pit_status",
        "missingness",
        "quarantine_impact",
    }
    assert rows["source_freshness"]["state"] in {"READY", "READY_WITH_WARNINGS"}
    assert rows["holdings_snapshot_freshness"]["state"] == "READY_WITH_WARNINGS"
    assert rows["holdings_snapshot_validity"]["state"] == "READY"
    assert rows["provider_discrepancy_state"]["state"] == "READY_WITH_WARNINGS"
    assert all(row["fail_closed_behavior"] for row in rows.values())


def test_invalid_owner_holdings_snapshot_blocks_readiness_and_manifest_status() -> None:
    module = _module()
    rows, state = module._data_readiness_rows(
        trading_date="2026-06-30",
        previous_trading_date="2026-06-29",
        asof_ts="2026-06-30T08:30:00+08:00",
        canonical=[
            {
                "trade_date": "2026-06-30",
                "canonical_return_1d": "0.01",
                "no_lookahead_status": "passed_current_or_past_only",
            }
        ],
        index_rows=[{"trade_date": "2026-06-30"}],
        regime_rows=[{"trade_date": "2026-06-30"}],
        holdings={
            "mode": "invalid_holdings_snapshot_fail_closed",
            "snapshot_id": "invalid_holdings_snapshot",
            "real_snapshot_supplied": True,
            "validation": {"valid": False, "errors": ["stale_snapshot"]},
        },
        provider_rows=[],
        provider_quarantine=[],
        predecessor_manifest={"ready_factor_count": 0},
    )
    by_check = {row["check_id"]: row for row in rows}
    assert state == "BLOCKED"
    assert by_check["holdings_snapshot_validity"]["state"] == "BLOCKED"
    assert "stale_snapshot" in by_check["holdings_snapshot_validity"]["current_value"]

    manifest = module._manifest(
        predecessor_manifest={"status": "PASS_WITH_WARNINGS", "ready_factor_count": 0},
        trading_date="2026-06-30",
        asof_ts="2026-06-30T08:30:00+08:00",
        readiness_state="BLOCKED",
        holdings={
            "mode": "invalid_holdings_snapshot_fail_closed",
            "real_snapshot_supplied": True,
            "snapshot_id": "invalid_holdings_snapshot",
        },
        risk={"predecessor_risk_state": "normal_risk_review_only", "gross_exposure": "0", "cash_weight": "0"},
        bands=[],
        warnings=[],
    )
    assert manifest["status"] == "BLOCKED"


def test_daily_risk_state_constraints_and_position_band_statuses_are_non_actionable() -> None:
    manifest = _manifest_once()
    assert manifest["constraints_operationalized"] == 13
    assert manifest["symbols_evaluated"] == 41
    assert manifest["symbols_abstained"] == 12

    risk_rows = _rows(PREFIX + "daily_portfolio_risk_state.csv")
    assert len(risk_rows) == 1
    risk = risk_rows[0]
    assert risk["gross_exposure"]
    assert risk["cash_weight"]
    assert risk["portfolio_volatility"]
    assert risk["ewma_volatility"]
    assert risk["beta_to_csi300"]
    assert risk["cvar_95_daily"]
    assert risk["average_correlation"]
    assert risk["largest_risk_contributors"]
    assert risk["provider_quality_state"]
    assert risk["regime_state"]

    constraints = _rows(PREFIX + "daily_constraint_evaluation.csv")
    assert len({row["constraint_id"] for row in constraints}) == 13
    for row in constraints:
        assert row["current_value"] != ""
        assert row["threshold"] != ""
        assert row["breach"] in {"true", "false"}
        assert row["severity"] in {"none", "low", "medium", "high"}
        assert row["evidence_availability"]
        assert row["fail_closed"] in {"true", "false"}
        assert row["action_instruction"] == "none"

    statuses = _rows(PREFIX + "daily_position_band_status.csv")
    assert len(statuses) == 41
    allowed = {"BELOW_BAND", "WITHIN_BAND", "ABOVE_BAND", "ABSTAIN", "INSUFFICIENT_DATA"}
    assert {row["band_status"] for row in statuses} <= allowed
    assert sum(1 for row in statuses if row["band_status"] == "ABSTAIN") == 12
    assert int(manifest["symbols_within_band"]) == sum(1 for row in statuses if row["band_status"] == "WITHIN_BAND")
    assert int(manifest["symbols_above_band"]) == sum(1 for row in statuses if row["band_status"] == "ABOVE_BAND")
    assert int(manifest["symbols_below_band"]) == sum(1 for row in statuses if row["band_status"] == "BELOW_BAND")
    assert not FORBIDDEN_PATTERN.search((ROOT / (PREFIX + "daily_position_band_status.csv")).read_text(encoding="utf-8"))


def test_exposure_envelope_immutable_snapshot_console_and_deterministic_replay() -> None:
    first = _manifest_once()
    first_manifest_text = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    module = _module()
    assert module.run_goal_premarket_position_management_operational01(ROOT)
    second = json.loads((ROOT / MANIFEST_PATH).read_text(encoding="utf-8"))
    second_manifest_text = (ROOT / MANIFEST_PATH).read_text(encoding="utf-8")
    assert first == second
    assert first_manifest_text == second_manifest_text

    envelope = _rows(PREFIX + "daily_exposure_envelope.csv")
    assert len(envelope) == 1
    assert envelope[0]["current_gross_exposure"]
    assert envelope[0]["acceptable_gross_exposure_min"]
    assert envelope[0]["acceptable_gross_exposure_max"]
    assert envelope[0]["current_cash_weight"]
    assert envelope[0]["volatility_budget"]
    assert envelope[0]["beta_budget"]
    assert envelope[0]["risk_state"]
    assert envelope[0]["abstain"] in {"true", "false"}

    snapshot_manifest = json.loads((ROOT / (PREFIX + "immutable_snapshot_manifest.json")).read_text(encoding="utf-8"))
    snapshot_date = snapshot_manifest["snapshot_date"]
    snapshot_dir = ROOT / SNAPSHOT_ROOT / snapshot_date
    for name in [
        "manifest.json",
        "data_readiness.csv",
        "portfolio_risk_state.csv",
        "constraint_evaluation.csv",
        "position_band_status.csv",
        "exposure_envelope.csv",
        "abstention_summary.csv",
        "warnings.csv",
        "operational_run_summary.csv",
    ]:
        assert (snapshot_dir / name).exists(), name
        assert name in snapshot_manifest["checksums"]

    latest = json.loads((ROOT / SNAPSHOT_ROOT / "latest_manifest.json").read_text(encoding="utf-8"))
    assert latest["snapshot_date"] == snapshot_date
    assert latest["snapshot_manifest_path"].endswith(f"{snapshot_date}/manifest.json")

    console = (ROOT / (PREFIX + "read_only_console.md")).read_text(encoding="utf-8")
    for section in [
        "Morning Overview",
        "Portfolio Risk State",
        "Exposure Envelope",
        "Constraint Breaches",
        "Position Band Status",
        "Top Risk Contributors",
        "Abstentions",
        "Data Quality / Provider Warnings",
        "Provenance / Audit",
    ]:
        assert section in console
    assert "validated snapshot" in console.lower()
    assert "fetch providers directly" not in console.lower()
    assert "recompute covariance" not in console.lower()
    assert not FORBIDDEN_PATTERN.search(console)


def test_shadow_experiment_freeze_contract_does_not_execute_future_experiment() -> None:
    manifest = _manifest_once()
    assert manifest["shadow_experiment_prepared"] is True
    assert manifest["shadow_experiment_started"] is False
    assert manifest["paper_trading_started"] is False

    contract = _rows(PREFIX + "shadow_experiment_contract.csv")
    assert {row["field_name"] for row in contract} >= {
        "frozen_policy_set",
        "frozen_band_methodology",
        "frozen_thresholds",
        "decision_timestamp",
        "eligible_trading_days",
        "immutable_snapshot_contract",
        "shadow_ledger_contract",
        "evaluation_metrics",
    }

    freeze = json.loads((ROOT / (PREFIX + "experiment_freeze_manifest.json")).read_text(encoding="utf-8"))
    assert freeze["experiment_status"] == "prepared_not_started"
    assert freeze["future_days_fabricated"] is False
    assert freeze["paper_trading_started"] is False
    assert freeze["broker_trading_started"] is False
    assert freeze["post_start_changes_require_versioning"] is True
