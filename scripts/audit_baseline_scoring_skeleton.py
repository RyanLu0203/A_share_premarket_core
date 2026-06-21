from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.scoring.baseline import audit_baseline_scoring_skeleton


if __name__ == "__main__":
    raise SystemExit(0 if audit_baseline_scoring_skeleton(ROOT) else 1)
