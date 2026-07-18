from __future__ import annotations

import json
from pathlib import Path

import pytest

from ashare_premarket.alpha_validation.config import CONFIG_PATH, load_goal12_config
from ashare_premarket.quant_foundation.features import FEATURE_COLUMNS

ROOT = Path(__file__).resolve().parents[2]


def test_repository_config_is_complete_predeclared_and_production_locked() -> None:
    config = load_goal12_config(ROOT)
    candidate = dict(config["candidate_contract"])

    assert set(candidate["feature_directions"]) | set(candidate["regime_context_features"]) == set(FEATURE_COLUMNS)
    assert set(candidate["feature_directions"]).isdisjoint(candidate["regime_context_features"])
    assert config["labels"]["horizons"] == [1, 5, 20]
    assert config["labels"]["primary_horizon"] == 5
    assert config["splits"]["maximum_label_horizon"] == 20
    assert config["robustness"]["expanding_window_minimum_dates"] == 126
    assert config["robustness"]["expanding_window_step"] == 63
    assert config["governance"]["production_ready"] is False
    assert config["governance"]["ready_factor_count"] == 0
    assert config["governance"]["write_routes_allowed"] == 0


def test_config_fails_closed_if_governance_or_candidate_coverage_is_relaxed(tmp_path: Path) -> None:
    source = json.loads((ROOT / CONFIG_PATH).read_text(encoding="utf-8"))
    path = tmp_path / CONFIG_PATH
    path.parent.mkdir(parents=True)
    source["governance"]["production_ready"] = True
    path.write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(ValueError, match="goal12_production_lock_violation"):
        load_goal12_config(tmp_path)

    source["governance"]["production_ready"] = False
    source["candidate_contract"]["feature_directions"].pop("return_1d")
    path.write_text(json.dumps(source), encoding="utf-8")
    with pytest.raises(ValueError, match="goal12_candidate_registry_mismatch"):
        load_goal12_config(tmp_path)
