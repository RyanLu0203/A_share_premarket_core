from __future__ import annotations

from _bootstrap import ROOT
from ashare_premarket.validation.gates import run_goal06b_regression_suite


if __name__ == "__main__":
    raise SystemExit(0 if run_goal06b_regression_suite(ROOT) else 1)
