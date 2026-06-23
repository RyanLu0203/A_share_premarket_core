from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_goal07a_maps_required_upstream_warnings_to_domains() -> None:
    payload = json.loads((ROOT / "configs/risk/goal07a_upstream_warning_mapping.yaml").read_text(encoding="utf-8"))
    mapping = {row["warning_code"]: row["risk_domain_id"] for row in payload["mappings"]}
    assert mapping == {
        "calibration_not_reliable_for_thresholding": "calibration_risk",
        "feature_sign_instability_bounded": "feature_stability_risk",
        "provider_source_concentration_disclosed": "provider_concentration_risk",
        "selected_score_variant_weak_rank_signal": "model_confidence_risk",
        "single_provider_mode_akshare_direct": "provider_concentration_risk",
        "weak_target_horizon_rank_signal": "target_horizon_risk",
        "target_horizon_calibration_warning": "calibration_risk",
    }
    assert all(row["goal07a_action"] == "document_only_no_risk_tag_assignment" for row in payload["mappings"])
