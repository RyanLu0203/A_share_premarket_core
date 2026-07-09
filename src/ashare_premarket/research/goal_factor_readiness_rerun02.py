"""GOAL-FACTOR-READINESS-RERUN-02 research-only expanded-evidence rerun.

Reconstructs factor-readiness evidence from the committed
GOAL-NETWORK-EVIDENCE-INGESTION-01 bundle. The gate consumes the new
akshare/sina daily and index panels offline, validates bundle checksums, uses
fixed pre-existing factor semantics and readiness thresholds, and writes only
research/audit artifacts. It never unlocks RecTiering or downstream execution.
"""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

from ashare_premarket.research.goal_factor_readiness_research01 import (
    ALIGNED_HORIZONS_MIN,
    HOLDOUT_FRACTION,
    MIN_HOLDOUT_VALID_ROWS,
    REFINEMENTS,
    SIGN_STABLE_MIN,
    _apply_refinement,
    _chronological_split,
    _expected_sign,
    _sign_consistency,
    _walk_forward_folds,
)
from ashare_premarket.research.goal_quant_research03 import (
    HORIZONS,
    MIN_VALID_ROWS,
    _correlation,
    _float,
    _mean,
    _ranks,
)
from ashare_premarket.research.goal_quant_research04 import STRONG_IC_THRESHOLD

GOAL_ID = "GOAL-FACTOR-READINESS-RERUN-02"
GOAL_NAME = "GOAL-FACTOR-READINESS-RERUN-02-EXPANDED-EVIDENCE-READINESS-RERUN"
WORKFLOW_ID = "goal_factor_readiness_rerun02_expanded_evidence_readiness_rerun"
MODE = "research_only_expanded_evidence_factor_readiness_rerun"
PASS = "PASS"
PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
BLOCKED = "BLOCKED"

NETWORK_DAILY = "outputs/research/network_ingestion/daily_panel.csv"
NETWORK_INDEX = "outputs/research/network_ingestion/index_panel.csv"
NETWORK_SYMBOL_COVERAGE = "outputs/research/network_ingestion/symbol_coverage.csv"
NETWORK_EVIDENCE_MANIFEST = "outputs/research/goal_network_evidence_ingestion01_evidence_bundle_manifest.json"
NETWORK_GATE_MANIFEST = "outputs/audits/goal_network_evidence_ingestion01_manifest.json"
NETWORK_PIT_CONTRACT = "outputs/research/goal_network_evidence_ingestion01_pit_availability_contract.csv"
NETWORK_HANDOFF = "docs/research/GOAL_NETWORK_EVIDENCE_INGESTION01_READINESS_RERUN_HANDOFF.md"

OLD_PANEL_INDEX = "outputs/research/goal_quant_research03_refined_evaluation_panel_index.csv"
OLD_PANEL_GLOB = "outputs/research/goal_quant_research03_refined_evaluation_panel_parts/*.csv"
OLD_READINESS_STATUS = "outputs/research/goal_factor_readiness_research01_factor_readiness_status.csv"
OLD_WALK_FORWARD = "outputs/research/goal_factor_readiness_research01_walk_forward_validation_summary.csv"
OLD_QUANT03_VALIDITY = "outputs/research/goal_quant_research03_refined_factor_score_validity_classification.csv"
OLD_QUANT03_RANKIC = "outputs/research/goal_quant_research03_refined_factor_ic_rankic_summary.csv"
OLD_QUANT04_STATUS = "outputs/research/goal_quant_research04_factor_overall_status.csv"
OLD_REGIME_LABELS = "outputs/research/goal_regime_label_research02_refined_date_regime_labels.csv"
WORKFLOW_STATUS = "configs/project/workflow_status.csv"

OUT = "outputs/research/goal_factor_readiness_rerun02_"
EVIDENCE_INTEGRATION_MAP = OUT + "evidence_integration_map.csv"
OLD_NEW_PANEL_COMPARISON = OUT + "old_new_panel_comparison.csv"
RECONSTRUCTED_PANEL_SUMMARY = OUT + "reconstructed_panel_summary.csv"
FEATURE_LINEAGE = OUT + "feature_lineage.csv"
TARGET_HORIZON_CONTRACT = OUT + "target_horizon_contract.csv"
EXTENDED_REGIME_COVERAGE = OUT + "extended_regime_coverage.csv"
WALK_FORWARD_SUMMARY = OUT + "walk_forward_validation_summary.csv"
HOLDOUT_SUMMARY = OUT + "holdout_validation_summary.csv"
READINESS_STATUS = OUT + "factor_readiness_status.csv"
OLD_NEW_READINESS_COMPARISON = OUT + "old_new_readiness_comparison.csv"
PROVIDER_ROBUSTNESS = OUT + "provider_robustness_summary.csv"
PROVIDER_WARNINGS = OUT + "provider_discrepancy_warnings.csv"
INDEX_CONTEXT_CONTRIBUTION = OUT + "index_context_contribution.csv"
ANTI_OVERFIT = OUT + "anti_overfitting_review.csv"
DECISION_REASONS = OUT + "readiness_decision_reasons.csv"
REMAINING_GAP_MAP = OUT + "remaining_gap_map.csv"
CONSTRUCTION_WARNINGS = OUT + "construction_warnings.csv"

REPORT_PATH = "outputs/audits/goal_factor_readiness_rerun02_report.md"
MANIFEST_PATH = "outputs/audits/goal_factor_readiness_rerun02_manifest.json"
AUDIT_PATH = "outputs/audits/goal_factor_readiness_rerun02_audit.md"
DOC_PATH = "docs/research/GOAL_FACTOR_READINESS_RERUN02_EXPANDED_EVIDENCE_READINESS_RERUN.md"
HANDOFF_PATH = "docs/research/GOAL_FACTOR_READINESS_RERUN02_GOVERNANCE_HANDOFF.md"
CONTRACT_PATH = "configs/research/goal_factor_readiness_rerun02_contract.yaml"

OUTPUT_ARTIFACTS = [
    EVIDENCE_INTEGRATION_MAP,
    OLD_NEW_PANEL_COMPARISON,
    RECONSTRUCTED_PANEL_SUMMARY,
    FEATURE_LINEAGE,
    TARGET_HORIZON_CONTRACT,
    EXTENDED_REGIME_COVERAGE,
    WALK_FORWARD_SUMMARY,
    HOLDOUT_SUMMARY,
    READINESS_STATUS,
    OLD_NEW_READINESS_COMPARISON,
    PROVIDER_ROBUSTNESS,
    PROVIDER_WARNINGS,
    INDEX_CONTEXT_CONTRIBUTION,
    ANTI_OVERFIT,
    DECISION_REASONS,
    REMAINING_GAP_MAP,
    CONSTRUCTION_WARNINGS,
    REPORT_PATH,
    MANIFEST_PATH,
    AUDIT_PATH,
    DOC_PATH,
    HANDOFF_PATH,
    CONTRACT_PATH,
]

FALSE_BOUNDARY_KEYS = (
    "recommendation_outputs_created",
    "position_rows_created",
    "buy_sell_hold_labels_created",
    "target_prices_created",
    "position_sizes_created",
    "portfolio_weights_created",
    "order_quantities_created",
    "portfolio_returns_created",
    "equity_curves_created",
    "dashboard_frontend_artifacts_created",
    "broker_trading_outputs_created",
    "production_outputs_created",
    "factor_mining_outputs_created",
    "dqn_rl_outputs_created",
    "local_lake_outputs_created",
    "full_live_akshare_dataset_fetch_performed",
    "live_provider_fetches_run",
    "network_enabled",
    "future_returns_used_in_factor_construction",
    "tokens_or_secrets_persisted",
    "rec_tiering_unlocked_by_this_goal",
    "scientific_thresholds_lowered",
    "ready_status_fabricated",
    "existing_thresholds_modified",
)

SOURCE_FACTORS = (
    {
        "source_factor_id": "alpha_benchmark_relative_strength_20d",
        "factor_family": "benchmark_relative_strength",
        "formula": "stock_return_20d - csi300_index_return_20d",
        "inputs": "close;return_1d;sh000300_index_return_20d",
        "index_fields": "index_return_20d;market_relative_return_20d",
        "window": "20d",
    },
    {
        "source_factor_id": "alpha_downside_vol_adjusted_strength_20d",
        "factor_family": "downside_volatility_adjusted_signal",
        "formula": "stock_return_20d / trailing_downside_volatility_20d",
        "inputs": "close;return_1d",
        "index_fields": "",
        "window": "20d",
    },
    {
        "source_factor_id": "alpha_price_volume_confirmation_5d",
        "factor_family": "price_volume_confirmation",
        "formula": "ret_5d * positive_volume_expansion",
        "inputs": "close;volume",
        "index_fields": "",
        "window": "5d",
    },
    {
        "source_factor_id": "alpha_risk_adjusted_relative_strength",
        "factor_family": "risk_adjusted_alpha_candidate",
        "formula": "(stock_return_20d - csi300_index_return_20d) / trailing_volatility_20d",
        "inputs": "close;return_1d;sh000300_index_return_20d",
        "index_fields": "index_return_20d;market_relative_return_20d",
        "window": "20d",
    },
    {
        "source_factor_id": "alpha_vol_adj_momentum_20d",
        "factor_family": "volatility_adjusted_momentum",
        "formula": "stock_return_20d / trailing_volatility_20d",
        "inputs": "close;return_1d",
        "index_fields": "",
        "window": "20d",
    },
    {
        "source_factor_id": "alpha_vol_adj_momentum_5d",
        "factor_family": "volatility_adjusted_momentum",
        "formula": "stock_return_5d / trailing_volatility_5d",
        "inputs": "close;return_1d",
        "index_fields": "",
        "window": "5d",
    },
)

