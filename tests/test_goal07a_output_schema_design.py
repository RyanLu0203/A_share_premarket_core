from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_output_schema_has_only_allowed_future_fields() -> None:
    schema = json.loads((ROOT / "configs/risk/goal07a_future_risk_overlay_output_schema.yaml").read_text(encoding="utf-8"))
    allowed = set(schema["allowed_future_schema_fields"])
    forbidden = set(schema["forbidden_schema_fields"])
    assert not (allowed & forbidden)
    assert {"data_quality_risk_tag", "overall_risk_state", "risk_governance_flags", "review_only"} <= allowed
    assert schema["empty_schema_sample"]["row_count"] == 0


def test_goal07a_output_schema_excludes_recommendation_position_and_tradable_fields() -> None:
    schema = json.loads((ROOT / "configs/risk/goal07a_future_risk_overlay_output_schema.yaml").read_text(encoding="utf-8"))
    allowed = set(schema["allowed_future_schema_fields"])
    forbidden = {
        "buy",
        "sell",
        "hold",
        "recommended_position",
        "position_weight",
        "portfolio_weight",
        "risk_score",
        "final_score",
        "final_rank",
        "tradable_rank",
        "trade_signal",
        "order_action",
        "broker_instruction",
    }
    assert forbidden <= set(schema["forbidden_schema_fields"])
    assert not forbidden & allowed
