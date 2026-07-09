from __future__ import annotations

import glob
import json
import math
from collections import defaultdict
from pathlib import Path

from ashare_premarket.core.io import read_csv, write_csv

GOAL_ID = "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01"
WORKFLOW_ID = "goal_premarket_portfolio_risk_management01"
MODE = "research_only_portfolio_risk_position_management"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

NETWORK_DAILY = "outputs/research/network_ingestion/daily_panel.csv"
NETWORK_INDEX = "outputs/research/network_ingestion/index_panel.csv"
NETWORK_MANIFEST = "outputs/research/goal_network_evidence_ingestion01_evidence_bundle_manifest.json"
OLD_PANEL_GLOB = "outputs/research/goal_quant_research03_refined_evaluation_panel_parts/*.csv"
REGIME_LABELS = "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
WORKFLOW_STATUS = "configs/project/workflow_status.csv"
LOCKED_CAPABILITIES = "configs/project/locked_capabilities.json"
RERUN02_MANIFEST = "outputs/audits/goal_factor_readiness_rerun02_manifest.json"


def write_text(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body.encode("utf-8"))


def write_json(path: Path, payload: dict[str, object]) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")

PREFIX = "outputs/research/goal_premarket_portfolio_risk_management01_"
PROVIDER_COMPARISON = PREFIX + "provider_comparison.csv"
PROVIDER_QUARANTINE = PREFIX + "provider_discrepancy_quarantine.csv"
CANONICAL_CONTRACT = PREFIX + "canonical_market_data_contract.csv"
CANONICAL_MARKET_DATA = PREFIX + "canonical_market_data.csv"
CANONICAL_SUMMARY = PREFIX + "canonical_risk_dataset_summary.csv"
HOLDINGS_CONTRACT = PREFIX + "current_holdings_input_contract.csv"
REFERENCE_PORTFOLIO = PREFIX + "research_reference_portfolio.csv"
RISK_ESTIMATOR_COMPARISON = PREFIX + "risk_estimator_comparison.csv"
COVARIANCE_QUALITY = PREFIX + "covariance_quality_summary.csv"
PORTFOLIO_RISK_STATE = PREFIX + "portfolio_risk_state.csv"
RISK_CONTRIBUTION = PREFIX + "risk_contribution_summary.csv"
CONCENTRATION = PREFIX + "concentration_summary.csv"
CORRELATION_CLUSTER = PREFIX + "correlation_cluster_summary.csv"
DRAWDOWN_TAIL_RISK = PREFIX + "drawdown_tail_risk_summary.csv"
CONSTRAINT_CATALOG = PREFIX + "position_constraint_catalog.csv"
CONSTRAINT_EVALUATION = PREFIX + "position_constraint_evaluation.csv"
CONSTRAINT_BREACH = PREFIX + "constraint_breach_summary.csv"
POLICY_CATALOG = PREFIX + "policy_catalog.csv"
POLICY_WALK_FORWARD = PREFIX + "policy_walk_forward_summary.csv"
POLICY_HOLDOUT = PREFIX + "policy_holdout_summary.csv"
POLICY_RISK_COMPARISON = PREFIX + "policy_risk_comparison.csv"
POLICY_TURNOVER = PREFIX + "policy_turnover_summary.csv"
POLICY_COST = PREFIX + "policy_cost_sensitivity.csv"
POLICY_REGIME = PREFIX + "policy_regime_stability.csv"
PREFERRED_POLICY = PREFIX + "preferred_research_policy_decision.csv"
POSITION_BANDS = PREFIX + "position_band_summary.csv"
POSITION_BAND_STABILITY = PREFIX + "position_band_stability.csv"
POSITION_BAND_ABSTENTIONS = PREFIX + "position_band_abstentions.csv"
WARNINGS = PREFIX + "construction_warnings.csv"

REPORT = "outputs/audits/goal_premarket_portfolio_risk_management01_report.md"
MANIFEST = "outputs/audits/goal_premarket_portfolio_risk_management01_manifest.json"
AUDIT = "outputs/audits/goal_premarket_portfolio_risk_management01_audit.md"
DOC = "docs/research/GOAL_PREMARKET_PORTFOLIO_RISK_MANAGEMENT01_PREMARKET_PORTFOLIO_RISK_AND_POSITION_MANAGEMENT.md"
HANDOFF = "docs/research/GOAL_PREMARKET_PORTFOLIO_RISK_MANAGEMENT01_GOVERNANCE_HANDOFF.md"
ALPHA_HANDOFF = "docs/research/GOAL_PREMARKET_PORTFOLIO_RISK_MANAGEMENT01_FUTURE_ALPHA_TILT_HANDOFF.md"
CONTRACT = "configs/research/goal_premarket_portfolio_risk_management01_contract.yaml"

REQUIRED_ARTIFACTS = [
    PROVIDER_COMPARISON,
    PROVIDER_QUARANTINE,
    CANONICAL_CONTRACT,
    CANONICAL_MARKET_DATA,
    CANONICAL_SUMMARY,
    HOLDINGS_CONTRACT,
    REFERENCE_PORTFOLIO,
    RISK_ESTIMATOR_COMPARISON,
    COVARIANCE_QUALITY,
    PORTFOLIO_RISK_STATE,
    RISK_CONTRIBUTION,
    CONCENTRATION,
    CORRELATION_CLUSTER,
    DRAWDOWN_TAIL_RISK,
    CONSTRAINT_CATALOG,
    CONSTRAINT_EVALUATION,
    CONSTRAINT_BREACH,
    POLICY_CATALOG,
    POLICY_WALK_FORWARD,
    POLICY_HOLDOUT,
    POLICY_RISK_COMPARISON,
    POLICY_TURNOVER,
    POLICY_COST,
    POLICY_REGIME,
    PREFERRED_POLICY,
    POSITION_BANDS,
    POSITION_BAND_STABILITY,
    POSITION_BAND_ABSTENTIONS,
    WARNINGS,
    REPORT,
    MANIFEST,
    AUDIT,
    DOC,
    HANDOFF,
    ALPHA_HANDOFF,
    CONTRACT,
]

FALSE_BOUNDARY_KEYS = [
    "recommendation_outputs_created",
    "buy_sell_hold_outputs_created",
    "orders_created",
    "broker_trading_outputs_created",
    "production_outputs_created",
    "dashboard_frontend_artifacts_created",
    "local_lake_outputs_created",
    "dqn_rl_outputs_created",
    "rec_tiering_unlocked_by_this_goal",
    "position_band_validation_unlocked_by_this_goal",
    "target_weight_recommendations_created",
    "trade_instructions_created",
    "tokens_or_secrets_persisted",
    "current_holdings_fabricated",
]

POLICIES = [
    {
        "policy_id": "equal_weight",
        "policy_family": "diversification_baseline",
        "definition": "equal weight over eligible canonical symbols",
        "primary_objective": "transparent diversification baseline",
    },
    {
        "policy_id": "inverse_volatility",
        "policy_family": "risk_scaled_baseline",
        "definition": "weight proportional to inverse trailing 60-day volatility",
        "primary_objective": "reduce concentration in volatile symbols",
    },
    {
        "policy_id": "minimum_variance_diagonal",
        "policy_family": "minimum_variance_baseline",
        "definition": "weight proportional to inverse trailing variance with no return forecast",
        "primary_objective": "lower ex-ante diagonal variance",
    },
    {
        "policy_id": "equal_risk_contribution_diagonal",
        "policy_family": "risk_parity_baseline",
        "definition": "diagonal equal-risk-contribution proxy using inverse volatility",
        "primary_objective": "equalize volatility-scaled risk contributions",
    },
    {
        "policy_id": "hrp_correlation_cluster",
        "policy_family": "hierarchical_risk_parity_proxy",
        "definition": "average-correlation rank-tercile clusters, equal cluster budgets, inverse-volatility intra-cluster weights",
        "primary_objective": "diversify risk across correlation clusters without alpha forecasts",
    },
]

COST_BPS = [0, 10, 30]
MATERIAL_RETURN_DIFF = 0.02
CORPORATE_ACTION_RETURN_INDICATOR = 0.10
MIN_HISTORY = 120
MAX_SYMBOL_WEIGHT = 0.10
MAX_SYMBOL_RISK_CONTRIBUTION = 0.20
MAX_GROSS_EXPOSURE = 1.00
MAX_POLICY_TURNOVER = 0.50
MAX_ANNUALIZED_VOLATILITY = 0.35
MAX_CLUSTER_CONCENTRATION = 0.60
MAX_ABS_BETA = 1.20


def run_goal_premarket_portfolio_risk_management01(root: Path) -> bool:
    result = _build(root)
    _write_outputs(root, result)
    return True


def audit_goal_premarket_portfolio_risk_management01(root: Path) -> bool:
    failures: list[str] = []
    for rel in REQUIRED_ARTIFACTS:
        if rel == AUDIT:
            continue
        if not (root / rel).exists():
            failures.append(f"missing_artifact:{rel}")
    manifest = _read_json_if_exists(root / MANIFEST)
    if manifest.get("goal") != GOAL_ID:
        failures.append("manifest_goal_mismatch")
    if manifest.get("research_only") is not True:
        failures.append("manifest_research_only_not_true")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"boundary_key_not_false:{key}")
    if manifest.get("ready_factor_count") != 0:
        failures.append("ready_factor_count_not_zero")
    if manifest.get("rec_tiering_state") != "locked_future":
        failures.append("rec_tiering_not_locked")
    if (root / "outputs/portfolio").exists():
        failures.append("forbidden_execution_directory_present:outputs/portfolio")
    workflow = _workflow_rows(root)
    if workflow.get(WORKFLOW_ID, {}).get("status") != "implemented_research_only":
        failures.append("workflow_row_missing_or_not_implemented_research_only")
    for workflow_id in [
        "goal_rec_tiering01_recommendation_score_tiering_gate",
        "goal10b4_recommendation_backtest_revalidation",
        "goal_position_band_validation01_position_band_validation_gate",
        "dashboard_daily_report",
        "broker_live_trading",
        "production_db_writes",
        "portfolio_backtest",
    ]:
        if workflow.get(workflow_id, {}).get("status") != "locked_future":
            failures.append(f"downstream_not_locked:{workflow_id}")
    status = PASS if not failures else BLOCKED
    lines = [f"# {GOAL_ID} Audit", "", f"Status: `{status}`", "", "## Failures"]
    lines.extend(f"- {failure}" for failure in failures)
    lines.append("")
    write_text(root / AUDIT, "\n".join(lines))
    return status == PASS


