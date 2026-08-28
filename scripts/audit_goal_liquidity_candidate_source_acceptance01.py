from _bootstrap import ROOT
from ashare_premarket.research.liquidity_candidate_source_contract import audit_goal


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal(ROOT) else 1)
