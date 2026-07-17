from __future__ import annotations

from pathlib import Path

import pytest

from ashare_premarket.quant_foundation.alpha import build_interpretable_alpha
from ashare_premarket.quant_foundation.contracts import FORBIDDEN_ACTION_FIELDS, canonical_checksum
from ashare_premarket.quant_foundation.features import build_feature_rows, load_feature_config
from .conftest import make_snapshot

ROOT = Path(__file__).resolve().parents[2]


def _latest(rows: list[dict[str, object]], symbol: str) -> dict[str, object]:
    return [row for row in rows if row["symbol"] == symbol][-1]


def test_interpretable_alpha_uses_prespecified_components_and_second_risk_adjustment() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    scores = build_interpretable_alpha(features, config)
    row = _latest(scores, "600036.SH")
    components = row["component_scores"]

    assert row["score_status"] == "SCORED"
    assert row["alpha_version"] == "goal11_interpretable_alpha_v1"
    assert row["risk_version"] == "goal11_risk_penalty_v1"
    assert row["source_feature_checksum"] == _latest(features, "600036.SH")["checksum"]
    assert row["alpha_score"] == pytest.approx(
        components["momentum"]
        + components["trend"]
        + components["volume_strength"]
        - row["risk_penalty"]
    )
    assert row["risk_penalty"] == pytest.approx(
        0.4 * components["volatility_risk"]
        + 0.25 * components["drawdown_risk"]
        + 0.2 * components["instability_risk"]
        + 0.15 * components["liquidity_risk"]
    )
    assert row["risk_adjusted_score"] == pytest.approx(
        row["alpha_score"] - row["risk_penalty"]
    )
    assert row["second_stage_risk_adjustment_disclosed"] is True
    assert row["checksum"] == canonical_checksum(
        {key: value for key, value in row.items() if key != "checksum"}
    )


def test_alpha_abstains_when_required_volume_or_risk_evidence_is_missing() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(
        make_snapshot(include_ohlcv=False, include_index=False), config
    )
    row = _latest(build_interpretable_alpha(features, config), "600036.SH")

    assert row["score_status"] == "ABSTAINED"
    assert row["alpha_score"] is None
    assert row["risk_penalty"] is None
    assert row["risk_adjusted_score"] is None
    assert "MISSING_REQUIRED_ALPHA_FEATURE:ABNORMAL_VOLUME_20D" in row["abstention_reasons"]
    assert tuple(row["abstention_reasons"]) == tuple(sorted(row["abstention_reasons"]))


def test_alpha_is_deterministic_non_actionable_and_point_in_time() -> None:
    config = load_feature_config(ROOT)
    base_features = build_feature_rows(make_snapshot(), config)
    shocked_features = build_feature_rows(
        make_snapshot(future_price_shock_after=70), config
    )
    base_scores = build_interpretable_alpha(base_features, config)
    assert base_scores == build_interpretable_alpha(base_features, config)

    cut_date = str(base_scores[70 * 2]["date"])
    base = [row for row in base_scores if row["date"] == cut_date]
    shocked = [row for row in build_interpretable_alpha(shocked_features, config) if row["date"] == cut_date]
    assert [row["alpha_score"] for row in base] == [row["alpha_score"] for row in shocked]
    assert not any(FORBIDDEN_ACTION_FIELDS & set(row) for row in base_scores)


def test_alpha_rejects_tampered_feature_lineage() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    features[-1]["momentum_20d"] = 99.0
    with pytest.raises(ValueError, match="feature_row_checksum_mismatch"):
        build_interpretable_alpha(features, config)


def test_alpha_rejects_mixed_feature_snapshot_lineage() -> None:
    config = load_feature_config(ROOT)
    features = build_feature_rows(make_snapshot(), config)
    features[-1]["source_snapshot_id"] = "different-governed-snapshot"
    features[-1]["checksum"] = canonical_checksum(
        {key: value for key, value in features[-1].items() if key != "checksum"}
    )

    with pytest.raises(ValueError, match="mixed_feature_snapshot_lineage"):
        build_interpretable_alpha(features, config)
