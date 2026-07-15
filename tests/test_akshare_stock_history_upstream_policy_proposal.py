from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "configs/providers/akshare_stock_history_upstream_policy_proposal.yaml"


def _proposal() -> dict[str, object]:
    return json.loads(PROPOSAL.read_text(encoding="utf-8"))


def test_secondary_upstream_proposal_is_explicitly_inactive() -> None:
    proposal = _proposal()
    secondary = proposal["proposed_secondary_upstream"]

    assert proposal["status"] == "proposal_only_not_activated"
    assert secondary["selection_status"] == "candidate_only_not_callable_by_runtime"
    assert proposal["failure_and_retry_policy"]["automatic_secondary_activation_allowed"] is False
    assert proposal["failure_and_retry_policy"]["silent_fallback_allowed"] is False


def test_secondary_upstream_proposal_preserves_full_evidence_contract() -> None:
    proposal = _proposal()
    coverage = proposal["freshness_and_coverage"]
    consistency = proposal["source_consistency_checks"]

    assert proposal["primary_upstream"]["function"] == "stock_zh_a_hist"
    assert proposal["proposed_secondary_upstream"]["function"] == "stock_zh_a_hist_tx"
    assert coverage["required_trade_date"] == "current_resolved_t_minus_one"
    assert coverage["required_symbol_coverage"] == "all_existing_contract_required_symbols"
    assert coverage["partial_snapshot_allowed"] is False
    assert consistency["bounded_overlap_required"] is True
    assert consistency["material_ohlc_conflict_policy"] == "quarantine_and_block_snapshot"
    assert consistency["volume_amount_semantics"] == "must_be_resolved_before_activation"
