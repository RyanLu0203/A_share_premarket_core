from _bootstrap import ROOT
from ashare_premarket.providers.liquidity_source_acceptance import audit_goal


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal(ROOT) else 1)
