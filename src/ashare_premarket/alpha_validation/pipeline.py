from __future__ import annotations

import hashlib
import math
from collections import Counter
from statistics import median
from typing import Mapping, Sequence

from ashare_premarket.alpha_validation.data import HistoricalBundle
from ashare_premarket.alpha_validation.decisions import decide_candidate
from ashare_premarket.alpha_validation.folds import build_purged_chronological_splits
from ashare_premarket.alpha_validation.labels import build_forward_labels
from ashare_premarket.alpha_validation.models import run_purged_fixed_linear_baseline
from ashare_premarket.alpha_validation.nulls import run_null_controls
from ashare_premarket.alpha_validation.research import evaluate_single_factor
from ashare_premarket.alpha_validation.robustness import build_predeclared_slices
from ashare_premarket.alpha_validation.statistics import (
    benjamini_hochberg,
    date_bootstrap_interval,
    date_sign_flip_pvalue,
)
from ashare_premarket.quant_foundation.alpha import build_interpretable_alpha
from ashare_premarket.quant_foundation.contracts import (
    canonical_checksum,
    validate_research_output_fields,
)
from ashare_premarket.quant_foundation.features import FEATURE_COLUMNS, build_feature_rows


def run_validation_from_bundle(
    bundle: HistoricalBundle,
    goal11_config: Mapping[str, object],
    goal12_config: Mapping[str, object],
) -> dict[str, object]:
    _validate_governance(goal12_config)
    features = build_feature_rows(bundle.snapshot, goal11_config)
    labels = build_forward_labels(
        bundle.snapshot,
        bundle.trading_calendar,
        dict(goal12_config["labels"]),
    )
    maximum_horizon = int(dict(goal12_config["splits"])["maximum_label_horizon"])
    eligible_dates = tuple(bundle.trading_calendar[:-maximum_horizon])
    splits = build_purged_chronological_splits(
        eligible_dates,
        dict(goal12_config["splits"]),
        label_horizon=maximum_horizon,
    )
    final_dates = set(map(str, dict(splits["final_holdout"])["dates"]))
    discovery_dates = set(eligible_dates) - final_dates
    metrics_config = dict(goal12_config["metrics"])
    inference_config = dict(goal12_config["inference"])
    candidates = dict(goal12_config["candidate_contract"])
    directions = {str(key): int(value) for key, value in dict(candidates["feature_directions"]).items()}
    contexts = set(map(str, candidates["regime_context_features"]))
    horizons = tuple(map(int, dict(goal12_config["labels"])["horizons"]))
    structurally_missing_features = {
        feature_name
        for feature_name in directions
        if all(row.get(feature_name) is None for row in features)
    }

    labels_by_horizon = {
        horizon: [row for row in labels if int(row["horizon_trading_days"]) == horizon]
        for horizon in horizons
    }
    factor_results: list[dict[str, object]] = []
    null_controls: list[dict[str, object]] = []
    hypothesis_p_values: dict[str, float] = {}
    for feature_name in FEATURE_COLUMNS:
        for horizon in horizons:
            key = f"feature:{feature_name}:{horizon}d"
            if feature_name in contexts:
                factor_results.append(
                    _ineligible_metric_record(
                        feature_name,
                        horizon,
                        key,
                        "DATE_LEVEL_CONTEXT_NOT_CROSS_SECTIONAL_FACTOR",
                    )
                )
                continue
            if feature_name in structurally_missing_features:
                factor_results.append(
                    _ineligible_metric_record(
                        feature_name,
                        horizon,
                        key,
                        f"STRUCTURALLY_MISSING_FEATURE:{feature_name.upper()}",
                        candidate_type="STRUCTURALLY_MISSING_FEATURE",
                    )
                )
                continue
            record, controls = _factor_horizon_evidence(
                features,
                labels_by_horizon[horizon],
                feature_name,
                directions[feature_name],
                horizon,
                key,
                discovery_dates,
                final_dates,
                splits,
                metrics_config,
                inference_config,
            )
            factor_results.append(record)
            null_controls.extend(controls)
            if record["discovery_null_p"] is not None:
                hypothesis_p_values[key] = float(record["discovery_null_p"])

    alpha_rows = build_interpretable_alpha(features, goal11_config)
    structural_alpha_features = sorted(
        feature_name
        for feature_name in map(str, dict(goal11_config["alpha"])["required_features"])
        if feature_name in structurally_missing_features
    )
    alpha_eligibility_reason = ";".join(
        f"STRUCTURALLY_MISSING_ALPHA_FEATURE:{feature_name.upper()}"
        for feature_name in structural_alpha_features
    ) or None
    combined_results: list[dict[str, object]] = []
    for candidate_id, score_field in (
        ("interpretable_alpha", "alpha_score"),
        ("risk_adjusted_alpha", "risk_adjusted_score"),
    ):
        score_features = _score_feature_rows(alpha_rows, score_field)
        for horizon in horizons:
            key = f"combined:{candidate_id}:{horizon}d"
            record, controls = _factor_horizon_evidence(
                score_features,
                labels_by_horizon[horizon],
                score_field,
                1,
                horizon,
                key,
                discovery_dates,
                final_dates,
                splits,
                metrics_config,
                inference_config,
            )
            record["candidate_id"] = candidate_id
            record["candidate_type"] = "PRE_SPECIFIED_INTERPRETABLE_SCORE"
            if alpha_eligibility_reason is not None:
                record["eligibility_reason"] = alpha_eligibility_reason
            combined_results.append(record)
            null_controls.extend(controls)
            if record["discovery_null_p"] is not None:
                hypothesis_p_values[key] = float(record["discovery_null_p"])

    linear_config = dict(goal11_config["linear_ranker"])
    for horizon in horizons:
        model = run_purged_fixed_linear_baseline(
            features,
            labels_by_horizon[horizon],
            splits,
            linear_config,
            metrics_config,
        )
        key = f"combined:fixed_linear_ranker:{horizon}d"
        record: dict[str, object] = {
            "candidate_id": "fixed_linear_ranker",
            "candidate_type": "FIXED_PURGED_LINEAR_RANKER",
            "candidate_key": key,
            "horizon_trading_days": horizon,
            "model_result": model,
            "full": None,
            "discovery": None,
            "final_holdout": None,
            "fold_test_metrics": [fold["test"] for fold in model.get("fold_metrics", [])],
            "confidence_interval": None,
            "discovery_null_p": None,
            "final_holdout_null_p": None,
            "fdr_q": None,
            "eligibility_reason": (
                None if model["status"] == "COMPLETE_RESEARCH_ONLY" else ";".join(model["insufficiency_reasons"])
            ),
        }
        if model["status"] == "COMPLETE_RESEARCH_ONLY":
            model_features = _model_score_feature_rows(model["scores"])
            metric_record, controls = _factor_horizon_evidence(
                model_features,
                labels_by_horizon[horizon],
                "model_score",
                1,
                horizon,
                key,
                discovery_dates,
                final_dates,
                splits,
                metrics_config,
                inference_config,
            )
            for field in (
                "full",
                "discovery",
                "final_holdout",
                "fold_test_metrics",
                "confidence_interval",
                "discovery_null_p",
                "final_holdout_null_p",
            ):
                record[field] = metric_record[field]
            null_controls.extend(controls)
            if record["discovery_null_p"] is not None:
                hypothesis_p_values[key] = float(record["discovery_null_p"])
        record["checksum"] = canonical_checksum(
            {field: value for field, value in record.items() if field != "checksum"}
        )
        combined_results.append(record)

    adjusted = benjamini_hochberg(hypothesis_p_values)
    _attach_fdr(factor_results, adjusted)
    _attach_fdr(combined_results, adjusted)
    fdr_results: dict[str, object] = {
        "method": "BENJAMINI_HOCHBERG",
        "family": "ALL_ELIGIBLE_FEATURE_AND_COMBINED_DISCOVERY_HYPOTHESES_ACROSS_HORIZONS",
        "hypothesis_count": len(adjusted),
        "adjusted_q_values": adjusted,
    }
    fdr_results["checksum"] = canonical_checksum(fdr_results)

    slice_contract = build_predeclared_slices(
        features,
        eligible_dates,
        splits,
        dict(goal12_config["robustness"]),
    )
    primary_horizon = int(dict(goal12_config["labels"])["primary_horizon"])
    robustness_results: list[dict[str, object]] = []
    for feature_name in directions:
        primary = next(
            row
            for row in factor_results
            if row["candidate_id"] == feature_name
            and int(row["horizon_trading_days"]) == primary_horizon
        )
        robustness_results.append(
            _evaluate_robustness(
                features,
                labels_by_horizon[primary_horizon],
                feature_name,
                directions[feature_name],
                slice_contract,
                primary,
                discovery_dates,
                final_dates,
                metrics_config,
                dict(goal12_config["decision_policy"]),
            )
        )
    robustness: dict[str, object] = {
        "slice_contract": slice_contract,
        "factor_results": robustness_results,
    }
    robustness["checksum"] = canonical_checksum(robustness)

    decisions: list[dict[str, object]] = []
    policy = dict(goal12_config["decision_policy"])
    robustness_by_feature = {
        str(row["candidate_id"]): row for row in robustness_results
    }
    decision_provenance = {
        "calendar_version": str(dict(goal12_config["labels"])["calendar_contract"]),
        "code_commit": bundle.snapshot.code_commit,
        "source_data_checksum": bundle.snapshot.source_checksum,
        "source_snapshot_id": bundle.snapshot.snapshot_id,
    }
    for feature_name in FEATURE_COLUMNS:
        rows = [row for row in factor_results if row["candidate_id"] == feature_name]
        decision = _decide_from_records(
                feature_name,
                rows,
                primary_horizon,
                policy,
                robustness_by_feature.get(feature_name),
            )
        decisions.append(
            _governed_decision_summary(
                decision,
                feature_or_model_version=str(goal11_config["feature_version"]),
                horizon=primary_horizon,
                records=rows,
                provenance=decision_provenance,
            )
        )
    combined_versions = {
        "interpretable_alpha": str(dict(goal11_config["alpha"])["version"]),
        "risk_adjusted_alpha": (
            f"{dict(goal11_config['alpha'])['version']}+"
            f"{dict(goal11_config['risk'])['version']}"
        ),
        "fixed_linear_ranker": str(dict(goal11_config["linear_ranker"])["version"]),
    }
    for candidate_id in candidates["combined_candidates"]:
        rows = [row for row in combined_results if row["candidate_id"] == candidate_id]
        decision = _decide_from_records(
                str(candidate_id), rows, primary_horizon, policy, None
            )
        decisions.append(
            _governed_decision_summary(
                decision,
                feature_or_model_version=combined_versions[str(candidate_id)],
                horizon=primary_horizon,
                records=rows,
                provenance=decision_provenance,
            )
        )
    decisions = sorted(decisions, key=lambda row: str(row["candidate_id"]))

    data_audit = _data_audit(bundle, features, labels, eligible_dates, horizons)
    result: dict[str, object] = {
        "goal_id": "GOAL-12",
        "code_commit": bundle.snapshot.code_commit,
        "status": "COMPLETE_RESEARCH_ONLY",
        "research_only": True,
        "production_ready": False,
        "ready_factor_count": 0,
        "production_model_promoted": False,
        "data_audit": data_audit,
        "feature_rows": features,
        "label_rows": labels,
        "alpha_rows": alpha_rows,
        "splits": splits,
        "single_factor_results": factor_results,
        "null_controls": null_controls,
        "fdr_results": fdr_results,
        "combined_models": combined_results,
        "robustness": robustness,
        "decisions": decisions,
    }
    validate_research_output_fields(result)
    result["checksum"] = canonical_checksum(result)
    return result


