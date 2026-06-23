from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.models.goal06d import run_goal06d_model_comparison_calibration


if __name__ == "__main__":
    raise SystemExit(0 if run_goal06d_model_comparison_calibration(ROOT) else 1)