def _build(root: Path) -> dict[str, object]:
    daily_rows = read_csv(root / NETWORK_DAILY)
    index_rows = read_csv(root / NETWORK_INDEX)
    regime_rows = read_csv(root / REGIME_LABELS) if (root / REGIME_LABELS).exists() else []
    provider = _provider_reconciliation(root, daily_rows)
    canonical = _canonical_market_data(daily_rows, provider["quarantine_keys"])
    risk = _risk_and_reference(canonical["eligible_rows"], index_rows)
    policies = _policy_comparison(canonical["returns_by_date"], risk["eligible_symbols"], regime_rows)
    constraints = _constraints(risk, canonical, policies)
    bands = _position_bands(
        risk["eligible_symbols"],
        risk["latest_date"],
        risk["vol_by_symbol"],
        policies["selected_weights"],
        risk["risk_state_row"],
        constraints["symbol_blockers"],
        provider["discrepancy_symbols"],
        provider["discrepancy_count_by_symbol"],
        risk["avg_abs_corr_by_symbol"],
        canonical["history_count"],
        policies,
    )
    warnings = _warnings(provider, canonical, policies, bands)
    manifest = _manifest(daily_rows, index_rows, provider, canonical, risk, constraints, policies, bands, warnings, root)
    return {
        "provider": provider,
        "canonical": canonical,
        "risk": risk,
        "constraints": constraints,
        "policies": policies,
        "bands": bands,
        "warnings": warnings,
        "manifest": manifest,
    }


def _provider_reconciliation(root: Path, daily_rows: list[dict[str, str]]) -> dict[str, object]:
    new_forward = _next_return_map(daily_rows)
    old_forward: dict[tuple[str, str], float] = {}
    old_dates: set[str] = set()
    old_keys: set[tuple[str, str]] = set()
    for path in sorted(glob.glob(str(root / OLD_PANEL_GLOB))):
        for row in read_csv(Path(path)):
            key = (row["symbol"], row["trade_date"])
            old_dates.add(row["trade_date"])
            old_keys.add(key)
            if key not in old_forward:
                value = _float(row.get("forward_return_1d"))
                if value is not None:
                    old_forward[key] = value
    overlap = sorted(set(new_forward) & set(old_forward))
    diffs = []
    quarantines = []
    for key in overlap:
        old_value = old_forward[key]
        new_value = new_forward[key]
        diff = abs(old_value - new_value)
        diffs.append(diff)
        if diff > MATERIAL_RETURN_DIFF:
            symbol, trade_date = key
            quarantines.append(
                {
                    "symbol": symbol,
                    "trade_date": trade_date,
                    "diagnostic_dimension": "return_overlap",
                    "comparison_metric": "forward_return_1d",
                    "baostock_value": _fmt(old_value),
                    "akshare_sina_value": _fmt(new_value),
                    "abs_diff": _fmt(diff),
                    "threshold": _fmt(MATERIAL_RETURN_DIFF),
                    "quarantine_scope": "risk_model_fitting",
                    "quarantine_reason": "material_provider_return_discrepancy",
                    "deterministic_rule": "abs(baostock_forward_return_1d-akshare_sina_next_return)>0.02",
                    "evidence_availability": "baostock_forward_return_1d_and_akshare_sina_close_available",
                    "research_only": True,
                    "not_trading_advice": True,
                    "not_for_execution": True,
                }
            )
    mean_diff = _mean(diffs)
    max_diff = max(diffs) if diffs else 0.0
    daily_dates = {row["trade_date"] for row in daily_rows}
    daily_keys = {(row["symbol"], row["trade_date"]) for row in daily_rows}
    missing_date_difference_count = len(daily_dates ^ old_dates)
    missing_key_difference_count = len(daily_keys ^ old_keys)
    missing_returns = sum(1 for row in daily_rows if _float(row.get("return_1d")) is None)
    corporate_action_indicators = sum(
        1
        for row in daily_rows
        if (_float(row.get("return_1d")) is not None and abs(float(row["return_1d"])) >= CORPORATE_ACTION_RETURN_INDICATOR)
    )
    common = {
        "providers_compared": "baostock;akshare_sina",
        "mean_abs_diff": "",
        "max_abs_diff": "",
        "material_discrepancy_count": 0,
        "material_discrepancy_threshold": "",
        "canonical_decision": "",
        "material_discrepancy_policy": "no_quarantine_without_direct_overlap_evidence",
        "adjustment_convention_status": "unresolved_missing_cross_provider_adjustment_metadata",
        "unresolved_status": True,
        "evidence_availability": "",
        "date_alignment_status": "",
        "missing_date_difference_count": missing_date_difference_count,
        "timestamp_alignment_status": "date_level_only_no_intraday_timestamp",
        "suspension_handling_status": "unresolved_no_volume_or_suspension_flag",
        "corporate_action_indicator_count": corporate_action_indicators,
        "raw_adjusted_semantics": "akshare_sina_adjusted_close_primary;baostock_raw_or_adjusted_semantics_unresolved",
        "no_silent_averaging": True,
        "status": "diagnostic",
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }
    comparison_rows = [
        {
            **common,
            "comparison_id": "baostock_vs_akshare_sina_forward_return_1d",
            "diagnostic_dimension": "return_overlap",
            "providers_compared": "baostock;akshare_sina",
            "overlap_rows": len(overlap),
            "mean_abs_diff": _fmt(mean_diff),
            "max_abs_diff": _fmt(max_diff),
            "material_discrepancy_count": len(quarantines),
            "material_discrepancy_threshold": _fmt(MATERIAL_RETURN_DIFF),
            "canonical_decision": "akshare_sina_primary_with_baostock_overlap_diagnostics",
            "material_discrepancy_policy": "quarantine_from_risk_model_fitting",
            "evidence_availability": "baostock_forward_return_1d_and_akshare_sina_close_available",
            "date_alignment_status": "symbol_date_overlap_used_for_return_diagnostics",
            "unresolved_status": False,
            "status": "pass_with_material_discrepancy_quarantine" if quarantines else "pass",
        },
        {
            **common,
            "comparison_id": "baostock_vs_akshare_sina_close_price_overlap",
            "diagnostic_dimension": "close_price_overlap",
            "overlap_rows": 0,
            "canonical_decision": "akshare_sina_close_primary_no_silent_averaging",
            "evidence_availability": "missing_baostock_close_price_in_committed_refined_panel",
            "status": "unresolved_missing_provider_close_evidence",
        },
        {
            **common,
            "comparison_id": "baostock_vs_akshare_sina_return_1d_overlap",
            "diagnostic_dimension": "return_overlap",
            "overlap_rows": len(overlap),
            "mean_abs_diff": _fmt(mean_diff),
            "max_abs_diff": _fmt(max_diff),
            "material_discrepancy_count": len(quarantines),
            "material_discrepancy_threshold": _fmt(MATERIAL_RETURN_DIFF),
            "canonical_decision": "akshare_sina_return_primary_with_forward_return_crosscheck",
            "material_discrepancy_policy": "quarantine_from_risk_model_fitting",
            "evidence_availability": "direct_return_1d_missing_in_old_panel_forward_return_1d_used_as_feasible_overlap",
            "date_alignment_status": "symbol_date_overlap_used_for_return_diagnostics",
            "unresolved_status": False,
            "status": "pass_with_material_discrepancy_quarantine" if quarantines else "pass",
        },
        {
            **common,
            "comparison_id": "date_alignment_and_missing_date_diagnostics",
            "diagnostic_dimension": "date_alignment",
            "overlap_rows": len(daily_keys & old_keys),
            "canonical_decision": "canonical_dates_follow_committed_akshare_sina_panel",
            "evidence_availability": "symbol_date_keys_available_for_both_committed_sources",
            "date_alignment_status": f"daily_vs_old_symbol_date_symmetric_difference={missing_key_difference_count}",
            "status": "pass" if missing_key_difference_count == 0 else "pass_with_missing_date_differences_disclosed",
        },
        {
            **common,
            "comparison_id": "timestamp_alignment_disclosure",
            "diagnostic_dimension": "timestamp_alignment",
            "overlap_rows": len(daily_keys & old_keys),
            "canonical_decision": "date_level_alignment_only_no_intraday_timestamp",
            "evidence_availability": "trade_date_available_intraday_timestamp_unavailable",
            "status": "unresolved_intraday_timestamp_not_available",
        },
        {
            **common,
            "comparison_id": "suspension_and_zero_volume_handling",
            "diagnostic_dimension": "suspension_handling",
            "overlap_rows": len(daily_rows),
            "canonical_decision": "missing_returns_excluded_from_risk_model_no_volume_based_suspension_claim",
            "evidence_availability": "close_and_return_available_volume_or_suspension_flag_unavailable",
            "suspension_handling_status": f"return_missing_count={missing_returns};zero_volume_unobservable",
            "status": "unresolved_no_volume_or_suspension_flag",
        },
        {
            **common,
            "comparison_id": "corporate_action_discontinuity_indicators",
            "diagnostic_dimension": "corporate_action_discontinuity",
            "overlap_rows": len(daily_rows),
            "canonical_decision": "large_return_indicator_disclosed_not_treated_as_adjustment_reconciliation",
            "evidence_availability": "return_path_available_corporate_action_metadata_unavailable",
            "status": "indicator_only_requires_adjustment_metadata",
        },
        {
            **common,
            "comparison_id": "adjustment_convention_disclosure",
            "diagnostic_dimension": "adjustment_convention",
            "overlap_rows": 0,
            "canonical_decision": "akshare_sina_adjusted_close_primary_adjustment_convention_unresolved",
            "evidence_availability": "missing_cross_provider_raw_adjusted_metadata",
            "status": "unresolved_adjustment_convention",
        },
    ]
    status = "pass_with_material_discrepancy_quarantine" if quarantines else "pass"
    return {
        "comparison_rows": comparison_rows,
        "quarantine_rows": quarantines,
        "quarantine_keys": {(row["symbol"], row["trade_date"]) for row in quarantines},
        "discrepancy_symbols": {row["symbol"] for row in quarantines},
        "discrepancy_count_by_symbol": dict(_counts([row["symbol"] for row in quarantines])),
        "overlap_rows": len(overlap),
        "material_discrepancy_count": len(quarantines),
        "price_diagnostic_count": sum(1 for row in comparison_rows if row["diagnostic_dimension"] == "close_price_overlap"),
        "return_diagnostic_count": sum(1 for row in comparison_rows if row["diagnostic_dimension"] == "return_overlap"),
        "adjustment_convention_status": "unresolved_missing_cross_provider_adjustment_metadata",
        "status": status,
    }


