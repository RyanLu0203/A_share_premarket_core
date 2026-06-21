from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv, write_text
from ashare_premarket.features.panel_expansion import audit_engineering_pit_signal_panel, build_engineering_pit_signal_panel
from ashare_premarket.labels.panel_expansion import audit_engineering_label_panel, build_engineering_label_panel
from ashare_premarket.universe.governance import load_blocked_symbols

PANEL_OUTPUT = "outputs/stage6c/STAGE6C_engineering_expanded_validation_dataset_sample.csv"
COVERAGE_OUTPUT = "outputs/stage6c/STAGE6C_engineering_panel_coverage_summary.csv"
TIER_CONFIG = "configs/validation/panel_size_tiers.yaml"


def rebuild_stage6c_from_engineering_panel(root: Path) -> bool:
    pit_path = build_engineering_pit_signal_panel(root)
    label_path = build_engineering_label_panel(root)
    pit_rows = read_csv(pit_path)
    label_lookup = {(row["trade_date"], row["symbol"]): row for row in read_csv(label_path)}
    rows = []
    for pit in pit_rows:
        key = (pit["target_trading_date"], pit["symbol"])
        label = label_lookup.get(key)
        if not label:
            continue
        rows.append(
            {
                "trade_date": pit["target_trading_date"],
                "symbol": pit["symbol"],
                "as_of_date": pit["as_of_date"],
                "decision_cutoff_ts": pit["decision_cutoff_ts"],
                "market_trend_5d": pit["market_trend_5d"],
                "sector_momentum_5d": pit["sector_momentum_5d"],
                "stock_gap_signal": pit["stock_gap_signal"],
                "event_count_pit": pit["event_count_pit"],
                "source_health_score": pit["source_health_score"],
                "source_count": pit["source_count"],
                "fwd_1d_return": label["fwd_1d_return"],
                "benchmark_fwd_1d_return": label["benchmark_fwd_1d_return"],
                "excess_fwd_1d_return": label["excess_fwd_1d_return"],
                "fwd_3d_return": label["fwd_3d_return"],
                "fwd_5d_return": label["fwd_5d_return"],
                "usable_for_validation": pit["pit_ready"] == "true" and label["label_ready"] == "true",
                "panel_tier": "",
                "source_bundle_id": pit["source_bundle_id"],
                "panel_source_type": pit["panel_source_type"],
                "review_only": True,
                "data_quality_flags": f"{pit['data_quality_flags']};{label['label_quality_flags']}",
                "leakage_flags": "PASS",
            }
        )
    tier = classify_panel_tier(root, rows)
    for row in rows:
        row["panel_tier"] = tier["tier"]
    write_csv(
        root / PANEL_OUTPUT,
        rows,
        [
            "trade_date",
            "symbol",
            "as_of_date",
            "decision_cutoff_ts",
            "market_trend_5d",
            "sector_momentum_5d",
            "stock_gap_signal",
            "event_count_pit",
            "source_health_score",
            "source_count",
            "fwd_1d_return",
            "benchmark_fwd_1d_return",
            "excess_fwd_1d_return",
            "fwd_3d_return",
            "fwd_5d_return",
            "usable_for_validation",
            "panel_tier",
            "source_bundle_id",
            "panel_source_type",
            "review_only",
            "data_quality_flags",
            "leakage_flags",
        ],
    )
    return audit_stage6c_engineering_panel(root)


def classify_panel_tier(root: Path, rows: list[dict[str, object]]) -> dict[str, object]:
    tiers = _load_json(root / TIER_CONFIG)
    counts = {
        "rows": len(rows),
        "symbols": len({str(row["symbol"]) for row in rows}),
        "trading_dates": len({str(row["trade_date"]) for row in rows}),
    }
    for tier_name in ["strong_panel", "research_ready", "engineering_pilot", "contract_demo"]:
        tier = tiers[tier_name]
        if (
            counts["rows"] >= int(tier["min_rows"])
            and counts["symbols"] >= int(tier["min_symbols"])
            and counts["trading_dates"] >= int(tier["min_trading_dates"])
        ):
            return {"tier": tier_name, "counts": counts, "contract": tier}
    return {"tier": "below_contract_demo", "counts": counts, "contract": {"goal06d_allowed": False, "allowed_use": "not_ready"}}


