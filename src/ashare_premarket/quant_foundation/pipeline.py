from __future__ import annotations

from typing import Mapping, Sequence

from ashare_premarket.quant_foundation.alpha import build_interpretable_alpha
from ashare_premarket.quant_foundation.contracts import GovernedSnapshot, canonical_checksum
from ashare_premarket.quant_foundation.evaluation import evaluate_rankings
from ashare_premarket.quant_foundation.features import build_feature_rows
from ashare_premarket.quant_foundation.linear_ranker import run_chronological_linear_ranker


def run_quant_intelligence_pipeline(
    snapshot: GovernedSnapshot,
    label_rows: Sequence[Mapping[str, object]],
    config: Mapping[str, object],
) -> dict[str, object]:
    features = build_feature_rows(snapshot, config)
    alpha = build_interpretable_alpha(features, config)
    linear = run_chronological_linear_ranker(features, label_rows, config)
    evaluation = evaluate_rankings(features, alpha, linear["scores"], label_rows, config)
    result: dict[str, object] = {
        "goal_id": "GOAL-11",
        "status": "COMPLETE_RESEARCH_ONLY",
        "research_only": True,
        "source_snapshot_id": snapshot.snapshot_id,
        "source_snapshot_row_checksum": snapshot.row_checksum,
        "generation_timestamp": snapshot.generation_timestamp,
        "code_commit": snapshot.code_commit,
        "feature_version": config["feature_version"],
        "feature_rows": features,
        "alpha_rows": alpha,
        "linear_ranker": linear,
        "evaluation": evaluation,
        "ready_factor_count": 0,
        "production_model_promoted": False,
        "generated_artifact_policy": "LOCAL_IGNORED_ONLY",
    }
    result["checksum"] = canonical_checksum(result)
    return result
