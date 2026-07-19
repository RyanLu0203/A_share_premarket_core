from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.quant_foundation.features import FEATURE_COLUMNS

CONFIG_PATH = "configs/quant/goal12_alpha_validation_v1.json"


def load_goal12_config(root: Path) -> dict[str, object]:
    config = json.loads((root / CONFIG_PATH).read_text(encoding="utf-8"))
    if config.get("schema_version") != "1.0" or config.get("research_only") is not True:
        raise ValueError("invalid_goal12_config_contract")
    governance = dict(config.get("governance", {}))
    if (
        governance.get("production_ready") is not False
        or governance.get("ready_factor_count") != 0
        or governance.get("recommendation_outputs_allowed") is not False
        or governance.get("write_routes_allowed") != 0
        or governance.get("final_pr_state") != "DRAFT"
    ):
        raise ValueError("goal12_production_lock_violation")
    candidates = dict(config.get("candidate_contract", {}))
    directions = dict(candidates.get("feature_directions", {}))
    contexts = tuple(map(str, candidates.get("regime_context_features", ())))
    if (
        set(directions) | set(contexts) != set(FEATURE_COLUMNS)
        or set(directions) & set(contexts)
        or any(int(direction) not in {-1, 1} for direction in directions.values())
    ):
        raise ValueError("goal12_candidate_registry_mismatch")
    if tuple(candidates.get("combined_candidates", ())) != (
        "interpretable_alpha",
        "risk_adjusted_alpha",
        "fixed_linear_ranker",
    ):
        raise ValueError("goal12_combined_candidate_registry_mismatch")
    labels = dict(config.get("labels", {}))
    horizons = tuple(int(value) for value in labels.get("horizons", ()))
    if horizons != (1, 5, 20) or int(labels.get("primary_horizon", -1)) not in horizons:
        raise ValueError("goal12_label_config_mismatch")
    splits = dict(config.get("splits", {}))
    if (
        int(splits.get("maximum_label_horizon", -1)) != max(horizons)
        or splits.get("mode") != "EXPANDING_PURGED_CHRONOLOGICAL"
    ):
        raise ValueError("goal12_split_config_mismatch")
    robustness = dict(config.get("robustness", {}))
    if (
        int(robustness.get("expanding_window_minimum_dates", 0)) <= 0
        or int(robustness.get("expanding_window_step", 0)) <= 0
    ):
        raise ValueError("goal12_robustness_config_mismatch")
    policy = dict(config.get("decision_policy", {}))
    if policy.get("version") != "goal12_research_decision_policy_v1":
        raise ValueError("goal12_decision_policy_version_mismatch")
    return config
