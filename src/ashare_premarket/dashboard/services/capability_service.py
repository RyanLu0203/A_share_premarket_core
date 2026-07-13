from __future__ import annotations

from collections import Counter
from typing import Any

from ashare_premarket.dashboard.repositories.base import WorkspaceRepositoryBase
from ashare_premarket.domain.quant_contracts.factor_evidence import LockedFactorEvidenceProvider


class CapabilityService(WorkspaceRepositoryBase):
    def quant_capabilities(self) -> dict[str, Any]:
        factor_evidence = LockedFactorEvidenceProvider().snapshot()
        rerun = self.store.json("outputs/audits/goal_factor_readiness_rerun02_manifest.json")
        quant04 = self.store.json("outputs/audits/goal_quant_research04_manifest.json")
        statuses = Counter(row.get("overall_factor_status") for row in self.store.csv("outputs/research/goal_quant_research04_factor_overall_status.csv"))
        decision_reasons = {
            row.get("candidate_id", ""): row
            for row in self.store.csv("outputs/research/goal_factor_readiness_rerun02_readiness_decision_reasons.csv")
        }
        candidate_rows = [
            {**row, **decision_reasons.get(row.get("candidate_id", ""), {})}
            for row in self.store.csv("outputs/research/goal_factor_readiness_rerun02_factor_readiness_status.csv")
        ]
        return {
            "ready_factor_count": factor_evidence.ready_factor_count,
            "alpha_overview_state": factor_evidence.readiness_status,
            "factor_monitor_state": factor_evidence.readiness_status,
            "ic_rankic_lab_state": "BLOCKED_PENDING_READY_FACTOR",
            "factor_correlation_state": "LOCKED_NO_READY_FACTORS",
            "candidate_diagnostics_state": "LOCKED_READ_ONLY_HISTORICAL",
            "recommendation_tiering_state": "locked_future",
            "issue_10_state": "locked",
            "candidate_readiness": {
                "evaluated": int(rerun.get("candidates_evaluated", 0)),
                "ready": int(rerun.get("ready_factor_count", 0)),
                "conditionally_useful": int(rerun.get("conditionally_useful_candidate_count", 0)),
                "not_ready": int(rerun.get("candidates_evaluated", 0)) - int(rerun.get("ready_factor_count", 0)),
            },
            "quant04_refined_factors": {
                "evaluated": int(quant04.get("evaluated_refined_factor_count", 0)),
                "ready": int(quant04.get("ready_factor_count", 0)),
                "conditionally_useful": statuses.get("conditionally_useful", 0),
                "not_ready": statuses.get("not_ready", 0),
            },
            "unlock_conditions": ["scientifically ready factor evidence", "explicit owner authorization"],
            "factor_table_contract": ["factor", "IC", "RankIC", "IR", "sign stability", "horizon stability", "regime consistency", "OOS status", "readiness"],
            "candidate_rows": candidate_rows,
            "market_regime_context_available": True,
            "factor_regime_analysis_locked": True,
            "research_only": True,
        }
