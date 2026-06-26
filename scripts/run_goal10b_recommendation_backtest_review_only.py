from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.backtest.goal10b import run_goal10b_recommendation_backtest_review_only


if __name__ == "__main__":
    raise SystemExit(0 if run_goal10b_recommendation_backtest_review_only(ROOT) else 1)