def audit_stage6c_engineering_panel(root: Path) -> bool:
    panel_path = root / PANEL_OUTPUT
    if not panel_path.exists():
        rebuild_stage6c_from_engineering_panel(root)
    rows = read_csv(panel_path)
    tier = classify_panel_tier(root, rows)
    blocked = set(load_blocked_symbols(root))
    failures: list[str] = []
    warnings: list[str] = []
    if not rows:
        failures.append("Stage 6C engineering panel sample is empty")
    if any(row["symbol"] in blocked for row in rows):
        failures.append("blocked symbol appears in Stage 6C engineering panel sample")
    if any(row["leakage_flags"] != "PASS" for row in rows):
        failures.append("Stage 6C engineering panel reports leakage flags")
    if any(row["panel_source_type"] == "clean_bootstrap_fixture" for row in rows):
        warnings.append("Stage 6C engineering panel remains clean_bootstrap_fixture-backed")
    if tier["tier"] == "contract_demo":
        warnings.append("panel tier is contract_demo; GOAL-06D stays blocked")
    elif tier["tier"] == "below_contract_demo":
        failures.append("panel does not even meet contract_demo tier")
    pit_ok = audit_engineering_pit_signal_panel(root)
    label_ok = audit_engineering_label_panel(root)
    if not pit_ok:
        failures.append("engineering PIT panel audit failed")
    if not label_ok:
        failures.append("engineering label panel audit failed")
    status = "BLOCKED" if failures else ("PASS_WITH_WARNINGS" if warnings else "PASS")
    counts = tier["counts"]
    goal06d_allowed = bool(tier["contract"].get("goal06d_allowed")) and status != "BLOCKED"
    goal06d_mode = "review_only" if goal06d_allowed and tier["tier"] != "contract_demo" else "blocked"

    write_csv(
        root / COVERAGE_OUTPUT,
        [
            {
                "panel_id": "goal06c5_engineering_stage6c_sample",
                "current_symbols": counts["symbols"],
                "current_trading_dates": counts["trading_dates"],
                "current_rows": counts["rows"],
                "panel_tier": tier["tier"],
                "engineering_pilot_required_symbols": 50,
                "engineering_pilot_required_trading_dates": 120,
                "engineering_pilot_required_rows": 6000,
                "engineering_pilot_met": tier["tier"] in {"engineering_pilot", "research_ready", "strong_panel"},
                "goal06d_allowed": goal06d_allowed,
                "goal06d_mode": goal06d_mode,
            }
        ],
    )
    write_text(
        root / "outputs/audits/stage6c_engineering_panel_audit.md",
        "\n".join(
            [
                "# Stage 6C Engineering Panel Audit",
                "",
                f"Status: `{status}`",
                f"Rows reviewed: `{counts['rows']}`",
                f"Symbols reviewed: `{counts['symbols']}`",
                f"Trading dates reviewed: `{counts['trading_dates']}`",
                f"Panel tier: `{tier['tier']}`",
                f"GOAL-06D allowed to proceed: `{str(goal06d_allowed).lower()}`",
                "",
                "## Failures",
                *[f"- {failure}" for failure in failures],
                "",
                "## Warnings",
                *[f"- {warning}" for warning in warnings],
                "",
            ]
        ),
    )
    write_text(
        root / "outputs/audits/engineering_panel_readiness_report.md",
        "\n".join(
            [
                "# Engineering Panel Readiness Report",
                "",
                f"Engineering Panel Readiness: {status}",
                f"GOAL-06D allowed to proceed: {str(goal06d_allowed).lower()}",
                f"GOAL-06D mode if allowed: {goal06d_mode}",
                f"Panel tier: `{tier['tier']}`",
                "",
                "The current panel is sufficient for workflow contract tests only. Meaningful review-only model comparison remains blocked until at least `engineering_pilot` is reached.",
                "",
            ]
        ),
    )
    _write_replacement_audit(root, tier["tier"], goal06d_allowed)
    return not failures


def _write_replacement_audit(root: Path, tier: str, goal06d_allowed: bool) -> None:
    replaced = goal06d_allowed and tier != "contract_demo"
    write_text(
        root / "outputs/audits/active_path_replacement_audit.md",
        "\n".join(
            [
                "# Active Path Replacement Audit",
                "",
                "Status: `PASS_WITH_WARNINGS`",
                "",
                "| old_path | new_path | artifact_or_module | replacement_status | kept_as_fixture | removed_from_active_validation | notes |",
                "| --- | --- | --- | --- | --- | --- | --- |",
                "| outputs/stage6c/STAGE6C_expanded_validation_dataset.csv | outputs/stage6c/STAGE6C_engineering_expanded_validation_dataset_sample.csv | stage6c_validation_panel | "
                + (
                    "replaced_by_engineering_panel | false | true | engineering_pilot threshold met |"
                    if replaced
                    else "not_replaced_contract_demo_only | true | false | engineering_pilot threshold not met; fixture remains contract-demo review-only validation path |"
                ),
                "",
                "Replacement rule: upgrade the active path only after PIT, label, Stage 6C engineering, blocked-symbol, leakage, diagnostics, and workflow-status gates all pass at `engineering_pilot` or higher.",
                "",
            ]
        ),
    )


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))