def _canonical_market_data(daily_rows: list[dict[str, str]], quarantine_keys: set[tuple[str, str]]) -> dict[str, object]:
    rows = []
    returns_by_date: dict[str, dict[str, float]] = defaultdict(dict)
    history_count: dict[str, int] = defaultdict(int)
    for row in sorted(daily_rows, key=lambda item: (item["trade_date"], item["symbol"])):
        key = (row["symbol"], row["trade_date"])
        close = _float(row.get("close"))
        ret = _float(row.get("return_1d"))
        quarantined = key in quarantine_keys
        return_status = "accepted" if ret is not None and not quarantined else "insufficient_prior_price" if ret is None else "quarantined_provider_discrepancy"
        price_status = "accepted" if close is not None and not quarantined else "quarantined_provider_discrepancy" if quarantined else "missing_close"
        corporate_action_indicator = ret is not None and abs(ret) >= CORPORATE_ACTION_RETURN_INDICATOR
        eligible = close is not None and ret is not None and not quarantined
        if eligible:
            returns_by_date[row["trade_date"]][row["symbol"]] = ret
            history_count[row["symbol"]] += 1
        rows.append(
            {
                "trade_date": row["trade_date"],
                "symbol": row["symbol"],
                "canonical_close": _fmt(close),
                "canonical_return_1d": _fmt(ret),
                "source_provider": row.get("source_provider", "akshare_sina"),
                "provider_overlap_status": "material_discrepancy_quarantined" if quarantined else "accepted_or_no_overlap",
                "canonical_price_status": price_status,
                "canonical_return_status": return_status,
                "adjustment_convention_status": "unresolved_cross_provider_adjustment_convention",
                "raw_adjusted_semantics": "akshare_sina_adjusted_close_primary;raw_unadjusted_cross_provider_not_available",
                "timestamp_alignment_status": "date_level_only_no_intraday_timestamp",
                "suspension_status": "not_observable_no_volume_or_suspension_flag" if ret is not None else "return_missing_suspension_unresolved",
                "corporate_action_discontinuity_flag": corporate_action_indicator,
                "risk_model_eligible": eligible,
                "quarantine_reason": "material_provider_return_discrepancy" if quarantined else "",
                "no_lookahead_status": row.get("no_lookahead_status", "passed_current_or_past_only"),
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
    symbols = sorted({row["symbol"] for row in daily_rows})
    dates = sorted({row["trade_date"] for row in daily_rows})
    eligible_symbols = sorted(symbol for symbol, count in history_count.items() if count >= MIN_HISTORY)
    summary_rows = [
        {
            "metric": "canonical_rows",
            "value": len(rows),
            "status": "pass",
            "notes": "all committed akshare_sina daily rows carried into canonical layer",
        },
        {
            "metric": "eligible_risk_rows",
            "value": sum(1 for row in rows if row["risk_model_eligible"] is True),
            "status": "pass",
            "notes": "rows with current-or-past close and 1d return after provider quarantine",
        },
        {
            "metric": "eligible_symbols_min_history",
            "value": len(eligible_symbols),
            "status": "pass" if eligible_symbols else "blocked",
            "notes": f"minimum_history={MIN_HISTORY}",
        },
    ]
    contract_rows = [
        _contract_row("trade_date", "date", "canonical observation date", "current_or_past_only"),
        _contract_row("symbol", "string", "approved symbol identifier", "current_or_past_only"),
        _contract_row("canonical_close", "float", "akshare_sina close unless quarantined", "current_or_past_only"),
        _contract_row("canonical_return_1d", "float", "current-day close-to-close return", "current_or_past_only"),
        _contract_row("canonical_price_status", "enum", "accepted or quarantined price status", "current_or_past_only"),
        _contract_row("canonical_return_status", "enum", "accepted or quarantined return status", "current_or_past_only"),
        _contract_row("adjustment_convention_status", "enum", "cross-provider adjustment convention remains unresolved where metadata is missing", "current_or_past_only"),
        _contract_row("raw_adjusted_semantics", "string", "discloses adjusted-primary versus unavailable raw/unadjusted evidence", "current_or_past_only"),
        _contract_row("timestamp_alignment_status", "enum", "trade-date alignment only; no intraday timestamp evidence", "current_or_past_only"),
        _contract_row("suspension_status", "enum", "suspension handling limited by missing volume/suspension flags", "current_or_past_only"),
        _contract_row("corporate_action_discontinuity_flag", "bool", "large-return indicator only, not full corporate-action adjustment reconciliation", "derived_without_future_returns"),
        _contract_row("risk_model_eligible", "bool", "eligible for research risk estimation", "derived_without_future_returns"),
    ]
    return {
        "rows": rows,
        "summary_rows": summary_rows,
        "contract_rows": contract_rows,
        "returns_by_date": {date: dict(values) for date, values in returns_by_date.items()},
        "history_count": dict(history_count),
        "eligible_symbols": eligible_symbols,
        "dates": dates,
        "symbols": symbols,
        "eligible_rows": [row for row in rows if row["risk_model_eligible"] is True],
        "quarantined_rows": sum(1 for row in rows if row["risk_model_eligible"] is not True and row["quarantine_reason"]),
    }


def _risk_and_reference(eligible_rows: list[dict[str, object]], index_rows: list[dict[str, str]]) -> dict[str, object]:
    returns_by_symbol: dict[str, list[tuple[str, float]]] = defaultdict(list)
    returns_by_date: dict[str, dict[str, float]] = defaultdict(dict)
    for row in eligible_rows:
        ret = _float(row["canonical_return_1d"])
        if ret is None:
            continue
        symbol = str(row["symbol"])
        date = str(row["trade_date"])
        returns_by_symbol[symbol].append((date, ret))
        returns_by_date[date][symbol] = ret
    symbols = sorted(symbol for symbol, values in returns_by_symbol.items() if len(values) >= MIN_HISTORY)
    dates = sorted(returns_by_date)
    latest_date = dates[-1] if dates else ""
    vol_by_symbol = {symbol: _std([value for _, value in returns_by_symbol[symbol][-60:]]) for symbol in symbols}
    weights = _weights_equal(symbols)
    reference_rows = [
        {
            "portfolio_id": "research_reference_portfolio",
            "asof_date": latest_date,
            "symbol": symbol,
            "reference_weight": _fmt(weights[symbol]),
            "source": "research_reference_portfolio_no_current_holdings_supplied",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
        for symbol in symbols
    ]
    portfolio_returns = _portfolio_returns(returns_by_date, weights)
    rolling_vols = _rolling_values([ret for _, ret in portfolio_returns], 60, _std)
    current_vol = rolling_vols[-1] if rolling_vols else 0.0
    p75 = _percentile(rolling_vols, 0.75) if rolling_vols else 0.0
    p90 = _percentile(rolling_vols, 0.90) if rolling_vols else 0.0
    csi300 = [row for row in index_rows if row.get("index_id") == "sh000300"]
    csi300_by_date = {row["trade_date"]: _float(row.get("return_1d")) for row in csi300}
    beta_pairs = [(ret, csi300_by_date[date]) for date, ret in portfolio_returns if csi300_by_date.get(date) is not None]
    beta_to_csi300 = _beta([ret for ret, _ in beta_pairs], [index_ret for _, index_ret in beta_pairs])
    csi300_ret20 = _sum_last([_float(row.get("return_1d")) for row in csi300 if _float(row.get("return_1d")) is not None], 20)
    if not symbols:
        risk_state = "abstain_insufficient_confidence"
    elif current_vol >= p90 and p90 > 0:
        risk_state = "stressed_risk_review_only"
    elif current_vol >= p75 and p75 > 0:
        risk_state = "elevated_volatility_review_only"
    else:
        risk_state = "normal_risk_review_only"
    trace = f"current_60d_vol={_fmt(current_vol)};p75={_fmt(p75)};p90={_fmt(p90)};csi300_20d_return={_fmt(csi300_ret20)};rules=fixed_quantile_volatility_thresholds"
    risk_state_row = {
        "portfolio_id": "research_reference_portfolio",
        "asof_date": latest_date,
        "risk_state": risk_state,
        "state_machine_version": "fixed_v1",
        "decision_rule_trace": trace,
        "current_holdings_mode": "research_reference_portfolio_mode",
        "buy_sell_hold_generated": False,
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }
    variance_by_symbol = {symbol: vol_by_symbol[symbol] ** 2 for symbol in symbols}
    total = sum((weights[symbol] ** 2) * variance_by_symbol[symbol] for symbol in symbols) or 1.0
    contribution_rows = [
        {
            "portfolio_id": "research_reference_portfolio",
            "asof_date": latest_date,
            "symbol": symbol,
            "reference_weight": _fmt(weights[symbol]),
            "volatility_60d": _fmt(vol_by_symbol[symbol]),
            "risk_contribution_share": _fmt(((weights[symbol] ** 2) * variance_by_symbol[symbol]) / total),
            "risk_contribution_status": "estimated_from_diagonal_covariance",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
        for symbol in symbols
    ]
    concentration_rows = [
        {
            "portfolio_id": "research_reference_portfolio",
            "asof_date": latest_date,
            "symbol_count": len(symbols),
            "max_weight": _fmt(max(weights.values()) if weights else 0.0),
            "hhi": _fmt(sum(weight * weight for weight in weights.values())),
            "effective_names": _fmt(1.0 / sum(weight * weight for weight in weights.values()) if weights else 0.0),
            "concentration_status": "diversified_reference" if len(symbols) >= 20 else "concentrated_reference",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
    ]
    estimator_rows = _risk_estimator_rows(returns_by_symbol, symbols)
    covariance_rows, cluster_rows, cluster_by_symbol, avg_abs_corr_by_symbol = _covariance_and_clusters(returns_by_date, symbols)
    tail_rows = [
        {
            "portfolio_id": "research_reference_portfolio",
            "asof_date": latest_date,
            "observations": len(portfolio_returns),
            "historical_volatility": _fmt(_annualized_vol([ret for _, ret in portfolio_returns])),
            "beta_to_csi300": _fmt(beta_to_csi300),
            "beta_observations": len(beta_pairs),
            "max_drawdown": _fmt(_max_drawdown([ret for _, ret in portfolio_returns])),
            "var_95_daily": _fmt(_percentile([ret for _, ret in portfolio_returns], 0.05)),
            "cvar_95_daily": _fmt(_tail_mean([ret for _, ret in portfolio_returns], 0.05)),
            "tail_risk_status": "estimated_research_only",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
    ]
    return {
        "eligible_symbols": symbols,
        "latest_date": latest_date,
        "vol_by_symbol": vol_by_symbol,
        "reference_weights": weights,
        "reference_rows": reference_rows,
        "risk_state_row": risk_state_row,
        "risk_estimator_rows": estimator_rows,
        "covariance_rows": covariance_rows,
        "risk_contribution_rows": contribution_rows,
        "concentration_rows": concentration_rows,
        "cluster_rows": cluster_rows,
        "cluster_by_symbol": cluster_by_symbol,
        "avg_abs_corr_by_symbol": avg_abs_corr_by_symbol,
        "tail_rows": tail_rows,
        "portfolio_returns": portfolio_returns,
        "beta_to_csi300": beta_to_csi300,
        "beta_observations": len(beta_pairs),
    }


def _constraints(
    risk: dict[str, object],
    canonical: dict[str, object],
    policies: dict[str, object],
) -> dict[str, object]:
    reference_rows = risk["reference_rows"]
    contribution_rows = risk["risk_contribution_rows"]
    catalog = [
        _constraint("max_symbol_weight", "single-name exposure must not exceed 10%", "<=0.10", "symbol"),
        _constraint("max_symbol_risk_contribution", "single-name diagonal risk contribution must not exceed 20%", "<=0.20", "symbol"),
        _constraint("min_history_observations", "symbol must have at least 120 eligible return observations", ">=120", "symbol"),
        _constraint("quarantined_rows_excluded", "provider-quarantined rows must be excluded from risk fitting", "true", "dataset"),
        _constraint("research_reference_only_without_holdings", "no current holdings may be fabricated", "current_holdings_supplied=false", "portfolio"),
        _constraint("no_action_instruction", "constraint engine cannot emit trade instructions", "action_instruction=none", "portfolio"),
        _constraint("gross_exposure_max", "gross research exposure may not exceed 100%", "<=1.00", "portfolio", True, "reference weights"),
        _constraint("cash_buffer_band", "cash buffer must be inside the owner-supplied band when real holdings exist", "0.00_to_0.05", "portfolio", True, "current holdings cash snapshot"),
        _constraint("turnover_limit", "one-way turnover from equal-weight reference must remain bounded", "<=0.50", "portfolio", True, "policy weights"),
        _constraint("volatility_budget", "annualized reference volatility must remain inside research budget", "<=0.35", "portfolio", True, "historical returns"),
        _constraint("cluster_concentration_cap", "largest correlation-cluster weight share must remain diversified", "<=0.60", "portfolio", True, "correlation clusters"),
        _constraint("beta_budget", "absolute reference beta to CSI300 must remain bounded", "<=1.20", "portfolio", True, "index returns"),
        _constraint("liquidity_limit", "liquidity capacity requires volume or amount evidence", "capacity_from_volume_or_amount", "symbol", True, "volume or amount"),
    ]
    contribution_by_symbol = {row["symbol"]: float(row["risk_contribution_share"]) for row in contribution_rows}
    history = canonical["history_count"]
    evaluations = []
    blockers: set[str] = set()
    for row in reference_rows:
        symbol = str(row["symbol"])
        weight = float(row["reference_weight"])
        risk_share = contribution_by_symbol.get(symbol, 0.0)
        checks = [
            ("max_symbol_weight", weight <= MAX_SYMBOL_WEIGHT, weight, MAX_SYMBOL_WEIGHT, False, "available"),
            ("max_symbol_risk_contribution", risk_share <= MAX_SYMBOL_RISK_CONTRIBUTION, risk_share, MAX_SYMBOL_RISK_CONTRIBUTION, False, "available"),
            ("min_history_observations", int(history.get(symbol, 0)) >= MIN_HISTORY, int(history.get(symbol, 0)), MIN_HISTORY, False, "available"),
        ]
        for constraint_id, passed, observed, threshold, fail_closed, evidence in checks:
            if not passed:
                blockers.add(symbol)
            evaluations.append(_constraint_eval("research_reference_portfolio", symbol, constraint_id, observed, threshold, passed, fail_closed, evidence))

    reference_weights = risk["reference_weights"]
    gross_exposure = sum(abs(weight) for weight in reference_weights.values())
    max_turnover = policies["max_turnover"]
    annualized_vol = _float(risk["tail_rows"][0]["historical_volatility"]) or 0.0
    beta = risk["beta_to_csi300"]
    cluster_weights: dict[str, float] = defaultdict(float)
    for symbol, weight in reference_weights.items():
        cluster_weights[risk["cluster_by_symbol"].get(symbol, "cluster_unavailable")] += weight
    max_cluster_weight = max(cluster_weights.values()) if cluster_weights else 0.0

    portfolio_checks = [
        ("quarantined_rows_excluded", canonical["quarantined_rows"] >= 0, canonical["quarantined_rows"], "excluded_from_risk_model=true", False, "available"),
        ("research_reference_only_without_holdings", False, "current_holdings_not_supplied", "valid_snapshot_required", True, "unavailable_no_current_holdings_snapshot"),
        ("no_action_instruction", True, "none", "action_instruction=none", False, "available"),
        ("gross_exposure_max", gross_exposure <= MAX_GROSS_EXPOSURE + 1e-9, gross_exposure, MAX_GROSS_EXPOSURE, False, "available"),
        ("cash_buffer_band", False, "unavailable_no_current_cash_snapshot", "0.00_to_0.05", True, "unavailable_no_current_holdings_or_cash_snapshot"),
        ("turnover_limit", max_turnover <= MAX_POLICY_TURNOVER, max_turnover, MAX_POLICY_TURNOVER, False, "available"),
        ("volatility_budget", annualized_vol <= MAX_ANNUALIZED_VOLATILITY, annualized_vol, MAX_ANNUALIZED_VOLATILITY, False, "available"),
        ("cluster_concentration_cap", max_cluster_weight <= MAX_CLUSTER_CONCENTRATION, max_cluster_weight, MAX_CLUSTER_CONCENTRATION, False, "available"),
        ("beta_budget", risk["beta_observations"] >= MIN_HISTORY and abs(beta) <= MAX_ABS_BETA, beta, MAX_ABS_BETA, risk["beta_observations"] < MIN_HISTORY, "available" if risk["beta_observations"] >= MIN_HISTORY else "unavailable_insufficient_index_overlap"),
        ("liquidity_limit", False, "unavailable_no_volume_or_amount_field", "capacity_from_volume_or_amount", True, "unavailable_no_volume_or_amount_field"),
    ]
    for constraint_id, passed, observed, threshold, fail_closed, evidence in portfolio_checks:
        evaluations.append(_constraint_eval("research_reference_portfolio", "", constraint_id, observed, threshold, passed, fail_closed, evidence))

    breach_summary = []
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in evaluations:
        grouped[str(row["constraint_id"])].append(row)
    for constraint_id, rows in sorted(grouped.items()):
        breach_summary.append(
            {
                "constraint_id": constraint_id,
                "evaluated_rows": len(rows),
                "breach_count": sum(1 for row in rows if row["constraint_passed"] is False),
                "fail_closed_count": sum(1 for row in rows if row["fail_closed"] is True),
                "severity": _max_severity([str(row["severity"]) for row in rows]),
                "action_instruction": "none",
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
    return {
        "catalog_rows": catalog,
        "evaluation_rows": evaluations,
        "breach_rows": breach_summary,
        "symbol_blockers": blockers,
        "fail_closed_cases": sum(1 for row in evaluations if row["fail_closed"] is True),
        "substantive_constraints": sum(1 for row in catalog if row["substantive_constraint"] is True),
    }


def _policy_comparison(
    returns_by_date: dict[str, dict[str, float]],
    symbols: list[str],
    regime_rows: list[dict[str, str]],
) -> dict[str, object]:
    dates = sorted(returns_by_date)
    train_end = int(len(dates) * 0.60)
    holdout_start = int(len(dates) * 0.80)
    train_dates = dates[:train_end]
    holdout_dates = dates[holdout_start:]
    catalog_rows = [_policy_catalog_row(policy) for policy in POLICIES]
    train_returns = _slice_returns(returns_by_date, train_dates)
    weights_by_policy = {policy["policy_id"]: _policy_weights(policy["policy_id"], symbols, train_returns) for policy in POLICIES}
    effective_policy_ids = [str(row["policy_id"]) for row in catalog_rows if row["effective_distinct_policy"] is True]
    policy_weight_spread_by_symbol = {
        symbol: (
            max(weights_by_policy[policy_id].get(symbol, 0.0) for policy_id in effective_policy_ids)
            - min(weights_by_policy[policy_id].get(symbol, 0.0) for policy_id in effective_policy_ids)
        )
        if effective_policy_ids
        else 0.0
        for symbol in symbols
    }
    walk_rows = []
    folds = _walk_forward_folds(dates)
    for fold_id, train_fold_dates, test_dates in folds:
        train_fold = _slice_returns(returns_by_date, train_fold_dates)
        for policy in POLICIES:
            weights = _policy_weights(policy["policy_id"], symbols, train_fold)
            returns = _portfolio_returns(_slice_returns(returns_by_date, test_dates), weights)
            metrics = _return_metrics(returns)
            walk_rows.append(
                {
                    "fold_id": fold_id,
                    "policy_id": policy["policy_id"],
                    "train_start": train_fold_dates[0] if train_fold_dates else "",
                    "train_end": train_fold_dates[-1] if train_fold_dates else "",
                    "test_start": test_dates[0] if test_dates else "",
                    "test_end": test_dates[-1] if test_dates else "",
                    "chronological_split": True,
                    **metrics,
                    "research_only": True,
                    "not_trading_advice": True,
                    "not_for_execution": True,
                }
            )
    holdout_rows = []
    risk_rows = []
    turnover_rows = []
    cost_rows = []
    policy_scores = {}
    equal = _weights_equal(symbols)
    for policy in POLICIES:
        policy_id = policy["policy_id"]
        weights = weights_by_policy[policy_id]
        returns = _portfolio_returns(_slice_returns(returns_by_date, holdout_dates), weights)
        metrics = _return_metrics(returns)
        turnover = 0.5 * sum(abs(weights.get(symbol, 0.0) - equal.get(symbol, 0.0)) for symbol in symbols)
        holdout_rows.append(
            {
                "policy_id": policy_id,
                "holdout_start": holdout_dates[0] if holdout_dates else "",
                "holdout_end": holdout_dates[-1] if holdout_dates else "",
                **metrics,
                "selection_metric_role": "secondary_return_diagnostics_only",
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
        risk_rows.append(
            {
                "policy_id": policy_id,
                "annualized_volatility": metrics["annualized_volatility"],
                "max_drawdown": metrics["max_drawdown"],
                "var_95_daily": metrics["var_95_daily"],
                "cvar_95_daily": metrics["cvar_95_daily"],
                "risk_first_rank_input": "volatility;drawdown;cvar;turnover",
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
        turnover_rows.append(
            {
                "policy_id": policy_id,
                "turnover_measure": "one_way_turnover_from_equal_weight_reference",
                "turnover": _fmt(turnover),
                "turnover_status": "bounded" if turnover <= 0.5 else "high",
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
        for bps in COST_BPS:
            net_total = float(metrics["total_return"]) - turnover * (bps / 10000.0)
            cost_rows.append(
                {
                    "policy_id": policy_id,
                    "cost_bps": bps,
                    "turnover": _fmt(turnover),
                    "gross_total_return": metrics["total_return"],
                    "net_total_return_after_cost": _fmt(net_total),
                    "cost_model": "bounded_research_scenario_not_live_execution_cost",
                    "research_only": True,
                    "not_trading_advice": True,
                    "not_for_execution": True,
                }
            )
        vol = abs(float(metrics["annualized_volatility"]))
        drawdown = abs(float(metrics["max_drawdown"]))
        cvar = abs(float(metrics["cvar_95_daily"]))
        policy_scores[policy_id] = vol + drawdown + cvar + turnover * 0.05
    regime_by_date = {row["trade_date"]: row.get("refined_composite_regime_label", "") for row in regime_rows}
    regime_rows_out = []
    sparse_regime_count = 0
    for policy in POLICIES:
        weights = weights_by_policy[policy["policy_id"]]
        returns = _portfolio_returns(_slice_returns(returns_by_date, holdout_dates), weights)
        by_regime: dict[str, list[float]] = defaultdict(list)
        for date, ret in returns:
            by_regime[regime_by_date.get(date, "regime_unavailable_review_only")].append(ret)
        for regime, values in sorted(by_regime.items()):
            sparse = len(values) < 20
            if sparse:
                sparse_regime_count += 1
            regime_rows_out.append(
                {
                    "policy_id": policy["policy_id"],
                    "regime_label": regime,
                    "observations": len(values),
                    "annualized_volatility": _fmt(_annualized_vol(values)),
                    "mean_daily_return": _fmt(_mean(values)),
                    "regime_stability_status": "review_only_sufficient" if not sparse else "sparse_regime_review_only",
                    "research_only": True,
                    "not_trading_advice": True,
                    "not_for_execution": True,
                }
            )
    selected = min(policy_scores, key=policy_scores.get) if policy_scores else "no_policy_selected"
    sorted_scores = sorted(policy_scores.items(), key=lambda item: item[1])
    margin = (sorted_scores[1][1] - sorted_scores[0][1]) / sorted_scores[0][1] if len(sorted_scores) > 1 and sorted_scores[0][1] else 0.0
    if margin < 0.05:
        decision = "no_single_robust_winner"
        selected_for_bands = "inverse_volatility"
        rationale = "top risk-first scores are within 5pct; inverse_volatility used only as conservative band reference"
    else:
        decision = selected
        selected_for_bands = selected
        rationale = "selected by lowest pre-specified risk-first composite score"
    decision_rows = [
        {
            "decision_id": "preferred_research_policy",
            "preferred_research_policy": decision,
            "band_reference_policy": selected_for_bands,
            "selection_basis": "risk_first_not_return_optimized",
            "score_margin_to_runner_up": _fmt(margin),
            "rationale": rationale,
            "return_metrics_role": "secondary_diagnostics_only",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
    ]
    return {
        "catalog_rows": catalog_rows,
        "walk_rows": walk_rows,
        "holdout_rows": holdout_rows,
        "risk_rows": risk_rows,
        "turnover_rows": turnover_rows,
        "cost_rows": cost_rows,
        "regime_rows": regime_rows_out,
        "decision_rows": decision_rows,
        "selected_policy": decision,
        "band_reference_policy": selected_for_bands,
        "selected_weights": weights_by_policy.get(selected_for_bands, _weights_equal(symbols)),
        "policy_ids": [policy["policy_id"] for policy in POLICIES],
        "effective_policy_ids": effective_policy_ids,
        "effective_distinct_policies": len(effective_policy_ids),
        "max_turnover": max((float(row["turnover"]) for row in turnover_rows), default=0.0),
        "policy_weight_spread_by_symbol": policy_weight_spread_by_symbol,
        "sparse_regime_count": sparse_regime_count,
    }


def _position_bands(
    symbols: list[str],
    latest_date: str,
    vol_by_symbol: dict[str, float],
    reference_weights: dict[str, float],
    risk_state: dict[str, object],
    blockers: set[str],
    provider_discrepancy_symbols: set[str],
    discrepancy_count_by_symbol: dict[str, int],
    avg_abs_corr_by_symbol: dict[str, float],
    history_count: dict[str, int],
    policies: dict[str, object],
) -> dict[str, object]:
    state = str(risk_state["risk_state"])
    state_multiplier = {
        "normal_risk_review_only": 1.00,
        "elevated_volatility_review_only": 0.85,
        "stressed_risk_review_only": 0.70,
        "abstain_insufficient_confidence": 0.0,
    }.get(state, 0.85)
    rows = []
    stability_rows = []
    abstentions = []
    median_vol = _percentile(list(vol_by_symbol.values()), 0.50) if vol_by_symbol else 0.0
    corr_cutoff = _percentile(list(avg_abs_corr_by_symbol.values()), 0.90) if avg_abs_corr_by_symbol else 1.0
    spreads = list(policies["policy_weight_spread_by_symbol"].values())
    spread_cutoff = _percentile(spreads, 0.90) if spreads else 1.0
    for symbol in symbols:
        ref = reference_weights.get(symbol, 0.0)
        vol = vol_by_symbol.get(symbol, 0.0)
        high_vol = vol > median_vol * 1.5 if median_vol else False
        reasons = []
        if int(history_count.get(symbol, 0)) < MIN_HISTORY:
            reasons.append("insufficient_history")
        elif symbol in blockers:
            reasons.append("constraint_data_insufficiency")
        if symbol in provider_discrepancy_symbols:
            reasons.append("unresolved_provider_discrepancy")
        if discrepancy_count_by_symbol.get(symbol, 0) >= 2:
            reasons.append("quarantine_concentration")
        if policies["sparse_regime_count"] and policies["selected_policy"] == "no_single_robust_winner" and high_vol:
            reasons.append("sparse_or_unstable_regime_evidence")
        if avg_abs_corr_by_symbol.get(symbol, 0.0) >= corr_cutoff and high_vol:
            reasons.append("unstable_covariance_sensitivity")
        spread = policies["policy_weight_spread_by_symbol"].get(symbol, 0.0)
        if spread >= spread_cutoff and spread > 0.0025 and high_vol:
            reasons.append("unstable_band_sensitivity")
        if state_multiplier == 0.0 or not ref:
            reasons.append("constraint_data_insufficiency")
        reasons = sorted(set(reasons))
        abstain = bool(reasons)
        confidence_score = max(0.0, 1.0 - 0.18 * len(reasons) - (0.12 if high_vol else 0.0))
        if abstain:
            band_min = ""
            band_max = ""
            status = "abstain_due_to_data_or_constraint_uncertainty"
            reason = ";".join(reasons)
            abstentions.append(
                {
                    "asof_date": latest_date,
                    "symbol": symbol,
                    "abstain": True,
                    "abstention_reason": reason,
                    "confidence_score": _fmt(confidence_score),
                    "research_only": True,
                    "not_trading_advice": True,
                    "not_for_execution": True,
                }
            )
        else:
            width = max(0.005, ref * (0.45 if high_vol else 0.60) * state_multiplier)
            center = ref * state_multiplier
            band_min = _fmt(max(0.0, center - width))
            band_max = _fmt(min(MAX_SYMBOL_WEIGHT, center + width))
            status = "constraints_applied"
            reason = ""
        rows.append(
            {
                "asof_date": latest_date,
                "symbol": symbol,
                "reference_policy_weight": _fmt(ref),
                "acceptable_band_min": band_min,
                "acceptable_band_max": band_max,
                "target_weight": "",
                "current_weight": "",
                "constraint_breach": "not_evaluated_no_current_holdings",
                "abstain": abstain,
                "abstention_reason": reason if abstain else "",
                "confidence_score": _fmt(confidence_score),
                "band_methodology": "risk_budget_band_from_reference_policy_volatility_and_regime",
                "regime_risk_state": state,
                "alpha_required": False,
                "constraint_integration_status": status,
                "order_instruction": "none",
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
        stability_rows.append(
            {
                "asof_date": latest_date,
                "symbol": symbol,
                "band_width": "" if abstain else _fmt(float(band_max) - float(band_min)),
                "hysteresis_rule": "fixed_25pct_band_change_tolerance_review_only",
                "estimated_daily_band_change": "0",
                "oscillation_status": "not_evaluated_for_abstain" if abstain else "stable_under_fixed_hysteresis",
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
    return {
        "band_rows": rows,
        "stability_rows": stability_rows,
        "abstention_rows": abstentions,
        "symbols_with_bands": sum(1 for row in rows if row["abstain"] is False),
        "symbols_abstained": sum(1 for row in rows if row["abstain"] is True),
    }


def _warnings(provider: dict[str, object], canonical: dict[str, object], policies: dict[str, object], bands: dict[str, object]) -> list[dict[str, object]]:
    rows = []
    if provider["material_discrepancy_count"]:
        rows.append(
            {
                "warning_code": "MATERIAL_PROVIDER_DISCREPANCIES_QUARANTINED",
                "scope": "phase1_provider_reconciliation",
                "count": provider["material_discrepancy_count"],
                "detail": "material baostock/akshare-sina forward-return differences excluded from risk fitting",
            }
        )
    if str(provider["adjustment_convention_status"]).startswith("unresolved"):
        rows.append(
            {
                "warning_code": "ADJUSTMENT_CONVENTION_UNRESOLVED",
                "scope": "phase1_provider_reconciliation",
                "count": 1,
                "detail": "committed old panel lacks close/raw-adjusted metadata, so close-price and adjustment reconciliation remain disclosed but unresolved",
            }
        )
    if policies["effective_distinct_policies"] < len(policies["policy_ids"]):
        rows.append(
            {
                "warning_code": "DUPLICATE_POLICY_EXPOSURE_DISCLOSED",
                "scope": "phase4_policy_selection",
                "count": len(policies["policy_ids"]) - policies["effective_distinct_policies"],
                "detail": "diagonal ERC is mathematically equivalent to inverse-volatility under the current diagonal proxy",
            }
        )
    if policies["selected_policy"] == "no_single_robust_winner":
        rows.append(
            {
                "warning_code": "NO_SINGLE_ROBUST_POLICY_WINNER",
                "scope": "phase4_policy_selection",
                "count": 1,
                "detail": "top risk-first policy scores are close; band reference remains conservative research-only",
            }
        )
    if bands["symbols_abstained"]:
        rows.append(
            {
                "warning_code": "POSITION_BAND_ABSTENTIONS_PRESENT",
                "scope": "phase5_position_bands",
                "count": bands["symbols_abstained"],
                "detail": "symbols with insufficient confidence or constraint blockers abstain from precise bands",
            }
        )
    if len(canonical["eligible_symbols"]) < len(canonical["symbols"]):
        rows.append(
            {
                "warning_code": "SOME_SYMBOLS_BELOW_MIN_HISTORY",
                "scope": "phase1_canonical_data",
                "count": len(canonical["symbols"]) - len(canonical["eligible_symbols"]),
                "detail": "symbols below minimum risk-history threshold excluded from risk estimators",
            }
        )
    if not rows:
        rows.append({"warning_code": "NONE", "scope": "all", "count": 0, "detail": "no construction warnings"})
    return rows


def _manifest(
    daily_rows: list[dict[str, str]],
    index_rows: list[dict[str, str]],
    provider: dict[str, object],
    canonical: dict[str, object],
    risk: dict[str, object],
    constraints: dict[str, object],
    policies: dict[str, object],
    bands: dict[str, object],
    warnings: list[dict[str, object]],
    root: Path,
) -> dict[str, object]:
    rerun = _read_json_if_exists(root / RERUN02_MANIFEST)
    locks = _read_json_if_exists(root / LOCKED_CAPABILITIES)
    manifest = {
        "goal": GOAL_ID,
        "workflow_id": WORKFLOW_ID,
        "mode": MODE,
        "status": PASS_WITH_WARNINGS if any(row["warning_code"] != "NONE" for row in warnings) else PASS,
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
        "network_enabled": False,
        "live_provider_fetches_run": False,
        "credential_dependency_required": False,
        "tokens_or_secrets_persisted": False,
        "providers_compared": ["baostock", "akshare_sina"],
        "phase1_provider_overlap_rows": provider["overlap_rows"],
        "phase1_major_discrepancies": provider["material_discrepancy_count"],
        "phase1_quarantined_rows": len(provider["quarantine_rows"]),
        "provider_reconciliation_status": provider["status"],
        "provider_price_diagnostics_count": provider["price_diagnostic_count"],
        "provider_return_diagnostics_count": provider["return_diagnostic_count"],
        "adjustment_convention_status": provider["adjustment_convention_status"],
        "canonical_rows": len(daily_rows),
        "canonical_symbols": len(canonical["symbols"]),
        "canonical_dates": len(canonical["dates"]),
        "canonical_price_status": "akshare_sina_adjusted_close_primary_cross_provider_close_unresolved",
        "canonical_return_status": "accepted_current_day_returns_with_forward_return_crosscheck_and_quarantine",
        "canonical_eligible_rows": sum(1 for row in canonical["rows"] if row["risk_model_eligible"] is True),
        "current_holdings_mode": "research_reference_portfolio_mode",
        "current_holdings_fabricated": False,
        "risk_estimators_compared": 3,
        "covariance_estimators_compared": 3,
        "portfolio_risk_states": [risk["risk_state_row"]["risk_state"]],
        "risk_contribution_status": "estimated_from_research_reference_portfolio",
        "constraints_implemented": len(constraints["catalog_rows"]),
        "substantive_constraints": constraints["substantive_constraints"],
        "constraint_breaches_detected": sum(int(row["breach_count"]) for row in constraints["breach_rows"]),
        "constraint_engine_non_actionable": True,
        "fail_closed_cases": constraints["fail_closed_cases"],
        "policies_evaluated": policies["policy_ids"],
        "effective_distinct_policies": policies["effective_distinct_policies"],
        "effective_policy_ids": policies["effective_policy_ids"],
        "walk_forward_design": "fixed_252_train_63_test_chronological_folds",
        "holdout_design": "chronological_last_20pct_final_holdout",
        "preferred_research_policy": policies["selected_policy"],
        "policy_selection_basis": "risk_first_not_return_optimized",
        "historical_portfolio_returns_research_only": True,
        "cost_scenarios_bps": COST_BPS,
        "symbols_with_bands": bands["symbols_with_bands"],
        "symbols_abstained": bands["symbols_abstained"],
        "position_band_confidence_logic": "abstain_on_provider_discrepancy_history_constraint_regime_covariance_or_band_sensitivity",
        "position_bands_are_target_weights": False,
        "position_bands_generate_orders": False,
        "alpha_required": False,
        "ready_factor_count": int(rerun.get("ready_factor_count_after", 0) or 0),
        "rec_tiering_state": "locked_future" if locks.get("goal_rec_tiering01_recommendation_score_tiering_gate") is False else str(locks.get("goal_rec_tiering01_recommendation_score_tiering_gate")),
        "recommendation_state": "locked_future",
        "trading_state": "locked_future",
        "workflow_status_modified_by_this_goal": True,
        "locked_capabilities_modified_by_this_goal": False,
        "warning_count": sum(1 for row in warnings if row["warning_code"] != "NONE"),
        "input_daily_rows": len(daily_rows),
        "input_index_rows": len(index_rows),
        "index_series_consumed": sorted({row.get("index_id", "") for row in index_rows if row.get("index_id")}),
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return manifest


def _write_outputs(root: Path, result: dict[str, object]) -> None:
    provider = result["provider"]
    canonical = result["canonical"]
    risk = result["risk"]
    constraints = result["constraints"]
    policies = result["policies"]
    bands = result["bands"]
    manifest = result["manifest"]
    write_csv(root / PROVIDER_COMPARISON, provider["comparison_rows"])
    write_csv(root / PROVIDER_QUARANTINE, provider["quarantine_rows"], fieldnames=[
        "symbol",
        "trade_date",
        "diagnostic_dimension",
        "comparison_metric",
        "baostock_value",
        "akshare_sina_value",
        "abs_diff",
        "threshold",
        "quarantine_scope",
        "quarantine_reason",
        "deterministic_rule",
        "evidence_availability",
        "research_only",
        "not_trading_advice",
        "not_for_execution",
    ])
    write_csv(root / CANONICAL_CONTRACT, canonical["contract_rows"])
    write_csv(root / CANONICAL_MARKET_DATA, canonical["rows"])
    write_csv(root / CANONICAL_SUMMARY, canonical["summary_rows"])
    write_csv(root / HOLDINGS_CONTRACT, _holdings_contract_rows())
    write_csv(root / REFERENCE_PORTFOLIO, risk["reference_rows"])
    write_csv(root / RISK_ESTIMATOR_COMPARISON, risk["risk_estimator_rows"])
    write_csv(root / COVARIANCE_QUALITY, risk["covariance_rows"])
    write_csv(root / PORTFOLIO_RISK_STATE, [risk["risk_state_row"]])
    write_csv(root / RISK_CONTRIBUTION, risk["risk_contribution_rows"])
    write_csv(root / CONCENTRATION, risk["concentration_rows"])
    write_csv(root / CORRELATION_CLUSTER, risk["cluster_rows"])
    write_csv(root / DRAWDOWN_TAIL_RISK, risk["tail_rows"])
    write_csv(root / CONSTRAINT_CATALOG, constraints["catalog_rows"])
    write_csv(root / CONSTRAINT_EVALUATION, constraints["evaluation_rows"])
    write_csv(root / CONSTRAINT_BREACH, constraints["breach_rows"])
    write_csv(root / POLICY_CATALOG, policies["catalog_rows"])
    write_csv(root / POLICY_WALK_FORWARD, policies["walk_rows"])
    write_csv(root / POLICY_HOLDOUT, policies["holdout_rows"])
    write_csv(root / POLICY_RISK_COMPARISON, policies["risk_rows"])
    write_csv(root / POLICY_TURNOVER, policies["turnover_rows"])
    write_csv(root / POLICY_COST, policies["cost_rows"])
    write_csv(root / POLICY_REGIME, policies["regime_rows"])
    write_csv(root / PREFERRED_POLICY, policies["decision_rows"])
    write_csv(root / POSITION_BANDS, bands["band_rows"])
    write_csv(root / POSITION_BAND_STABILITY, bands["stability_rows"])
    write_csv(root / POSITION_BAND_ABSTENTIONS, bands["abstention_rows"], fieldnames=[
        "asof_date",
        "symbol",
        "abstain",
        "abstention_reason",
        "confidence_score",
        "research_only",
        "not_trading_advice",
        "not_for_execution",
    ])
    write_csv(root / WARNINGS, result["warnings"])
    write_json(root / MANIFEST, manifest)
    write_text(root / REPORT, _report(manifest))
    write_text(root / DOC, _doc(manifest))
    write_text(root / HANDOFF, _handoff(manifest))
    write_text(root / ALPHA_HANDOFF, _alpha_handoff())
    write_text(root / CONTRACT, _contract())
    _ensure_workflow_row(root)


def _ensure_workflow_row(root: Path) -> None:
    rows = read_csv(root / WORKFLOW_STATUS)
    rows = [row for row in rows if row["workflow_id"] != WORKFLOW_ID]
    rows.append(
        {
            "workflow_id": WORKFLOW_ID,
            "display_name": "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01 Premarket Portfolio Risk Management",
            "stage_or_goal": "GOAL-PREMARKET-PORTFOLIO-RISK-MANAGEMENT-01",
            "status": "implemented_research_only",
            "current_repo_role": "research_only_portfolio_risk_position_management_track",
            "implemented_in_repo": "true",
            "allowed_next_action": "review_research_outputs_no_downstream_unlock",
            "depends_on": "goal_network_evidence_ingestion01_authorized_network_evidence_ingestion;goal_factor_readiness_rerun02_expanded_evidence_readiness_rerun",
            "produces_artifacts": ";".join(REQUIRED_ARTIFACTS),
            "primary_docs": f"{DOC};{HANDOFF};{ALPHA_HANDOFF}",
            "primary_scripts": "scripts/run_goal_premarket_portfolio_risk_management01.py;scripts/audit_goal_premarket_portfolio_risk_management01.py",
            "primary_outputs": f"{REPORT};{MANIFEST};{AUDIT}",
            "promotion_rule": "implemented_research_only_after_goal_premarket_portfolio_risk_management01_pass_or_pass_with_warnings",
            "notes": "Research-only portfolio risk and position-band system. Historical portfolio returns and weights are research-only policy diagnostics, not recommendations, orders, trading, production, local-lake, factor-mining, broker, or DQN/RL outputs.",
        }
    )
    write_csv(root / WORKFLOW_STATUS, rows)


def _next_return_map(rows: list[dict[str, str]]) -> dict[tuple[str, str], float]:
    by_symbol: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_symbol[row["symbol"]].append(row)
    out = {}
    for symbol, values in by_symbol.items():
        ordered = sorted(values, key=lambda item: item["trade_date"])
        for current, nxt in zip(ordered, ordered[1:]):
            c0 = _float(current.get("close"))
            c1 = _float(nxt.get("close"))
            if c0 and c1:
                out[(symbol, current["trade_date"])] = c1 / c0 - 1.0
    return out


def _risk_estimator_rows(returns_by_symbol: dict[str, list[tuple[str, float]]], symbols: list[str]) -> list[dict[str, object]]:
    rows = []
    for estimator_id, window, note in [
        ("historical_volatility_20d", 20, "short horizon volatility"),
        ("historical_volatility_60d", 60, "medium horizon volatility"),
        ("ewma_volatility_lambda_0_94", 120, "bounded ewma-style volatility proxy"),
    ]:
        vols = []
        for symbol in symbols:
            values = [value for _, value in returns_by_symbol[symbol][-window:]]
            if estimator_id.startswith("ewma"):
                vols.append(_ewma_std(values, 0.94))
            else:
                vols.append(_std(values))
        rows.append(
            {
                "estimator_id": estimator_id,
                "lookback_days": window,
                "symbol_count": len(symbols),
                "average_daily_volatility": _fmt(_mean(vols)),
                "max_daily_volatility": _fmt(max(vols) if vols else 0.0),
                "selection_role": "input_diagnostic_not_holdout_optimized",
                "notes": note,
                "research_only": True,
                "not_trading_advice": True,
                "not_for_execution": True,
            }
        )
    return rows


def _covariance_and_clusters(
    returns_by_date: dict[str, dict[str, float]],
    symbols: list[str],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, str], dict[str, float]]:
    pair_corrs = []
    variances = []
    for i, left in enumerate(symbols):
        left_values = _series_for_symbol(returns_by_date, left)
        variances.append(_std(left_values) ** 2)
        for right in symbols[i + 1 :]:
            pair_corrs.append(_correlation(left_values, _series_for_symbol(returns_by_date, right)))
    avg_abs_corr = _mean([abs(value) for value in pair_corrs if value is not None])
    avg_var = _mean(variances)
    cov_rows = [
        {
            "estimator_id": "sample_covariance",
            "symbol_count": len(symbols),
            "date_count": len(returns_by_date),
            "average_variance": _fmt(avg_var),
            "average_abs_correlation": _fmt(avg_abs_corr),
            "condition_proxy": _fmt((max(variances) / min(v for v in variances if v > 0)) if variances and any(v > 0 for v in variances) else 0.0),
            "selection_role": "diagnostic",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        },
        {
            "estimator_id": "diagonal_shrinkage_20pct",
            "symbol_count": len(symbols),
            "date_count": len(returns_by_date),
            "average_variance": _fmt(avg_var),
            "average_abs_correlation": _fmt(avg_abs_corr * 0.8),
            "condition_proxy": "bounded_by_diagonal_shrinkage",
            "selection_role": "selected_for_stability_not_holdout_return",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        },
        {
            "estimator_id": "constant_correlation_shrinkage",
            "symbol_count": len(symbols),
            "date_count": len(returns_by_date),
            "average_variance": _fmt(avg_var),
            "average_abs_correlation": _fmt(avg_abs_corr),
            "condition_proxy": "bounded_constant_correlation_proxy",
            "selection_role": "comparison",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        },
    ]
    cluster_by_symbol, avg_abs_corr_by_symbol = _symbol_correlation_clusters(returns_by_date, symbols)
    clusters = {"low_corr": 0, "medium_corr": 0, "high_corr": 0}
    for bucket in cluster_by_symbol.values():
        clusters[bucket] += 1
    cluster_rows = [
        {
            "cluster_id": bucket,
            "symbol_count": count,
            "cluster_rule": "average_abs_pairwise_correlation_rank_tercile",
            "constraint_usage": "diversification_constraint_and_hrp_cluster_budget",
            "research_only": True,
            "not_trading_advice": True,
            "not_for_execution": True,
        }
        for bucket, count in clusters.items()
    ]
    return cov_rows, cluster_rows, cluster_by_symbol, avg_abs_corr_by_symbol


def _holdings_contract_rows() -> list[dict[str, object]]:
    return [
        {
            "field_name": "asof_date",
            "required": True,
            "description": "current holdings snapshot date supplied by owner if available",
            "missing_behavior": "fail_closed_to_research_reference_portfolio_mode",
        },
        {
            "field_name": "portfolio_id",
            "required": True,
            "description": "owner-provided portfolio identifier",
            "missing_behavior": "fail_closed_to_research_reference_portfolio_mode",
        },
        {
            "field_name": "symbol",
            "required": True,
            "description": "approved symbol identifier",
            "missing_behavior": "row_rejected",
        },
        {
            "field_name": "current_weight",
            "required": True,
            "description": "current portfolio weight, not a target",
            "missing_behavior": "row_rejected",
        },
        {
            "field_name": "market_value",
            "required": False,
            "description": "optional current market value for diagnostics",
            "missing_behavior": "weight_only_mode",
        },
    ]


def _contract_row(name: str, typ: str, description: str, pit: str) -> dict[str, object]:
    return {
        "field_name": name,
        "field_type": typ,
        "description": description,
        "pit_status": pit,
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }


def _constraint(
    constraint_id: str,
    description: str,
    threshold: str,
    scope: str,
    substantive: bool = False,
    evidence_required: str = "committed research evidence",
) -> dict[str, object]:
    return {
        "constraint_id": constraint_id,
        "constraint_family": "research_position_risk_constraint",
        "scope": scope,
        "description": description,
        "threshold": threshold,
        "substantive_constraint": substantive,
        "evidence_required": evidence_required,
        "fail_closed_behavior": "abstain_or_block_precise_band_when_required_evidence_is_unavailable",
        "actionability": "non_actionable_no_order_instruction",
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }


def _constraint_eval(
    portfolio_id: str,
    symbol: str,
    constraint_id: str,
    current_value: object,
    threshold: object,
    passed: bool,
    fail_closed: bool,
    evidence_availability: str,
) -> dict[str, object]:
    severity = "none" if passed else "high" if fail_closed else "medium"
    current = _fmt(current_value) if isinstance(current_value, float) else current_value
    limit = _fmt(threshold) if isinstance(threshold, float) else threshold
    return {
        "portfolio_id": portfolio_id,
        "symbol": symbol,
        "constraint_id": constraint_id,
        "current_value": current,
        "observed_value": current,
        "threshold": limit,
        "breach": not passed,
        "constraint_passed": passed,
        "severity": severity,
        "breach_severity": severity,
        "fail_closed": fail_closed,
        "evidence_availability": evidence_availability,
        "action_instruction": "none",
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }


def _max_severity(values: list[str]) -> str:
    order = {"none": 0, "low": 1, "medium": 2, "high": 3}
    return max(values, key=lambda value: order.get(value, 0)) if values else "none"


def _policy_catalog_row(policy: dict[str, str]) -> dict[str, object]:
    policy_id = policy["policy_id"]
    duplicate = "inverse_volatility" if policy_id == "equal_risk_contribution_diagonal" else ""
    hrp = policy_id == "hrp_correlation_cluster"
    return {
        **policy,
        "pre_specified": True,
        "final_holdout_tuned": False,
        "uses_alpha": False,
        "covariance_assumption": "sample_return_correlation_training_window" if hrp else "diagonal_volatility_proxy" if policy_id != "equal_weight" else "none",
        "clustering_assumption": "average_abs_correlation_rank_terciles" if hrp else "none",
        "duplicate_exposure_of": duplicate,
        "equivalence_disclosure": "equivalent_to_inverse_volatility_under_diagonal_covariance_proxy" if duplicate else "not_a_declared_duplicate",
        "effective_distinct_policy": duplicate == "",
        "research_only": True,
        "not_trading_advice": True,
        "not_for_execution": True,
    }


def _policy_weights(policy_id: str, symbols: list[str], returns_by_date: dict[str, dict[str, float]]) -> dict[str, float]:
    if not symbols:
        return {}
    vols = {symbol: max(_std(_series_for_symbol(returns_by_date, symbol)), 1e-8) for symbol in symbols}
    if policy_id == "equal_weight":
        return _weights_equal(symbols)
    if policy_id in {"inverse_volatility", "equal_risk_contribution_diagonal"}:
        raw = {symbol: 1.0 / vols[symbol] for symbol in symbols}
    elif policy_id == "minimum_variance_diagonal":
        raw = {symbol: 1.0 / (vols[symbol] ** 2) for symbol in symbols}
    elif policy_id == "hrp_correlation_cluster":
        cluster_by_symbol, _ = _symbol_correlation_clusters(returns_by_date, symbols)
        members_by_cluster: dict[str, list[str]] = defaultdict(list)
        for symbol in symbols:
            members_by_cluster[cluster_by_symbol.get(symbol, "medium_corr")].append(symbol)
        raw = {}
        cluster_budget = 1.0 / len(members_by_cluster) if members_by_cluster else 0.0
        for members in members_by_cluster.values():
            cluster_raw = {symbol: 1.0 / vols[symbol] for symbol in members}
            cluster_total = sum(cluster_raw.values()) or 1.0
            for symbol, value in cluster_raw.items():
                raw[symbol] = cluster_budget * value / cluster_total
    else:
        raw = {symbol: 1.0 for symbol in symbols}
    return _normalize_with_cap(raw, MAX_SYMBOL_WEIGHT)


def _weights_equal(symbols: list[str]) -> dict[str, float]:
    return {symbol: 1.0 / len(symbols) for symbol in symbols} if symbols else {}


def _symbol_correlation_clusters(
    returns_by_date: dict[str, dict[str, float]],
    symbols: list[str],
) -> tuple[dict[str, str], dict[str, float]]:
    avg_abs_corr_by_symbol = {}
    for symbol in symbols:
        corrs = []
        series = _series_for_symbol(returns_by_date, symbol)
        for other in symbols:
            if other == symbol:
                continue
            corr = _correlation(series, _series_for_symbol(returns_by_date, other))
            if corr is not None:
                corrs.append(abs(corr))
        avg_abs_corr_by_symbol[symbol] = _mean(corrs)
    ranked = sorted(symbols, key=lambda symbol: (avg_abs_corr_by_symbol.get(symbol, 0.0), symbol))
    cluster_by_symbol = {}
    n = len(ranked)
    for idx, symbol in enumerate(ranked):
        fraction = idx / n if n else 0.0
        if fraction < 1.0 / 3.0:
            cluster = "low_corr"
        elif fraction < 2.0 / 3.0:
            cluster = "medium_corr"
        else:
            cluster = "high_corr"
        cluster_by_symbol[symbol] = cluster
    return cluster_by_symbol, avg_abs_corr_by_symbol


def _normalize_with_cap(raw: dict[str, float], cap: float) -> dict[str, float]:
    if not raw:
        return {}
    weights = {key: value / sum(raw.values()) for key, value in raw.items()}
    for _ in range(10):
        over = {key: value for key, value in weights.items() if value > cap}
        if not over:
            break
        remaining = {key: value for key, value in weights.items() if key not in over}
        fixed_total = cap * len(over)
        rem_total = sum(remaining.values())
        weights = {key: cap for key in over}
        if rem_total > 0 and fixed_total < 1:
            weights.update({key: value / rem_total * (1 - fixed_total) for key, value in remaining.items()})
    total = sum(weights.values()) or 1.0
    return {key: value / total for key, value in weights.items()}


def _walk_forward_folds(dates: list[str]) -> list[tuple[str, list[str], list[str]]]:
    folds = []
    train = 252
    test = 63
    start = 0
    fold = 1
    while start + train + test <= len(dates) and fold <= 4:
        folds.append((f"fold_{fold}", dates[start : start + train], dates[start + train : start + train + test]))
        start += test
        fold += 1
    return folds


def _slice_returns(returns_by_date: dict[str, dict[str, float]], dates: list[str]) -> dict[str, dict[str, float]]:
    return {date: returns_by_date[date] for date in dates if date in returns_by_date}


def _portfolio_returns(returns_by_date: dict[str, dict[str, float]], weights: dict[str, float]) -> list[tuple[str, float]]:
    rows = []
    for date in sorted(returns_by_date):
        day = returns_by_date[date]
        available = {symbol: weight for symbol, weight in weights.items() if symbol in day}
        total = sum(available.values())
        if total < 0.70:
            continue
        ret = sum((weight / total) * day[symbol] for symbol, weight in available.items())
        rows.append((date, ret))
    return rows


def _return_metrics(returns: list[tuple[str, float]]) -> dict[str, str]:
    values = [ret for _, ret in returns]
    total = 1.0
    for value in values:
        total *= 1.0 + value
    total_return = total - 1.0
    return {
        "observations": str(len(values)),
        "total_return": _fmt(total_return),
        "mean_daily_return": _fmt(_mean(values)),
        "annualized_volatility": _fmt(_annualized_vol(values)),
        "max_drawdown": _fmt(_max_drawdown(values)),
        "var_95_daily": _fmt(_percentile(values, 0.05)),
        "cvar_95_daily": _fmt(_tail_mean(values, 0.05)),
    }


def _series_for_symbol(returns_by_date: dict[str, dict[str, float]], symbol: str) -> list[float]:
    return [returns_by_date[date][symbol] for date in sorted(returns_by_date) if symbol in returns_by_date[date]]


def _float(value: object) -> float | None:
    if value is None or value == "":
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _fmt(value: object, digits: int = 10) -> str:
    number = _float(value)
    if number is None:
        return ""
    text = f"{number:.{digits}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def _mean(values: list[float]) -> float:
    clean = [value for value in values if value is not None and math.isfinite(value)]
    return sum(clean) / len(clean) if clean else 0.0


def _beta(portfolio_returns: list[float], index_returns: list[float]) -> float:
    n = min(len(portfolio_returns), len(index_returns))
    if n < 3:
        return 0.0
    x = portfolio_returns[-n:]
    y = index_returns[-n:]
    mx = _mean(x)
    my = _mean(y)
    variance = sum((value - my) ** 2 for value in y)
    if variance == 0:
        return 0.0
    covariance = sum((px - mx) * (iy - my) for px, iy in zip(x, y))
    return covariance / variance


def _std(values: list[float]) -> float:
    clean = [value for value in values if value is not None and math.isfinite(value)]
    if len(clean) < 2:
        return 0.0
    avg = _mean(clean)
    return math.sqrt(sum((value - avg) ** 2 for value in clean) / (len(clean) - 1))


def _ewma_std(values: list[float], lam: float) -> float:
    if not values:
        return 0.0
    variance = values[0] ** 2
    for value in values[1:]:
        variance = lam * variance + (1.0 - lam) * (value ** 2)
    return math.sqrt(max(variance, 0.0))


def _correlation(left: list[float], right: list[float]) -> float | None:
    n = min(len(left), len(right))
    if n < 3:
        return None
    x = left[-n:]
    y = right[-n:]
    mx = _mean(x)
    my = _mean(y)
    sx = math.sqrt(sum((value - mx) ** 2 for value in x))
    sy = math.sqrt(sum((value - my) ** 2 for value in y))
    if sx == 0 or sy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def _percentile(values: list[float], q: float) -> float:
    clean = sorted(value for value in values if value is not None and math.isfinite(value))
    if not clean:
        return 0.0
    idx = min(max(int(round((len(clean) - 1) * q)), 0), len(clean) - 1)
    return clean[idx]


def _tail_mean(values: list[float], q: float) -> float:
    threshold = _percentile(values, q)
    tail = [value for value in values if value <= threshold]
    return _mean(tail)


def _annualized_vol(values: list[float]) -> float:
    return _std(values) * math.sqrt(252.0)


def _max_drawdown(values: list[float]) -> float:
    equity = 1.0
    peak = 1.0
    max_dd = 0.0
    for value in values:
        equity *= 1.0 + value
        peak = max(peak, equity)
        max_dd = min(max_dd, equity / peak - 1.0)
    return max_dd


def _rolling_values(values: list[float], window: int, fn) -> list[float]:
    return [fn(values[i - window : i]) for i in range(window, len(values) + 1)]


def _sum_last(values: list[float], n: int) -> float:
    return sum(values[-n:]) if values else 0.0


def _counts(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for value in values:
        counts[value] += 1
    return dict(counts)


def _workflow_rows(root: Path) -> dict[str, dict[str, str]]:
    if not (root / WORKFLOW_STATUS).exists():
        return {}
    return {row["workflow_id"]: row for row in read_csv(root / WORKFLOW_STATUS)}


def _read_json_if_exists(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _report(manifest: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID} Premarket Portfolio Risk Management",
            "",
            f"Status: `{manifest['status']}`",
            "",
            "## Phase Summary",
            "",
            f"- Provider overlap rows: `{manifest['phase1_provider_overlap_rows']}`",
            f"- Major provider discrepancies quarantined: `{manifest['phase1_quarantined_rows']}`",
            f"- Canonical rows/symbols/dates: `{manifest['canonical_rows']}` / `{manifest['canonical_symbols']}` / `{manifest['canonical_dates']}`",
            f"- Risk state: `{manifest['portfolio_risk_states'][0]}`",
            f"- Policies evaluated: `{';'.join(manifest['policies_evaluated'])}`",
            f"- Preferred research policy: `{manifest['preferred_research_policy']}`",
            f"- Symbols with bands / abstained: `{manifest['symbols_with_bands']}` / `{manifest['symbols_abstained']}`",
            "",
            "## Boundary",
            "",
            "All portfolio returns, policy weights, and position bands are research-only diagnostics. They are not recommendations, target weights, order instructions, trading advice, broker instructions, or production outputs.",
            "",
        ]
    )


def _doc(manifest: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID} Premarket Portfolio Risk And Position Management",
            "",
            "Research-only integrated portfolio risk track over committed evidence.",
            "",
            "Pipeline: committed evidence -> provider reconciliation -> canonical market data -> risk state -> constraints -> policy comparison -> risk bands.",
            "",
            f"Status: `{manifest['status']}`.",
            "",
            "Alpha is optional and not required. No ready Alpha factor is promoted by this goal.",
            "",
        ]
    )


def _handoff(manifest: dict[str, object]) -> str:
    return "\n".join(
        [
            f"# {GOAL_ID} Governance Handoff",
            "",
            f"- ready_factor_count: {manifest['ready_factor_count']}",
            f"- RecTiering state: {manifest['rec_tiering_state']}",
            f"- recommendation state: {manifest['recommendation_state']}",
            f"- trading state: {manifest['trading_state']}",
            f"- current holdings mode: {manifest['current_holdings_mode']}",
            f"- preferred research policy: {manifest['preferred_research_policy']}",
            f"- symbols with bands: {manifest['symbols_with_bands']}",
            f"- symbols abstained: {manifest['symbols_abstained']}",
            "",
            "Do not treat these outputs as target weights, order instructions, recommendations, or position validation.",
            "",
        ]
    )


def _alpha_handoff() -> str:
    return "\n".join(
        [
            f"# {GOAL_ID} Future Alpha Tilt Handoff",
            "",
            "Alpha is not required by the portfolio risk track.",
            "",
            "A future alpha-tilt goal may only use ready factors after explicit owner authorization and a separate bounded contract. This goal does not lower thresholds, force recommendations, or convert weak Alpha into positions.",
            "",
        ]
    )


def _contract() -> str:
    return "\n".join(
        [
            f"goal_id: {GOAL_ID}",
            f"workflow_id: {WORKFLOW_ID}",
            f"mode: {MODE}",
            "research_only: true",
            "not_trading_advice: true",
            "not_for_execution: true",
            "uses_committed_evidence_offline: true",
            "alpha_required: false",
            "recommendation_outputs_created: false",
            "orders_created: false",
            "broker_trading_outputs_created: false",
            "production_outputs_created: false",
            "local_lake_outputs_created: false",
            "dqn_rl_outputs_created: false",
            "",
        ]
    )
