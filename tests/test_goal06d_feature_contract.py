from __future__ import annotations

import json
from pathlib import Path

from ashare_premarket.models.goal06d import validate_feature_contract

ROOT = Path(__file__).resolve().parents[1]


def _contract() -> dict[str, object]:
    return json.loads((ROOT / "configs/models/goal06d_feature_contract.yaml").read_text(encoding="utf-8"))


def test_goal06d_feature_contract_uses_only_pit_safe_columns() -> None:
    contract = _contract()
    features = set(contract["feature_columns"])
    forbidden = set(contract["forbidden_feature_columns"])
    patterns = tuple(contract["forbidden_feature_name_patterns"])

    assert "excess_fwd_3d_return" == contract["primary_target"]
    assert features == {
        "market_trend_5d",
        "stock_momentum_5d",
        "stock_momentum_20d",
        "stock_gap_signal",
        "stock_volatility_20d",
        "turnover_proxy",
        "relative_strength_20d",
        "source_health_score",
        "source_count",
    }
    assert not features & forbidden
    assert all(not any(pattern in feature.lower() for pattern in patterns) for feature in features)


def test_goal06d_feature_audit_blocks_label_and_forward_return_features() -> None:
    contract = _contract()
    contract["feature_columns"] = ["market_trend_5d", "excess_fwd_3d_return", "label_ready"]

    audit = validate_feature_contract(ROOT, [], contract)

    assert audit["status"] == "BLOCKED"
    assert any("forbidden feature column selected: excess_fwd_3d_return" in item for item in audit["failures"])
    assert any("forbidden feature column selected: label_ready" in item for item in audit["failures"])
    assert any("forbidden feature name pattern selected: excess_fwd_3d_return" in item for item in audit["failures"])
    assert any("forbidden feature name pattern selected: label_ready" in item for item in audit["failures"])
