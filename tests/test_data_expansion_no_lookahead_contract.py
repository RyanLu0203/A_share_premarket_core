from __future__ import annotations

from pathlib import Path

from ashare_premarket.audit.common import forbidden_lookahead_columns
from ashare_premarket.data_expansion.goal_data_expansion_research01 import (
    FALSE_BOUNDARY_KEYS,
    SCHEMA_CONTRACTS,
    TRUE_MARKER_KEYS,
    evaluate_goal_data_expansion_research01,
)

ROOT = Path(__file__).resolve().parents[1]


def test_data_expansion_schemas_exclude_lookahead_and_factor_evaluation_fields() -> None:
    for contract in SCHEMA_CONTRACTS.values():
        assert forbidden_lookahead_columns(contract.fields) == []
        forbidden_tokens = {"ic", "rank_ic", "label_ready", "future_return_1d", "future_return_5d"}
        assert not forbidden_tokens.intersection({field.lower() for field in contract.fields})


def test_data_expansion_manifest_preserves_no_lookahead_and_boundary_flags(monkeypatch) -> None:
    monkeypatch.delenv("ASHARE_ALLOW_AKSHARE_NETWORK", raising=False)
    result = evaluate_goal_data_expansion_research01(ROOT)
    manifest = result["manifest"]

    assert result["run_mode"] == "offline_dry_run"
    assert manifest["fresh_clone_replay_requires_live_network"] is False
    assert manifest["recommended_next_goal"] == "GOAL-REGIME-LABEL-RESEARCH-02-EXPANDED-MARKET-REGIME-LABEL-REFINEMENT-GATE"
    for key in FALSE_BOUNDARY_KEYS:
        assert manifest[key] is False
    for key in TRUE_MARKER_KEYS:
        assert manifest[key] is True

