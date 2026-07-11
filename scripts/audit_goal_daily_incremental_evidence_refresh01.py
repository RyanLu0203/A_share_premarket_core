from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.daily_refresh.goal_daily_incremental_evidence_refresh01 import (
    audit_goal_daily_incremental_evidence_refresh01,
)


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal_daily_incremental_evidence_refresh01(ROOT) else 1)