def _factor_horizon_evidence(
    features: Sequence[Mapping[str, object]],
    labels: Sequence[Mapping[str, object]],
    feature_name: str,
    direction: int,
    horizon: int,
    candidate_key: str,
    discovery_dates: set[str],
    final_dates: set[str],
    splits: Mapping[str, object],
    metrics: Mapping[str, object],
    inference: Mapping[str, object],
) -> tuple[dict[str, object], list[dict[str, object]]]:
    arguments = {
        "feature_name": feature_name,
        "direction": direction,
        "minimum_cross_section": int(metrics["minimum_cross_section"]),
        "quantile_count": int(metrics["quantile_count"]),
        "top_k": int(metrics["top_k"]),
        "validate_checksums": False,
    }
    analysis_dates = discovery_dates | final_dates
    full_raw = evaluate_single_factor(
        features, labels, allowed_dates=analysis_dates, **arguments
    )
    discovery_raw = evaluate_single_factor(
        features, labels, allowed_dates=discovery_dates, **arguments
    )
    final_raw = evaluate_single_factor(
        features, labels, allowed_dates=final_dates, **arguments
    )
    winsorized = evaluate_single_factor(
        features,
        labels,
        allowed_dates=discovery_dates,
        preprocessing="winsorized_1pct",
        **arguments,
    )
    controls: list[dict[str, object]] = []
    discovery_null_p = None
    if discovery_raw["by_date"]:
        control = run_null_controls(candidate_key, discovery_raw["by_date"], inference)
        control["scope"] = "DISCOVERY_ONLY"
        control["checksum"] = canonical_checksum(
            {key: value for key, value in control.items() if key != "checksum"}
        )
        controls.append(control)
        discovery_null_p = control["conservative_null_p"]
    holdout_interval = None
    holdout_p = None
    if final_raw["by_date"]:
        rank_values = [
            float(row["rank_ic"])
            for row in final_raw["by_date"]
            if row["rank_ic"] is not None
        ]
        seed = _seed(int(inference["base_seed"]), f"{candidate_key}:final")
        holdout_interval = date_bootstrap_interval(
            rank_values,
            repetitions=int(inference["date_bootstrap_repetitions"]),
            confidence=float(inference["bootstrap_confidence"]),
            seed=seed,
        )
        holdout_p = date_sign_flip_pvalue(
            rank_values,
            repetitions=int(inference["sign_flip_repetitions"]),
            seed=_seed(seed, "sign"),
        )
    fold_metrics = []
    for fold in splits["folds"]:
        fold_metric = evaluate_single_factor(
            features,
            labels,
            allowed_dates=set(map(str, fold["test_dates"])),
            **arguments,
        )
        fold_metrics.append(_compact_metric(fold_metric))
    record: dict[str, object] = {
        "candidate_id": feature_name,
        "candidate_type": "SINGLE_FACTOR",
        "candidate_key": candidate_key,
        "horizon_trading_days": horizon,
        "eligibility_reason": None,
        "full": _compact_metric(full_raw),
        "discovery": _compact_metric(discovery_raw),
        "final_holdout": _compact_metric(final_raw),
        "fold_test_metrics": fold_metrics,
        "confidence_interval": holdout_interval,
        "discovery_null_p": discovery_null_p,
        "final_holdout_null_p": holdout_p,
        "fdr_q": None,
        "outlier_sensitivity_rank_ic_delta": _difference(
            discovery_raw.get("rank_ic_mean"), winsorized.get("rank_ic_mean")
        ),
        "winsorized_discovery": _compact_metric(winsorized),
    }
    record["checksum"] = canonical_checksum(record)
    return record, controls


