from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import (
    run_goal_daily_incremental_evidence_refresh01,
)


if __name__ == "__main__":
    raise SystemExit(0 if run_goal_daily_incremental_evidence_refresh01(ROOT, print_summary=True) else 1)