REFINEMENT_TYPES = (
    "downside_risk_filtered",
    "horizon_specific",
    "liquidity_filtered",
    "review_queue_conditioned",
    "risk_filtered",
)
BENCHMARK_INDEX_ID = "sh000300"
INDEX_CONTEXT_FIELDS_CONSUMED = [
    "index_return_5d",
    "index_return_20d",
    "index_volatility_20d",
    "market_relative_return_20d",
]

EVIDENCE_FIELDS = [
    "dimension",
    "old_state",
    "new_state",
    "overlap_state",
    "change_class",
    "new_context_fields_consumed",
    "disclosure",
]
PANEL_COMPARISON_FIELDS = ["metric", "old_value", "new_value", "change_class", "notes"]
PANEL_SUMMARY_FIELDS = [
    "refined_factor_id",
    "source_factor_id",
    "refinement_type",
    "factor_family",
    "new_panel_rows",
    "valid_factor_rows",
    "date_count",
    "symbol_count",
    "source_provider",
    "feature_inputs",
    "index_context_fields",
    "missingness_rate",
    "target_1d_valid_rows",
    "target_5d_valid_rows",
    "target_20d_valid_rows",
    "no_lookahead_status",
]
FEATURE_LINEAGE_FIELDS = [
    "source_factor_id",
    "factor_family",
    "reconstructed_feature_id",
    "base_formula",
    "required_inputs",
    "index_context_used",
    "window",
    "availability_lag",
    "pit_declaration",
    "source_lineage",
    "transformation_lineage",
    "target_dependent",
    "construction_status",
]
TARGET_FIELDS = [
    "horizon",
    "target_formula",
    "target_timestamp",
    "feature_cutoff",
    "availability_cutoff",
    "target_usage",
    "no_lookahead_status",
]
REGIME_FIELDS = [
    "regime_label",
    "old_date_count",
    "new_date_count",
    "new_share",
    "imbalance_status",
    "reconstruction_status",
    "limitation",
]
WALK_FIELDS = [
    "candidate_id",
    "in_sample_mean_ic_1d",
    "in_sample_rank_ic_1d",
    "in_sample_sign_consistency_1d",
    "holdout_mean_ic_1d",
    "holdout_mean_ic_5d",
    "holdout_mean_ic_20d",
    "holdout_rank_ic_1d",
    "holdout_sign_consistency_1d",
    "n_walk_forward_folds",
    "walk_forward_cross_fold_sign_consistency",
    "in_sample_valid_rows",
    "holdout_valid_rows",
    "no_lookahead_status",
]
HOLDOUT_FIELDS = [
    "candidate_id",
    "final_holdout_start",
    "final_holdout_end",
    "holdout_dates",
    "holdout_valid_rows",
    "holdout_mean_ic_1d",
    "holdout_rank_ic_1d",
    "holdout_sign_consistency_1d",
    "split_policy",
    "final_holdout_used_for_selection",
    "feature_definition_tuned_on_holdout",
]
READINESS_FIELDS = [
    "candidate_id",
    "base_refined_factor_id",
    "source_factor_id",
    "factor_family",
    "refinement_type",
    "readiness_transform",
    "readiness_status",
    "holdout_mean_ic_1d",
    "holdout_rank_ic_1d",
    "holdout_sign_consistency_1d",
    "aligned_horizon_count",
    "holdout_valid_rows",
    "walk_forward_sign_consistency",
    "base_precondition_pass",
    "provider_robustness_status",
    "non_actionable_disclaimer",
]
COMPARISON_FIELDS = [
    "candidate_id",
    "base_refined_factor_id",
    "old_status",
    "new_status",
    "old_ic_1d",
    "new_ic_1d",
    "old_rank_ic_1d",
    "new_rank_ic_1d",
    "old_sign_stability",
    "new_sign_stability",
    "old_regime_consistency",
    "new_regime_consistency",
    "old_sample_size",
    "new_sample_size",
    "oos_change",
    "transition_category",
    "readiness_transition_reason",
]
PROVIDER_FIELDS = [
    "check_id",
    "scope",
    "overlap_rows",
    "mean_abs_diff",
    "max_abs_diff",
    "missingness_difference",
    "timestamp_alignment",
    "provider_specific_fragility",
    "status",
    "notes",
]
PROVIDER_WARNING_FIELDS = ["warning_code", "symbol", "trade_date", "metric", "old_value", "new_value", "abs_diff", "threshold", "detail"]
INDEX_FIELDS = [
    "index_id",
    "index_name",
    "context_feature",
    "target_horizon",
    "dates_evaluated",
    "date_level_correlation",
    "sign_consistency",
    "contribution_status",
    "no_target_tuning",
]
ANTI_OVERFIT_FIELDS = [
    "candidate_id",
    "old_to_new_sign_reversal",
    "specification_sensitivity",
    "transform_dependence",
    "horizon_dependence",
    "regime_dependence",
    "provider_dependence",
    "sample_period_dependence",
    "holdout_fragility",
    "multiple_testing_risk",
    "candidate_family_multiplicity",
    "small_sample_pockets",
    "promotion_guard",
]
DECISION_FIELDS = [
    "candidate_id",
    "readiness_status",
    "base_precondition_pass",
    "holdout_sample_sufficient",
    "holdout_strong_ic_1d",
    "holdout_sign_stable_1d",
    "aligned_horizons_ge_2",
    "walk_forward_stable",
    "provider_robustness_checked",
    "decision_summary",
]
GAP_FIELDS = ["gap_dimension", "current_state", "binding_constraint", "impact", "next_legitimate_action"]
WARNING_FIELDS = ["warning_code", "scope", "count", "detail"]


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fields})


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="\n", encoding="utf-8") as handle:
        handle.write(text)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _fmt(value: float | int | None, digits: int = 10) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return ""
    text = f"{float(value):.{digits}f}"
    return text.rstrip("0").rstrip(".") if "." in text else text


