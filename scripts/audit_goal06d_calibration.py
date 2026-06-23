from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.models.goal06d import audit_goal06d_calibration


if __name__ == "__main__":
    raise SystemExit(0 if audit_goal06d_calibration(ROOT) else 1)