def _evaluate_robustness(
    features: Sequence[Mapping[str, object]],
    labels: Sequence[Mapping[str, object]],
    feature_name: str,
    direction: int,
    slices: Mapping[str, object],
    primary: Mapping[str, object],
    discovery_dates: set[str],
    final_dates: set[str],
    metrics: Mapping[str, object],
    policy: Mapping[str, object],
) -> dict[str, object]:
    arguments = {
        "feature_name": feature_name,
        "direction": direction,
        "minimum_cross_section": int(metrics["minimum_cross_section"]),
        "quantile_count": int(metrics["quantile_count"]),
        "top_k": int(metrics["top_k"]),
        "validate_checksums": False,
    }
    evaluated: list[dict[str, object]] = []
    for slice_row in slices["date_slices"]:
        metric = evaluate_single_factor(
            features,
            labels,
            allowed_dates=set(map(str, slice_row["dates"])),
            **arguments,
        )
        evaluated.append(
            {
                "slice_id": slice_row["slice_id"],
                "slice_type": "DATE",
                "metrics": _compact_metric(metric),
            }
        )
    for slice_row in slices["universe_slices"]:
        metric = evaluate_single_factor(
            features,
            labels,
            allowed_dates=discovery_dates,
            allowed_symbols=set(map(str, slice_row["symbols"])),
            **arguments,
        )
        evaluated.append(
            {
                "slice_id": slice_row["slice_id"],
                "slice_type": "UNIVERSE",
                "metrics": _compact_metric(metric),
            }
        )
    winsorized_final = evaluate_single_factor(
        features,
        labels,
        allowed_dates=final_dates,
        preprocessing="winsorized_1pct",
        **arguments,
    )
    imputed = _training_median_sensitivity(
        features,
        labels,
        feature_name,
        direction,
        discovery_dates,
        final_dates,
        arguments,
        float(policy["maximum_missing_rate"]),
    )
    valid_slice_values = [
        float(row["metrics"]["rank_ic_mean"])
        for row in evaluated
        if row["metrics"]["rank_ic_mean"] is not None
    ]
    subperiod_values = [
        float(row["metrics"]["rank_ic_mean"])
        for row in evaluated
        if row["slice_id"] in {"early_subperiod", "late_subperiod"}
        and row["metrics"]["rank_ic_mean"] is not None
    ]
    fold_values = [
        float(row["rank_ic_mean"])
        for row in primary["fold_test_metrics"]
        if row["rank_ic_mean"] is not None
    ]
    result: dict[str, object] = {
        "candidate_id": feature_name,
        "slice_results": evaluated,
        "robustness_positive_rate": _positive_rate(valid_slice_values),
        "subperiod_positive_rate": _positive_rate(subperiod_values),
        "fold_positive_rate": _positive_rate(fold_values),
        "raw_vs_winsorized_final_rank_ic_delta": _difference(
            dict(primary.get("final_holdout") or {}).get("rank_ic_mean"),
            winsorized_final.get("rank_ic_mean"),
        ),
        "winsorized_final": _compact_metric(winsorized_final),
        "training_median_imputation": imputed,
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _training_median_sensitivity(
    features: Sequence[Mapping[str, object]],
    labels: Sequence[Mapping[str, object]],
    feature_name: str,
    direction: int,
    discovery_dates: set[str],
    final_dates: set[str],
    arguments: Mapping[str, object],
    maximum_missing_rate: float,
) -> dict[str, object]:
    training_rows = [row for row in features if str(row["date"]) in discovery_dates]
    observed = [float(row[feature_name]) for row in training_rows if row.get(feature_name) is not None]
    if not observed:
        return {
            "status": "NOT_PERMITTED_STRUCTURAL_MISSINGNESS",
            "fit_scope": "DEVELOPMENT_ONLY",
            "metrics": None,
        }
    missing_rate = 1.0 - len(observed) / len(training_rows)
    if missing_rate > maximum_missing_rate:
        return {
            "status": "NOT_PERMITTED_EXCESS_MISSINGNESS",
            "fit_scope": "DEVELOPMENT_ONLY",
            "training_missing_rate": _clean(missing_rate),
            "metrics": None,
        }
    imputation = float(median(observed))
    transformed = []
    for row in features:
        copy = dict(row)
        if copy.get(feature_name) is None:
            copy[feature_name] = imputation
        transformed.append(copy)
    metric_arguments = dict(arguments)
    metric_arguments.pop("feature_name")
    metric_arguments.pop("direction")
    metric = evaluate_single_factor(
        transformed,
        labels,
        feature_name=feature_name,
        direction=direction,
        allowed_dates=final_dates,
        **metric_arguments,
    )
    return {
        "status": "EVALUATED_TRAINING_ONLY_IMPUTATION_SENSITIVITY",
        "fit_scope": "DEVELOPMENT_ONLY",
        "imputation_value": _clean(imputation),
        "training_missing_rate": _clean(missing_rate),
        "metrics": _compact_metric(metric),
    }


def _decide_from_records(
    candidate_id: str,
    records: Sequence[Mapping[str, object]],
    primary_horizon: int,
    policy: Mapping[str, object],
    robustness: Mapping[str, object] | None,
) -> dict[str, object]:
    primary = next(
        (row for row in records if int(row["horizon_trading_days"]) == primary_horizon),
        None,
    )
    if primary is None or primary.get("eligibility_reason"):
        reason = (
            str(primary.get("eligibility_reason"))
            if primary is not None
            else "PRIMARY_HORIZON_EVIDENCE_UNAVAILABLE"
        )
        return decide_candidate(
            candidate_id,
            {
                "eligible": False,
                "eligibility_reason": reason,
                "valid_date_count": 0,
                "observation_row_count": 0,
                "median_breadth": 0,
                "missing_rate": 1,
                "zero_variance_rate": 1,
                "symbol_concentration": 1,
                "date_concentration": 1,
                "ranking_turnover": 0,
            },
            policy,
        )
    full = primary.get("full")
    holdout = primary.get("final_holdout")
    if full is None or holdout is None or holdout.get("rank_ic_mean") is None:
        eligibility_reason = "INSUFFICIENT_FINAL_HOLDOUT_EVIDENCE"
        eligible = False
    else:
        eligibility_reason = None
        eligible = True
    horizon_values = [
        float(row["final_holdout"]["rank_ic_mean"])
        for row in records
        if row.get("final_holdout") is not None
        and row["final_holdout"].get("rank_ic_mean") is not None
    ]
    horizon_consistency = (
        sum(value > 0 for value in horizon_values) / len(records) if records else 0.0
    )
    fold_values = [
        float(row["rank_ic_mean"])
        for row in primary.get("fold_test_metrics", [])
        if row.get("rank_ic_mean") is not None
    ]
    fold_rate = _positive_rate(fold_values)
    evidence: dict[str, object] = {
        "eligible": eligible,
        "eligibility_reason": eligibility_reason,
        "valid_date_count": int(full.get("valid_date_count", 0)) if full else 0,
        "observation_row_count": int(full.get("observation_row_count", 0)) if full else 0,
        "median_breadth": float(full.get("median_breadth", 0)) if full else 0,
        "missing_rate": float(full.get("missing_rate", 1)) if full else 1,
        "zero_variance_rate": float(full.get("zero_variance_rate", 1)) if full else 1,
        "symbol_concentration": float(full.get("symbol_concentration", 1)) if full else 1,
        "date_concentration": float(full.get("date_concentration", 1)) if full else 1,
        "oos_rank_ic": _float_or_zero(holdout.get("rank_ic_mean")) if holdout else 0,
        "confidence_interval_low": (
            float(primary["confidence_interval"][0]) if primary.get("confidence_interval") else 0
        ),
        "fdr_q": float(primary.get("fdr_q") if primary.get("fdr_q") is not None else 1),
        "null_p": max(
            float(primary.get("discovery_null_p") if primary.get("discovery_null_p") is not None else 1),
            float(primary.get("final_holdout_null_p") if primary.get("final_holdout_null_p") is not None else 1),
        ),
        "sign_stability": (
            float(robustness.get("fold_positive_rate") or 0)
            if robustness is not None
            else float(fold_rate or 0)
        ),
        "subperiod_positive_rate": (
            float(robustness.get("subperiod_positive_rate") or 0)
            if robustness is not None
            else float(fold_rate or 0)
        ),
        "robustness_positive_rate": (
            float(robustness.get("robustness_positive_rate") or 0)
            if robustness is not None
            else float(fold_rate or 0)
        ),
        "horizon_consistency": _clean(horizon_consistency),
        "ranking_turnover": _float_or_zero(holdout.get("ranking_turnover")) if holdout else 0,
    }
    return decide_candidate(candidate_id, evidence, policy)


def _governed_decision_summary(
    decision: Mapping[str, object],
    *,
    feature_or_model_version: str,
    horizon: int,
    records: Sequence[Mapping[str, object]],
    provenance: Mapping[str, object],
) -> dict[str, object]:
    evidence = dict(decision["evidence"])
    reason_codes = tuple(map(str, decision["reason_codes"]))
    warnings = tuple(map(str, decision["warnings"]))
    result = dict(decision)
    result.pop("checksum", None)
    result.update(
        {
            "feature_or_model_version": feature_or_model_version,
            "horizon": horizon,
            "research_status": str(decision["status"]),
            "evidence_summary": {
                "eligible": evidence.get("eligible") is True,
                "eligibility_reason": evidence.get("eligibility_reason"),
                "reason_codes": reason_codes,
            },
            "warning_codes": warnings,
            "sample_counts": {
                "valid_date_count": int(evidence.get("valid_date_count", 0)),
                "observation_row_count": int(evidence.get("observation_row_count", 0)),
                "median_breadth": float(evidence.get("median_breadth", 0)),
            },
            "metric_summary": {
                "oos_rank_ic": evidence.get("oos_rank_ic"),
                "confidence_interval_low": evidence.get("confidence_interval_low"),
                "fdr_q": evidence.get("fdr_q"),
                "ranking_turnover": evidence.get("ranking_turnover"),
            },
            "null_comparison": {
                "conservative_p": evidence.get("null_p"),
                "method": "MAX_DISCOVERY_AND_FINAL_DATE_LEVEL_NULL_P",
            },
            "stability_summary": {
                "sign_stability": evidence.get("sign_stability"),
                "subperiod_positive_rate": evidence.get("subperiod_positive_rate"),
                "robustness_positive_rate": evidence.get("robustness_positive_rate"),
                "horizon_consistency": evidence.get("horizon_consistency"),
            },
            "provenance": {
                **dict(provenance),
                "evidence_checksums": tuple(
                    str(record["checksum"])
                    for record in sorted(
                        records, key=lambda row: int(row["horizon_trading_days"])
                    )
                ),
                "policy_version": str(decision["policy_version"]),
            },
        }
    )
    validate_research_output_fields(result)
    result["checksum"] = canonical_checksum(result)
    return result


def _ineligible_metric_record(
    candidate_id: str,
    horizon: int,
    key: str,
    reason: str,
    *,
    candidate_type: str = "REGIME_CONTEXT",
) -> dict[str, object]:
    result: dict[str, object] = {
        "candidate_id": candidate_id,
        "candidate_type": candidate_type,
        "candidate_key": key,
        "horizon_trading_days": horizon,
        "eligibility_reason": reason,
        "full": None,
        "discovery": None,
        "final_holdout": None,
        "fold_test_metrics": [],
        "confidence_interval": None,
        "discovery_null_p": None,
        "final_holdout_null_p": None,
        "fdr_q": None,
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _score_feature_rows(
    rows: Sequence[Mapping[str, object]], score_field: str
) -> list[dict[str, object]]:
    output = []
    for row in rows:
        feature: dict[str, object] = {
            "date": row["date"],
            "symbol": row["symbol"],
            score_field: row.get(score_field) if row.get("score_status") == "SCORED" else None,
        }
        feature["checksum"] = canonical_checksum(feature)
        output.append(feature)
    return output


def _model_score_feature_rows(
    rows: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    output = []
    for row in rows:
        feature: dict[str, object] = {
            "date": row["date"],
            "symbol": row["symbol"],
            "model_score": row["model_score"],
        }
        feature["checksum"] = canonical_checksum(feature)
        output.append(feature)
    return output


def _compact_metric(metric: Mapping[str, object]) -> dict[str, object]:
    compact = dict(metric)
    compact["by_date"] = [
        {key: value for key, value in row.items() if key != "rows"}
        for row in metric["by_date"]
    ]
    compact["checksum"] = canonical_checksum(
        {key: value for key, value in compact.items() if key != "checksum"}
    )
    return compact


def _attach_fdr(
    records: Sequence[dict[str, object]], adjusted: Mapping[str, float]
) -> None:
    for record in records:
        record["fdr_q"] = adjusted.get(str(record["candidate_key"]))
        record["checksum"] = canonical_checksum(
            {key: value for key, value in record.items() if key != "checksum"}
        )


def _data_audit(
    bundle: HistoricalBundle,
    features: Sequence[Mapping[str, object]],
    labels: Sequence[Mapping[str, object]],
    eligible_dates: Sequence[str],
    horizons: Sequence[int],
) -> dict[str, object]:
    missingness = {
        feature: _clean(
            sum(row.get(feature) is None for row in features) / len(features)
        )
        for feature in FEATURE_COLUMNS
    }
    label_counts: dict[str, object] = {}
    for horizon in horizons:
        horizon_rows = [
            row for row in labels if int(row["horizon_trading_days"]) == horizon
        ]
        available = [row for row in horizon_rows if row["label_status"] == "AVAILABLE"]
        missing_reasons = Counter(
            str(row["missing_reason"])
            for row in horizon_rows
            if row["label_status"] != "AVAILABLE"
        )
        label_counts[str(horizon)] = {
            "available": len(available),
            "missing": len(horizon_rows) - len(available),
            "available_feature_date_start": min(
                (str(row["feature_date"]) for row in available), default=None
            ),
            "available_feature_date_end": max(
                (str(row["feature_date"]) for row in available), default=None
            ),
            "realizable_label_date_start": min(
                (str(row["label_date"]) for row in available), default=None
            ),
            "realizable_label_date_end": max(
                (str(row["label_date"]) for row in available), default=None
            ),
            "missing_reason_counts": dict(sorted(missing_reasons.items())),
        }
    symbols_by_date = Counter(str(row["date"]) for row in features)
    eligible_breadths = [symbols_by_date[str(trade_date)] for trade_date in eligible_dates]
    breadth_distribution = Counter(eligible_breadths)
    result: dict[str, object] = {
        "status": "PASS_WITH_DISCLOSED_LIMITATIONS",
        "snapshot_id": bundle.snapshot.snapshot_id,
        "source_checksum": bundle.snapshot.source_checksum,
        "adjustment": bundle.snapshot.adjustment,
        "metadata": dict(bundle.metadata),
        "feature_row_count": len(features),
        "feature_date_start": min(str(row["date"]) for row in features),
        "feature_date_end": max(str(row["date"]) for row in features),
        "eligible_feature_date_start": min(map(str, eligible_dates)),
        "eligible_feature_date_end": max(map(str, eligible_dates)),
        "eligible_signal_date_count": len(eligible_dates),
        "eligible_symbol_breadth": {
            "minimum": min(eligible_breadths),
            "median": _clean(float(median(eligible_breadths))),
            "maximum": max(eligible_breadths),
            "distribution": {
                str(count): frequency
                for count, frequency in sorted(breadth_distribution.items())
            },
        },
        "feature_missingness": missingness,
        "label_counts_by_horizon": label_counts,
        "no_silent_amount_zero_fill": True,
        "survivorship_risk_disclosed": True,
        "full_ohlcv_available": False,
    }
    result["checksum"] = canonical_checksum(result)
    return result


def _validate_governance(config: Mapping[str, object]) -> None:
    governance = dict(config["governance"])
    if governance.get("production_ready") is not False or governance.get("ready_factor_count") != 0:
        raise ValueError("goal12_pipeline_production_lock_violation")


def _positive_rate(values: Sequence[float]) -> float | None:
    return _clean(sum(value > 0 for value in values) / len(values)) if values else None


def _difference(left: object, right: object) -> float | None:
    if left is None or right is None:
        return None
    return _clean(float(right) - float(left))


def _float_or_zero(value: object) -> float:
    return 0.0 if value is None else float(value)


def _seed(seed: int, label: str) -> int:
    digest = hashlib.sha256(f"{seed}:{label}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def _clean(value: float) -> float:
    if not math.isfinite(value):
        raise ValueError("non_finite_goal12_pipeline_metric")
    rounded = round(value, 12)
    return 0.0 if rounded == 0 else rounded