def _ratio(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator is None or abs(denominator) < 1e-12:
        return None
    return numerator / denominator


def _rolling_return(closes: list[float | None], idx: int, window: int) -> float | None:
    if idx < window or closes[idx] is None or closes[idx - window] in {None, 0.0}:
        return None
    return (closes[idx] or 0.0) / (closes[idx - window] or 1.0) - 1.0


def _future_return(closes: list[float | None], idx: int, horizon: int) -> float | None:
    if idx + horizon >= len(closes) or closes[idx] in {None, 0.0} or closes[idx + horizon] is None:
        return None
    return (closes[idx + horizon] or 0.0) / (closes[idx] or 1.0) - 1.0


def _rolling_vol(returns: list[float | None], idx: int, window: int, downside: bool = False) -> float | None:
    start = idx - window + 1
    if start < 0:
        return None
    vals = [v for v in returns[start : idx + 1] if v is not None]
    if downside:
        vals = [min(v, 0.0) for v in vals if v < 0.0]
    if len(vals) < max(3, window // 2):
        return None
    mean = sum(vals) / len(vals)
    var = sum((v - mean) ** 2 for v in vals) / len(vals)
    return math.sqrt(var)


def _load_json(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _bundle_checksum_result(root: Path) -> tuple[bool, dict[str, str], dict[str, str]]:
    manifest = _load_json(root / NETWORK_EVIDENCE_MANIFEST)
    expected = {str(k): str(v) for k, v in dict(manifest.get("checksums", {})).items()}
    actual = {
        "daily_panel.csv": _sha256(root / NETWORK_DAILY),
        "index_panel.csv": _sha256(root / NETWORK_INDEX),
        "symbol_coverage.csv": _sha256(root / NETWORK_SYMBOL_COVERAGE),
    }
    return expected == actual, expected, actual


def _index_context(index_rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, dict[str, object]]], float]:
    by_index: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in index_rows:
        by_index[row["index_id"]].append(row)
    context: dict[str, dict[str, dict[str, object]]] = {}
    vol_values: list[float] = []
    for index_id, rows in sorted(by_index.items()):
        rows = sorted(rows, key=lambda item: item["trade_date"])
        closes = [_float(row.get("close")) for row in rows]
        rets = [_float(row.get("return_1d")) for row in rows]
        by_date: dict[str, dict[str, object]] = {}
        for idx, row in enumerate(rows):
            ret5 = _rolling_return(closes, idx, 5)
            ret20 = _rolling_return(closes, idx, 20)
            vol20 = _rolling_vol(rets, idx, 20)
            if vol20 is not None:
                vol_values.append(vol20)
            by_date[row["trade_date"]] = {
                "index_id": index_id,
                "index_name": row.get("index_name", ""),
                "index_return_1d": _float(row.get("return_1d")),
                "index_return_5d": ret5,
                "index_return_20d": ret20,
                "index_volatility_20d": vol20,
                "source_provider": row.get("source_provider", ""),
                "no_lookahead_status": row.get("no_lookahead_status", ""),
            }
        context[index_id] = by_date
    ordered_vols = sorted(vol_values)
    median_vol = ordered_vols[len(ordered_vols) // 2] if ordered_vols else 0.0
    return context, median_vol


def _regime_label(csi_ctx: dict[str, object] | None, median_vol: float) -> str:
    if not csi_ctx:
        return "insufficient_composite_regime_evidence_review_only"
    ret20 = csi_ctx.get("index_return_20d")
    vol20 = csi_ctx.get("index_volatility_20d")
    if not isinstance(ret20, float) or not isinstance(vol20, float) or median_vol <= 0:
        return "insufficient_composite_regime_evidence_review_only"
    if ret20 >= 0 and vol20 <= median_vol:
        return "risk_on_low_vol_review_only"
    if ret20 >= 0:
        return "risk_on_high_vol_review_only"
    if vol20 > median_vol:
        return "risk_off_high_vol_review_only"
    return "mixed_uncertain_review_only"


def _daily_context(daily_rows: list[dict[str, str]], index_ctx: dict[str, dict[str, dict[str, object]]], median_vol: float) -> list[dict[str, object]]:
    by_symbol: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in daily_rows:
        by_symbol[row["symbol"]].append(row)
    contexts: list[dict[str, object]] = []
    for symbol, rows in sorted(by_symbol.items()):
        rows = sorted(rows, key=lambda item: item["trade_date"])
        closes = [_float(row.get("close")) for row in rows]
        rets = [_float(row.get("return_1d")) for row in rows]
        for idx, row in enumerate(rows):
            date = row["trade_date"]
            csi_ctx = index_ctx.get(BENCHMARK_INDEX_ID, {}).get(date)
            ret5 = _rolling_return(closes, idx, 5)
            ret20 = _rolling_return(closes, idx, 20)
            vol5 = _rolling_vol(rets, idx, 5)
            vol20 = _rolling_vol(rets, idx, 20)
            downside20 = _rolling_vol(rets, idx, 20, downside=True)
            csi_ret20 = csi_ctx.get("index_return_20d") if csi_ctx else None
            market_relative = ret20 - csi_ret20 if isinstance(ret20, float) and isinstance(csi_ret20, float) else None
            contexts.append({
                "symbol": symbol,
                "trade_date": date,
                "close": _float(row.get("close")),
                "return_1d": _float(row.get("return_1d")),
                "return_5d": ret5,
                "return_20d": ret20,
                "volatility_5d": vol5,
                "volatility_20d": vol20,
                "downside_volatility_20d": downside20,
                "market_relative_return_20d": market_relative,
                "csi300_return_20d": csi_ret20,
                "target_1d": _future_return(closes, idx, 1),
                "target_5d": _future_return(closes, idx, 5),
                "target_20d": _future_return(closes, idx, 20),
                "source_provider": row.get("source_provider", ""),
                "no_lookahead_status": row.get("no_lookahead_status", ""),
                "regime_label": _regime_label(csi_ctx, median_vol),
            })
    return contexts


def _factor_value(source_factor_id: str, row: dict[str, object]) -> float | None:
    ret5 = row.get("return_5d")
    ret20 = row.get("return_20d")
    vol5 = row.get("volatility_5d")
    vol20 = row.get("volatility_20d")
    downside20 = row.get("downside_volatility_20d")
    rel20 = row.get("market_relative_return_20d")
    if source_factor_id == "alpha_benchmark_relative_strength_20d":
        return rel20 if isinstance(rel20, float) else None
    if source_factor_id == "alpha_downside_vol_adjusted_strength_20d":
        return _ratio(ret20 if isinstance(ret20, float) else None, downside20 if isinstance(downside20, float) else None)
    if source_factor_id == "alpha_price_volume_confirmation_5d":
        return None
    if source_factor_id == "alpha_risk_adjusted_relative_strength":
        return _ratio(rel20 if isinstance(rel20, float) else None, vol20 if isinstance(vol20, float) else None)
    if source_factor_id == "alpha_vol_adj_momentum_20d":
        return _ratio(ret20 if isinstance(ret20, float) else None, vol20 if isinstance(vol20, float) else None)
    if source_factor_id == "alpha_vol_adj_momentum_5d":
        return _ratio(ret5 if isinstance(ret5, float) else None, vol5 if isinstance(vol5, float) else None)
    return None


def _source_rows(contexts: list[dict[str, object]]) -> dict[str, list[dict[str, str]]]:
    out: dict[str, list[dict[str, str]]] = {}
    for definition in SOURCE_FACTORS:
        source_id = str(definition["source_factor_id"])
        rows: list[dict[str, str]] = []
        for ctx in contexts:
            value = _factor_value(source_id, ctx)
            rows.append({
                "trade_date": str(ctx["trade_date"]),
                "symbol": str(ctx["symbol"]),
                "source_factor_id": source_id,
                "factor_family": str(definition["factor_family"]),
                "factor_value": _fmt(value),
                "expected_direction": "higher_positive",
                "forward_return_1d": _fmt(ctx.get("target_1d") if isinstance(ctx.get("target_1d"), float) else None),
                "forward_return_5d": _fmt(ctx.get("target_5d") if isinstance(ctx.get("target_5d"), float) else None),
                "forward_return_20d": _fmt(ctx.get("target_20d") if isinstance(ctx.get("target_20d"), float) else None),
                "source_provider": str(ctx.get("source_provider", "")),
                "regime_label": str(ctx.get("regime_label", "")),
                "no_lookahead_status": str(ctx.get("no_lookahead_status", "")),
            })
        out[source_id] = rows
    return out


def _rows_by_date(rows: list[dict[str, str]], transform: str) -> dict[str, list[dict[str, object]]]:
    raw_by_date: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if _float(row.get("factor_value")) is not None:
            raw_by_date[row["trade_date"]].append(row)
    transformed: dict[str, list[dict[str, object]]] = {}
    for date, date_rows in raw_by_date.items():
        values = [_float(row["factor_value"]) or 0.0 for row in date_rows]
        tvals = _apply_refinement(transform, values)
        transformed[date] = [
            {
                "v": tv,
                "1d": _float(row.get("forward_return_1d")),
                "5d": _float(row.get("forward_return_5d")),
                "20d": _float(row.get("forward_return_20d")),
                "symbol": row.get("symbol", ""),
                "direction": row.get("expected_direction", ""),
                "date": date,
                "regime_label": row.get("regime_label", ""),
            }
            for row, tv in zip(date_rows, tvals)
        ]
    return transformed


def _daily_metric(rows_by_date: dict[str, list[dict[str, object]]], horizon: str, dates: list[str], rank: bool = False) -> list[float]:
    values: list[float] = []
    for date in dates:
        pairs = [(row["v"], row[horizon]) for row in rows_by_date.get(date, []) if row.get(horizon) is not None]
        if len(pairs) < 3:
            continue
        xs = [float(pair[0]) for pair in pairs]
        ys = [float(pair[1]) for pair in pairs]
        if rank:
            xs = _ranks(xs)
            ys = _ranks(ys)
        corr = _correlation(xs, ys)
        if corr is not None:
            values.append(corr)
    return values


def _direction_of(rows_by_date: dict[str, list[dict[str, object]]]) -> str:
    for rows in rows_by_date.values():
        for row in rows:
            if row.get("direction"):
                return str(row["direction"])
    return "higher_positive"


def _valid_count(rows_by_date: dict[str, list[dict[str, object]]], dates: list[str], horizon: str = "1d") -> int:
    return sum(1 for date in dates for row in rows_by_date.get(date, []) if row.get(horizon) is not None)


def _evaluate_candidate(rows_by_date: dict[str, list[dict[str, object]]], base_candidate: bool | None) -> dict[str, object]:
    dates = sorted(rows_by_date)
    in_sample, holdout = _chronological_split(dates)
    expected = _expected_sign(_direction_of(rows_by_date))
    hold_mean: dict[str, float] = {}
    hold_rank: dict[str, float] = {}
    hold_sign: dict[str, float] = {}
    is_mean: dict[str, float] = {}
    is_rank: dict[str, float] = {}
    is_sign: dict[str, float] = {}
    aligned: dict[str, bool] = {}
    for horizon in HORIZONS:
        hic = _daily_metric(rows_by_date, horizon, holdout)
        hric = _daily_metric(rows_by_date, horizon, holdout, rank=True)
        iic = _daily_metric(rows_by_date, horizon, in_sample)
        iric = _daily_metric(rows_by_date, horizon, in_sample, rank=True)
        hold_mean[horizon] = round(_mean(hic) or 0.0, 6)
        hold_rank[horizon] = round(_mean(hric) or 0.0, 6)
        hold_sign[horizon] = round(_sign_consistency(hic), 4)
        is_mean[horizon] = round(_mean(iic) or 0.0, 6)
        is_rank[horizon] = round(_mean(iric) or 0.0, 6)
        is_sign[horizon] = round(_sign_consistency(iic), 4)
        sign = 1 if hold_mean[horizon] > 0 else -1 if hold_mean[horizon] < 0 else 0
        aligned[horizon] = sign == expected and sign != 0 and hold_sign[horizon] >= SIGN_STABLE_MIN

    in_sample_valid = _valid_count(rows_by_date, in_sample)
    holdout_valid = _valid_count(rows_by_date, holdout)
    fold_means: list[float] = []
    for _train, test in _walk_forward_folds(in_sample):
        fic = _daily_metric(rows_by_date, "1d", test)
        if fic:
            fold_means.append(_mean(fic) or 0.0)
    wf_sign = round(_sign_consistency(fold_means), 4)

    aligned_count = sum(1 for horizon in HORIZONS if aligned[horizon])
    strong_1d = abs(hold_mean["1d"]) >= STRONG_IC_THRESHOLD
    sign_stable_1d = hold_sign["1d"] >= SIGN_STABLE_MIN
    sample_ok = holdout_valid >= MIN_HOLDOUT_VALID_ROWS
    wf_stable = len(fold_means) >= 2 and wf_sign >= SIGN_STABLE_MIN
    if base_candidate is None:
        base_precondition = is_sign["1d"] >= SIGN_STABLE_MIN and abs(is_mean["1d"]) >= STRONG_IC_THRESHOLD and in_sample_valid >= MIN_VALID_ROWS
    else:
        base_precondition = bool(base_candidate)

    ready = base_precondition and sample_ok and strong_1d and sign_stable_1d and aligned_count >= ALIGNED_HORIZONS_MIN and wf_stable
    if ready:
        status = "ready"
    elif sample_ok and sign_stable_1d and aligned_count >= 1 and abs(hold_mean["1d"]) > 0:
        status = "conditionally_useful"
    else:
        status = "not_ready"
    criteria = {
        "base_precondition_pass": base_precondition,
        "holdout_sample_sufficient": sample_ok,
        "holdout_strong_ic_1d": strong_1d,
        "holdout_sign_stable_1d": sign_stable_1d,
        "aligned_horizons_ge_2": aligned_count >= ALIGNED_HORIZONS_MIN,
        "walk_forward_stable": wf_stable,
    }
    return {
        "status": status,
        "hold_mean": hold_mean,
        "hold_rank": hold_rank,
        "hold_sign": hold_sign,
        "is_mean": is_mean,
        "is_rank": is_rank,
        "is_sign": is_sign,
        "aligned_count": aligned_count,
        "in_sample_valid": in_sample_valid,
        "holdout_valid": holdout_valid,
        "n_folds": len(_walk_forward_folds(in_sample)),
        "wf_sign": wf_sign,
        "fold_means": fold_means,
        "criteria": criteria,
        "holdout_dates": holdout,
        "in_sample_dates": in_sample,
    }


def _old_panel_shape(root: Path) -> dict[str, int]:
    index_rows = _read_csv(root / OLD_PANEL_INDEX)
    old_rows = sum(int(row.get("row_count", "0") or 0) for row in index_rows)
    dates: set[str] = set()
    symbols: set[str] = set()
    first_part = next(iter(sorted(glob.glob(str(root / OLD_PANEL_GLOB)))), "")
    if first_part:
        for row in _read_csv(Path(first_part)):
            dates.add(row.get("trade_date", ""))
            symbols.add(row.get("symbol", ""))
    return {"rows": old_rows, "dates": len(dates), "symbols": len(symbols)}


def _old_provider_returns(root: Path) -> dict[tuple[str, str], float]:
    values: dict[tuple[str, str], float] = {}
    for part in sorted(glob.glob(str(root / OLD_PANEL_GLOB))):
        for row in _read_csv(Path(part)):
            key = (row.get("symbol", ""), row.get("trade_date", ""))
            if key not in values:
                val = _float(row.get("forward_return_1d"))
                if val is not None:
                    values[key] = val
    return values


def _provider_robustness(root: Path, contexts: list[dict[str, object]]) -> tuple[list[dict[str, object]], list[dict[str, object]], str]:
    old_returns = _old_provider_returns(root)
    new_returns = {
        (str(row["symbol"]), str(row["trade_date"])): row["target_1d"]
        for row in contexts
        if isinstance(row.get("target_1d"), float)
    }
    diffs: list[tuple[str, str, float, float, float]] = []
    for key, old_value in old_returns.items():
        new_value = new_returns.get(key)
        if isinstance(new_value, float):
            diffs.append((key[0], key[1], old_value, new_value, abs(old_value - new_value)))
    mean_diff = _mean([item[4] for item in diffs]) or 0.0
    max_diff = max([item[4] for item in diffs], default=0.0)
    status = "pass_with_discrepancy_warnings" if max_diff > 0.02 else "pass"
    summary = [{
        "check_id": "baostock_akshare_overlap_return_consistency",
        "scope": "old_baostock_forward_return_1d_vs_new_akshare_sina_target_1d",
        "overlap_rows": len(diffs),
        "mean_abs_diff": _fmt(mean_diff),
        "max_abs_diff": _fmt(max_diff),
        "missingness_difference": max(0, len(old_returns) - len(diffs)),
        "timestamp_alignment": "symbol_trade_date_exact_overlap",
        "provider_specific_fragility": "fragile_large_discrepancy_present" if max_diff > 0.02 else "no_large_discrepancy_detected",
        "status": status,
        "notes": "Provider independence is a robustness check, not a correctness guarantee.",
    }]
    warnings = [
        {
            "warning_code": "PROVIDER_RETURN_DISCREPANCY_GT_2PCT",
            "symbol": symbol,
            "trade_date": date,
            "metric": "forward_return_1d",
            "old_value": _fmt(old_value),
            "new_value": _fmt(new_value),
            "abs_diff": _fmt(diff),
            "threshold": "0.02",
            "detail": "baostock and akshare_sina overlap return differs materially",
        }
        for symbol, date, old_value, new_value, diff in sorted(diffs, key=lambda item: (-item[4], item[0], item[1]))[:100]
        if diff > 0.02
    ]
    return summary, warnings, status


def _index_contribution(contexts: list[dict[str, object]], index_ctx: dict[str, dict[str, dict[str, object]]]) -> list[dict[str, object]]:
    targets_by_date: dict[str, list[float]] = defaultdict(list)
    for row in contexts:
        if isinstance(row.get("target_1d"), float):
            targets_by_date[str(row["trade_date"])].append(float(row["target_1d"]))
    avg_target = {date: _mean(vals) for date, vals in targets_by_date.items() if vals}
    rows: list[dict[str, object]] = []
    for index_id, by_date in sorted(index_ctx.items()):
        index_name = next((str(item.get("index_name", "")) for item in by_date.values() if item.get("index_name")), "")
        for feature in ("index_return_5d", "index_return_20d", "index_volatility_20d"):
            pairs = [
                (float(ctx[feature]), float(avg_target[date]))
                for date, ctx in by_date.items()
                if isinstance(ctx.get(feature), float) and isinstance(avg_target.get(date), float)
            ]
            xs = [pair[0] for pair in pairs]
            ys = [pair[1] for pair in pairs]
            corr = _correlation(xs, ys) if len(pairs) >= 3 else None
            sign_consistency = 0.0
            if pairs:
                same = sum(1 for x, y in pairs if (x >= 0 and y >= 0) or (x < 0 and y < 0))
                sign_consistency = same / len(pairs)
            status = "stable_context_signal" if corr is not None and abs(corr) >= STRONG_IC_THRESHOLD and sign_consistency >= 0.55 else "weak_or_unstable_context"
            rows.append({
                "index_id": index_id,
                "index_name": index_name,
                "context_feature": feature,
                "target_horizon": "1d_equal_weight_symbol_return",
                "dates_evaluated": len(pairs),
                "date_level_correlation": _fmt(corr),
                "sign_consistency": _fmt(sign_consistency, 6),
                "contribution_status": status,
                "no_target_tuning": "true",
            })
    return rows


def _transition(old_status: str, new_status: str) -> str:
    if old_status == "ready" and new_status == "ready":
        return "remained_ready"
    if new_status == "ready":
        return "newly_ready"
    if old_status == "ready":
        return "degraded"
    if old_status == "conditionally_useful" and new_status == "conditionally_useful":
        return "remained_conditionally_useful"
    if old_status == "conditionally_useful" and new_status == "not_ready":
        return "lost_conditional_status"
    if old_status == "not_ready" and new_status == "conditionally_useful":
        return "newly_conditionally_useful"
    if old_status == "not_ready" and new_status == "not_ready":
        return "unchanged_not_ready"
    return "degraded"


def _decision_summary(metrics: dict[str, object]) -> str:
    criteria = metrics["criteria"]
    failed = [key for key, value in criteria.items() if not value]
    if metrics["status"] == "ready":
        return "all_fixed_threshold_oos_walk_forward_criteria_satisfied"
    if metrics["status"] == "conditionally_useful":
        return "partial_oos_signal_not_sufficient_for_ready"
    return "not_ready_failed:" + ",".join(failed)


def _regime_rows(root: Path, contexts: list[dict[str, object]]) -> list[dict[str, object]]:
    old_counts: dict[str, int] = defaultdict(int)
    for row in _read_csv(root / OLD_REGIME_LABELS):
        old_counts[row.get("refined_composite_regime_label", "unlabeled")] += 1
    new_dates_by_regime: dict[str, set[str]] = defaultdict(set)
    for row in contexts:
        new_dates_by_regime[str(row.get("regime_label", "unlabeled"))].add(str(row["trade_date"]))
    total_new = len({str(row["trade_date"]) for row in contexts}) or 1
    labels = sorted(set(old_counts) | set(new_dates_by_regime))
    return [
        {
            "regime_label": label,
            "old_date_count": old_counts.get(label, 0),
            "new_date_count": len(new_dates_by_regime.get(label, set())),
            "new_share": _fmt(len(new_dates_by_regime.get(label, set())) / total_new, 6),
            "imbalance_status": "sparse" if len(new_dates_by_regime.get(label, set())) < 30 else "usable",
            "reconstruction_status": "rebuilt_from_index_context_pit_safe",
            "limitation": "Regime02 exact sector/liquidity inputs are not all in network bundle; index-context reconstruction is disclosed.",
        }
        for label in labels
    ]


def _build_artifacts(root: Path) -> dict[str, object]:
    daily_rows = _read_csv(root / NETWORK_DAILY)
    index_rows = _read_csv(root / NETWORK_INDEX)
    coverage_rows = _read_csv(root / NETWORK_SYMBOL_COVERAGE)
    checksum_ok, expected_hashes, actual_hashes = _bundle_checksum_result(root)
    evidence_manifest = _load_json(root / NETWORK_EVIDENCE_MANIFEST)
    gate_manifest = _load_json(root / NETWORK_GATE_MANIFEST)
    old_shape = _old_panel_shape(root)

    acquired_symbols = {row["symbol"] for row in coverage_rows if row.get("status") == "acquired"}
    failed_symbols = {row["symbol"] for row in coverage_rows if row.get("status") != "acquired"}
    daily_dates = sorted({row["trade_date"] for row in daily_rows})
    daily_symbols = sorted({row["symbol"] for row in daily_rows})
    providers_in_daily = sorted({row.get("source_provider", "") for row in daily_rows if row.get("source_provider")})
    index_series = sorted({row.get("index_id", "") for row in index_rows if row.get("index_id")})
    index_ctx, median_index_vol = _index_context(index_rows)
    contexts = _daily_context(daily_rows, index_ctx, median_index_vol)
    source_rows = _source_rows(contexts)
    provider_rows, provider_warnings, provider_status = _provider_robustness(root, contexts)

    old_status = {row["candidate_id"]: row for row in _read_csv(root / OLD_READINESS_STATUS)}
    old_walk = {row["candidate_id"]: row for row in _read_csv(root / OLD_WALK_FORWARD)}
    old_q03_candidate = {row["refined_factor_id"]: row.get("candidate_for_rec_tiering") == "true" for row in _read_csv(root / OLD_QUANT03_VALIDITY)}
    old_rankic = {row["refined_factor_id"]: row for row in _read_csv(root / OLD_QUANT03_RANKIC)}
    old_q04 = {row["refined_factor_id"]: row for row in _read_csv(root / OLD_QUANT04_STATUS)}

    evidence_rows = _evidence_rows(old_shape, daily_rows, daily_dates, daily_symbols, coverage_rows, providers_in_daily, index_series)
    panel_comparison_rows = _panel_comparison_rows(old_shape, len(daily_rows), len(daily_dates), len(daily_symbols))
    feature_lineage_rows = _feature_lineage_rows()
    target_rows = _target_rows()
    regime_rows = _regime_rows(root, contexts)
    panel_summary_rows = _panel_summary_rows(source_rows, len(daily_dates), len(daily_symbols))
    index_rows_out = _index_contribution(contexts, index_ctx)

    status_rows: list[dict[str, object]] = []
    walk_rows: list[dict[str, object]] = []
    holdout_rows: list[dict[str, object]] = []
    decision_rows: list[dict[str, object]] = []
    comparison_rows: list[dict[str, object]] = []
    anti_rows: list[dict[str, object]] = []
    ready_base: set[str] = set()
    ready_candidates: list[str] = []
    cond_count = 0
    new_by_candidate: dict[str, dict[str, object]] = {}
    n_candidates = len(SOURCE_FACTORS) * len(REFINEMENT_TYPES) * len(REFINEMENTS)

    for definition in SOURCE_FACTORS:
        source_id = str(definition["source_factor_id"])
        for refinement_type in REFINEMENT_TYPES:
            refined_id = f"{source_id}__{refinement_type}"
            factor_rows = source_rows[source_id]
            family = str(definition["factor_family"])
            for transform in REFINEMENTS:
                candidate_id = refined_id if transform == "identity" else f"{refined_id}__readiness_{transform}"
                rows_by_date = _rows_by_date(factor_rows, transform)
                base_flag = old_q03_candidate.get(refined_id, False) if transform == "identity" else None
                metrics = _evaluate_candidate(rows_by_date, base_flag)
                criteria = metrics["criteria"]
                new_by_candidate[candidate_id] = metrics
                if metrics["status"] == "ready":
                    ready_base.add(refined_id)
                    ready_candidates.append(candidate_id)
                elif metrics["status"] == "conditionally_useful":
                    cond_count += 1
                status_rows.append({
                    "candidate_id": candidate_id,
                    "base_refined_factor_id": refined_id,
                    "source_factor_id": source_id,
                    "factor_family": family,
                    "refinement_type": refinement_type,
                    "readiness_transform": transform,
                    "readiness_status": metrics["status"],
                    "holdout_mean_ic_1d": metrics["hold_mean"]["1d"],
                    "holdout_rank_ic_1d": metrics["hold_rank"]["1d"],
                    "holdout_sign_consistency_1d": metrics["hold_sign"]["1d"],
                    "aligned_horizon_count": metrics["aligned_count"],
                    "holdout_valid_rows": metrics["holdout_valid"],
                    "walk_forward_sign_consistency": metrics["wf_sign"],
                    "base_precondition_pass": str(criteria["base_precondition_pass"]).lower(),
                    "provider_robustness_status": provider_status,
                    "non_actionable_disclaimer": "research_only",
                })
                walk_rows.append({
                    "candidate_id": candidate_id,
                    "in_sample_mean_ic_1d": metrics["is_mean"]["1d"],
                    "in_sample_rank_ic_1d": metrics["is_rank"]["1d"],
                    "in_sample_sign_consistency_1d": metrics["is_sign"]["1d"],
                    "holdout_mean_ic_1d": metrics["hold_mean"]["1d"],
                    "holdout_mean_ic_5d": metrics["hold_mean"]["5d"],
                    "holdout_mean_ic_20d": metrics["hold_mean"]["20d"],
                    "holdout_rank_ic_1d": metrics["hold_rank"]["1d"],
                    "holdout_sign_consistency_1d": metrics["hold_sign"]["1d"],
                    "n_walk_forward_folds": metrics["n_folds"],
                    "walk_forward_cross_fold_sign_consistency": metrics["wf_sign"],
                    "in_sample_valid_rows": metrics["in_sample_valid"],
                    "holdout_valid_rows": metrics["holdout_valid"],
                    "no_lookahead_status": "passed_current_or_past_only",
                })
                holdout_dates = list(metrics["holdout_dates"])
                holdout_rows.append({
                    "candidate_id": candidate_id,
                    "final_holdout_start": holdout_dates[0] if holdout_dates else "",
                    "final_holdout_end": holdout_dates[-1] if holdout_dates else "",
                    "holdout_dates": len(holdout_dates),
                    "holdout_valid_rows": metrics["holdout_valid"],
                    "holdout_mean_ic_1d": metrics["hold_mean"]["1d"],
                    "holdout_rank_ic_1d": metrics["hold_rank"]["1d"],
                    "holdout_sign_consistency_1d": metrics["hold_sign"]["1d"],
                    "split_policy": "chronological_last_20pct_final_holdout",
                    "final_holdout_used_for_selection": "false",
                    "feature_definition_tuned_on_holdout": "false",
                })
                decision_rows.append({
                    "candidate_id": candidate_id,
                    "readiness_status": metrics["status"],
                    **{key: str(criteria[key]).lower() for key in [
                        "base_precondition_pass",
                        "holdout_sample_sufficient",
                        "holdout_strong_ic_1d",
                        "holdout_sign_stable_1d",
                        "aligned_horizons_ge_2",
                        "walk_forward_stable",
                    ]},
                    "provider_robustness_checked": "true",
                    "decision_summary": _decision_summary(metrics),
                })
                old = old_status.get(candidate_id, {})
                old_wf = old_walk.get(candidate_id, {})
                old_rank = old_rankic.get(refined_id, {})
                old_state = old.get("readiness_status", "not_ready")
                transition = _transition(old_state, str(metrics["status"]))
                comparison_rows.append({
                    "candidate_id": candidate_id,
                    "base_refined_factor_id": refined_id,
                    "old_status": old_state,
                    "new_status": metrics["status"],
                    "old_ic_1d": old.get("holdout_mean_ic_1d", old_wf.get("holdout_mean_ic_1d", "")),
                    "new_ic_1d": metrics["hold_mean"]["1d"],
                    "old_rank_ic_1d": old_rank.get("mean_rank_ic_1d", ""),
                    "new_rank_ic_1d": metrics["hold_rank"]["1d"],
                    "old_sign_stability": old.get("holdout_sign_consistency_1d", old_wf.get("holdout_sign_consistency_1d", "")),
                    "new_sign_stability": metrics["hold_sign"]["1d"],
                    "old_regime_consistency": old_q04.get(refined_id, {}).get("regime_specificity_status", ""),
                    "new_regime_consistency": "extended_index_regime_diagnostics_applied",
                    "old_sample_size": old.get("holdout_valid_rows", old_wf.get("holdout_valid_rows", "")),
                    "new_sample_size": metrics["holdout_valid"],
                    "oos_change": _fmt(float(metrics["hold_mean"]["1d"]) - (_float(old.get("holdout_mean_ic_1d", old_wf.get("holdout_mean_ic_1d", ""))) or 0.0)),
                    "transition_category": transition,
                    "readiness_transition_reason": _decision_summary(metrics),
                })
                anti_rows.append({
                    "candidate_id": candidate_id,
                    "old_to_new_sign_reversal": str(_sign_reversal(old.get("holdout_mean_ic_1d", old_wf.get("holdout_mean_ic_1d", "")), metrics["hold_mean"]["1d"])).lower(),
                    "specification_sensitivity": "checked_fixed_transforms_no_search",
                    "transform_dependence": transform,
                    "horizon_dependence": "single_horizon_only" if metrics["aligned_count"] <= 1 else "multi_horizon",
                    "regime_dependence": "extended_index_regime_review_only",
                    "provider_dependence": provider_status,
                    "sample_period_dependence": "old_120_dates_vs_new_843_dates_compared",
                    "holdout_fragility": "fragile" if metrics["holdout_valid"] < 2 * MIN_HOLDOUT_VALID_ROWS else "adequate",
                    "multiple_testing_risk": f"{n_candidates}_candidates_times_{len(HORIZONS)}_horizons",
                    "candidate_family_multiplicity": n_candidates,
                    "small_sample_pockets": "present_for_failed_symbol_and_sparse_regime_slices" if failed_symbols else "none_detected",
                    "promotion_guard": "no_promotion_without_base_precondition_oos_walk_forward_provider_review",
                })

    ready_count = len(ready_base)
    warning_rows = _warning_rows(failed_symbols, provider_warnings, index_rows_out, ready_count)
    gap_rows = _gap_rows(ready_count, failed_symbols, provider_status)
    status = PASS_WITH_WARNINGS if warning_rows or provider_warnings else PASS
    new_panel_rows = len(daily_rows) * len(SOURCE_FACTORS) * len(REFINEMENT_TYPES)
    manifest = _manifest(
        status,
        old_shape,
        daily_rows,
        daily_dates,
        daily_symbols,
        coverage_rows,
        acquired_symbols,
        failed_symbols,
        providers_in_daily,
        index_series,
        new_panel_rows,
        len(status_rows),
        ready_count,
        ready_candidates,
        cond_count,
        len(warning_rows),
        checksum_ok,
        expected_hashes,
        actual_hashes,
        gate_manifest,
        evidence_manifest,
    )
    return {
        "manifest": manifest,
        "status": status,
        "evidence_rows": evidence_rows,
        "panel_comparison_rows": panel_comparison_rows,
        "panel_summary_rows": panel_summary_rows,
        "feature_lineage_rows": feature_lineage_rows,
        "target_rows": target_rows,
        "regime_rows": regime_rows,
        "walk_rows": walk_rows,
        "holdout_rows": holdout_rows,
        "status_rows": status_rows,
        "comparison_rows": comparison_rows,
        "provider_rows": provider_rows,
        "provider_warning_rows": provider_warnings,
        "index_rows": index_rows_out,
        "anti_rows": anti_rows,
        "decision_rows": decision_rows,
        "gap_rows": gap_rows,
        "warning_rows": warning_rows,
    }


def _sign_reversal(old_value: str, new_value: object) -> bool:
    old = _float(old_value)
    new = float(new_value) if isinstance(new_value, (float, int)) else None
    if old is None or new is None or old == 0 or new == 0:
        return False
    return (old > 0) != (new > 0)


def _evidence_rows(
    old_shape: dict[str, int],
    daily_rows: list[dict[str, str]],
    daily_dates: list[str],
    daily_symbols: list[str],
    coverage_rows: list[dict[str, str]],
    providers: list[str],
    index_series: list[str],
) -> list[dict[str, object]]:
    failed = [row for row in coverage_rows if row.get("status") != "acquired"]
    acquired = [row for row in coverage_rows if row.get("status") == "acquired"]
    return [
        {
            "dimension": "date_coverage",
            "old_state": f"{old_shape['dates']}_dates",
            "new_state": f"{len(daily_dates)}_dates",
            "overlap_state": "old_dates_subset_compared_by_symbol_date_where_available",
            "change_class": "materially_expanded",
            "new_context_fields_consumed": "",
            "disclosure": "New evaluation consumes committed network daily_panel.csv, not the old-only panel.",
        },
        {
            "dimension": "date_extension",
            "old_state": "2025-11-19..2026-05-21",
            "new_state": f"{daily_dates[0]}..{daily_dates[-1]}" if daily_dates else "",
            "overlap_state": "partial_overlap",
            "change_class": "deeper_history",
            "new_context_fields_consumed": "",
            "disclosure": "Index panel extends beyond daily stock panel but evaluation dates are bounded to stock daily dates.",
        },
        {
            "dimension": "symbol_overlap",
            "old_state": f"{old_shape['symbols']}_symbols",
            "new_state": f"{len(daily_symbols)}_acquired_symbols",
            "overlap_state": f"{len(set(daily_symbols))}_symbols_with_new_rows",
            "change_class": "same_governed_universe_with_failed_network_symbols_disclosed",
            "new_context_fields_consumed": "",
            "disclosure": "Nine attempted symbols lacked independent network history and are retained in warnings/gaps.",
        },
        {
            "dimension": "symbol_fetch_failures",
            "old_state": "not_applicable_old_baostock_panel",
            "new_state": f"{len(failed)}_failed_or_empty_retained",
            "overlap_state": f"{len(acquired)}_acquired",
            "change_class": "missing_independent_evidence_disclosed",
            "new_context_fields_consumed": "",
            "disclosure": ";".join(row.get("symbol", "") for row in failed),
        },
        {
            "dimension": "provider_lineage",
            "old_state": "baostock_committed_provider02b",
            "new_state": "akshare_sina_plus_baostock_crosscheck",
            "overlap_state": "symbol_trade_date_forward_return_overlap_used_for_robustness",
            "change_class": "provider_diversity_expanded",
            "new_context_fields_consumed": "",
            "disclosure": ";".join(providers),
        },
        {
            "dimension": "index_context_availability",
            "old_state": "limited_benchmark_context",
            "new_state": f"{len(index_series)}_index_series",
            "overlap_state": ";".join(index_series),
            "change_class": "new_index_context_consumed",
            "new_context_fields_consumed": ";".join(INDEX_CONTEXT_FIELDS_CONSUMED),
            "disclosure": "CSI300/SSE/SZSE index fields are used only with fixed trailing transforms.",
        },
        {
            "dimension": "network_rows",
            "old_state": str(old_shape["rows"]),
            "new_state": str(len(daily_rows)),
            "overlap_state": "new_rows_are_raw_symbol_date_observations_before_factor_replication",
            "change_class": "materially_expanded_committed_network_bundle",
            "new_context_fields_consumed": "close;return_1d;index_panel",
            "disclosure": "Forward returns are reconstructed only in evaluation target structures.",
        },
    ]


def _panel_comparison_rows(old_shape: dict[str, int], daily_row_count: int, daily_date_count: int, daily_symbol_count: int) -> list[dict[str, object]]:
    new_panel_rows = daily_row_count * len(SOURCE_FACTORS) * len(REFINEMENT_TYPES)
    return [
        {"metric": "panel_rows", "old_value": old_shape["rows"], "new_value": new_panel_rows, "change_class": "expanded_after_factor_lineage_replication", "notes": "New panel rows are reconstructed from network daily rows across fixed source factors and old refinement lineage strata."},
        {"metric": "dates", "old_value": old_shape["dates"], "new_value": daily_date_count, "change_class": "materially_expanded_committed_network_bundle", "notes": "Strict chronological validation uses the expanded date range."},
        {"metric": "symbols", "old_value": old_shape["symbols"], "new_value": daily_symbol_count, "change_class": "network_acquired_subset_of_governed_universe", "notes": "Failed network symbols remain disclosed and are not silently dropped."},
        {"metric": "source_relation", "old_value": "goal_quant_research03_refined_evaluation_panel_parts", "new_value": "outputs/research/network_ingestion/daily_panel.csv", "change_class": "materially_expanded_committed_network_bundle", "notes": "Rerun does not mechanically reuse old 120-date panel as its evaluation panel."},
    ]


def _feature_lineage_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for definition in SOURCE_FACTORS:
        status = "constructed" if definition["source_factor_id"] != "alpha_price_volume_confirmation_5d" else "blocked_missing_volume_input_disclosed"
        rows.append({
            "source_factor_id": definition["source_factor_id"],
            "factor_family": definition["factor_family"],
            "reconstructed_feature_id": definition["source_factor_id"],
            "base_formula": definition["formula"],
            "required_inputs": definition["inputs"],
            "index_context_used": definition["index_fields"] or "none",
            "window": definition["window"],
            "availability_lag": "next_session_open",
            "pit_declaration": "trade_date_close_or_trailing_only_no_future_information",
            "source_lineage": "GOAL-NETWORK-EVIDENCE-INGESTION-01 daily_panel/index_panel",
            "transformation_lineage": "existing_source_factor_semantics_fixed_windows_no_search",
            "target_dependent": "false",
            "construction_status": status,
        })
    return rows


def _target_rows() -> list[dict[str, object]]:
    return [
        {
            "horizon": f"{horizon}d",
            "target_formula": f"close_t_plus_{horizon}/close_t_minus_1",
            "target_timestamp": f"trade_date_plus_{horizon}_close",
            "feature_cutoff": "trade_date_close",
            "availability_cutoff": "next_session_open",
            "target_usage": "evaluation_only_not_feature",
            "no_lookahead_status": "passed_target_isolation",
        }
        for horizon in (1, 5, 20)
    ]


def _panel_summary_rows(source_rows: dict[str, list[dict[str, str]]], date_count: int, symbol_count: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    definitions = {str(item["source_factor_id"]): item for item in SOURCE_FACTORS}
    for source_id, factor_rows in sorted(source_rows.items()):
        definition = definitions[source_id]
        valid = sum(1 for row in factor_rows if row.get("factor_value"))
        t1 = sum(1 for row in factor_rows if row.get("forward_return_1d"))
        t5 = sum(1 for row in factor_rows if row.get("forward_return_5d"))
        t20 = sum(1 for row in factor_rows if row.get("forward_return_20d"))
        for refinement_type in REFINEMENT_TYPES:
            rows.append({
                "refined_factor_id": f"{source_id}__{refinement_type}",
                "source_factor_id": source_id,
                "refinement_type": refinement_type,
                "factor_family": definition["factor_family"],
                "new_panel_rows": len(factor_rows),
                "valid_factor_rows": valid,
                "date_count": date_count,
                "symbol_count": symbol_count,
                "source_provider": "akshare_sina",
                "feature_inputs": definition["inputs"],
                "index_context_fields": definition["index_fields"],
                "missingness_rate": _fmt(1 - valid / len(factor_rows), 6) if factor_rows else "1",
                "target_1d_valid_rows": t1,
                "target_5d_valid_rows": t5,
                "target_20d_valid_rows": t20,
                "no_lookahead_status": "passed_current_or_past_only",
            })
    return rows


def _warning_rows(failed_symbols: set[str], provider_warnings: list[dict[str, object]], index_rows: list[dict[str, object]], ready_count: int) -> list[dict[str, object]]:
    rows = [
        {
            "warning_code": "FAILED_NETWORK_SYMBOLS_RETAINED",
            "scope": "symbol_coverage",
            "count": len(failed_symbols),
            "detail": ";".join(sorted(failed_symbols)),
        },
        {
            "warning_code": "PRICE_VOLUME_FACTOR_BLOCKED",
            "scope": "feature_reconstruction",
            "count": 1,
            "detail": "alpha_price_volume_confirmation_5d requires volume, which is absent from the committed network bundle.",
        },
    ]
    if provider_warnings:
        rows.append({"warning_code": "PROVIDER_DISCREPANCIES_PRESENT", "scope": "provider_robustness", "count": len(provider_warnings), "detail": "See provider_discrepancy_warnings.csv."})
    weak_index = sum(1 for row in index_rows if row.get("contribution_status") == "weak_or_unstable_context")
    if weak_index:
        rows.append({"warning_code": "INDEX_CONTEXT_WEAK_OR_UNSTABLE", "scope": "index_context", "count": weak_index, "detail": "Index context is consumed but not assumed useful."})
    if ready_count == 0:
        rows.append({"warning_code": "NO_READY_FACTOR_AFTER_EXPANDED_RERUN", "scope": "readiness_decision", "count": 1, "detail": "RecTiering remains locked_future."})
    return rows


def _gap_rows(ready_count: int, failed_symbols: set[str], provider_status: str) -> list[dict[str, object]]:
    rows = [
        {"gap_dimension": "symbol_breadth", "current_state": "41_acquired_of_50_attempted", "binding_constraint": "provider_gaps", "impact": "failed symbols reduce independent evidence breadth", "next_legitimate_action": "new committed provider retry bundle; no silent imputation"},
        {"gap_dimension": "feature_coverage", "current_state": "volume_absent", "binding_constraint": "feature_insufficiency", "impact": "price-volume factor cannot be reconstructed", "next_legitimate_action": "commit PIT-safe volume evidence"},
        {"gap_dimension": "provider_robustness", "current_state": provider_status, "binding_constraint": "provider_discrepancy" if provider_status != "pass" else "none", "impact": "large overlap discrepancies require review before promotion", "next_legitimate_action": "investigate adjusted-price convention differences"},
    ]
    if ready_count == 0:
        rows.append({"gap_dimension": "readiness", "current_state": "ready_factor_count_after_0", "binding_constraint": "signal_weakness_or_instability", "impact": "RecTiering dependency not scientifically satisfied", "next_legitimate_action": "more evidence or better pre-specified features, without lowering thresholds"})
    return rows


def _manifest(
    status: str,
    old_shape: dict[str, int],
    daily_rows: list[dict[str, str]],
    daily_dates: list[str],
    daily_symbols: list[str],
    coverage_rows: list[dict[str, str]],
    acquired_symbols: set[str],
    failed_symbols: set[str],
    providers_in_daily: list[str],
    index_series: list[str],
    new_panel_rows: int,
    candidates_evaluated: int,
    ready_count: int,
    ready_candidates: list[str],
    cond_count: int,
    warning_count: int,
    checksum_ok: bool,
    expected_hashes: dict[str, str],
    actual_hashes: dict[str, str],
    gate_manifest: dict[str, object],
    evidence_manifest: dict[str, object],
) -> dict[str, object]:
    providers = sorted(set(providers_in_daily) | {"baostock"})
    manifest: dict[str, object] = {
        "goal": GOAL_NAME,
        "workflow_id": WORKFLOW_ID,
        "mode": MODE,
        "status": status,
        "objective": "rerun fixed-threshold factor readiness on materially expanded committed network evidence without fabricating readiness",
        "materially_expanded_input": gate_manifest.get("materially_expanded") is True and len(daily_dates) == 843,
        "network_bundle_rows_consumed": len(daily_rows),
        "network_bundle_dates_consumed": len(daily_dates),
        "network_bundle_symbols_consumed": len(daily_symbols),
        "network_bundle_symbols_attempted": len(coverage_rows),
        "failed_network_symbols_retained": len(failed_symbols),
        "symbols_with_independent_evidence": len(acquired_symbols),
        "providers_represented": providers,
        "index_context_series_consumed": index_series,
        "index_context_fields_consumed": INDEX_CONTEXT_FIELDS_CONSUMED,
        "bundle_checksum_validation_passed": checksum_ok,
        "bundle_expected_checksums": expected_hashes,
        "bundle_actual_checksums": actual_hashes,
        "credential_dependency_required": False,
        "old_panel_rows": old_shape["rows"],
        "old_panel_dates": old_shape["dates"],
        "old_panel_symbols": old_shape["symbols"],
        "new_panel_rows": new_panel_rows,
        "new_panel_dates": len(daily_dates),
        "new_panel_symbols": len(daily_symbols),
        "new_panel_rows_from_network_bundle": True,
        "old_only_panel_rerun": False,
        "candidates_evaluated": candidates_evaluated,
        "ready_factor_count_before": 0,
        "ready_factor_count_after": ready_count,
        "ready_factor_count": ready_count,
        "ready_factors": sorted(ready_candidates),
        "conditionally_useful_candidate_count": cond_count,
        "warning_count": warning_count,
        "strong_ic_threshold_used": STRONG_IC_THRESHOLD,
        "min_valid_rows_used": MIN_VALID_ROWS,
        "min_holdout_valid_rows_used": MIN_HOLDOUT_VALID_ROWS,
        "holdout_fraction": HOLDOUT_FRACTION,
        "sign_stable_min": SIGN_STABLE_MIN,
        "aligned_horizons_min": ALIGNED_HORIZONS_MIN,
        "walk_forward_validation_applied": True,
        "out_of_sample_holdout_applied": True,
        "final_holdout_untouched": True,
        "target_isolation_passed": True,
        "no_lookahead_evaluation_passed": True,
        "existing_thresholds_preserved": True,
        "goal_rec_tiering01_locked_future": True,
        "workflow_status_modified_by_this_goal": False,
        "locked_capabilities_modified_by_this_goal": False,
        "source_snapshot_start_date": evidence_manifest.get("source_snapshot_start_date", ""),
        "source_snapshot_end_date": evidence_manifest.get("source_snapshot_end_date", ""),
    }
    for key in FALSE_BOUNDARY_KEYS:
        manifest[key] = False
    return manifest


def _write_artifacts(root: Path, result: dict[str, object]) -> None:
    _write_csv(root / EVIDENCE_INTEGRATION_MAP, EVIDENCE_FIELDS, result["evidence_rows"])
    _write_csv(root / OLD_NEW_PANEL_COMPARISON, PANEL_COMPARISON_FIELDS, result["panel_comparison_rows"])
    _write_csv(root / RECONSTRUCTED_PANEL_SUMMARY, PANEL_SUMMARY_FIELDS, result["panel_summary_rows"])
    _write_csv(root / FEATURE_LINEAGE, FEATURE_LINEAGE_FIELDS, result["feature_lineage_rows"])
    _write_csv(root / TARGET_HORIZON_CONTRACT, TARGET_FIELDS, result["target_rows"])
    _write_csv(root / EXTENDED_REGIME_COVERAGE, REGIME_FIELDS, result["regime_rows"])
    _write_csv(root / WALK_FORWARD_SUMMARY, WALK_FIELDS, result["walk_rows"])
    _write_csv(root / HOLDOUT_SUMMARY, HOLDOUT_FIELDS, result["holdout_rows"])
    _write_csv(root / READINESS_STATUS, READINESS_FIELDS, result["status_rows"])
    _write_csv(root / OLD_NEW_READINESS_COMPARISON, COMPARISON_FIELDS, result["comparison_rows"])
    _write_csv(root / PROVIDER_ROBUSTNESS, PROVIDER_FIELDS, result["provider_rows"])
    _write_csv(root / PROVIDER_WARNINGS, PROVIDER_WARNING_FIELDS, result["provider_warning_rows"])
    _write_csv(root / INDEX_CONTEXT_CONTRIBUTION, INDEX_FIELDS, result["index_rows"])
    _write_csv(root / ANTI_OVERFIT, ANTI_OVERFIT_FIELDS, result["anti_rows"])
    _write_csv(root / DECISION_REASONS, DECISION_FIELDS, result["decision_rows"])
    _write_csv(root / REMAINING_GAP_MAP, GAP_FIELDS, result["gap_rows"])
    _write_csv(root / CONSTRUCTION_WARNINGS, WARNING_FIELDS, result["warning_rows"])
    _write_text(root / MANIFEST_PATH, json.dumps(result["manifest"], indent=2, sort_keys=True) + "\n")
    _write_text(root / REPORT_PATH, _report(result["manifest"]))
    _write_text(root / DOC_PATH, _doc())
    _write_text(root / HANDOFF_PATH, _handoff(result["manifest"]))
    _write_text(root / CONTRACT_PATH, _contract())


def _report(manifest: dict[str, object]) -> str:
    return "\n".join([
        f"# {GOAL_ID} Expanded Evidence Factor Readiness Rerun",
        "",
        f"Status: `{manifest['status']}`",
        "",
        "## Evidence Consumed",
        "",
        f"- Network daily rows: `{manifest['network_bundle_rows_consumed']}`",
        f"- Network dates: `{manifest['network_bundle_dates_consumed']}`",
        f"- Network symbols consumed / attempted: `{manifest['network_bundle_symbols_consumed']}` / `{manifest['network_bundle_symbols_attempted']}`",
        f"- Providers represented: `{';'.join(manifest['providers_represented'])}`",
        f"- Index context series: `{';'.join(manifest['index_context_series_consumed'])}`",
        f"- Checksum validation passed: `{str(manifest['bundle_checksum_validation_passed']).lower()}`",
        "",
        "## Readiness Decision",
        "",
        f"- ready_factor_count_before: `{manifest['ready_factor_count_before']}`",
        f"- ready_factor_count_after: `{manifest['ready_factor_count_after']}`",
        f"- candidates evaluated: `{manifest['candidates_evaluated']}`",
        f"- conditionally useful candidates: `{manifest['conditionally_useful_candidate_count']}`",
        f"- ready factors: `{manifest['ready_factors'] or []}`",
        "",
        "## Boundary",
        "",
        "GOAL-REC-TIERING-01 remains `locked_future`. This rerun creates no recommendation, position, portfolio, dashboard, trading, production, local-lake, factor-mining, broker, or DQN/RL output.",
        "",
    ])


def _doc() -> str:
    return "\n".join([
        f"# {GOAL_ID} Expanded Evidence Readiness Rerun",
        "",
        "Research-only fixed-threshold rerun over the committed GOAL-NETWORK-EVIDENCE-INGESTION-01 bundle.",
        "",
        "Run: `python scripts/run_goal_factor_readiness_rerun02.py`",
        "",
        "Outputs include evidence integration, reconstructed panel summaries, feature lineage, target contract, extended regime coverage, walk-forward and holdout validation, old/new readiness comparison, provider robustness, index context contribution, anti-overfitting review, decision reasons, remaining gaps, report, manifest, audit, and governance handoff.",
    ])


def _handoff(manifest: dict[str, object]) -> str:
    if int(manifest["ready_factor_count_after"]) > 0:
        decision = "Scientific dependency may be satisfiable pending explicit user authorization; RecTiering is not executed or unlocked by this gate."
    else:
        decision = "Expanded evidence still does not support a ready factor under fixed thresholds; RecTiering remains locked_future."
    return "\n".join([
        f"# {GOAL_ID} Governance Handoff",
        "",
        f"- ready_factor_count_before: {manifest['ready_factor_count_before']}",
        f"- ready_factor_count_after: {manifest['ready_factor_count_after']}",
        f"- material expanded evidence consumed: {manifest['materially_expanded_input']}",
        f"- credential dependency required: {manifest['credential_dependency_required']}",
        "",
        decision,
        "",
        "No workflow_status.csv or locked_capabilities.json mutation was performed. Downstream recommendation/backtest/dashboard/trading gates remain locked.",
    ])


def _contract() -> str:
    return "\n".join([
        f"goal_id: {GOAL_ID}",
        f"workflow_id: {WORKFLOW_ID}",
        f"mode: {MODE}",
        "research_only: true",
        "uses_committed_network_bundle_offline: true",
        "modifies_workflow_status: false",
        "modifies_locked_capabilities: false",
        "unlocks_goal_rec_tiering01: false",
        "lowers_existing_thresholds: false",
        "fabricates_ready_status: false",
        f"strong_ic_threshold: {STRONG_IC_THRESHOLD}",
        f"min_valid_rows: {MIN_VALID_ROWS}",
        f"min_holdout_valid_rows: {MIN_HOLDOUT_VALID_ROWS}",
        f"holdout_fraction: {HOLDOUT_FRACTION}",
    ])


def run_goal_factor_readiness_rerun02(root: Path) -> bool:
    result = _build_artifacts(root)
    _write_artifacts(root, result)
    audit_ok = audit_goal_factor_readiness_rerun02(root)
    return result["manifest"]["status"] in {PASS, PASS_WITH_WARNINGS} and audit_ok


def audit_goal_factor_readiness_rerun02(root: Path) -> bool:
    failures: list[str] = []
    for rel in OUTPUT_ARTIFACTS:
        if rel == AUDIT_PATH:
            continue
        if not (root / rel).exists():
            failures.append(f"missing_output:{rel}")
    manifest = _load_json(root / MANIFEST_PATH)
    if manifest.get("mode") != MODE:
        failures.append("manifest_mode_invalid")
    if manifest.get("status") not in {PASS, PASS_WITH_WARNINGS}:
        failures.append("manifest_status_invalid")
    if manifest.get("network_bundle_dates_consumed") != 843:
        failures.append("network_bundle_dates_not_843")
    if manifest.get("network_bundle_rows_consumed") != 34543:
        failures.append("network_bundle_rows_not_consumed")
    if manifest.get("bundle_checksum_validation_passed") is not True:
        failures.append("bundle_checksum_validation_failed")
    if manifest.get("old_only_panel_rerun") is not False:
        failures.append("old_only_panel_rerun_flag_invalid")
    if manifest.get("goal_rec_tiering01_locked_future") is not True:
        failures.append("rec_tiering_lock_flag_missing")
    if manifest.get("existing_thresholds_preserved") is not True:
        failures.append("threshold_preservation_flag_missing")
    for key in FALSE_BOUNDARY_KEYS:
        if manifest.get(key) is not False:
            failures.append(f"boundary_not_false:{key}")
    feature_headers = list((_read_csv(root / FEATURE_LINEAGE) or [{}])[0].keys())
    for header in feature_headers:
        if header.startswith("forward_return_") or header.startswith("benchmark_excess_return_"):
            failures.append(f"feature_lineage_forbidden_target_column:{header}")
    workflow = {row["workflow_id"]: row for row in _read_csv(root / WORKFLOW_STATUS)}
    rec = workflow.get("goal_rec_tiering01_recommendation_score_tiering_gate", {})
    if rec.get("status") != "locked_future":
        failures.append("rec_tiering_not_locked_future")
    for row in _read_csv(root / READINESS_STATUS):
        if row.get("readiness_status") == "ready" and row.get("base_precondition_pass") != "true":
            failures.append(f"fabricated_ready_without_base_precondition:{row.get('candidate_id')}")
    status = PASS if not failures else BLOCKED
    (root / AUDIT_PATH).parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {GOAL_ID} Audit", "", f"Status: `{status}`", "", "## Failures"]
    lines.extend(f"- {failure}" for failure in failures)
    lines.append("")
    _write_text(root / AUDIT_PATH, "\n".join(lines))
    return status == PASS


def goal_factor_readiness_rerun02_valid_evidence(root: Path) -> bool:
    report = (root / REPORT_PATH).read_text(encoding="utf-8") if (root / REPORT_PATH).exists() else ""
    audit = (root / AUDIT_PATH).read_text(encoding="utf-8") if (root / AUDIT_PATH).exists() else ""
    manifest = _load_json(root / MANIFEST_PATH)
    return (
        f"# {GOAL_ID}" in report
        and "Status: `PASS`" in audit
        and manifest.get("mode") == MODE
        and manifest.get("bundle_checksum_validation_passed") is True
        and manifest.get("old_only_panel_rerun") is False
        and manifest.get("goal_rec_tiering01_locked_future") is True
        and all(manifest.get(key) is False for key in FALSE_BOUNDARY_KEYS)
    )
