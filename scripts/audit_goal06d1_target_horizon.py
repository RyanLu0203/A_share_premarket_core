from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.models.goal06d1 import audit_goal06d1_target_horizon


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal06d1_target_horizon(ROOT) else 1)
