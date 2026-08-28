from _bootstrap import ROOT
from ashare_premarket.providers.liquidity_readiness_batch import run_goal


if __name__ == "__main__":
    raise SystemExit(0 if run_goal(ROOT) else 1)
